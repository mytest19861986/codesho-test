import { ParentDashboardScreen, type ParentSummaryData } from "@/features/parent/ParentDashboardScreen";

const syntheticParentSummary: ParentSummaryData = {
  studentName: "دانش‌آموز کوشا (سنتتیک)",
  learningPathTitle: "مسیر جامع برنامه‌نویسی و هوش مصنوعی",
  currentCourseTitle: "برنامه‌نویسی پایتون و هوش مصنوعی",
  totalLessons: 6,
  completedLessons: 4,
  completionPercentage: 66,
  activeAssignments: [
    { id: "a1", title: "پروژه ماشین‌حساب پایتون", code: "py-calc-p1" },
    { id: "a2", title: "طراحی دستیار هوشمند متنی", code: "py-bot-p2" },
  ],
  recentFeedbacks: [
    {
      id: "fb-1",
      mentorName: "دکتر سهرابی",
      date: "۱۴۰۳/۰۶/۱۷",
      content: "تمرین به زیبایی و با رعایت دقیق ساختار ماژولار انجام شد. پیشرفت دانش‌آموز در درک توابع بسیار چشمگیر است.",
    },
  ],
};

export default function ParentDashboardPage() {
  return <ParentDashboardScreen summary={syntheticParentSummary} />;
}
