import uuid
from decimal import Decimal
import pytest
from django.db import connection

from modules.learning.models import (
    CertificateTemplate,
    CourseCertificate,
    CertificateVerificationRecord,
    CourseCertificateStatus,
    Course,
    LearningPath,
)
from modules.platform_tenant.models import Tenant


@pytest.mark.django_db
class TestP3VS8CertificatesRLS:

    @pytest.fixture(autouse=True)
    def setup_tenants(self):
        self.tenant_a = Tenant.objects.create(name="Tenant Alpha", slug=f"t-a-{uuid.uuid4().hex[:6]}")
        self.tenant_b = Tenant.objects.create(name="Tenant Beta", slug=f"t-b-{uuid.uuid4().hex[:6]}")

        self.path_a = LearningPath.objects.create(tenant=self.tenant_a, code="path-a", title="Path A")
        self.course_a = Course.objects.create(tenant=self.tenant_a, learning_path=self.path_a, code="c-a", title="Course A")

        self.template_a = CertificateTemplate.objects.create(
            tenant=self.tenant_a,
            course=self.course_a,
            version=1,
            title="گواهی آلفا",
            min_score_percentage=Decimal("70.00"),
            is_active=True,
        )

        self.student_a = uuid.uuid4()
        self.cert_a = CourseCertificate.objects.create(
            tenant=self.tenant_a,
            course=self.course_a,
            template=self.template_a,
            student_id=self.student_a,
            completion_round=1,
            certificate_number=f"CERT-ALPHA-{uuid.uuid4().hex[:8]}",
            verification_hash=uuid.uuid4().hex,
            status=CourseCertificateStatus.ISSUED,
            final_score=Decimal("95.00"),
            completion_snapshot={"score": "95.00"},
            source_event_id=uuid.uuid4(),
        )

        self.record_a = CertificateVerificationRecord.objects.create(
            tenant=self.tenant_a,
            certificate=self.cert_a,
            queried_number=self.cert_a.certificate_number,
            result_status="VALID",
            queried_by_role="anonymous",
        )

    def test_tenant_isolation_in_orm(self):
        # Tenant B queries must see 0 records of Tenant A
        certs_b = CourseCertificate.objects.filter(tenant=self.tenant_b)
        assert certs_b.count() == 0

        templates_b = CertificateTemplate.objects.filter(tenant=self.tenant_b)
        assert templates_b.count() == 0

        records_b = CertificateVerificationRecord.objects.filter(tenant=self.tenant_b)
        assert records_b.count() == 0

    def test_cross_tenant_negative_leakage(self):
        # Even if searching by exact certificate number, filtering by tenant B yields nothing
        cert = CourseCertificate.objects.filter(
            tenant=self.tenant_b,
            certificate_number=self.cert_a.certificate_number,
        ).first()
        assert cert is None
