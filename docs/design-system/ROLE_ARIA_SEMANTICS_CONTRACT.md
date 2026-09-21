# ROLE_ARIA_SEMANTICS_CONTRACT.md — CodeSho Role-Based ARIA Semantics & Screen Reader Contract

> **Wave 5.13 Phase 2 Architecture Specification**  
> **Status**: CONTRACT_SPECIFIED ✅  
> **Hard Locks Enforced**: `CODE_CHANGE = 0`, `DATABASE_MIGRATION = 0`, `PRODUCTION_TOUCH = 0`  
> **Authority**: Commander AI & Human Project Manager  

---

## 1. Context & Architectural Rationale

This contract formalizes the exact Accessible Rich Internet Applications (ARIA) roles, states, and screen reader speech output across CodeSho's four role experiences (**Student**, **Mentor**, **Parent**, **Governance Admin**).

Per the foundational **Humane Pedagogical Invariant**, screen reader announcements must strictly reflect qualitative mastery, encouragement, and self-paced exploration, with zero anxiety-inducing score callouts or competitive comparisons.

---

## 2. Role 1: Student Surface (`/student`)

### Semantic Topology
```text
[role="banner"] Header -> Branding & Session Info
[role="main"]
  ├── [role="region" aria-label="خلاصه مسیر یادگیری"] StudentCommandHero
  ├── [role="region" aria-label="روند رشد و مهارت‌ها"] GrowthCard & SkillMap
  └── [role="feed" aria-label="پروژه‌ها و چالش‌های فعال"] MissionGrid
```

### Component Semantics Contract
1. **StudentCommandHero**:
   - `role="region"`
   - `aria-label="داشبورد یادگیری دانش‌آموز"`
   - Screen Reader Speech: `«داشبورد یادگیری فردی. ۳ ماموریت فعال و ۲ بازخورد جدید از منتور در دسترس است.»`
2. **GrowthCard**:
   - Progress Bar: `role="progressbar"`, `aria-valuenow="3"`, `aria-valuemin="1"`, `aria-valuemax="5"`, `aria-valuetext="گام ۳ از ۵ در مسیر تسلط"`
   - Non-Punitive Invariant: Screen reader explicitly says `گام ۳ از ۵` instead of percentage completion to avoid test anxiety.
3. **MissionCard**:
   - `role="article"`
   - `aria-labelledby="mission-title-{id}"`
   - `aria-describedby="mission-desc-{id}"`
   - Action Button: `aria-label="مشاهده جزییات ماموریت {title}"`

---

## 3. Role 2: Mentor Surface (`/mentor`)

### Semantic Topology
```text
[role="main"]
  ├── [role="region" aria-label="صف ارزیابی کیفی پروژه‌ها"] MentorReviewQueue
  └── [role="complementary" aria-label="اطلاعات و شواهد پروژه"] EvidenceSidebar
```

### Component Semantics Contract
1. **MentorWorkspace Queue**:
   - `role="table"` or `role="list" aria-label="لیست ارزیابی کیفی"`
   - Pending Badge: `role="status" aria-label="در انتظار یادداشت تشویقی"`
2. **Coaching Feedback Drawer**:
   - `role="dialog" aria-modal="true" aria-label="ثبت بازخورد منتور برای {student}"`
   - Feedback Textarea: `aria-required="true" aria-label="یادداشت‌های تسهیل‌گری و نقاط قوت"`

---

## 4. Role 3: Parent Surface (`/parent`)

### Semantic Topology
```text
[role="main"]
  ├── [role="region" aria-label="کارت همدلی و دیدگاه والد"] EmpathyOverview
  └── [role="region" aria-label="سیر تحول و دستاوردهای فرزند"] ChildJourneyTimeline
```

### Component Semantics Contract
1. **EmpathyOverview**:
   - `role="region" aria-label="خلاصه هفتگی تجارب یادگیری فرزند"`
   - Tone Contract: Screen reader reads: `«گزارش پیشرفت کیفی: علاقه به حل مسئله و تفکر خلاق در این هفته تقویت شده است.»`
2. **Encouragement Prompt Trigger**:
   - `role="button" aria-label="ارسال پیام تشویقی به فرزند"`

---

## 5. Role 4: Governance Admin (`/admin/dashboard`)

### Semantic Topology
```text
[role="main"]
  ├── [role="region" aria-label="شاخص‌های سلامت سیستم و تله‌متری حاکمیتی"] GovernanceKPIs
  └── [role="table" aria-label="گزارش ممیزی رویدادهای سامانه"] AuditLogTable
```

### Component Semantics Contract
1. **System Health Status**:
   - `role="status" aria-live="polite"`
   - Output: `«وضعیت سیستم: تمامی خدمات پایدار، ایزولاسیون چندمستاجری فعال و سالم است.»`
2. **Audit Grid**:
   - Standard grid accessibility (`role="grid"`, `aria-colcount`, `aria-rowcount`) ensuring rapid keyboard inspection for system operators.

---

## 6. Verification & Governance Check
- `CODE_CHANGE: 0`
- `DATABASE_MIGRATION: 0`
- `PRODUCTION_TOUCH: 0`
- `HUMANE_PEDAGOGICAL_INVARIANT: 100% ENFORCED`
