"use client";

import React from "react";
import {
  StudentLearningOperationsDashboard,
  ReflectionItem,
  GoalItem,
  GrowthSuggestionItem,
} from "@/components/operations/StudentLearningOperationsDashboard";

export default function StudentOperationsPage() {
  const sampleReflections: ReflectionItem[] = [
    {
      id: "refl-1",
      promptType: "بازنگری هفتگی یادگیری",
      content: "در تمرین‌های این هفته درک حلقه‌های تو در تو و توابع بازگشتی بسیار روان‌تر شد. ابتدا در شرط توقف بازگشت به خطا می‌خوردم اما با ترسیم درخت اجرا بر روی کاغذ مشکل را کشف کردم.",
      moodSentiment: "GROWTH_MINDSET",
      createdAt: "۱۴۰۵/۰۶/۱۹",
      mentorFeedback: "عالی است! رسم درخت فراخوانی دقیقاً بهترین روش تسلط بر الگوریتم‌های بازگشتی است. ادامه بده.",
    },
    {
      id: "refl-2",
      promptType: "عطف به مایلستون و تسلط جدید",
      content: "پروژه حل پشته و صف بدون کتابخانه‌های آماده را به پایان رساندم. اعتماد به نفسم در کار با اشاره‌گرها و متغیرها بالاتر رفته است.",
      moodSentiment: "CONFIDENT",
      createdAt: "۱۴۰۵/۰۶/۱۲",
    },
  ];

  const sampleGoals: GoalItem[] = [
    {
      id: "goal-1",
      title: "تسلط کامل بر الگوریتم‌های مرتب‌سازی و جستجوی دودویی در پایتون",
      domain: "ALGORITHMS_CORE",
      status: "ACTIVE",
      actionSteps: [
        { order: 1, text: "پیاده‌سازی جستجوی دودویی به روش تکرارشونده", completed: true },
        { order: 2, text: "پیاده‌سازی مرتب‌سازی ادغامی (Merge Sort)", completed: false },
        { order: 3, text: "تحلیل پیچیدگی زمانی O(n log n)", completed: false },
      ],
    },
    {
      id: "goal-2",
      title: "توسعه اولین وب‌سرویس REST با جانگو",
      domain: "BACKEND_SERVICES",
      status: "PAUSED",
      actionSteps: [
        { order: 1, text: "تعریف مدل‌ها و مایگریشن‌های اسکیما", completed: true },
        { order: 2, text: "طراحی ویوهای عمومی با DRF", completed: false },
      ],
    },
  ];

  const sampleSuggestions: GrowthSuggestionItem[] = [
    {
      id: "sugg-1",
      action: "تمرین چالش مقایسه سرعت اجرای جستجوی خطی و دودویی بر روی آرایه ۱۰۰۰ عنصری",
      rationale: "با توجه به علاقه شما به الگوریتم‌ها، سنجش تجربی زمان اجرا به درک شهودی Big-O کمک شایانی می‌کند.",
      evidenceCode: "EXP-ALGO-BINSEARCH-01",
      status: "PRESENTED",
    },
  ];

  return (
    <main>
      <StudentLearningOperationsDashboard
        studentName="دانش‌آموز کوشای کدشو"
        reflections={sampleReflections}
        goals={sampleGoals}
        suggestions={sampleSuggestions}
      />
    </main>
  );
}
