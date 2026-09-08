# Phase 3 Vertical Slice 5 Boundary Plan (P3-VS5)

## 1. Context and Authority
- Authority: `COMMANDER_P3_VS4_FINAL_DISPOSITION`
- Directive: `BEGIN: P3-VS5 DISCOVERY PHASE`
- Scope: `P3-VS5-STUDENT-ENROLLMENT-COHORT-AND-PROGRESSION-POLICIES`
- Invariants:
  * Runtime Locked: No runtime implementation until Fleet Reviews (Qwen, GLM, Gemini) pass.
  * Zero PII: Synthetic identifiers for students, mentors, and cohorts.
  * Fail-Closed Multi-Tenancy: Strict PostgreSQL 17 FORCE RLS on all tenant models (`app.tenant_id`).
  * Source of Truth: Authoritative enrollment state machine, cohort boundaries, and progression eligibility in PostgreSQL.

---

## 2. Domain Entities, State Machine & Business Rules (Qwen & GLM Invariants)

1. **مدل‌های داده‌ای و تضمین دیتابیسی روابط (Database-Enforced Invariants)**:
   - مدل `Cohort` (گروه کلاسی مقید به دوره و مستأجر):
     * `id`: UUID
     * `tenant`: ForeignKey(`platform_tenant.Tenant`)
     * `course`: ForeignKey(`learning.Course`, on_delete=CASCADE)
     * `code`: CharField(max_length=64)
     * `title`: CharField(max_length=160)
     * `max_capacity`: PositiveIntegerField(default=30)
     * `start_date`: DateField(null=True, blank=True)
     * `end_date`: DateField(null=True, blank=True)
     * `is_active`: BooleanField(default=True)
     * قیدهای یکتایی دیتابیس:
       - `UNIQUE (tenant, course, code)`
       - `UNIQUE (tenant, course, id)` -> **جهت پشتیبانی از کلید خارجی ترکیبی با دوره**

   - مدل `CourseEnrollment`:
     * `id`: UUID
     * `tenant`: ForeignKey(`platform_tenant.Tenant`)
     * `student_id`: UUIDField(db_index=True)
     * `course`: ForeignKey(`learning.Course`, on_delete=CASCADE)
     * `cohort`: ForeignKey(`Cohort`, null=True, blank=True, on_delete=SET_NULL)
     * `status`: CharField(choices=[`ENROLLED`, `ACTIVE`, `SUSPENDED`, `COMPLETED`])
     * `idempotency_key`: CharField(max_length=255, null=True, blank=True)
     * `enrolled_at`: DateTimeField(auto_now_add=True)
     * `completed_at`: DateTimeField(null=True, blank=True)
     * **تضمین دیتابیسی هم‌خوانی Cohort و Course (Database Foreign Key Constraint)**:
       - استفاده از قید ترکیبی دیتابیسی در سطح PostgreSQL:
         `FOREIGN KEY (tenant_id, course_id, cohort_id) REFERENCES learning_cohort (tenant_id, course_id, id)`
       - این قید هرگونه ناهمخوانی بین دوره ثبت‌نام و دوره کوهورت را مستقیماً در لایه موتور دیتابیس مسدود می‌سازد.
     * قیدهای یکتایی:
       - `UNIQUE (tenant, student_id, course)`
       - `UNIQUE (tenant, idempotency_key)`

   - مدل `CoursePrerequisite`:
     * `tenant`: ForeignKey(`platform_tenant.Tenant`)
     * `course`: ForeignKey(`learning.Course`, related_name="prerequisites")
     * `prerequisite_course`: ForeignKey(`learning.Course`, related_name="required_for")
     * قید دیتابیس: `CheckConstraint(check=~Q(course=F('prerequisite_course')))` برای جلوگیری از خود-پیش‌نیازی.
     * قید یکتایی: `UNIQUE (tenant, course, prerequisite_course)`

2. **سیاست قطعی ظرفیت و منبع حقیقت (Capacity Source of Truth & Re-admission Policy)**:
   - **منبع حقیقت ظرفیت (Source of Truth)**:
     - منبع انحصاری حقیقت ظرفیت، شمارش قطعی رکوردهای تراکنشی دیتابیس با قفل ردیف است:
       `SELECT COUNT(*) FROM learning_courseenrollment WHERE tenant_id = :t AND cohort_id = :c AND status IN ('enrolled', 'active')`
     - ستون شمارنده فیزیکی حذف شد تا خطر اختلاف حالت (State Drift) به صفر برسد.
   - **سیاست ظرفیت در تعلیق و بازگشت (`SUSPENDED -> ACTIVE`)**:
     - وضعیت `SUSPENDED` ظرفیت کوهورت را موقتاً آزاد می‌کند.
     - **انتقال مجدد `SUSPENDED -> ACTIVE` مشمول اعتبارسنجی مجدد ظرفیت کوهورت در تراکنش قفل‌شده است.**
     - چنانچه ظرفیت کوهورت در زمان بازگشت تکمیل شده باشد، انتقال به `ACTIVE` با خطای معتبر `CohortCapacityExceededError` مسدود شده و کاربر در وضعیت تعلیق یا صف انتظار باقی می‌ماند.

3. **سیاست الزامی یا اختیاری بودن کوهورت (Cohort Requirement Policy)**:
   - فیلد `is_cohort_mandatory` در مدل `Course`:
     - پیش‌فرض: `False` (دوره‌های خودآموز Self-paced کوهورت اختیاری دارند).
     - در صورت `True` بودن، ثبت‌نام بدون انتخاب کوهورت فعال با اعتبارسنجی دیتابیسی/دامین مسدود می‌گردد.

4. **ماشین وضعیت کامل ثبت‌نام (Complete State Machine)**:
   - `ENROLLED`: ثبت‌نام اولیه (اشغال‌کننده ظرفیت).
   - `ENROLLED -> ACTIVE`: با اولین رویداد `lesson_completed` یا تایید منتور.
   - `ACTIVE -> SUSPENDED`: آزادسازی ظرفیت کوهورت.
   - `SUSPENDED -> ACTIVE`: با احراز مجدد ظرفیت کوهورت.
   - `ACTIVE -> COMPLETED`: وضعیت پایانی (Terminal State). خروج از `COMPLETED` ناممکن است.

5. **تست‌های الزامی بحرانی**:
   - تست قید ترکیبی دیتابیسی (درج کوهورت متعلق به دوره‌ای دیگر باید در لایه دیتابیس خطای قید بدهد).
   - تست پر شدن ظرفیت و ممانعت از بازگشت از تعلیق (`SUSPENDED -> ACTIVE` over capacity -> Rejected).
   - تست دوره‌های با کوهورت الزامی.
   - تست جلوگیری از چرخه پیش‌نیازها (DAG cycle prevention).
   - تست پایانی بودن `COMPLETED`.
