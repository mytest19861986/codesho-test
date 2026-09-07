import { AdminLearningScreen, type CurriculumItem } from "@/features/admin_learning/AdminLearningScreen";

const syntheticCurriculum: CurriculumItem[] = [
  {
    id: "c-1",
    type: "course",
    code: "py-core",
    title: "برنامه‌نویسی پایتون و هوش مصنوعی",
    state: "published",
  },
  {
    id: "l-1",
    type: "lesson",
    code: "py-intro",
    title: "مبانی متغیرها و ساختارهای داده",
    state: "published",
  },
  {
    id: "a-1",
    type: "assignment",
    code: "py-calc-p1",
    title: "پروژه ماشین‌حساب پایتون",
    state: "published",
  },
  {
    id: "c-2",
    type: "course",
    code: "ml-foundations",
    title: "یادگیری ماشین و تحلیل داده با پایتون",
    state: "draft",
  },
];

export default function AdminLearningPage() {
  return <AdminLearningScreen initialItems={syntheticCurriculum} />;
}
