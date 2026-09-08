"use client";

import React from "react";
import { DashboardScreen } from "@/features/dashboard/DashboardScreen";
import type { DashboardModel } from "@/features/dashboard/dashboard.types";
import { StreakIndicator } from "@/components/gamification/StreakIndicator";
import { BadgeShelf, BadgeItem } from "@/components/gamification/BadgeShelf";
import { EnrollmentCard, EnrollmentItem } from "@/components/enrollment/EnrollmentCard";

const syntheticEnrollments: EnrollmentItem[] = [
  {
    id: "enr-1",
    courseTitle: "برنامه‌نویسی پایتون و هوش مصنوعی",
    courseCode: "python-core",
    cohortTitle: "کوهورت پاییزه - کد الف",
    cohortCode: "FALL-2026-A",
    currentCount: 18,
    maxCapacity: 25,
    status: "active",
    enrolledAt: "۱۴۰۵/۰۶/۱۵",
  },
  {
    id: "enr-2",
    courseTitle: "توسعه فرانت‌اند تعاملی وب",
    courseCode: "web-frontend",
    cohortTitle: "کوهورت عصرگاهی - کد ب",
    cohortCode: "FALL-2026-B",
    currentCount: 30,
    maxCapacity: 30,
    status: "enrolled",
    enrolledAt: "۱۴۰۵/۰۶/۱۸",
  },
];

const syntheticStudentModel: DashboardModel = {
  student: {
    displayName: "دانش‌آموز کوشا (سنتتیک)",
  },
  learning: {
    selectedCourseId: "c1",
    courses: [
      {
        id: "c1",
        code: "python-core",
        title: "برنامه‌نویسی پایتون و هوش مصنوعی",
        state: "published",
      },
      {
        id: "c2",
        code: "web-frontend",
        title: "توسعه فرانت‌اند تعاملی وب",
        state: "published",
      },
    ],
    lessons: [
      {
        id: "l1",
        code: "py-intro",
        title: "آشنایی با متغیرها و ساختارهای داده",
        position: 1,
        state: "published",
      },
      {
        id: "l2",
        code: "py-loops",
        title: "حلقه‌ها، شروط و توابع در پایتون",
        position: 2,
        state: "published",
      },
      {
        id: "l3",
        code: "py-project",
        title: "پروژه عملی: ساخت دستیار هوشمند",
        position: 3,
        state: "published",
      },
    ],
  },
};

const syntheticBadges: BadgeItem[] = [
  {
    id: "b1",
    badge_code: "FIRST_LESSON",
    badge_level: 1,
    title: "نخستین گام یادگیری",
    description: "تکمیل موفقیت‌آمیز اولین درس پایتون",
    is_earned: true,
  },
  {
    id: "b2",
    badge_code: "STREAK_3_DAYS",
    badge_level: 1,
    title: "پشتکار ۳ روزه",
    description: "استمرار در فعالیت آموزشی برای ۳ روز متوالی",
    is_earned: true,
  },
  {
    id: "b3",
    badge_code: "STREAK_7_DAYS",
    badge_level: 1,
    title: "مشعل یادگیری",
    description: "استمرار در فعالیت آموزشی برای ۷ روز متوالی",
    is_earned: false,
  },
  {
    id: "b4",
    badge_code: "SUBMISSION_STAR",
    badge_level: 1,
    title: "تلاشگر برتر",
    description: "ارسال تمرین و دریافت اولین بازخورد مربی",
    is_earned: true,
  },
];

export default function StudentDashboardPage() {
  return (
    <DashboardScreen model={syntheticStudentModel} state="ready">
      {/* P3-VS4 Gamification Progression & Badges Section */}
      <section
        style={{
          maxWidth: "78rem",
          margin: "0 auto 1.5rem",
          padding: "0 1.5rem",
          direction: "rtl",
        }}
        aria-label="پیشرفت و دستاوردهای دانش‌آموز"
      >
        <StreakIndicator
          currentStreak={3}
          longestStreak={5}
          totalXp={240}
          level={3}
        />
        <BadgeShelf badges={syntheticBadges} />
      </section>

      {/* VS2 Mentor Feedback Visibility Section */}
      <section
        style={{
          maxWidth: "78rem",
          margin: "0 auto 3rem",
          padding: "0 1.5rem",
          direction: "rtl",
        }}
        aria-labelledby="feedback-history-title"
      >
        <div
          style={{
            background: "var(--cs-color-bg-surface, #ffffff)",
            border: "1px solid var(--cs-color-border-subtle, #e2e8f0)",
            borderRadius: "1rem",
            padding: "1.5rem",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
            <h2 id="feedback-history-title" style={{ margin: 0, fontSize: "1.25rem" }}>
              📋 بازخوردهای دریافتی از مربیان
            </h2>
            <span
              style={{
                fontSize: "0.85rem",
                padding: "0.25rem 0.75rem",
                borderRadius: "9999px",
                background: "#f0fdf4",
                color: "#166534",
                fontWeight: 700,
                border: "1px solid #bbf7d0",
              }}
            >
              ۱ بازخورد جدید
            </span>
          </div>

          <div
            style={{
              padding: "1.25rem",
              borderRadius: "0.75rem",
              background: "#f8fafc",
              border: "1px solid #e2e8f0",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
              <strong style={{ fontSize: "1.05rem" }}>پروژه ماشین‌حساب پایتون (py-calc-p1)</strong>
              <span style={{ fontSize: "0.85rem", color: "#64748b" }}>مربی: دکتر سهرابی | ۱۴۰۳/۰۶/۱۷</span>
            </div>
            <p style={{ margin: "0.5rem 0", color: "#334155", fontSize: "0.95rem", lineHeight: "1.6" }}>
              <strong>نظر و راهنمایی مربی:</strong> راهکار ارائه شده بسیار تمیز و ماژولار است. تابع به درستی پیاده‌سازی شده و اصول نگارش تمیز پایتون (PEP 8) رعایت شده است. به عنوان گام بعدی، مدیریت خطا برای تقسیم بر صفر را اضافه کنید.
            </p>
            <div style={{ marginTop: "0.75rem", display: "flex", gap: "0.5rem" }}>
              <span
                style={{
                  fontSize: "0.8rem",
                  padding: "0.2rem 0.6rem",
                  borderRadius: "0.25rem",
                  background: "#dcfce7",
                  color: "#15803d",
                  fontWeight: 600,
                }}
              >
                وضعیت: تأیید شده و تکمیل
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Phase 3 VS5 Course Enrollments & Cohorts Section */}
      <section
        style={{
          maxWidth: "78rem",
          margin: "0 auto 2rem",
          padding: "0 1.5rem",
        }}
      >
        <EnrollmentCard enrollments={syntheticEnrollments} />
      </section>

      {/* Phase 3 Synthetic Media Attachments Section */}
      <section
        style={{
          maxWidth: "78rem",
          margin: "0 auto 3rem",
          padding: "0 1.5rem",
          direction: "rtl",
        }}
        aria-labelledby="media-attachments-title"
      >
        <div
          style={{
            background: "var(--cs-color-bg-surface, #ffffff)",
            border: "1px solid var(--cs-color-border-subtle, #e2e8f0)",
            borderRadius: "1rem",
            padding: "1.5rem",
          }}
        >
          <h2 id="media-attachments-title" style={{ margin: "0 0 1rem 0", fontSize: "1.25rem" }}>
            📁 منابع و رسانه‌های ضمیمه آموزشی
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1rem" }}>
            <div style={{ padding: "1rem", borderRadius: "0.75rem", background: "#f8fafc", border: "1px solid #e2e8f0" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
                <span aria-hidden="true" style={{ fontSize: "1.25rem" }}>📄</span>
                <strong>راهنمای سریع سینتکس پایتون</strong>
              </div>
              <p style={{ margin: "0.25rem 0", fontSize: "0.85rem", color: "#64748b" }}>
                فرمت: PDF | حجم: ۱.۲ مگابایت | درس: مبانی متغیرها
              </p>
              <span style={{ display: "inline-block", marginTop: "0.5rem", fontSize: "0.75rem", padding: "0.15rem 0.5rem", borderRadius: "0.25rem", background: "#e0f2fe", color: "#0369a1" }}>
                تأیید اصالت داده: SYNTHETIC
              </span>
            </div>
            <div style={{ padding: "1rem", borderRadius: "0.75rem", background: "#f8fafc", border: "1px solid #e2e8f0" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
                <span aria-hidden="true" style={{ fontSize: "1.25rem" }}>📊</span>
                <strong>دیاگرام ساختارهای داده و حافظه</strong>
              </div>
              <p style={{ margin: "0.25rem 0", fontSize: "0.85rem", color: "#64748b" }}>
                فرمت: PNG | حجم: ۴۸۰ کیلوبایت | درس: ساختارهای داده
              </p>
              <span style={{ display: "inline-block", marginTop: "0.5rem", fontSize: "0.75rem", padding: "0.15rem 0.5rem", borderRadius: "0.25rem", background: "#e0f2fe", color: "#0369a1" }}>
                تأیید اصالت داده: SYNTHETIC
              </span>
            </div>
          </div>
        </div>
      </section>
    </DashboardScreen>
  );
}
