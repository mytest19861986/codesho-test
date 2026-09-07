import { MentorDashboardScreen, type MentorSubmissionItem } from "@/features/mentor/MentorDashboardScreen";

const syntheticSubmissions: MentorSubmissionItem[] = [
  {
    id: "sub-1",
    assignmentTitle: "پروژه ماشین‌حساب پایتون",
    assignmentCode: "py-calc-p1",
    lessonTitle: "توابع و شروط در پایتون",
    studentName: "دانش‌آموز کوشا (سنتتیک)",
    content: "def add(a, b):\n    return a + b\n\ndef calculate():\n    print(add(5, 7))\n\ncalculate()",
    state: "submitted",
    submittedAt: "۱۴۰۳/۰۶/۱۷ - ۱۰:۳۰",
  },
  {
    id: "sub-2",
    assignmentTitle: "ساخت کامپوننت دکمه مدرن در React",
    assignmentCode: "react-btn-p1",
    lessonTitle: "مبانی React و CSS ماژولار",
    studentName: "دانش‌آموز پویا (سنتتیک)",
    content: "export const Button = ({ label, onClick }) => (\n  <button className=\"btn-primary\" onClick={onClick}>\n    {label}\n  </button>\n);",
    state: "under_review",
    submittedAt: "۱۴۰۳/۰۶/۱۷ - ۰۹:۱۵",
  },
  {
    id: "sub-3",
    assignmentTitle: "طراحی اسکیما و مایگریشن چندمستأجری",
    assignmentCode: "pg-rls-p1",
    lessonTitle: "امنیت پایگاه داده PostgreSQL",
    studentName: "دانش‌آموز آرمان (سنتتیک)",
    content: "ALTER TABLE learning_submission ENABLE ROW LEVEL SECURITY;\nALTER TABLE learning_submission FORCE ROW LEVEL SECURITY;",
    state: "reviewed",
    submittedAt: "۱۴۰۳/۰۶/۱۶ - ۱۸:۰۰",
    feedback: "عالی! استفاده از FORCE ROW LEVEL SECURITY برای جلوگیری از دسترسی مستقیم سوپریوزر بسیار دقیق است.",
  },
];

export default function MentorDashboardPage() {
  return (
    <MentorDashboardScreen
      mentorName="دکتر سهرابی"
      submissions={syntheticSubmissions}
    />
  );
}