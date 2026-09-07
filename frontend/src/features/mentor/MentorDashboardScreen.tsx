"use client";

import React, { useState } from "react";
import { AppShell, type NavigationItem } from "@/components/layout";
import styles from "./mentor.module.css";

export interface MentorSubmissionItem {
  readonly id: string;
  readonly assignmentTitle: string;
  readonly assignmentCode: string;
  readonly lessonTitle: string;
  readonly studentName: string;
  readonly content: string;
  readonly state: "submitted" | "under_review" | "reviewed";
  readonly submittedAt: string;
  readonly feedback?: string;
}

export interface MentorDashboardProps {
  readonly mentorName: string;
  readonly submissions: MentorSubmissionItem[];
  readonly onStartReview?: (submissionId: string) => void;
  readonly onCompleteReview?: (submissionId: string, feedback: string) => void;
}

const navigationItems: NavigationItem[] = [
  { id: "mentor-dashboard", label: "صف بررسی", href: "/dashboard/mentor", icon: "⌂" },
];

function Brand() {
  return (
    <a className={styles.brand} href="/dashboard/mentor">
      <span aria-hidden="true">⌁</span>
      <span>کُدشو - پنل مربی</span>
    </a>
  );
}

export function MentorDashboardScreen({
  mentorName,
  submissions: initialSubmissions,
  onStartReview,
  onCompleteReview,
}: MentorDashboardProps) {
  const [submissions, setSubmissions] = useState<MentorSubmissionItem[]>(initialSubmissions);
  const [selectedId, setSelectedId] = useState<string>(initialSubmissions[0]?.id ?? "");
  const [feedbackText, setFeedbackText] = useState<string>("");

  const currentSubmission = submissions.find((s) => s.id === selectedId);

  const handleStartReview = (id: string) => {
    onStartReview?.(id);
    setSubmissions((prev) =>
      prev.map((s) => (s.id === id ? { ...s, state: "under_review" } : s))
    );
  };

  const handleCompleteReview = (id: string) => {
    if (!feedbackText.trim()) return;
    onCompleteReview?.(id, feedbackText);
    setSubmissions((prev) =>
      prev.map((s) => (s.id === id ? { ...s, state: "reviewed", feedback: feedbackText } : s))
    );
    setFeedbackText("");
  };

  return (
    <AppShell
      activeItemId="mentor-dashboard"
      brand={<Brand />}
      drawerCloseLabel="بستن منو"
      menuButtonLabel="باز کردن منوی مربی"
      bottomNavigationItems={navigationItems}
      navigationItems={navigationItems}
      navigationLabel="ناوبری مربی"
      tone="teacher"
      profileSlot={<span aria-label="حساب کاربری مربی" className={styles.profile}>م</span>}
    >
      <main className={styles.page} dir="rtl">
        <section aria-labelledby="mentor-greeting" className={styles.hero}>
          <div>
            <p className={styles.eyebrow}>فضای ارزیابی و بازخورد</p>
            <h1 id="mentor-greeting">سلام استاد {mentorName}</h1>
            <p className={styles.heroMeta}>تکالیف ارسالی دانش‌آموزان آماده بررسی</p>
          </div>
        </section>

        <div className={styles.mainGrid}>
          <section aria-labelledby="queue-heading">
            <h2 id="queue-heading" className={styles.sectionHeading}>صف تکالیف ({submissions.length})</h2>
            <div className={styles.queueList}>
              {submissions.map((sub) => (
                <button
                  key={sub.id}
                  type="button"
                  aria-pressed={sub.id === selectedId}
                  className={styles.queueItem}
                  onClick={() => setSelectedId(sub.id)}
                >
                  <div className={styles.queueItemHeader}>
                    <strong>{sub.assignmentTitle}</strong>
                    <span
                      className={`${styles.badge} ${
                        sub.state === "submitted"
                          ? styles.badgeSubmitted
                          : sub.state === "under_review"
                          ? styles.badgeUnderReview
                          : styles.badgeReviewed
                      }`}
                    >
                      {sub.state === "submitted"
                        ? "در انتظار بررسی"
                        : sub.state === "under_review"
                        ? "در حال بررسی"
                        : "بررسی شده"}
                    </span>
                  </div>
                  <div>دانش‌آموز: {sub.studentName}</div>
                  <small style={{ color: "var(--cs-color-text-secondary, #64748b)" }}>
                    درس: {sub.lessonTitle}
                  </small>
                </button>
              ))}
            </div>
          </section>

          <section aria-labelledby="detail-heading">
            <h2 id="detail-heading" className={styles.sectionHeading}>جزئیات تکلیف و ثبت بازخورد</h2>
            {currentSubmission ? (
              <div className={styles.detailPanel}>
                <div>
                  <h3>{currentSubmission.assignmentTitle} ({currentSubmission.assignmentCode})</h3>
                  <p style={{ margin: "0.25rem 0", color: "#64748b" }}>
                    دانش‌آموز: <strong>{currentSubmission.studentName}</strong> | تاریخ ارسال: {currentSubmission.submittedAt}
                  </p>
                </div>

                <div>
                  <h4>محتوای ارسالی دانش‌آموز:</h4>
                  <div className={styles.submissionBox}>{currentSubmission.content}</div>
                </div>

                {currentSubmission.state === "submitted" && (
                  <div>
                    <button
                      type="button"
                      className={styles.actionBtn}
                      onClick={() => handleStartReview(currentSubmission.id)}
                    >
                      شروع بررسی
                    </button>
                  </div>
                )}

                {currentSubmission.state === "under_review" && (
                  <div className={styles.feedbackForm}>
                    <label htmlFor="feedback-input"><strong>بازخورد تخصصی مربی:</strong></label>
                    <textarea
                      id="feedback-input"
                      className={styles.textarea}
                      placeholder="نقاط قوت، ضعف و راهنمایی‌های لازم را بنویسید..."
                      value={feedbackText}
                      onChange={(e) => setFeedbackText(e.target.value)}
                    />
                    <button
                      type="button"
                      className={styles.actionBtn}
                      onClick={() => handleCompleteReview(currentSubmission.id)}
                    >
                      تکمیل بررسی و ارسال بازخورد
                    </button>
                  </div>
                )}

                {currentSubmission.state === "reviewed" && (
                  <div style={{ background: "#f0fdf4", padding: "1rem", borderRadius: "0.5rem", border: "1px solid #bbf7d0" }}>
                    <h4 style={{ color: "#166534", margin: "0 0 0.5rem" }}>بازخورد ثبت شده:</h4>
                    <p style={{ margin: 0, color: "#15803d" }}>{currentSubmission.feedback ?? "بازخورد با موفقیت ثبت شد."}</p>
                  </div>
                )}
              </div>
            ) : (
              <p>تکلیفی برای نمایش انتخاب نشده است.</p>
            )}
          </section>
        </div>
      </main>
    </AppShell>
  );
}