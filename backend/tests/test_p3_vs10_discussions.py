import uuid
import pytest
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError, transaction

from modules.platform_tenant.models import Tenant
from modules.learning.models import (
    Course,
    Cohort,
    Lesson,
    CourseEnrollment,
    EnrollmentStatus,
    DiscussionThread,
    DiscussionComment,
    DiscussionModerationAction,
    DiscussionStatus,
    ModerationActionType,
)
from modules.learning.discussion_service import (
    DiscussionService,
    DiscussionAccessPolicy,
)


@pytest.mark.django_db
class TestP3VS10Discussions:
    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.tenant = Tenant.objects.create(name="Primary Tenant", slug="primary-tenant")
        self.other_tenant = Tenant.objects.create(name="Other Tenant", slug="other-tenant")

        self.course = Course.objects.create(
            tenant=self.tenant,
            code="CS-301",
            title="طراحی الگوریتم پیشرفته",
            state="published",
        )
        self.lesson = Lesson.objects.create(
            tenant=self.tenant,
            course=self.course,
            code="LES-101",
            title="برنامه‌نویسی پویا",
            position=1,
            state="published",
        )
        self.cohort = Cohort.objects.create(
            tenant=self.tenant,
            course=self.course,
            code="COH-2026-X",
            title="کوهورت تعاملی پاییز",
            max_capacity=30,
        )

        self.student_author = uuid.uuid4()
        self.peer_student = uuid.uuid4()
        self.unauthorized_student = uuid.uuid4()
        self.mentor_id = uuid.uuid4()

        # Enroll student_author and peer_student
        CourseEnrollment.objects.create(
            tenant=self.tenant,
            course=self.course,
            cohort=self.cohort,
            student_id=self.student_author,
            status=EnrollmentStatus.ACTIVE,
        )
        CourseEnrollment.objects.create(
            tenant=self.tenant,
            course=self.course,
            cohort=self.cohort,
            student_id=self.peer_student,
            status=EnrollmentStatus.ACTIVE,
        )

    # N1: Cross-tenant thread read / access attempt
    def test_n1_cross_tenant_isolation(self):
        thread = DiscussionService.create_thread(
            tenant_id=self.tenant.id,
            author_id=self.student_author,
            role="STUDENT",
            title="سؤال در مورد فیبوناچی",
            body="چگونه حالت پایه را بهینه کنیم؟",
            cohort_id=self.cohort.id,
        )
        # Attempting query from other tenant must return 0 rows
        assert DiscussionThread.objects.filter(tenant_id=self.other_tenant.id, id=thread.id).count() == 0

    # N2: Cross-tenant comment insertion violation
    def test_n2_cross_tenant_comment_insert_rejected(self):
        thread = DiscussionService.create_thread(
            tenant_id=self.tenant.id,
            author_id=self.student_author,
            role="STUDENT",
            title="بحث کوهورت",
            body="توضیحات اولیه",
            cohort_id=self.cohort.id,
        )
        with pytest.raises((ValidationError, PermissionDenied)):
            DiscussionService.create_comment(
                tenant_id=self.other_tenant.id,
                author_id=self.student_author,
                role="STUDENT",
                thread_id=thread.id,
                body="تلاش برای ارسال کامنت در تننت دیگر",
            )

    # N3: Unenrolled student creating thread -> 403 Forbidden
    def test_n3_unenrolled_student_cannot_create_thread(self):
        with pytest.raises(PermissionDenied):
            DiscussionService.create_thread(
                tenant_id=self.tenant.id,
                author_id=self.unauthorized_student,
                role="STUDENT",
                title="سؤال دانش‌آموز ثبت‌نام‌نشده",
                body="آیا این درخواست مسدود می‌شود؟",
                cohort_id=self.cohort.id,
            )

    # N4: Single-Scope XOR Constraint (Both Cohort and Lesson) -> Violation
    def test_n9_thread_both_cohort_and_lesson_rejected(self):
        with pytest.raises(ValidationError):
            thread = DiscussionThread(
                tenant=self.tenant,
                author_id=self.student_author,
                cohort=self.cohort,
                lesson=self.lesson,
                title="تلاش برای دو اسکوپ همزمان",
                body="این رشته نامعتبر است",
                status=DiscussionStatus.PENDING,
            )
            thread.full_clean()

    # N10: Single-Scope XOR Constraint (Neither Cohort nor Lesson) -> Violation
    def test_n10_thread_neither_cohort_nor_lesson_rejected(self):
        with pytest.raises(ValidationError):
            thread = DiscussionThread(
                tenant=self.tenant,
                author_id=self.student_author,
                cohort=None,
                lesson=None,
                title="تلاش بدون اسکوپ",
                body="این رشته نامعتبر است",
                status=DiscussionStatus.PENDING,
            )
            thread.full_clean()

    # N11: Child Safety Default PENDING & 4-tier visibility
    def test_n11_child_safety_default_pending_and_visibility(self):
        thread = DiscussionService.create_thread(
            tenant_id=self.tenant.id,
            author_id=self.student_author,
            role="STUDENT",
            title="سؤال جدید در انتظار بررسی",
            body="متن اولیه",
            cohort_id=self.cohort.id,
        )
        assert thread.status == DiscussionStatus.PENDING

        comment = DiscussionService.create_comment(
            tenant_id=self.tenant.id,
            author_id=self.student_author,
            role="STUDENT",
            thread_id=thread.id,
            body="پاسخ اولیه در انتظار بررسی",
        )
        assert comment.status == DiscussionStatus.PENDING

        # Author can view
        assert DiscussionAccessPolicy.can_view_thread(thread, self.student_author, "STUDENT") is True
        assert DiscussionAccessPolicy.can_view_comment(comment, self.student_author, "STUDENT") is True

        # Peer student CANNOT view until approved
        assert DiscussionAccessPolicy.can_view_thread(thread, self.peer_student, "STUDENT") is False
        assert DiscussionAccessPolicy.can_view_comment(comment, self.peer_student, "STUDENT") is False

        # Staff/Mentor CAN view pending
        assert DiscussionAccessPolicy.can_view_thread(thread, self.mentor_id, "MENTOR") is True
        assert DiscussionAccessPolicy.can_view_comment(comment, self.mentor_id, "MENTOR") is True

        # Now mentor approves
        DiscussionService.moderate_thread(
            tenant_id=self.tenant.id,
            thread_id=thread.id,
            action=ModerationActionType.APPROVE,
            performed_by=self.mentor_id,
            reason="تأیید محتوای آموزشی مناسب",
        )
        thread.refresh_from_db()
        assert thread.status == DiscussionStatus.APPROVED

        # Now peer student CAN view
        assert DiscussionAccessPolicy.can_view_thread(thread, self.peer_student, "STUDENT") is True

    # N12: Comment cross-thread parent reference violation
    def test_n8_comment_cross_thread_parent_rejected(self):
        thread1 = DiscussionService.create_thread(
            tenant_id=self.tenant.id,
            author_id=self.student_author,
            role="STUDENT",
            title="رشته اول",
            body="متن اول",
            cohort_id=self.cohort.id,
        )
        thread2 = DiscussionService.create_thread(
            tenant_id=self.tenant.id,
            author_id=self.student_author,
            role="STUDENT",
            title="رشته دوم",
            body="متن دوم",
            cohort_id=self.cohort.id,
        )
        comment_t1 = DiscussionService.create_comment(
            tenant_id=self.tenant.id,
            author_id=self.student_author,
            role="STUDENT",
            thread_id=thread1.id,
            body="کامنت در رشته ۱",
        )
        # Attempting reply in thread2 pointing to comment in thread1
        with pytest.raises(ValidationError):
            DiscussionService.create_comment(
                tenant_id=self.tenant.id,
                author_id=self.student_author,
                role="STUDENT",
                thread_id=thread2.id,
                body="تلاش برای ارجاع متقاطع به کامنت رشته دیگر",
                parent_id=comment_t1.id,
            )

    # N14: Self-parenting comment prevention
    def test_n14_comment_self_parenting_rejected(self):
        thread = DiscussionService.create_thread(
            tenant_id=self.tenant.id,
            author_id=self.student_author,
            role="STUDENT",
            title="رشته تست خودارجاعی",
            body="متن",
            cohort_id=self.cohort.id,
        )
        comment_id = uuid.uuid4()
        comment = DiscussionComment(
            id=comment_id,
            tenant=self.tenant,
            thread=thread,
            parent_id=comment_id,  # Self parent
            author_id=self.student_author,
            body="کامنت با پرنت خودش",
            status=DiscussionStatus.PENDING,
        )
        with pytest.raises(ValidationError):
            comment.full_clean()

    # N13: Locked thread prevents replies
    def test_n13_locked_thread_rejects_replies(self):
        thread = DiscussionService.create_thread(
            tenant_id=self.tenant.id,
            author_id=self.student_author,
            role="STUDENT",
            title="رشته قفل‌شده",
            body="متن",
            cohort_id=self.cohort.id,
        )
        thread.is_locked = True
        thread.save()

        with pytest.raises(PermissionDenied):
            DiscussionService.create_comment(
                tenant_id=self.tenant.id,
                author_id=self.peer_student,
                role="STUDENT",
                thread_id=thread.id,
                body="ارسال به رشته قفل",
            )

    # N5 & N6: Student unauthorized endorsement and pinning
    def test_n5_n6_student_cannot_pin_or_endorse(self):
        thread = DiscussionService.create_thread(
            tenant_id=self.tenant.id,
            author_id=self.student_author,
            role="STUDENT",
            title="رشته برای تست پین و تأیید",
            body="متن",
            cohort_id=self.cohort.id,
        )
        comment = DiscussionService.create_comment(
            tenant_id=self.tenant.id,
            author_id=self.student_author,
            role="STUDENT",
            thread_id=thread.id,
            body="پاسخ",
        )
        # Student cannot pin
        with pytest.raises(PermissionDenied):
            DiscussionService.pin_thread(
                tenant_id=self.tenant.id,
                thread_id=thread.id,
                user_id=self.student_author,
                role="STUDENT",
                is_pinned=True,
            )

        # Student cannot endorse
        with pytest.raises(PermissionDenied):
            DiscussionService.endorse_comment(
                tenant_id=self.tenant.id,
                comment_id=comment.id,
                mentor_id=self.student_author,
                role="STUDENT",
            )

    # N7: DiscussionModerationAction Append-Only & Immutability
    def test_n7_audit_trail_immutability(self):
        thread = DiscussionService.create_thread(
            tenant_id=self.tenant.id,
            author_id=self.student_author,
            role="STUDENT",
            title="رشته ممیزی",
            body="متن",
            cohort_id=self.cohort.id,
        )
        DiscussionService.moderate_thread(
            tenant_id=self.tenant.id,
            thread_id=thread.id,
            action=ModerationActionType.FLAG,
            performed_by=self.mentor_id,
            reason="محتوای مشکوک",
        )
        audit_entry = DiscussionModerationAction.objects.filter(target_thread=thread).first()
        assert audit_entry is not None

        # Attempting modification must fail
        audit_entry.reason = "دستکاری رکورد حسابرسی"
        with pytest.raises(ValidationError):
            audit_entry.save()

        # Attempting deletion must fail
        with pytest.raises(ValidationError):
            audit_entry.delete()

    # Atomic replies counter verification
    def test_atomic_replies_count_on_approved_transitions(self):
        thread = DiscussionService.create_thread(
            tenant_id=self.tenant.id,
            author_id=self.student_author,
            role="STUDENT",
            title="شمارش اتمیک",
            body="متن",
            cohort_id=self.cohort.id,
        )
        assert thread.replies_count == 0

        # Adding comment in PENDING does NOT increment replies_count
        comment = DiscussionService.create_comment(
            tenant_id=self.tenant.id,
            author_id=self.student_author,
            role="STUDENT",
            thread_id=thread.id,
            body="پاسخ شماره ۱",
        )
        thread.refresh_from_db()
        assert thread.replies_count == 0

        # Approving comment atomically increments replies_count to 1
        DiscussionService.moderate_comment(
            tenant_id=self.tenant.id,
            comment_id=comment.id,
            action=ModerationActionType.APPROVE,
            performed_by=self.mentor_id,
            reason="تأیید پاسخ",
        )
        thread.refresh_from_db()
        assert thread.replies_count == 1

        # Removing comment atomically decrements replies_count back to 0
        DiscussionService.moderate_comment(
            tenant_id=self.tenant.id,
            comment_id=comment.id,
            action=ModerationActionType.REMOVE,
            performed_by=self.mentor_id,
            reason="حذف به دلیل نقض قوانین",
        )
        thread.refresh_from_db()
        assert thread.replies_count == 0
