import hashlib
import hmac
import json
import uuid
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from modules.learning.models import (
    Course,
    Lesson,
    Progress,
    ProgressState,
    Assignment,
    Submission,
    SubmissionState,
    CodeAssessment,
    AssessmentResult,
    CertificateTemplate,
    CourseCertificate,
    CourseCertificateStatus,
    CertificateVerificationRecord,
)


def compute_canonical_verification_hash(
    tenant_id: str,
    course_id: str,
    student_id: str,
    certificate_number: str,
    final_score: Decimal,
    template_version: int,
    key_version: int,
    issued_at_iso: str,
    signing_key: str,
) -> str:
    canonical_payload = {
        "tenant_id": str(tenant_id),
        "course_id": str(course_id),
        "student_id": str(student_id),
        "certificate_number": str(certificate_number),
        "final_score": f"{final_score:.2f}",
        "template_version": int(template_version),
        "key_version": int(key_version),
        "issued_at_iso": str(issued_at_iso),
    }
    encoded_payload = json.dumps(canonical_payload, sort_keys=True).encode("utf-8")
    return hmac.new(
        key=signing_key.encode("utf-8"),
        msg=encoded_payload,
        digestmod=hashlib.sha256,
    ).hexdigest()


class CourseCompletionEvaluator:
    @classmethod
    def evaluate(cls, tenant_id, course_id, student_id):
        # 1. Non-optional published lessons completion check
        lessons = Lesson.objects.filter(
            tenant_id=tenant_id,
            course_id=course_id,
            state="published",
        )
        total_mandatory_lessons = lessons.count()
        if total_mandatory_lessons == 0:
            completed_mandatory_lessons = 0
        else:
            completed_mandatory_lessons = Progress.objects.filter(
                tenant_id=tenant_id,
                student_id=student_id,
                lesson__in=lessons,
                state=ProgressState.COMPLETED,
            ).values("lesson_id").distinct().count()

        lessons_passed = (completed_mandatory_lessons == total_mandatory_lessons)

        # 2. Assignments & Mentor Review check
        assignments = Assignment.objects.filter(
            tenant_id=tenant_id,
            lesson__course_id=course_id,
            state="published",
        )
        total_assignments = assignments.count()
        assignments_passed = True
        avg_assignment_score = Decimal("0.00")

        if total_assignments > 0:
            reviewed_submissions = Submission.objects.filter(
                tenant_id=tenant_id,
                assignment__in=assignments,
                student_id=student_id,
                state=SubmissionState.REVIEWED,
            )
            reviewed_count = reviewed_submissions.values("assignment_id").distinct().count()
            if reviewed_count < total_assignments:
                assignments_passed = False
            else:
                # Calculate average assignment score
                total_score = sum((sub.score or Decimal("0.00")) for sub in reviewed_submissions)
                avg_assignment_score = Decimal(str(total_score / Decimal(str(total_assignments))))

        # 3. Code Assessments check
        assessments = CodeAssessment.objects.filter(
            tenant_id=tenant_id,
            lesson__course_id=course_id,
            is_active=True,
        )
        total_assessments = assessments.count()
        assessments_passed = True
        avg_assessment_score = Decimal("0.00")

        if total_assessments > 0:
            passed_results = AssessmentResult.objects.filter(
                tenant_id=tenant_id,
                assessment__in=assessments,
                student_id=student_id,
                is_passed=True,
                is_final=True,
            )
            passed_count = passed_results.values("assessment_id").distinct().count()
            if passed_count < total_assessments:
                assessments_passed = False
            else:
                total_score = sum((res.score or Decimal("0.00")) for res in passed_results)
                avg_assessment_score = Decimal(str(total_score / Decimal(str(total_assessments))))

        # 4. Weighted Final Score computation
        if total_assignments > 0 and total_assessments > 0:
            w_assign = Decimal("0.40")
            w_assess = Decimal("0.60")
            final_score = (w_assign * avg_assignment_score) + (w_assess * avg_assessment_score)
        elif total_assignments > 0:
            final_score = avg_assignment_score
        elif total_assessments > 0:
            final_score = avg_assessment_score
        else:
            final_score = Decimal("100.00") if lessons_passed else Decimal("0.00")

        is_eligible = (lessons_passed and assignments_passed and assessments_passed)

        snapshot = {
            "total_mandatory_lessons": total_mandatory_lessons,
            "completed_mandatory_lessons": completed_mandatory_lessons,
            "total_assignments": total_assignments,
            "avg_assignment_score": f"{avg_assignment_score:.2f}",
            "total_assessments": total_assessments,
            "avg_assessment_score": f"{avg_assessment_score:.2f}",
            "final_score": f"{final_score:.2f}",
            "policy_version": 1,
        }

        return {
            "is_eligible": is_eligible,
            "final_score": final_score,
            "snapshot": snapshot,
        }


class CertificateIssuanceService:
    @classmethod
    def issue_certificate(cls, tenant, course_id, student_id, source_event_id):
        with transaction.atomic():
            # 1. Check existing certificate by source_event_id (Idempotent replay return)
            existing = CourseCertificate.objects.filter(
                tenant=tenant,
                source_event_id=source_event_id,
            ).first()
            if existing:
                return existing, False

            # 2. Check active certificate uniqueness
            active_cert = CourseCertificate.objects.filter(
                tenant=tenant,
                course_id=course_id,
                student_id=student_id,
                status=CourseCertificateStatus.ISSUED,
            ).select_for_update().first()
            if active_cert:
                return active_cert, False

            # 3. Fetch active template
            template = CertificateTemplate.objects.filter(
                tenant=tenant,
                course_id=course_id,
                is_active=True,
            ).order_by("-version").first()
            if not template:
                raise ValidationError("No active CertificateTemplate found for course.")

            # 4. Evaluate completion
            evaluation = CourseCompletionEvaluator.evaluate(
                tenant_id=tenant.id,
                course_id=course_id,
                student_id=student_id,
            )
            if not evaluation["is_eligible"]:
                raise ValidationError("Student has not completed all course requirements.")

            if evaluation["final_score"] < template.min_score_percentage:
                raise ValidationError(
                    f"Final score {evaluation['final_score']} is below passing threshold {template.min_score_percentage}."
                )

            # 5. Mint certificate number and verification digest
            tenant_slug = getattr(tenant, "slug", "TENANT")[:8].upper()
            year = timezone.now().strftime("%Y")
            cert_uuid_hex = uuid.uuid4().hex[:8].upper()
            certificate_number = f"CERT-{tenant_slug}-{year}-{cert_uuid_hex}"

            cert = CourseCertificate.objects.create(
                tenant=tenant,
                course_id=course_id,
                template=template,
                student_id=student_id,
                completion_round=1,
                certificate_number=certificate_number,
                verification_hash="PENDING",
                status=CourseCertificateStatus.ISSUED,
                final_score=evaluation["final_score"],
                completion_snapshot=evaluation["snapshot"],
                source_event_id=source_event_id,
            )

            signing_key = getattr(tenant, "signing_key", "default-signing-key-32-chars-long!")
            verification_hash = compute_canonical_verification_hash(
                tenant_id=tenant.id,
                course_id=course_id,
                student_id=student_id,
                certificate_number=certificate_number,
                final_score=evaluation["final_score"],
                template_version=template.version,
                key_version=1,
                issued_at_iso=cert.issued_at.isoformat(),
                signing_key=signing_key,
            )

            CourseCertificate.objects.filter(id=cert.id).update(verification_hash=verification_hash)
            cert.verification_hash = verification_hash
            return cert, True


class CertificateVerificationService:
    @classmethod
    def verify_by_number(cls, tenant, certificate_number, queried_by_role="anonymous"):
        with transaction.atomic():
            cert = CourseCertificate.objects.filter(
                tenant=tenant,
                certificate_number=certificate_number,
            ).select_related("course", "template").first()

            if not cert:
                CertificateVerificationRecord.objects.create(
                    tenant=tenant,
                    certificate=None,
                    queried_number=certificate_number,
                    result_status="NOT_FOUND",
                    queried_by_role=queried_by_role,
                )
                return {
                    "is_valid": False,
                    "status": "NOT_FOUND",
                    "data": None,
                }

            if cert.status == CourseCertificateStatus.REVOKED:
                CertificateVerificationRecord.objects.create(
                    tenant=tenant,
                    certificate=cert,
                    queried_number=certificate_number,
                    result_status="REVOKED",
                    queried_by_role=queried_by_role,
                )
                return {
                    "is_valid": False,
                    "status": "REVOKED",
                    "revoked_at": cert.revoked_at.isoformat() if cert.revoked_at else None,
                    "revocation_reason": cert.revocation_reason,
                    "data": None,
                }

            signing_key = getattr(tenant, "signing_key", "default-signing-key-32-chars-long!")
            expected_hash = compute_canonical_verification_hash(
                tenant_id=tenant.id,
                course_id=cert.course_id,
                student_id=cert.student_id,
                certificate_number=cert.certificate_number,
                final_score=cert.final_score,
                template_version=cert.template.version,
                key_version=1,
                issued_at_iso=cert.issued_at.isoformat(),
                signing_key=signing_key,
            )

            # Constant-time comparison
            if not hmac.compare_digest(expected_hash, cert.verification_hash):
                CertificateVerificationRecord.objects.create(
                    tenant=tenant,
                    certificate=cert,
                    queried_number=certificate_number,
                    result_status="INVALID_HASH",
                    queried_by_role=queried_by_role,
                )
                return {
                    "is_valid": False,
                    "status": "INVALID_HASH",
                    "data": None,
                }

            CertificateVerificationRecord.objects.create(
                tenant=tenant,
                certificate=cert,
                queried_number=certificate_number,
                result_status="VALID",
                queried_by_role=queried_by_role,
            )

            return {
                "is_valid": True,
                "status": "VALID",
                "data": {
                    "certificate_number": cert.certificate_number,
                    "course_title": cert.course.title if cert.course else "",
                    "template_title": cert.template.title if cert.template else "",
                    "final_score": f"{cert.final_score:.2f}",
                    "issued_at": cert.issued_at.isoformat(),
                    "verification_hash": cert.verification_hash,
                },
            }
