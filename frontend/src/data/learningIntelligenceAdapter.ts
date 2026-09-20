/**
 * Wave 5.7 Phase 5: Isolated Frontend Intelligence Adapter.
 * 
 * Provides mock & projection data layer for:
 * - Student Skill Constellation View
 * - Mentor Pedagogical Dossier & Socratic Prompts
 * - Parent Empathetic Growth Insights
 * 
 * Invariants:
 * 1. ZERO PRODUCTION ROUTE IMPACT: Does not alter existing Wave 5.6 live pages.
 * 2. NO_JUDGMENT_ENGINE: Pure understanding and support; zero child ranking.
 */
import {
  LearnerSkillGraphReadModel,
  MentorIntelligenceDossierReadModel,
  ParentInsightReadModel,
  StudentReflectionEntry,
  UnifiedIntelligenceProjection,
} from "./intelligenceTypes";

export const mockSkillGraph: LearnerSkillGraphReadModel = {
  learner_id: "student-cs-9804",
  student_code: "CS-9804",
  skills: [
    {
      slug: "python_basics",
      title: "مفاهیم پایه و ساختار داده‌های پایتون",
      category: "core",
      status: "DEMONSTRATED",
      prerequisites: [],
    },
    {
      slug: "error_handling",
      title: "مدیریت استثناها و پایداری کدهای خطا",
      category: "resilience",
      status: "DEMONSTRATED",
      prerequisites: ["python_basics"],
    },
    {
      slug: "async_flow",
      title: "جریان غیرهمزمان داده‌ها (Async Flow)",
      category: "advanced",
      status: "IN_PROGRESS",
      prerequisites: ["error_handling"],
    },
    {
      slug: "tenant_isolation",
      title: "تفکیک داده‌ها و ایزولاسیون معماری",
      category: "architecture",
      status: "IN_PROGRESS",
      prerequisites: ["async_flow"],
    },
  ],
};

export const mockMentorDossier: MentorIntelligenceDossierReadModel = {
  learner_id: "student-cs-9804",
  student_code: "CS-9804",
  display_name: "علی محمدی",
  pedagogical_summary: [
    "دانش‌آموز با استقامت بالا چالش Race Condition در پردازش غیرهمزمان را با ۴ بار آزمون و خطا حل کرد.",
    "در درک تفاوت میان قفل خوش‌بینانه و بدبینانه نیاز به گفتگوی عمیق مفهومی دارد.",
  ],
  evidence_trace: [
    "commit: feat/weather-async-fetch (e4a89bc)",
    "milestone: اتصال به سرویس هواشناسی با الگوی مدیریت خطا",
    "progress: 85%",
  ],
  suggested_socratic_prompts: [
    "اگر دو درخواست شبکه به طور همزمان وضعیت آب‌وهوا را به‌روزرسانی کنند، سیستم چگونه از برخورد داده‌ها جلوگیری می‌کند؟",
    "کدام استراتژی مدیریت خطا به نظرت پایداری تجربه کاربر را در شرایط قطعی اینترنت بهتر تضمین می‌کند؟",
  ],
  friction_signal: {
    signal_type: "CONCEPTUAL_FRICTION",
    concept: "Async Pipeline Error Handling",
    suggested_mentor_action: "پیشنهاد گفتگوی سقراطی پیرامون تجزیه مسئله به گام‌های کوچک‌تر",
    is_active: true,
  },
};

export const mockParentInsight: ParentInsightReadModel = {
  learner_id: "student-cs-9804",
  developmental_translation:
    "فرزند شما امروز نشان داد که در مواجهه با خطاهای پیچیده منطقی تسلیم نمی‌شود و با شجاعت و صبر توانست گره برنامه را باز کند. او حس مسئولیت‌پذیری بالایی در کار گروهی نشان داده است.",
  home_support_cues: [
    "امشب از او بپرسید جذاب‌ترین معمایی که امروز در کدهایش کشف و حل کرد چه بود؟",
    "صبر و پشتکار او را در رفع ابهامات پیچیده تحسین کنید.",
  ],
  technical_jargon_suppressed: true,
  last_briefing_at: "2026-09-21T00:30:00Z",
};

export const mockStudentReflections: StudentReflectionEntry[] = [
  {
    reflection_id: "refl-001",
    milestone_slug: "weather-async",
    reflection_text: "اولش مدیریت خطاهای async خیلی برام گیج‌کننده بود، ولی وقتی یونیت‌تست نوشتم و گام‌به‌گام ردیابی کردم فهمیدم جریان داده چطور کار می‌کنه.",
    sentiment: "confident",
    created_at: "2026-09-21T00:20:00Z",
    status: "RECORDED",
  },
];

export function useLearningIntelligence(role: "student" | "mentor" | "parent"): UnifiedIntelligenceProjection {
  switch (role) {
    case "student":
      return {
        skill_graph: mockSkillGraph,
        reflections: mockStudentReflections,
        mentor_dossier: null,
        parent_insight: null,
      };
    case "mentor":
      return {
        skill_graph: mockSkillGraph,
        mentor_dossier: mockMentorDossier,
        reflections: mockStudentReflections,
        parent_insight: null,
      };
    case "parent":
      return {
        parent_insight: mockParentInsight,
        skill_graph: null,
        mentor_dossier: null,
        reflections: [],
      };
    default:
      return {};
  }
}
