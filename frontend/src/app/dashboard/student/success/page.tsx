"use client";

import React from "react";
import {
  StudentSuccessTimeline,
  SuccessPlanData,
  ActionStepData,
  TimelineEventData,
} from "@/components/success/StudentSuccessTimeline";

export default function StudentSuccessPage() {
  const samplePlan: SuccessPlanData = {
    id: "plan-1",
    title: "مسیر تسلط پیشرفته بر توسعه وب و ساختارهای داده با پایتون و تایپ‌اسکریپت",
    targetPeriod: "ترم پاییز ۱۴۰۵ (CURRENT_TERM)",
    status: "ACTIVE",
    notes: "تمرکز اصلی این ترم بر یادگیری عمیق، حل تمرینات الگوریتمی و پیاده‌سازی گام‌به‌گام پروژه‌های واقعی بدون فشار نمره یا رتبه‌بندی کلاسی است.",
    createdAt: "۱۴۰۵/۰۶/۲۰",
  };

  const sampleActionSteps: ActionStepData[] = [
    {
      id: "step-1",
      sequenceOrder: 1,
      title: "تمرین‌های ساختارهای داده پایه‌ای (پشته، صف، لیست‌های پیوندی)",
      description: "حل ۱۰ چالش کدنویسی الگوریتمی با تحلیل دقیق پیچیدگی زمانی و مکانی.",
      status: "COMPLETED",
      isAuthoritative: false,
      targetDate: "۱۴۰۵/۰۶/۲۵",
    },
    {
      id: "step-2",
      sequenceOrder: 2,
      title: "توسعه اندپوینت‌های مدل‌محور با DRF و اعتبارسنجی اسکیما",
      description: "طراحی ویوهای REST و آزمون‌های رفتاری مثبت و منفی.",
      status: "IN_PROGRESS",
      isAuthoritative: false,
      targetDate: "۱۴۰۵/۰۷/۰۵",
    },
    {
      id: "step-3",
      sequenceOrder: 3,
      title: "یکپارچه‌سازی رابط کاربری با کامپوننت‌های دسترسی‌پذیر و واکنشی",
      description: "رعایت استانداردهای WCAG 2.2 AA، جریان راست‌به‌چپ (RTL) و عایق‌سازی BiDi.",
      status: "PENDING",
      isAuthoritative: false,
      targetDate: "۱۴۰۵/۰۷/۱۵",
    },
  ];

  const sampleTimelineEvents: TimelineEventData[] = [
    {
      id: "evt-1",
      eventType: "GOAL_ANCHORED",
      headline: "تثبیت هدف مهارتی تسلط بر الگوریتم‌های مرتب‌سازی و جستجو",
      detail: "هدف یادگیری ثبت گردید و معیارهای تکوینی سنجش تسلط مشخص شدند.",
      createdAt: "۱۴۰۵/۰۶/۱۵",
    },
    {
      id: "evt-2",
      eventType: "INSIGHT_CONNECTED",
      headline: "شناسایی الگوی یادگیری عمیق و تقویت مهارت حل مسئله",
      detail: "تحلیل تحلیلی رفتار یادگیری نشان‌دهنده سرعت مطلوب در درک مباحث تجریدی است.",
      createdAt: "۱405/06/18",
    },
    {
      id: "evt-3",
      eventType: "ACTION_DISPATCHED",
      headline: "آغاز گام عملیاتی پیاده‌سازی وب‌سرویس و مدل‌های داده",
      detail: "گام دوم برنامه یادگیری فعال شد و منابع تکمیلی برای دانش‌آموز بارگذاری گردید.",
      createdAt: "۱۴۰۵/۰۶/۲۰",
    },
  ];

  return (
    <main>
      <StudentSuccessTimeline
        studentName="دانش‌آموز کوشای کدشو"
        plan={samplePlan}
        actionSteps={sampleActionSteps}
        timelineEvents={sampleTimelineEvents}
        onTransitionStep={(stepId, status) => {
          console.log(`Transitioning step ${stepId} to ${status}`);
        }}
      />
    </main>
  );
}
