"use client";

import React from "react";
import {
  GrowthJourneyDashboard,
  GrowthMetricItem,
  GrowthTrendData,
  GrowthInsightItem,
  FormativeMilestoneItem,
} from "@/components/growth/GrowthJourneyDashboard";

export default function StudentGrowthPage() {
  const metrics: GrowthMetricItem[] = [
    { key: "CONCEPT_MASTERY", label: "تسلط مفهومی بر کدنویسی", value: 88, delta: 12 },
    { key: "CODING_VELOCITY", label: "سرعت و ریتم حل مسئله", value: 92, delta: 8 },
    { key: "PROBLEM_SOLVING", label: "پایداری در دیباگ و اصلاح خطا", value: 85, delta: 15 },
    { key: "CODE_QUALITY", label: "رعایت تمیزی و استانداردهای نحوی", value: 90, delta: 10 },
  ];

  const trend: GrowthTrendData = {
    domain: "FULLSTACK_FOUNDATIONS",
    direction: "ACCELERATING",
    score: 88.5,
    velocity: 12.0,
    totalMilestones: 4,
  };

  const insights: GrowthInsightItem[] = [
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
  ];

  const milestones: FormativeMilestoneItem[] = [
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
  ];

  return (
    <main style={{ minHeight: "100vh", background: "#f8fafc", padding: "2rem 0" }}>
      <GrowthJourneyDashboard
        studentName="سهراب سپهری"
        metrics={metrics}
        trend={trend}
        insights={insights}
        milestones={milestones}
      />
    </main>
  );
}
