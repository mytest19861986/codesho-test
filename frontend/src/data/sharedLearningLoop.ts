/**
 * Wave 5.5.4 — Cross-Role Learning Loop
 * Shared Synthetic Domain & Demo State Adapter
 * Principles:
 * STUDENT ACTION -> LEARNING EVIDENCE -> MENTOR INTERPRETATION -> PARENT UNDERSTANDING -> STUDENT CONTINUES
 */

export interface SharedLearningState {
  student: {
    id: string;
    name: string;
    avatar: string;
    level: string;
    streakDays: number;
  };
  activeProject: {
    id: string;
    title: string;
    branch: string;
    commitHash: string;
    progressPercentage: number;
    currentMilestone: string;
    recentActivity: string;
    lastCodeSnippet: string;
    skillsDemonstrated: string[];
  };
  mentorIntervention: {
    status: "OPEN" | "REVIEWING" | "FOLLOW_UP" | "RESOLVED";
    reason: string;
    recommendedAction: string;
    mentorNotes: string;
    feedbacks: Array<{
      id: string;
      sender: "MENTOR" | "STUDENT";
      timestamp: string;
      text: string;
      actionType: string;
    }>;
  };
  parentBridge: {
    lastBriefing: string;
    briefingTimestamp: string;
    parentEncouragementSent: boolean;
    parentEncouragementMessage: string;
  };
}

export const defaultSharedLearningState: SharedLearningState = {
  student: {
    id: "CS-9804",
    name: "علی محمدی",
    avatar: "ali",
    level: "پایتون پیشرفته • Python Explorer",
    streakDays: 7,
  },
  activeProject: {
    id: "proj-weather-async",
    title: "سامانه اطلاع‌رسانی وضعیت آب‌وهوا",
    branch: "feat/weather-async-fetch",
    commitHash: "e4a89bc",
    progressPercentage: 74,
    currentMilestone: "پیاده‌سازی بلوک‌های try/catch و دریافت پاسخ امن وب‌سرویس",
    recentActivity: "تلاش برای اتصال به وب‌سرویس و بهینه‌سازی پردازش داده‌های ابری",
    lastCodeSnippet: `async function fetchWeather(city) {\n  try {\n    const response = await fetch(\`https://api.example.com/weather?q=\${city}\`);\n    const data = await response.json();\n    renderWeather(data);\n  } catch (error) {\n    console.error('خطای ارتباط با سرور:', error);\n    showFallback('امکان دریافت اطلاعات در حال حاضر وجود ندارد.');\n  }\n}`,
    skillsDemonstrated: ["JavaScript ES6+", "DOM Manipulation", "Async/Await", "Error Handling"],
  },
  mentorIntervention: {
    status: "REVIEWING",
    reason: "گیر کردن در مدیریت خطاهای ناهمگام (Async/Await)",
    recommendedAction: "بررسی ساختار try/catch و تست سناریوی قطع شبکه",
    mentorNotes: "علی در مباحث پایه قوی است؛ بازخورد فنی به همراه تشویق انگیزشی ارسال شد.",
    feedbacks: [
      {
        id: "fb-initial",
        sender: "MENTOR",
        timestamp: "دیروز، ۱۶:۳۰",
        text: "علی عزیز، خط اول تابع رو داخل بلوک try قرار بده و پیام خطا رو کنترل کن.",
        actionType: "راهنمایی فنی",
      },
    ],
  },
  parentBridge: {
    lastBriefing: "علی در حال کار بر روی پروژه سامانه آب‌وهوا است. با راهنمایی مربی، چالش مدیریت خطاها برطرف شده و سرعت یادگیری بسیار مطلوب است.",
    briefingTimestamp: "امروز، ۱۱:۰۰",
    parentEncouragementSent: true,
    parentEncouragementMessage: "علی جان، به تلاشت افتخار می‌کنیم. با قدرت ادامه بده!",
  },
};

const STORAGE_KEY = "codesho_cross_role_learning_loop_state";

export function getSharedLearningState(): SharedLearningState {
  if (typeof window === "undefined") {
    return defaultSharedLearningState;
  }
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(defaultSharedLearningState));
      return defaultSharedLearningState;
    }
    return JSON.parse(raw);
  } catch {
    return defaultSharedLearningState;
  }
}

export function updateSharedLearningState(updater: (prev: SharedLearningState) => SharedLearningState): SharedLearningState {
  if (typeof window === "undefined") {
    return defaultSharedLearningState;
  }
  try {
    const current = getSharedLearningState();
    const updated = updater(current);
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    // Trigger storage event across open tabs/windows
    window.dispatchEvent(new Event("storage"));
    return updated;
  } catch {
    return defaultSharedLearningState;
  }
}

export function resetSharedLearningState(): SharedLearningState {
  if (typeof window === "undefined") {
    return defaultSharedLearningState;
  }
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(defaultSharedLearningState));
  window.dispatchEvent(new Event("storage"));
  return defaultSharedLearningState;
}
