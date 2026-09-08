import uuid
from decimal import Decimal
import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from modules.platform_tenant.models import Tenant
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
from modules.learning.certificates import (
    CourseCompletionEvaluator,
    CertificateIssuanceService,
    CertificateVerificationService,
    compute_canonical_verification_hash,
)


@pytest.mark.django_db
class TestP3VS8Certificates:
    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            slug="test-tenant",
        )
        self.student_id = uuid.uuid4()
        self.course = Course.objects.create(
            tenant=self.tenant,
            code="PY-101",
            title="آموزش جامع پایتون",
            state="published",
        )
        self.template = CertificateTemplate.objects.create(
            tenant=self.tenant,
            course=self.course,
            version=1,
            title="گواهی پایان دوره جامع پایتون",
            min_score_percentage=Decimal("70.00"),
            is_active=True,
        )

    def test_completion_evaluation_incomplete_lessons(self):
        # Create mandatory lesson
        lesson = Lesson.objects.create(
            tenant=self.tenant,
            course=self.course,
            code="L1",
            title="مقدمه",
            position=1,
            state="published",
        )
        res = CourseCompletionEvaluator.evaluate(
            tenant_id=self.tenant.id,
            course_id=self.course.id,
            student_id=self.student_id,
        )
        assert res["is_eligible"] is False

    def test_completion_evaluation_with_completed_lessons_no_assignments(self):
        lesson = Lesson.objects.create(
            tenant=self.tenant,
            course=self.course,
            code="L1",
            title="مقدمه",
            position=1,
            state="published",
        )
        Progress.objects.create(
            tenant=self.tenant,
            lesson=lesson,
            student_id=self.student_id,
            state=ProgressState.COMPLETED,
        )
        res = CourseCompletionEvaluator.evaluate(
            tenant_id=self.tenant.id,
            course_id=self.course.id,
            student_id=self.student_id,
        )
        assert res["is_eligible"] is True
        assert res["final_score"] == Decimal("100.00")

    def test_certificate_issuance_and_idempotent_replay(self):
        lesson = Lesson.objects.create(
            tenant=self.tenant,
            course=self.course,
            code="L1",
            title="مقدمه",
            position=1,
            state="published",
        )
        Progress.objects.create(
            tenant=self.tenant,
            lesson=lesson,
            student_id=self.student_id,
            state=ProgressState.COMPLETED,
        )
        event_id = uuid.uuid4()
        cert, created = CertificateIssuanceService.issue_certificate(
            tenant=self.tenant,
            course_id=self.course.id,
            student_id=self.student_id,
            source_event_id=event_id,
        )
        assert created is True
        assert cert.status == CourseCertificateStatus.ISSUED
        assert cert.final_score == Decimal("100.00")
        assert cert.certificate_number.startswith("CERT-")

        # Replay with same source_event_id returns existing record cleanly
        cert_replay, replay_created = CertificateIssuanceService.issue_certificate(
            tenant=self.tenant,
            course_id=self.course.id,
            student_id=self.student_id,
            source_event_id=event_id,
        )
        assert replay_created is False
        assert cert_replay.id == cert.id

    def test_certificate_verification_valid_and_revoked(self):
        lesson = Lesson.objects.create(
            tenant=self.tenant,
            course=self.course,
            code="L1",
            title="مقدمه",
            position=1,
            state="published",
        )
        Progress.objects.create(
            tenant=self.tenant,
            lesson=lesson,
            student_id=self.student_id,
            state=ProgressState.COMPLETED,
        )
        cert, _ = CertificateIssuanceService.issue_certificate(
            tenant=self.tenant,
            course_id=self.course.id,
            student_id=self.student_id,
            source_event_id=uuid.uuid4(),
        )

        # 1. Valid Query
        res = CertificateVerificationService.verify_by_number(
            tenant=self.tenant,
            certificate_number=cert.certificate_number,
            queried_by_role="anonymous",
        )
        assert res["is_valid"] is True
        assert res["status"] == "VALID"
        assert res["data"]["certificate_number"] == cert.certificate_number

        # 2. Revoke and Query
        cert.status = CourseCertificateStatus.REVOKED
        cert.revoked_at = timezone.now()
        cert.revocation_reason = "نقض قوانین آموزشی"
        cert.save()

        res_revoked = CertificateVerificationService.verify_by_number(
            tenant=self.tenant,
            certificate_number=cert.certificate_number,
            queried_by_role="parent",
        )
        assert res_revoked["is_valid"] is False
        assert res_revoked["status"] == "REVOKED"
        assert res_revoked["revocation_reason"] == "نقض قوانین آموزشی"

    def test_immutability_of_core_fields(self):
        lesson = Lesson.objects.create(
            tenant=self.tenant,
            course=self.course,
            code="L1",
            title="مقدمه",
            position=1,
            state="published",
        )
        Progress.objects.create(
            tenant=self.tenant,
            lesson=lesson,
            student_id=self.student_id,
            state=ProgressState.COMPLETED,
        )
        cert, _ = CertificateIssuanceService.issue_certificate(
            tenant=self.tenant,
            course_id=self.course.id,
            student_id=self.student_id,
            source_event_id=uuid.uuid4(),
        )

        # Attempt to mutate immutable field (final_score)
        cert.final_score = Decimal("99.99")
        with pytest.raises(ValidationError, match="strictly immutable"):
            cert.save()
