"use client";

import React from "react";
import {
  StudentCoachingDashboard,
  CoachingSessionData,
  SupportInterventionData,
  FollowUpActionData,
} from "@/components/coaching/StudentCoachingDashboard";

export default function StudentCoachingPage() {
  const sampleSessions: CoachingSessionData[] = [
    {
      id: "sess-1",
      title: "جلسه تحلیل پیشرفت در مفاهیم پیشرفته پایگاه‌داده و RLS",
      status: "COMPLETED",
      scheduledAt: "۱۴۰۵/۰۶/۲۲ - ساعت ۱۶:۰۰",
      startedAt: "۱۴۰۵/۰۶/۲۲ - ۱۶:۰۲",
      completedAt: "۱۴۰۵/۰۶/۲۲ - ۱۶:۴۵",
      summary: "بررسی تسلط بر کلیدهای خارجی ترکیبی، خط‌مشی‌های تفکیک مستاجر و پیاده‌سازی آزمون‌های رفتاری منفی.",
      notes: [
        {
          id: "note-1",
          noteType: "STRENGTH",
          content: "دانش‌آموز دید بسیار دقیقی نسبت به جلوگیری از نشت داده بین مستاجرها دارد.",
          createdAt: "۱۴۰۵/۰۶/۲۲",
        },
        {
          id: "note-2",
          noteType: "GROWTH_OPPORTUNITY",
          content: "پیشنهاد می‌شود روی تراکنش‌های همزمان و قفل‌های ادوایزری تمرین بیشتری صورت گیرد.",
          createdAt: "۱۴۰۵/۰۶/۲۲",
        },
      ],
    },
    {
      id: "sess-2",
      title: "جلسه بررسی راهبردهای توسعه کامپوننت‌های فرانت‌اند دسترس‌پذیر",
      status: "SCHEDULED",
      scheduledAt: "۱۴۰۵/۰۶/۲۸ - ساعت ۱۷:۰۰",
    },
  ];

  const sampleInterventions: SupportInterventionData[] = [
    {
      id: "int-1",
      title: "برنامه مکمل تمرین همزمانی با Advisory Locks در PostgreSQL",
      category: "ACADEMIC_SCAFFOLDING",
      status: "PROPOSED",
      isAuthoritative: false,
      rationale: "منتور متوجه ابهام در رفتار همزمانی چند درخواست موازی شده و این منبع تکمیلی را پیشنهاد کرده است.",
      proposedAt: "۱۴۰۵/۰۶/۲۳",
    },
    {
      id: "int-2",
      title: "کارگاه یادگیری همتایاری و مرور کد (Peer Review Workshop)",
      category: "PEER_STUDY_CONNECTION",
      status: "ACCEPTED",
      isAuthoritative: false,
      rationale: "فرصتی عالی برای هم‌افزایی با سایر هم‌دوره‌ای‌ها و یادگیری از کدهای یکدیگر.",
      studentFeedback: "با کمال میل شرکت می‌کنم تا بازخورد کدهایم را بگیرم.",
      proposedAt: "۱۴۰۵/۰۶/۲۰",
    },
  ];

  const sampleActions: FollowUpActionData[] = [
    {
      id: "act-1",
      title: "پیاده‌سازی آزمون‌های N1 تا N28 برای اطمینان از عدم رگرسیون معماری",
      status: "COMPLETED",
      dueDate: "۱۴۰۵/۰۶/۲۵",
    },
    {
      id: "act-2",
      title: "نوشتن سناریوی آزمایشی قفل تراکنشی با pg_advisory_xact_lock",
      status: "PENDING",
      dueDate: "۱۴۰۵/۰۶/۲۹",
    },
  ];

  return (
    <main style={{ minHeight: "100vh", backgroundColor: "#f8fafc" }}>
      <StudentCoachingDashboard
        sessions={sampleSessions}
        interventions={sampleInterventions}
        actions={sampleActions}
        onAcceptIntervention={(id, feedback) => {
          alert(`مداخله ${id} پذیرفته شد. بازخورد: ${feedback || "بدون متن"}`);
        }}
        onDeclineIntervention={(id, feedback) => {
          alert(`مداخله ${id} رد شد. بازخورد: ${feedback || "بدون متن"}`);
        }}
        onCompleteAction={(id) => {
          alert(`اقدام ${id} تکمیل گردید.`);
        }}
        onSkipAction={(id, reason) => {
          alert(`اقدام ${id} صرف‌نظر شد. دلیل: ${reason}`);
        }}
      />
    </main>
  );
}
