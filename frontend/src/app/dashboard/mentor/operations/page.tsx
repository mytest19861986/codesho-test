"use client";

import React, { useState } from "react";
import {
  MentorOperationsWorkspace,
  CaseloadItemData,
  SupportQueueItemData,
  CheckInItemData,
  ProgramAnalyticsData,
} from "@/components/mentor/MentorOperationsWorkspace";

export default function MentorOperationsPage() {
  const [supportQueue, setSupportQueue] = useState<SupportQueueItemData[]>([
    {
      id: "queue-1",
      studentName: "سارا احمدی (سنتتیک)",
      urgencyLevel: "URGENT",
      queueStatus: "PENDING",
      dueDate: "۱۴۰۵/۰۶/۲۳",
      sourceType: "مداخله تحصیلی",
      details: "نیاز به جلسه رفع اشکال در مفاهیم کلیدهای خارجی ترکیبی و RLS پس از بازخورد ارزیابی.",
    },
    {
      id: "queue-2",
      studentName: "علی رضایی (سنتتیک)",
      urgencyLevel: "MEDIUM",
      queueStatus: "IN_REVIEW",
      dueDate: "۱۴۰۵/۰۶/۲۵",
      sourceType: "جلسه مشاوره قبلی",
      details: "پیگیری تعهد ارسال نسخه بازنویسی‌شده پروژه مایگریشن چندمستاجری.",
    },
  ]);

  const [checkins, setCheckins] = useState<CheckInItemData[]>([
    {
      id: "checkin-1",
      studentName: "سارا احمدی (سنتتیک)",
      status: "SCHEDULED",
      scheduledStart: "۱۴۰۵/۰۶/۲۳ - ساعت ۱۵:۳۰",
      meetingLink: "https://meet.codesho.local/room/mentor-checkin-1",
      commitmentsCount: 2,
    },
    {
      id: "checkin-2",
      studentName: "محمد کمالی (سنتتیک)",
      status: "COMPLETED",
      scheduledStart: "۱۴۰۵/۰۶/۲۱ - ساعت ۱۱:۰۰",
      notes: "مرور پیشرفت پورتفولیو و تدوین دو اقدام تکمیلی.",
      commitmentsCount: 3,
    },
  ]);

  const sampleCaseload: CaseloadItemData[] = [
    {
      id: "case-1",
      studentName: "سارا احمدی (سنتتیک)",
      studentId: "std-101",
      capacityWeight: "1.20",
      assignedAt: "۱۴۰۵/۰۵/۰۱",
      isActive: true,
      focusArea: "معماری چندمستاجری و امنیت داده",
    },
    {
      id: "case-2",
      studentName: "علی رضایی (سنتتیک)",
      studentId: "std-102",
      capacityWeight: "1.00",
      assignedAt: "۱۴۰۵/۰۵/۱۰",
      isActive: true,
      focusArea: "توسعه فرانت‌اند و دسترس‌پذیری WCAG",
    },
    {
      id: "case-3",
      studentName: "محمد کمالی (سنتتیک)",
      studentId: "std-103",
      capacityWeight: "0.80",
      assignedAt: "۱۴۰۵/۰۵/۱۵",
      isActive: true,
      focusArea: "بهینه‌سازی کارایی و تست‌های منفی",
    },
  ];

  const sampleAnalytics: ProgramAnalyticsData = {
    totalAssignedStudents: 18,
    totalActiveInterventions: 4,
    totalCompletedCheckins: 32,
    averageResponseTimeHours: "2.40",
    supportCoverageRatio: "0.940",
    aggregatedAt: "۱۴۰۵/۰۶/۲۲ - ساعت ۱۸:۰۰",
  };

  const handleResolveQueueItem = (id: string, notes: string) => {
    setSupportQueue((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, queueStatus: "RESOLVED" } : item
      )
    );
  };

  const handleStartCheckin = (id: string) => {
    setCheckins((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, status: "IN_PROGRESS" } : item
      )
    );
  };

  const handleCompleteCheckin = (id: string, notes: string) => {
    setCheckins((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, status: "COMPLETED", notes } : item
      )
    );
  };

  return (
    <main style={{ minHeight: "100vh", backgroundColor: "#f8fafc" }}>
      <MentorOperationsWorkspace
        caseload={sampleCaseload}
        supportQueue={supportQueue.filter((q) => q.queueStatus !== "RESOLVED")}
        checkins={checkins}
        analytics={sampleAnalytics}
        onResolveQueueItem={handleResolveQueueItem}
        onStartCheckin={handleStartCheckin}
        onCompleteCheckin={handleCompleteCheckin}
      />
    </main>
  );
}
