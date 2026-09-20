/**
 * Wave 5.5.3 — Educator / Mentor Command Center
 * Synthetic Data & Domain Models
 * Principles: SIGNAL -> CONTEXT -> EVIDENCE -> ACTION
 */

export interface LearningEvidence {
  id: string;
  projectTitle: string;
  repoBranch: string;
  commitHash: string;
  summary: string;
  skillsDemonstrated: string[];
  recentActivity: string;
  lastCodeSnippet: string;
  parentContext: string;
  mentorNotes: string;
}

export interface Intervention {
  id: string;
  studentId: string;
  studentName: string;
  avatarSeed: string;
  cohort: string;
  reason: string;
  context: string;
  urgency: "HIGH" | "MEDIUM" | "LOW";
  status: "OPEN" | "REVIEWING" | "FOLLOW_UP" | "RESOLVED";
  recommendedAction: string;
  evidence: LearningEvidence;
  feedbackHistory: Array<{
    id: string;
    sender: "MENTOR" | "STUDENT";
    timestamp: string;
    text: string;
    actionType: string;
  }>;
}

export interface CohortPulseItem {
  id: string;
  type: "STALLED" | "STRUGGLING" | "MILESTONE" | "ENCOURAGEMENT" | "FOLLOW_UP";
  label: string;
  count: number;
  description: string;
  actionHint: string;
}

export const syntheticCohortPulse: CohortPulseItem[] = [
  {
    id: "cp-struggling",
    type: "STRUGGLING",
    label: "نیازمند مداخله مفهومی",
    count: 3,
    description: "توقف روی مفاهیم مدیریت حافظه و توابع ناهمگام بیش از ۴۸ ساعت",
    actionHint: "بررسی صف و ارسال راهنمای گام‌به‌گام"
  },
  {
    id: "cp-stalled",
    type: "STALLED",
    label: "رکود تمرین و غیبت",
    count: 2,
    description: "عدم ارسال کامیت یا تعامل در ۳ روز گذشته",
    actionHint: "ارسال پیام انگیزشی و اطلاع‌رسانی به والد"
  },
  {
    id: "cp-milestone",
    type: "MILESTONE",
    label: "دستاورد و جهش مهارتی",
    count: 5,
    description: "تکمیل موفق پروژه الگوریتم‌های مرتب‌سازی با بالاترین امتیاز آزمون",
    actionHint: "صدور بج شایستگی و تشویق عمومی"
  },
  {
    id: "cp-encouragement",
    type: "ENCOURAGEMENT",
    label: "فرصت‌های رشد و تقویت",
    count: 4,
    description: "پیشرفت پیوسته ۷ روزه و پتانسیل شروع چالش پیشرفته",
    actionHint: "پیشنهاد ماژول تکمیلی"
  },
  {
    id: "cp-followup",
    type: "FOLLOW_UP",
    label: "پیگیری‌های باز مربی",
    count: 2,
    description: "منتظر ارسال بازبینی مجدد پس از اصلاح توابع",
    actionHint: "ارزیابی پاسخ‌های ارسال‌شده"
  }
];

export const initialInterventions: Intervention[] = [
  {
    id: "int-1",
    studentId: "std-101",
    studentName: "علی محمدی",
    avatarSeed: "ali",
    cohort: "کدنویسی خلاق سطح ۲ (پاییز)",
    reason: "گیر کردن در مدیریت خطاهای ناهمگام (Async/Await)",
    context: "۳ تلاش ناموفق برای حل چالش وب‌سرویس وضعیت آب‌وهوا طی ۲۴ ساعت اخیر.",
    urgency: "HIGH",
    status: "OPEN",
    recommendedAction: "ارسال پیشنهاد دیباگ ساختار try/catch و بررسی پیام خطای سرور",
    evidence: {
      id: "ev-1",
      projectTitle: "سامانه اطلاع‌رسانی وضعیت آب‌وهوا",
      repoBranch: "feat/weather-async-fetch",
      commitHash: "e4a89bc",
      summary: "اتصال به API خارجی و پردازش ساختار JSON با مدیریت خطا.",
      skillsDemonstrated: ["JavaScript ES6+", "DOM Manipulation", "Async/Await"],
      recentActivity: "تلاش برای دریافت داده بدون بسته‌بندی در try/catch و ایجاد خطای UnhandledRejection.",
      lastCodeSnippet: `async function fetchWeather(city) {\n  // مشکل: خطای شبکه هندل نشده و برنامه متوقف می‌شود\n  const response = await fetch(\`https://api.example.com/weather?q=\${city}\`);\n  const data = await response.json();\n  renderWeather(data);\n}`,
      parentContext: "والد در نظرسنجی اخیر اشاره کرده که علی علاقه‌مند به کار با پروژه‌های ملموس است.",
      mentorNotes: "علی در مباحث پایه بسیار دقیق است اما در مدیریت خطاها دچار استرس می‌شود."
    },
    feedbackHistory: [
      {
        id: "fb-1",
        sender: "MENTOR",
        timestamp: "دیروز، ۱۶:۳۰",
        text: "علی عزیز، خط اول تابع رو داخل بلوک try قرار بده و نتیجه رو تست کن.",
        actionType: "راهنمایی فنی"
      }
    ]
  },
  {
    id: "int-2",
    studentId: "std-102",
    studentName: "سارا احمدی",
    avatarSeed: "sara",
    cohort: "کدنویسی خلاق سطح ۲ (پاییز)",
    reason: "ثبت جهش چشمگیر در ساخت بازی تعاملی فیزیک",
    context: "اتمام ۵ تسک چالش‌برانگیز در کمتر از ۲ روز کاری با رعایت استاندارد تمیزنویسی.",
    urgency: "MEDIUM",
    status: "REVIEWING",
    recommendedAction: "تأیید پروژه و اعطای نشان افتخار 'معمار الگوریتم'",
    evidence: {
      id: "ev-2",
      projectTitle: "شبیه‌ساز گرانش و برخورد دوبعدی",
      repoBranch: "master",
      commitHash: "c920f1a",
      summary: "پیاده‌سازی موتور فیزیک دوبعدی سبک روی Canvas با پشتیبانی از کشش فنری.",
      skillsDemonstrated: ["HTML5 Canvas", "Vector Math", "Object-Oriented Programming"],
      recentActivity: "بهینه‌سازی نرخ فریم با requestAnimationFrame و محاسبه شتاب ذرات.",
      lastCodeSnippet: `class Particle {\n  update() {\n    this.velocity.add(this.acceleration);\n    this.position.add(this.velocity);\n    this.acceleration.mult(0);\n  }\n}`,
      parentContext: "والدین در رصدخانه رشد روند را هفتگی پیگیری می‌کنند.",
      mentorNotes: "استعداد بالا در منطق ریاضی؛ آماده ورود به پروژه‌های چندنفره."
    },
    feedbackHistory: []
  },
  {
    id: "int-3",
    studentId: "std-103",
    studentName: "پارسا علوی",
    avatarSeed: "parsa",
    cohort: "پایگاه داده و معماری وب",
    reason: "عدم ارسال لاگ فعالیت بیش از ۷۲ ساعت پس از شروع تسک RLS",
    context: "تسک دسترسی مبتنی بر ردیف (Row-Level Security) در وضعیت پیش‌نویس رها شده است.",
    urgency: "HIGH",
    status: "OPEN",
    recommendedAction: "برقراری ارتباط انگیزشی و پیشنهاد جلسه رفع اشکال تعاملی",
    evidence: {
      id: "ev-3",
      projectTitle: "ایزولاسیون داده‌های سازمانی چندمستأجره",
      repoBranch: "chore/tenant-security-rules",
      commitHash: "88b1220",
      summary: "طراحی سیاست‌های امنیتی دسترسی به داده‌ها در سطح جداول.",
      skillsDemonstrated: ["PostgreSQL RLS", "Security Policy Design", "Relational Modeling"],
      recentActivity: "تنها یک کامیت اولیه روی فایل پیکربندی دیتابیس بدون پیاده‌سازی آزمون‌ها.",
      lastCodeSnippet: `-- سیاست امنیتی هنوز تکمیل نشده است\nALTER TABLE tenant_records ENABLE ROW LEVEL SECURITY;\n-- CREATE POLICY tenant_isolation_policy ON tenant_records ...`,
      parentContext: "والد نگران انگیزه و فشار دروس مدرسه است.",
      mentorNotes: "نیاز به بازخورد مثبت و یادآوری اینکه این مبحث در ابتدا دشوار است اما حل‌شدنی است."
    },
    feedbackHistory: []
  },
  {
    id: "int-4",
    studentId: "std-104",
    studentName: "مهسا کریمی",
    avatarSeed: "mahsa",
    cohort: "کدنویسی خلاق سطح ۲ (پاییز)",
    reason: "درخواست بازبینی دقیق شواهد ماژول رابط کاربری ریسپانسیو",
    context: "پروژه منوی همبرگری و کارت‌های تعاملی تکمیل شده و منتظر نظرات منتور است.",
    urgency: "LOW",
    status: "FOLLOW_UP",
    recommendedAction: "بررسی ساختار CSS Grid و تایید رعایت استانداردهای دسترسی‌پذیری (a11y)",
    evidence: {
      id: "ev-4",
      projectTitle: "کامپوننت سیستم طراحی منعطف",
      repoBranch: "ui/responsive-grid-system",
      commitHash: "44d711a",
      summary: "سیستم طراحی ماژولار با CSS Custom Properties و سازگاری کامل موبایل.",
      skillsDemonstrated: ["CSS Grid & Flexbox", "Design Tokens", "Accessibility"],
      recentActivity: "افزودن تست‌های کنتراست رنگی و تگ‌های ARIA.",
      lastCodeSnippet: `.mentorCard {\n  display: grid;\n  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));\n  gap: var(--space-4);\n}`,
      parentContext: "والدین همراه و مشوق در فعالیت‌های هنری و طراحی دیجیتال.",
      mentorNotes: "دقت بالا در جزئیات بصری؛ کیفیت کد بسیار مطلوب است."
    },
    feedbackHistory: [
      {
        id: "fb-4",
        sender: "MENTOR",
        timestamp: "امروز، ۱۰:۰۰",
        text: "کارت فوق‌العاده است مهسا، فقط کنتراست دکمه ثانویه در حالت Dark Mode را چک کن.",
        actionType: "بازبینی کد"
      }
    ]
  }
];
