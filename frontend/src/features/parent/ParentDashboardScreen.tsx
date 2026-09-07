"use client";

import React from "react";
import { AppShell, type NavigationItem } from "@/components/layout";
import styles from "./parent.module.css";

export interface ParentSummaryData {
  readonly studentName: string;
  readonly learningPathTitle: string;
  readonly currentCourseTitle: string;
  readonly totalLessons: number;
  readonly completedLessons: number;
  readonly completionPercentage: number;
  readonly activeAssignments: Array<{ readonly id: string; readonly title: string; readonly code: string }>;
  readonly recentFeedbacks: Array<{ readonly id: string; readonly content: string; readonly mentorName: string; readonly date: string }>;
}

const navigationItems: NavigationItem[] = [
  { id: "parent-dashboard", label: "داشبورد والد", href: "/dashboard/parent", icon: "⌂" },
];

function Brand() {
  return (
    <a className={styles.brand} href="/dashboard/parent">
      <span aria-hidden="true">⌁</span>
      <span>کُدشو - پنل اولیا</span>
    </a>
  );
}

export function ParentDashboardScreen({ summary }: { readonly summary: ParentSummaryData }) {
  return (
    <AppShell
      activeItemId="parent-dashboard"
      brand={<Brand />}
      drawerCloseLabel="بستن منو"
      menuButtonLabel="باز کردن منوی والد"
      bottomNavigationItems={navigationItems}
      navigationItems={navigationItems}
      navigationLabel="ناوبری والد"
      tone="learner"
      profileSlot={<span aria-label="حساب والد" className={styles.profile}>و</span>}
    >
      <main className={styles.page} dir="rtl">
        <section aria-labelledby="parent-greeting" className={styles.hero}>
          <div>
            <p className={styles.eyebrow}>نمای پیشرفت تحصیلی فرزند</p>
            <h1 id="parent-greeting">سلام، گزارش پیشرفت {summary.studentName}</h1>
            <p className={styles.heroMeta}>مسیر: {summary.learningPathTitle} | دوره فعال: {summary.currentCourseTitle}</p>
          </div>
        </section>

        <section aria-label="آمار و شاخص‌های یادگیری" className={styles.statsGrid}>
          <div className={styles.statCard}>
            <span>درس‌های تکمیل‌شده</span>
            <strong>{summary.completedLessons} از {summary.totalLessons}</strong>
          </div>
          <div className={styles.statCard}>
            <span>درصد پیشرفت کل</span>
            <strong>٪{summary.completionPercentage}</strong>
          </div>
          <div className={styles.statCard}>
            <span>تکالیف فعال / ارزیابی‌شده</span>
            <strong>{summary.activeAssignments.length}</strong>
          </div>
        </section>

        <div className={styles.sectionGrid}>
          <section aria-labelledby="feedback-title" className={styles.card}>
            <h2 id="feedback-title" className={styles.cardTitle}>
              <span>📋 آخرین بازخوردهای مربیان</span>
              <span className={`${styles.badge} ${styles.badgeSuccess}`}>تأیید شده</span>
            </h2>
            {summary.recentFeedbacks.length > 0 ? (
              <div className={styles.list}>
                {summary.recentFeedbacks.map((fb) => (
                  <div key={fb.id} className={styles.feedbackBox}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", color: "#64748b" }}>
                      <strong>مربی: {fb.mentorName}</strong>
                      <span>{fb.date}</span>
                    </div>
                    <p>{fb.content}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: "#64748b" }}>هنوز بازخوردی ثبت نشده است.</p>
            )}
          </section>

          <section aria-labelledby="assignments-title" className={styles.card}>
            <h2 id="assignments-title" className={styles.cardTitle}>
              <span>🎯 تکالیف و پروژه‌های دوره</span>
            </h2>
            <ul className={styles.list}>
              {summary.activeAssignments.map((a) => (
                <li key={a.id} className={styles.listItem}>
                  <div>
                    <strong>{a.title}</strong>
                    <div style={{ fontSize: "0.8rem", color: "#64748b" }}>کد: {a.code}</div>
                  </div>
                  <span className={`${styles.badge} ${styles.badgeInfo}`}>منتشر شده</span>
                </li>
              ))}
            </ul>
          </section>
        </div>
      </main>
    </AppShell>
  );
}
