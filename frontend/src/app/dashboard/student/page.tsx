"use client";

import React from "react";
import { DashboardScreen } from "@/features/dashboard/DashboardScreen";
import type { DashboardModel } from "@/features/dashboard/dashboard.types";
import { StreakIndicator } from "@/components/gamification/StreakIndicator";
import { BadgeShelf, BadgeItem } from "@/components/gamification/BadgeShelf";
import { EnrollmentCard, EnrollmentItem } from "@/components/enrollment/EnrollmentCard";
import { AssignmentSubmissionCard, AssignmentItem } from "@/components/submissions/AssignmentSubmissionCard";
import { InteractivePlaygroundCard } from "@/components/assessments/InteractivePlaygroundCard";
import { CertificateCard, CertificateData } from "@/components/certificates/CertificateCard";
import { AchievementTimeline, TimelineItem } from "@/components/certificates/AchievementTimeline";
import { DiscussionThreadList, DiscussionThreadItem } from "@/components/discussion/DiscussionThreadList";
import { DiscussionThreadDetail, DiscussionCommentItem } from "@/components/discussion/DiscussionThreadDetail";
import { DiscussionReplyComposer } from "@/components/discussion/DiscussionReplyComposer";
import { AdaptiveRecommendationCard, LearningRecommendationData } from "@/components/personalization/AdaptiveRecommendationCard";
import { StudentSkillRadar, SkillProgressItem } from "@/components/personalization/StudentSkillRadar";
import { LearningGapAlert, LearningGap } from "@/components/personalization/LearningGapAlert";
import { GrowthJourneyDashboard } from "@/components/growth/GrowthJourneyDashboard";

const syntheticAssignments: AssignmentItem[] = [
  {
    id: "asgn-1",
    code: "py-calc-p1",
    title: "پروژه ماشین‌حساب پایتون",
    lessonTitle: "توابع و شروط در پایتون",
    dueDate: "۱۴۰۵/۰۶/۳۰",
    maxScore: 100,
    submissionState: "reviewed",
    currentContent: "def add(a, b):\n    return a + b\n\ndef calculate():\n    print(add(5, 7))\n\ncalculate()",
    feedback: "عالی! استفاده از توابع ماژولار و مدیریت شروط بسیار تمیز و استاندارد پیاده‌سازی شده است.",
    score: 98,
  },
  {
    id: "asgn-2",
    code: "py-data-p2",
    title: "پیاده‌سازی ساختار صف و پشته در پایتون",
    lessonTitle: "ساختارهای داده پیشرفته",
    dueDate: "۱۴۰۵/۰۷/۰۵",
    maxScore: 100,
    submissionState: "draft",
    currentContent: "class Stack:\n    def __init__(self):\n        self.items = []\n    def push(self, item):\n        self.items.append(item)\n    def pop(self):\n        return self.items.pop()",
  },
];

const syntheticEnrollments: EnrollmentItem[] = [
  {
    id: "enr-1",
    courseTitle: "برنامه‌نویسی پایتون و هوش مصنوعی",
    courseCode: "python-core",
    cohortTitle: "کوهورت پاییزه - کد الف",
    cohortCode: "FALL-2026-A",
    currentCount: 18,
    maxCapacity: 25,
    status: "active",
    enrolledAt: "۱۴۰۵/۰۶/۱۵",
  },
  {
    id: "enr-2",
    courseTitle: "توسعه فرانت‌اند تعاملی وب",
    courseCode: "web-frontend",
    cohortTitle: "کوهورت عصرگاهی - کد ب",
    cohortCode: "FALL-2026-B",
    currentCount: 30,
    maxCapacity: 30,
    status: "enrolled",
    enrolledAt: "۱۴۰۵/۰۶/۱۸",
  },
];

const syntheticCertificate: CertificateData = {
  id: "cert-01",
  certificateNumber: "CERT-CODESHO-2026-A8F31B9D",
  courseTitle: "دوره جامع برنامه‌نویسی پایتون و هوش مصنوعی",
  templateTitle: "گواهی پایان دوره مهارت‌های آکادمیک کدنویسی",
  studentDisplayId: "STU-8821-X9",
  finalScore: "۹۶.۵۰",
  issuedAtPersian: "۱۸ شهریور ۱۴۰۵",
  verificationHash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  status: "ISSUED",
};

const syntheticTimeline: TimelineItem[] = [
  {
    id: "tl-5",
    eventType: "CERTIFICATE_ISSUED",
    title: "صدور رسمی گواهی پایان دوره",
    description: "گواهی با شماره CERT-CODESHO-2026-A8F31B9D با موفقیت صادر و تایید شد.",
    occurredAtPersian: "۱۸ شهریور ۱۴۰۵ - ساعت ۱۸:۳۰",
  },
  {
    id: "tl-4",
    eventType: "BADGE_AWARDED",
    title: "کسب نشان استادی پایتون",
    description: "نشان استادی به دلیل حل تمام چالش‌های الگوریتمی اعطا گردید.",
    occurredAtPersian: "۱۶ شهریور ۱۴۰۵ - ساعت ۱۱:۰۰",
  },
  {
    id: "tl-3",
    eventType: "ASSIGNMENT_REVIEWED",
    title: "تأیید پروژه ماشین‌حساب پایتون توسط منتور",
    description: "نمره ۹۸٪ همراه با بازخورد تفصیلی منتور ثبت گردید.",
    occurredAtPersian: "۱۲ شهریور ۱۴۰۵ - ساعت ۱۵:۲۰",
  },
  {
    id: "tl-2",
    eventType: "LESSON_COMPLETED",
    title: "تکمیل درس توابع و ساختارهای داده",
    description: "تمام تمرین‌های تعاملی با موفقیت به پایان رسید.",
    occurredAtPersian: "۰۵ شهریور ۱۴۰۵ - ساعت ۰۹:۴۵",
  },
  {
    id: "tl-1",
    eventType: "COURSE_ENROLLED",
    title: "شروع دوره در کوهورت پاییزه الف",
    description: "ثبت‌نام قطعی در دوره آموزشی پایتون.",
    occurredAtPersian: "۰۱ شهریور ۱۴۰۵ - ساعت ۱۰:۰۰",
  },
];

const syntheticStudentModel: DashboardModel = {
  student: {
    displayName: "دانش‌آموز کوشا (سنتتیک)",
  },
  learning: {
    selectedCourseId: "c1",
    courses: [
      {
        id: "c1",
        code: "python-core",
        title: "برنامه‌نویسی پایتون و هوش مصنوعی",
        state: "published",
      },
      {
        id: "c2",
        code: "web-frontend",
        title: "توسعه فرانت‌اند تعاملی وب",
        state: "published",
      },
    ],
    lessons: [
      {
        id: "l1",
        code: "py-intro",
        title: "آشنایی با متغیرها و ساختارهای داده",
        position: 1,
        state: "published",
      },
      {
        id: "l2",
        code: "py-loops",
        title: "حلقه‌ها، شروط و توابع در پایتون",
        position: 2,
        state: "published",
      },
      {
        id: "l3",
        code: "py-project",
        title: "پروژه عملی: ساخت دستیار هوشمند",
        position: 3,
        state: "published",
      },
    ],
  },
};

const syntheticBadges: BadgeItem[] = [
  {
    id: "b1",
    badge_code: "FIRST_LESSON",
    badge_level: 1,
    title: "نخستین گام یادگیری",
    description: "تکمیل موفقیت‌آمیز اولین درس پایتون",
    is_earned: true,
  },
  {
    id: "b2",
    badge_code: "STREAK_3_DAYS",
    badge_level: 1,
    title: "پشتکار ۳ روزه",
    description: "استمرار در فعالیت آموزشی برای ۳ روز متوالی",
    is_earned: true,
  },
  {
    id: "b3",
    badge_code: "STREAK_7_DAYS",
    badge_level: 1,
    title: "مشعل یادگیری",
    description: "استمرار در فعالیت آموزشی برای ۷ روز متوالی",
    is_earned: false,
  },
  {
    id: "b4",
    badge_code: "SUBMISSION_STAR",
    badge_level: 1,
    title: "تلاشگر برتر",
    description: "ارسال تمرین و دریافت اولین بازخورد مربی",
    is_earned: true,
  },
];

export default function StudentDashboardPage() {
  const [selectedThreadId, setSelectedThreadId] = React.useState<string | null>(null);
  const [isComposerOpen, setIsComposerOpen] = React.useState(false);

  const syntheticThreads: DiscussionThreadItem[] = [
    {
      id: "th-1",
      title: "بهینه‌سازی مرتب‌سازی ادغامی در پایتون",
      body: "در تمرین درس ساختارهای داده، چگونه می‌توان حافظه کمکی را به حداقل رساند؟ آیا روش درجا (in-place) برای لیست‌های پیوندی بهینه‌تر است؟",
      authorId: "usr-stu-101",
      status: "APPROVED",
      isPinned: true,
      isLocked: false,
      repliesCount: 3,
      scopeType: "COHORT",
      scopeTitle: "کوهورت پاییزه - کد الف",
      createdAt: "۱۴۰۵/۰۶/۲۵",
    },
    {
      id: "th-2",
      title: "رفع خطای بازگشت در توابع بازگشتی",
      body: "هنگام اجرای برنامه ماشین‌حساب پایتون، با ارور RecursionError مواجه می‌شوم. مقدار حداکثر عمق بازگشت را از کجا باید تنظیم کنیم؟",
      authorId: "usr-stu-102",
      status: "APPROVED",
      isPinned: false,
      isLocked: false,
      repliesCount: 1,
      scopeType: "LESSON",
      scopeTitle: "توابع و شروط در پایتون",
      createdAt: "۱۴۰۵/۰۶/۲۶",
    },
  ];

  const syntheticComments: DiscussionCommentItem[] = [
    {
      id: "com-1",
      threadId: "th-1",
      parentId: null,
      authorId: "usr-mentor-01",
      body: "برای لیست‌های پیوندی مرتب‌سازی ادغامی به صورت O(1) حافظه اضافی قابل پیاده‌سازی است زیرا نیازی به کپی آرایه‌ای نداریم و فقط اشاره‌گرها تغییر می‌کنند.",
      status: "APPROVED",
      isMentorEndorsed: true,
      endorsedById: "usr-mentor-01",
      endorsedAt: "۱۴۰۵/۰۶/۲۵",
      createdAt: "۱۴۰۵/۰۶/۲۵",
    },
    {
      id: "com-2",
      threadId: "th-1",
      parentId: "com-1",
      authorId: "usr-stu-101",
      body: "خیلی ممنون استاد! یعنی با تغییر اشاره‌گر next می‌توانیم بدون آرایه کمکی مرج را انجام دهیم؟",
      status: "APPROVED",
      isMentorEndorsed: false,
      endorsedById: null,
      endorsedAt: null,
      createdAt: "۱۴۰۵/۰۶/۲۵",
    },
  ];

  const syntheticRecommendations: LearningRecommendationData[] = [
    {
      id: "rec-1",
      student_id: "usr-stu-101",
      recommendation_type: "NEXT_CHALLENGE",
      status: "GENERATED",
      priority: 1,
      recommendation_reason: "با توجه به تسلط عالی بر ساختار حلقه‌ها در پایتون، ورود به چالش پیاده‌سازی توابع بازگشتی پیشنهاد می‌شود.",
      evidence_context: { prior_score: 95, skill: "loops-and-iterations" },
      target_skill_slug: "python-recursion",
      target_skill_title: "توابع بازگشتی در پایتون",
      created_at: "۱۴۰۵/۰۶/۲۶",
    },
    {
      id: "rec-2",
      student_id: "usr-stu-101",
      recommendation_type: "REMEDIAL_PRACTICE",
      status: "GENERATED",
      priority: 2,
      recommendation_reason: "مهارت مدیریت خطای بازگشت نیازمند تمرین هدفمند تکمیلی برای تسلط پایدار است.",
      evidence_context: { prior_score: 55, skill: "recursion-base-case" },
      target_skill_slug: "recursion-base-case",
      target_skill_title: "شرط پایه در توابع بازگشتی",
      created_at: "۱۴۰۵/۰۶/۲۶",
    },
  ];

  const syntheticSkills: SkillProgressItem[] = [
    {
      id: "sp-1",
      skill: { id: "sk-1", slug: "python-syntax", title: "دستور زبان و متغیرهای پایتون", category: "SYNTAX", difficulty_level: 1 },
      mastery_level: "MASTERED",
      mastery_score: 98,
      practice_count: 6,
    },
    {
      id: "sp-2",
      skill: { id: "sk-2", slug: "loops-and-iterations", title: "حلقه‌ها و تکرار در پایتون", category: "ALGORITHMS", difficulty_level: 2 },
      mastery_level: "PROFICIENT",
      mastery_score: 82,
      practice_count: 4,
    },
    {
      id: "sp-3",
      skill: { id: "sk-3", slug: "python-recursion", title: "توابع بازگشتی و پشته فراخوانی", category: "ALGORITHMS", difficulty_level: 3 },
      mastery_level: "DEVELOPING",
      mastery_score: 55,
      practice_count: 2,
    },
  ];

  const syntheticGaps: LearningGap[] = [
    {
      skill_id: "sk-3",
      skill_slug: "recursion-base-case",
      skill_title: "شرط توقف در توابع بازگشتی",
      severity: "MEDIUM",
      reason: "مهارت در حال شکوفایی، نیازمند تمرین تکمیلی شرط خروج",
    },
  ];

  const activeThread = syntheticThreads.find((t) => t.id === selectedThreadId);

  return (
    <DashboardScreen model={syntheticStudentModel} state="ready">
      {/* P3-VS13 Student Growth Insights & Longitudinal Learning Intelligence Section */}
      <section
        style={{
          maxWidth: "78rem",
          margin: "0 auto 2.5rem",
          padding: "0 1.5rem",
          direction: "rtl",
        }}
        aria-label="داشبورد بینش‌های رشد یادگیری و مسیر تسلط مهارتی"
        data-testid="p3-vs13-growth-section"
      >
        <GrowthJourneyDashboard
          studentName="دانش‌آموز فعال"
          metrics={[
            { key: "CONCEPT_MASTERY", label: "تسلط مفهومی بر کدنویسی", value: 88, delta: 12 },
            { key: "CODING_VELOCITY", label: "سرعت و ریتم حل مسئله", value: 92, delta: 8 },
            { key: "PROBLEM_SOLVING", label: "پایداری در دیباگ و اصلاح خطا", value: 85, delta: 15 },
            { key: "CODE_QUALITY", label: "رعایت تمیزی و استانداردهای نحوی", value: 90, delta: 10 },
          ]}
          trend={{
            domain: "FULLSTACK_FOUNDATIONS",
            direction: "ACCELERATING",
            score: 88.5,
            velocity: 12.0,
            totalMilestones: 4,
          }}
          insights={[
            {
              id: "ins-1",
              type: "COMPETENCY_GROWTH",
              title: "تسلط چشمگیر در مفاهیم حلقه‌ها و شروط",
              description: "با حل تمرین‌های چالش‌برانگیز بدون ارور زمان اجرا، ریتم یادگیری روند کاملاً صعودی داشته است.",
              confidence: "HIGH",
            },
            {
              id: "ins-2",
              type: "FOCUS_RECOMMENDATION",
              title: "تمرکز پیشنهادی برای گام آینده",
              description: "پیاده‌سازی توابع چندریختی در پایتون می‌تواند درک شی‌گرایی را به سطح عالی ارتقا دهد.",
              confidence: "HIGH",
            },
          ]}
          milestones={[
            {
              id: "ms-1",
              code: "MS-PY-01",
              title: "نخستین برنامه بدون خطای نحوی و اجرای صحیح در ترمینال",
              achievedAt: "۱۴۰۵/۰۶/۱۰",
            },
            {
              id: "ms-2",
              code: "MS-PY-02",
              title: "حل کامل چالش ساختارهای داده صف و پشته در پایتون",
              achievedAt: "۱۴۰۵/۰۶/۱۸",
            },
          ]}
        />
      </section>

      {/* P3-VS4 Gamification Progression & Badges Section */}
      <section
        style={{
          maxWidth: "78rem",
          margin: "0 auto 1.5rem",
          padding: "0 1.5rem",
          direction: "rtl",
        }}
        aria-label="پیشرفت و دستاوردهای دانش‌آموز"
      >
        <StreakIndicator
          currentStreak={3}
          longestStreak={5}
          totalXp={240}
          level={3}
        />
        <BadgeShelf badges={syntheticBadges} />
      </section>

      {/* VS2 Mentor Feedback Visibility Section */}
      <section
        style={{
          maxWidth: "78rem",
          margin: "0 auto 3rem",
          padding: "0 1.5rem",
          direction: "rtl",
        }}
        aria-labelledby="feedback-history-title"
      >
        <div
          style={{
            background: "var(--cs-color-bg-surface, #ffffff)",
            border: "1px solid var(--cs-color-border-subtle, #e2e8f0)",
            borderRadius: "1rem",
            padding: "1.5rem",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
            <h2 id="feedback-history-title" style={{ margin: 0, fontSize: "1.25rem" }}>
              📋 بازخوردهای دریافتی از مربیان
            </h2>
            <span
              style={{
                fontSize: "0.85rem",
                padding: "0.25rem 0.75rem",
                borderRadius: "9999px",
                background: "#f0fdf4",
                color: "#166534",
                fontWeight: 700,
                border: "1px solid #bbf7d0",
              }}
            >
              ۱ بازخورد جدید
            </span>
          </div>

          <div
            style={{
              padding: "1.25rem",
              borderRadius: "0.75rem",
              background: "#f8fafc",
              border: "1px solid #e2e8f0",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
              <strong style={{ fontSize: "1.05rem" }}>پروژه ماشین‌حساب پایتون (py-calc-p1)</strong>
              <span style={{ fontSize: "0.85rem", color: "#64748b" }}>مربی: دکتر سهرابی | ۱۴۰۳/۰۶/۱۷</span>
            </div>
            <p style={{ margin: "0.5rem 0", color: "#334155", fontSize: "0.95rem", lineHeight: "1.6" }}>
              <strong>نظر و راهنمایی مربی:</strong> راهکار ارائه شده بسیار تمیز و ماژولار است. تابع به درستی پیاده‌سازی شده و اصول نگارش تمیز پایتون (PEP 8) رعایت شده است. به عنوان گام بعدی، مدیریت خطا برای تقسیم بر صفر را اضافه کنید.
            </p>
            <div style={{ marginTop: "0.75rem", display: "flex", gap: "0.5rem" }}>
              <span
                style={{
                  fontSize: "0.8rem",
                  padding: "0.2rem 0.6rem",
                  borderRadius: "0.25rem",
                  background: "#dcfce7",
                  color: "#15803d",
                  fontWeight: 600,
                }}
              >
                وضعیت: تأیید شده و تکمیل
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Phase 3 VS5 Course Enrollments & Cohorts Section */}
      <section
        style={{
          maxWidth: "78rem",
          margin: "0 auto 2rem",
          padding: "0 1.5rem",
        }}
      >
        <EnrollmentCard enrollments={syntheticEnrollments} />
      </section>

      {/* Phase 3 VS6 Student Assignments & Submissions Section */}
      <section
        style={{
          maxWidth: "78rem",
          margin: "0 auto 2rem",
          padding: "0 1.5rem",
        }}
      >
        <AssignmentSubmissionCard assignments={syntheticAssignments} />
      </section>

      {/* Phase 3 VS7 Interactive Code Playground & Automated Assessment Section */}
      <section
        style={{
          maxWidth: "78rem",
          margin: "0 auto 2rem",
          padding: "0 1.5rem",
        }}
      >
        <InteractivePlaygroundCard />
      </section>

      {/* Phase 3 VS8 Course Completion Certificate & Learning Verification Section */}
      <section
        style={{
          maxWidth: "78rem",
          margin: "0 auto 2.5rem",
          padding: "0 1.5rem",
        }}
        aria-label="گواهی پایان دوره دانش‌آموز"
      >
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: "2rem", alignItems: "start" }}>
          <CertificateCard certificate={syntheticCertificate} />
          <AchievementTimeline items={syntheticTimeline} />
        </div>
      </section>

      {/* Phase 3 Synthetic Media Attachments Section */}
      <section
        style={{
          maxWidth: "78rem",
          margin: "0 auto 3rem",
          padding: "0 1.5rem",
          direction: "rtl",
        }}
        aria-labelledby="media-attachments-title"
      >
        <div
          style={{
            background: "var(--cs-color-bg-surface, #ffffff)",
            border: "1px solid var(--cs-color-border-subtle, #e2e8f0)",
            borderRadius: "1rem",
            padding: "1.5rem",
          }}
        >
          <h2 id="media-attachments-title" style={{ margin: "0 0 1rem 0", fontSize: "1.25rem" }}>
            📁 منابع و رسانه‌های ضمیمه آموزشی
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1rem" }}>
            <div style={{ padding: "1rem", borderRadius: "0.75rem", background: "#f8fafc", border: "1px solid #e2e8f0" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
                <span aria-hidden="true" style={{ fontSize: "1.25rem" }}>📄</span>
                <strong>راهنمای سریع سینتکس پایتون</strong>
              </div>
              <p style={{ margin: "0.25rem 0", fontSize: "0.85rem", color: "#64748b" }}>
                فرمت: PDF | حجم: ۱.۲ مگابایت | درس: مبانی متغیرها
              </p>
              <span style={{ display: "inline-block", marginTop: "0.5rem", fontSize: "0.75rem", padding: "0.15rem 0.5rem", borderRadius: "0.25rem", background: "#e0f2fe", color: "#0369a1" }}>
                تأیید اصالت داده: SYNTHETIC
              </span>
            </div>
            <div style={{ padding: "1rem", borderRadius: "0.75rem", background: "#f8fafc", border: "1px solid #e2e8f0" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
                <span aria-hidden="true" style={{ fontSize: "1.25rem" }}>📊</span>
                <strong>دیاگرام ساختارهای داده و حافظه</strong>
              </div>
              <p style={{ margin: "0.25rem 0", fontSize: "0.85rem", color: "#64748b" }}>
                فرمت: PNG | حجم: ۴۸۰ کیلوبایت | درس: ساختارهای داده
              </p>
              <span style={{ display: "inline-block", marginTop: "0.5rem", fontSize: "0.75rem", padding: "0.15rem 0.5rem", borderRadius: "0.25rem", background: "#e0f2fe", color: "#0369a1" }}>
                تأیید اصالت داده: SYNTHETIC
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* P3-VS10 Learning Community Discussion & Peer Interaction Section */}
      <section
        style={{
          maxWidth: "78rem",
          margin: "0 auto 3rem",
          padding: "0 1.5rem",
          direction: "rtl",
        }}
        aria-label="تالار گفتگو و تعاملات آموزشی دانش‌آموزان"
      >
        <div
          style={{
            background: "var(--cs-color-bg-surface, #ffffff)",
            border: "1px solid var(--cs-color-border-subtle, #e2e8f0)",
            borderRadius: "1rem",
            padding: "1.5rem",
            boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.05)",
          }}
        >
          {activeThread ? (
            <DiscussionThreadDetail
              thread={activeThread}
              comments={syntheticComments.filter((c) => c.threadId === activeThread.id)}
              currentUserId="usr-stu-101"
              currentUserRole="STUDENT"
              onAddReply={async (body, parentId) => {
                // Synthetic reply handler
                console.log("Adding reply:", { body, parentId });
              }}
              onBackToList={() => setSelectedThreadId(null)}
            />
          ) : (
            <DiscussionThreadList
              threads={syntheticThreads}
              selectedThreadId={selectedThreadId || undefined}
              onSelectThread={(id) => setSelectedThreadId(id)}
              onCreateNewThread={() => setIsComposerOpen(true)}
            />
          )}
        </div>
      </section>

      {/* P3-VS11 Adaptive Progression & Personalized Recommendations Section */}
      <section
        style={{
          maxWidth: "78rem",
          margin: "0 auto 3rem",
          padding: "0 1.5rem",
          direction: "rtl",
        }}
        aria-label="موتور یادگیری تطبیقی و رادار رشد مهارتی دانش‌آموز"
        data-testid="p3-vs11-personalization-section"
      >
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          <LearningGapAlert gaps={syntheticGaps} />

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "1.5rem" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              <h2 style={{ fontSize: "1.25rem", fontWeight: "bold", color: "#0f172a" }}>
                پیشنهادهای هوشمند و هدفمند آموزشی
              </h2>
              {syntheticRecommendations.map((rec) => (
                <AdaptiveRecommendationCard
                  key={rec.id}
                  recommendation={rec}
                  onAccept={(id) => console.log("Accepted recommendation:", id)}
                  onDismiss={(id) => console.log("Dismissed recommendation:", id)}
                />
              ))}
            </div>

            <div>
              <StudentSkillRadar
                skills={syntheticSkills}
                competencyIndex={78.5}
                totalSkills={3}
                masteredCount={1}
              />
            </div>
          </div>
        </div>
      </section>

      <DiscussionReplyComposer
        isOpen={isComposerOpen}
        onClose={() => setIsComposerOpen(false)}
        onSubmit={async (title, body, scopeType) => {
          console.log("Submitting new thread:", { title, body, scopeType });
        }}
        defaultScopeType="COHORT"
        scopeTitle="کوهورت پاییزه - کد الف"
      />
    </DashboardScreen>
  );
}
