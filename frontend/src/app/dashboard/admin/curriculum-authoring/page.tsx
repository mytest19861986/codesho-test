import React from "react";
import {
  CurriculumAuthoringWorkspace,
  type WorkspaceItem,
  type ChangeSetItem,
  type RubricItem,
  type ReadinessGateItem,
  type RollforwardPlanItem,
} from "@/components/curriculum/CurriculumAuthoringWorkspace";

const syntheticWorkspaces: WorkspaceItem[] = [
  {
    id: "ws-91a2-4411-88fc",
    courseTitle: "هوش مصنوعی و یادگیری عمیق در پایتون",
    workspaceTitle: "به‌روزرسانی جامع سرفصل پایتون ۱۴۰۵",
    status: "ACTIVE",
    createdAt: "۱۴۰۵/۰۱/۱۵",
  },
  {
    id: "ws-72bf-3392-11da",
    courseTitle: "توسعه وب مدرن با ری‌اکت و نکست‌جی‌اس",
    workspaceTitle: "افزودن مباحث معماری سِروِری React 19",
    status: "ACTIVE",
    createdAt: "۱۴۰۵/۰۱/۱۸",
  },
];

const syntheticChangeSets: ChangeSetItem[] = [
  {
    id: "cs-1001-aa22-55ff",
    title: "بازطراحی پروژه عملی فاز دوم یادگیری عمیق",
    changeSummary: "بهینه‌سازی کدهای پایه‌ای و جایگزینی مدل‌های قدیمی با ترنسفورمرهای مدرن",
    status: "IN_REVIEW",
    authorName: "مریم احمدی (مؤلف ارشد)",
    createdAt: "۱۴۰۵/۰۱/۲۰",
  },
  {
    id: "cs-1002-bb33-66ee",
    title: "به‌روزرسانی منابع و اسلایدهای مقدماتی",
    changeSummary: "تصحیح پیوندها و درج مراجع استاندارد بین‌المللی",
    status: "DRAFT",
    authorName: "سهراب سپهری",
    createdAt: "۱۴۰۵/۰۱/۲۲",
  },
];

const syntheticRubrics: RubricItem[] = [
  {
    id: "rb-401-cc77",
    rubricTitle: "روبریک ارزیابی شایستگی مهندسی نرم‌افزار و تمیزی کد",
    scaleType: "QUALITATIVE_STANDARD",
    status: "ACTIVE",
    isAntiRankingCompliant: true,
    criteriaCount: 4,
  },
  {
    id: "rb-402-dd88",
    rubricTitle: "روبریک تحلیلی درک نظری الگوریتم‌های هوش مصنوعی",
    scaleType: "QUALITATIVE_STANDARD",
    status: "ACTIVE",
    isAntiRankingCompliant: true,
    criteriaCount: 3,
  },
];

const syntheticGates: ReadinessGateItem[] = [
  {
    id: "gate-1",
    gateName: "تأییدیه داوری هیئت تحریریه (Editorial Sign-off)",
    isBlocking: true,
    verdict: "PASSED",
    evaluatedAt: "۱۴۰۵/۰۱/۲۳ ۱۰:۳۰",
  },
  {
    id: "gate-2",
    gateName: "انطباق روبریک با اصل منع رتبه‌بندی (Anti-Ranking)",
    isBlocking: true,
    verdict: "PASSED",
    evaluatedAt: "۱۴۰۵/۰۱/۲۳ ۱۰:۳۰",
  },
  {
    id: "gate-3",
    gateName: "تکمیل دارایی‌های چندرسانه‌ای و اسناد پشتیبان",
    isBlocking: false,
    verdict: "PASSED",
    evaluatedAt: "۱۴۰۵/۰۱/۲۳ ۱۰:۳۱",
  },
  {
    id: "gate-4",
    gateName: "تحلیل اثرات بر دوره‌های فعال (Impact Analysis)",
    isBlocking: true,
    verdict: "PASSED",
    evaluatedAt: "۱۴۰۵/۰۱/۲۳ ۱۰:۳۱",
  },
];

const syntheticRollforwardPlans: RollforwardPlanItem[] = [
  {
    id: "rf-801",
    cohortName: "دوره بهار ۱۴۰۵ - کد ۱۰۱",
    targetReleaseTag: "v2.1.0-lts",
    mode: "FUTURE_MODULES_ONLY",
    status: "APPROVED",
    scheduledDate: "۱۴۰۵/۰۲/۰۱",
  },
];

export default function CurriculumAuthoringPage() {
  return (
    <div style={{ padding: "1.5rem", maxWidth: "1400px", margin: "0 auto" }}>
      <CurriculumAuthoringWorkspace
        workspaces={syntheticWorkspaces}
        changeSets={syntheticChangeSets}
        rubrics={syntheticRubrics}
        readinessGates={syntheticGates}
        rollforwardPlans={syntheticRollforwardPlans}
      />
    </div>
  );
}
