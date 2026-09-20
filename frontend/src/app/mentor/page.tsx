"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  syntheticCohortPulse,
  initialInterventions,
  Intervention,
  CohortPulseItem,
} from "@/data/mentorSyntheticData";
import { updateSharedLearningState } from "@/data/sharedLearningLoop";
import {
  IconCheck,
  IconClose,
  IconClock,
  IconDocument,
  IconLaptop,
  IconShield,
  IconSparkles,
} from "@/components/ui";
import styles from "./mentor.module.css";

export default function MentorCommandCenterPage() {
  const [selectedCohort, setSelectedCohort] = useState<string>("all");
  const [interventions, setInterventions] = useState<Intervention[]>(initialInterventions);
  const [activeInterventionId, setActiveInterventionId] = useState<string>(initialInterventions[0].id);
  const [feedbackText, setFeedbackText] = useState<string>("");
  const [toastMsg, setToastMsg] = useState<string | null>(null);
  
  // Drawer states
  const [isEvidenceDrawerOpen, setIsEvidenceDrawerOpen] = useState<boolean>(false);
  const [isParentBriefingOpen, setIsParentBriefingOpen] = useState<boolean>(false);

  const activeIntervention = interventions.find((i) => i.id === activeInterventionId) || interventions[0];

  const showToast = (msg: string) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 3500);
  };

  const handleStatusChange = (newStatus: Intervention["status"]) => {
    setInterventions((prev) =>
      prev.map((item) =>
        item.id === activeIntervention.id ? { ...item, status: newStatus } : item
      )
    );
    if (activeIntervention.studentName.includes("علی")) {
      updateSharedLearningState((prev) => ({
        ...prev,
        mentorIntervention: {
          ...prev.mentorIntervention,
          status: newStatus,
        },
      }));
    }
    showToast(`وضعیت مداخله با موفقیت به «${newStatus}» به‌روزرسانی شد.`);
  };

  const handleSendFeedback = (actionType: string) => {
    if (!feedbackText.trim()) {
      showToast("لطفاً متن بازخورد یا راهنمایی را وارد کنید.");
      return;
    }

    const newFeedback = {
      id: `fb-${Date.now()}`,
      sender: "MENTOR" as const,
      timestamp: "هم‌اکنون",
      text: feedbackText.trim(),
      actionType,
    };

    setInterventions((prev) =>
      prev.map((item) =>
        item.id === activeIntervention.id
          ? {
              ...item,
              status: item.status === "OPEN" ? "REVIEWING" : item.status,
              feedbackHistory: [newFeedback, ...item.feedbackHistory],
            }
          : item
      )
    );

    if (activeIntervention.studentName.includes("علی")) {
      updateSharedLearningState((prev) => ({
        ...prev,
        mentorIntervention: {
          ...prev.mentorIntervention,
          status: prev.mentorIntervention.status === "OPEN" ? "REVIEWING" : prev.mentorIntervention.status,
          feedbacks: [
            {
              id: newFeedback.id,
              sender: "MENTOR",
              timestamp: "هم‌اکنون",
              text: newFeedback.text,
              actionType,
            },
            ...prev.mentorIntervention.feedbacks,
          ],
        },
      }));
    }

    setFeedbackText("");
    showToast(`اقدام «${actionType}» برای دانش‌آموز ثبت و ارسال گردید.`);
  };

  const handleResolveIntervention = () => {
    handleStatusChange("RESOLVED");
    showToast(`مداخله مربوط به ${activeIntervention.studentName} حل‌شده علامت‌گذاری شد.`);
  };

  const filteredInterventions = selectedCohort === "all"
    ? interventions
    : interventions.filter((i) => i.cohort.includes(selectedCohort));

  return (
    <div className={styles.mentorCommandCenter} dir="rtl">
      {/* Toast Notification */}
      {toastMsg && (
        <div
          style={{
            position: "fixed",
            bottom: "1.5rem",
            left: "50%",
            transform: "translateX(-50%)",
            background: "#0f172a",
            color: "#ffffff",
            padding: "0.75rem 1.5rem",
            borderRadius: "9999px",
            fontSize: "0.875rem",
            fontWeight: 600,
            zIndex: 1000,
            boxShadow: "0 10px 25px rgba(0,0,0,0.2)",
          }}
        >
          {toastMsg}
        </div>
      )}

      {/* 1. Header & Cohort Switcher */}
      <header className={styles.mentorHeader}>
        <div className={styles.mentorBrandGroup}>
          <div className={styles.mentorIconBadge}>
            <IconLaptop style={{ inlineSize: "1.75rem", blockSize: "1.75rem" }} />
          </div>
          <div className={styles.mentorHeaderTitles}>
            <h1 className={styles.mentorTitle}>مرکز فرماندهی مربیان (Mentor Command Center)</h1>
            <p className={styles.mentorSubtitle}>
              رصد هوشمند سیگنال‌های یادگیری، بررسی شواهد کد و هدایت متمرکز دانش‌آموزان
            </p>
          </div>
        </div>

        <div className={styles.cohortSwitcher}>
          <label htmlFor="cohortSelect" style={{ fontSize: "0.85rem", fontWeight: 700, color: "#475569" }}>
            دوره آموزشی:
          </label>
          <select
            id="cohortSelect"
            className={styles.cohortSelect}
            value={selectedCohort}
            onChange={(e) => setSelectedCohort(e.target.value)}
          >
            <option value="all">همه دوره‌های فعال ({interventions.length} دانش‌آموز)</option>
            <option value="پاییز">کدنویسی خلاق سطح ۲ (پاییز)</option>
            <option value="پایگاه داده">پایگاه داده و معماری وب</option>
          </select>
        </div>
      </header>

      {/* 2. Cohort Pulse (Human Pulse Signals) */}
      <section className={styles.pulseSection} aria-label="وضعیت انسانی دوره">
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>
            <IconSparkles style={{ inlineSize: "1.25rem", blockSize: "1.25rem", color: "#4f46e5" }} />
            <span>نبض پویای دوره (Cohort Pulse)</span>
          </h2>
        </div>

        <div className={styles.pulseGrid}>
          {syntheticCohortPulse.map((pulse: CohortPulseItem) => (
            <div
              key={pulse.id}
              className={`${styles.pulseCard} ${styles[`pulseType${pulse.type}`]}`}
              onClick={() => showToast(`فیلتر اعمال شد: ${pulse.label}`)}
            >
              <div className={styles.pulseTop}>
                <span className={styles.pulseLabel}>{pulse.label}</span>
                <span className={styles.pulseCount}>{pulse.count}</span>
              </div>
              <p className={styles.pulseDesc}>{pulse.description}</p>
              <div className={styles.pulseActionHint}>
                <span>اقدام: {pulse.actionHint}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 3. Main Workspace: Intervention Queue & Evidence Workspace */}
      <div className={styles.workspaceLayout}>
        {/* Left Column: Student Intervention Queue */}
        <section className={styles.queuePanel} aria-label="صف مداخله دانش‌آموزان">
          <div className={styles.sectionHeader}>
            <h2 className={styles.sectionTitle}>صف مداخلات فعال ({filteredInterventions.length})</h2>
          </div>

          <div className={styles.queueList}>
            {filteredInterventions.map((item) => {
              const isActive = item.id === activeIntervention.id;
              return (
                <article
                  key={item.id}
                  className={`${styles.queueItem} ${isActive ? styles.queueItemActive : ""}`}
                  onClick={() => setActiveInterventionId(item.id)}
                >
                  <div className={styles.queueItemHeader}>
                    <span className={styles.queueStudentName}>{item.studentName}</span>
                    <span className={`${styles.urgencyBadge} ${styles[`urgency${item.urgency}`]}`}>
                      {item.urgency === "HIGH" ? "فوریت بالا" : item.urgency === "MEDIUM" ? "متوسط" : "عادی"}
                    </span>
                  </div>

                  <div className={styles.queueReason}>{item.reason}</div>
                  <p className={styles.queueContext}>{item.context}</p>

                  <div className={styles.queueItemFooter}>
                    <span className={styles.queueStatusBadge}>وضعیت: {item.status}</span>
                    <button
                      type="button"
                      className={styles.queueActionLink}
                      onClick={(e) => {
                        e.stopPropagation();
                        setActiveInterventionId(item.id);
                        setIsEvidenceDrawerOpen(true);
                      }}
                    >
                      بررسی شواهد تفصیلی ←
                    </button>
                  </div>
                </article>
              );
            })}
          </div>
        </section>

        {/* Right Column: Learning Evidence Workspace & Action Studio */}
        <section className={styles.detailWorkspace} aria-label="فضای بررسی و استودیوی اقدام مربی">
          <div className={styles.detailHeader}>
            <div>
              <h2 className={styles.detailStudentTitle}>{activeIntervention.studentName}</h2>
              <p className={styles.detailCohortName}>{activeIntervention.cohort}</p>
            </div>

            <div className={styles.detailStatusControl}>
              <label htmlFor="interventionStatus" style={{ fontSize: "0.75rem", fontWeight: 700, color: "#475569" }}>
                وضعیت:
              </label>
              <select
                id="interventionStatus"
                className={styles.statusSelect}
                value={activeIntervention.status}
                onChange={(e) => handleStatusChange(e.target.value as Intervention["status"])}
              >
                <option value="OPEN">باز (OPEN)</option>
                <option value="REVIEWING">در حال بررسی (REVIEWING)</option>
                <option value="FOLLOW_UP">نیازمند پیگیری (FOLLOW_UP)</option>
                <option value="RESOLVED">حل‌شده (RESOLVED)</option>
              </select>
            </div>
          </div>

          {/* Evidence Meta Box */}
          <div className={styles.evidenceBlock}>
            <h3 className={styles.evidenceSectionTitle}>شواهد و پروژه فعال</h3>
            <div className={styles.evidenceMetaBox}>
              <div className={styles.evidenceMetaRow}>
                <span className={styles.metaLabel}>عنوان پروژه:</span>
                <span className={styles.metaValue}>{activeIntervention.evidence.projectTitle}</span>
              </div>
              <div className={styles.evidenceMetaRow}>
                <span className={styles.metaLabel}>شاخه و کامیت:</span>
                <span className={styles.metaValue} style={{ fontFamily: "monospace", direction: "ltr" }}>
                  {activeIntervention.evidence.repoBranch} ({activeIntervention.evidence.commitHash})
                </span>
              </div>
              <div className={styles.evidenceMetaRow}>
                <span className={styles.metaLabel}>مهارت‌های دیده‌شده:</span>
                <div className={styles.skillPills}>
                  {activeIntervention.evidence.skillsDemonstrated.map((s, idx) => (
                    <span key={idx} className={styles.skillPill}>
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Last Code Snippet */}
            <h4 style={{ fontSize: "0.85rem", fontWeight: 700, margin: "0.5rem 0 0.25rem 0", color: "#334155" }}>
              قطعه کد اخیر و محل چالش:
            </h4>
            <div className={styles.snippetBox}>
              <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>
                {activeIntervention.evidence.lastCodeSnippet}
              </pre>
            </div>
          </div>

          {/* Context Notes */}
          <div style={{ background: "#f8fafc", padding: "0.75rem 1rem", borderRadius: "0.5rem", border: "1px solid #e2e8f0" }}>
            <p style={{ margin: "0 0 0.4rem 0", fontSize: "0.8rem", color: "#475569" }}>
              <strong>یادداشت مربی:</strong> {activeIntervention.evidence.mentorNotes}
            </p>
            <p style={{ margin: 0, fontSize: "0.8rem", color: "#64748b" }}>
              <strong>زمینه والدین:</strong> {activeIntervention.evidence.parentContext}
            </p>
          </div>

          {/* Mentor Action Studio */}
          <div className={styles.actionStudio}>
            <h3 className={styles.evidenceSectionTitle}>استودیوی اقدام مربی (Action Studio)</h3>
            
            <div className={styles.composerBox}>
              <textarea
                className={styles.composerTextarea}
                placeholder="متن بازخورد مستقیم، راهنمای گام‌به‌گام یا پیام تشویق برای دانش‌آموز..."
                value={feedbackText}
                onChange={(e) => setFeedbackText(e.target.value)}
              />

              <div className={styles.actionButtonsRow}>
                <button
                  type="button"
                  className={styles.actionBtnSecondary}
                  onClick={() => setIsParentBriefingOpen(true)}
                >
                  پیش‌نویس گزارش والدین
                </button>
                <button
                  type="button"
                  className={styles.actionBtnSecondary}
                  onClick={() => handleSendFeedback("تشویق و انگیزه")}
                >
                  ارسال تشویق
                </button>
                <button
                  type="button"
                  className={styles.actionBtnPrimary}
                  onClick={() => handleSendFeedback("راهنمای فنی")}
                >
                  ارسال بازخورد و راهکار
                </button>
                <button
                  type="button"
                  style={{
                    padding: "0.5rem 1rem",
                    background: "#16a34a",
                    color: "#ffffff",
                    border: "none",
                    borderRadius: "0.5rem",
                    fontSize: "0.8rem",
                    fontWeight: 700,
                    cursor: "pointer",
                  }}
                  onClick={handleResolveIntervention}
                >
                  حل مداخله ✓
                </button>
              </div>
            </div>

            {/* Previous Feedback History */}
            {activeIntervention.feedbackHistory.length > 0 && (
              <div style={{ marginBlockStart: "1rem" }}>
                <h4 style={{ fontSize: "0.8rem", fontWeight: 700, color: "#64748b", margin: "0 0 0.5rem 0" }}>
                  تاریخچه تعاملات ثبت‌شده:
                </h4>
                <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
                  {activeIntervention.feedbackHistory.map((fb) => (
                    <div
                      key={fb.id}
                      style={{
                        padding: "0.5rem 0.75rem",
                        background: "#f1f5f9",
                        borderRadius: "0.375rem",
                        fontSize: "0.78rem",
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", color: "#64748b", marginBlockEnd: "0.2rem" }}>
                        <span>{fb.actionType}</span>
                        <span>{fb.timestamp}</span>
                      </div>
                      <div style={{ color: "#1e293b" }}>{fb.text}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </section>
      </div>

      {/* 4. Evidence Review Drawer */}
      {isEvidenceDrawerOpen && (
        <div className={styles.drawerOverlay} onClick={() => setIsEvidenceDrawerOpen(false)}>
          <div className={styles.drawerContent} onClick={(e) => e.stopPropagation()}>
            <div className={styles.drawerHeader}>
              <h3 style={{ margin: 0, fontSize: "1.1rem", fontWeight: 700 }}>
                شواهد عمیق یادگیری: {activeIntervention.studentName}
              </h3>
              <button
                type="button"
                className={styles.drawerCloseBtn}
                onClick={() => setIsEvidenceDrawerOpen(false)}
              >
                ✕
              </button>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              <div>
                <h4 style={{ fontSize: "0.9rem", fontWeight: 700, margin: "0 0 0.25rem 0" }}>خلاصه وضعیت</h4>
                <p style={{ fontSize: "0.85rem", color: "#475569", lineHeight: 1.5, margin: 0 }}>
                  {activeIntervention.evidence.summary}
                </p>
              </div>

              <div>
                <h4 style={{ fontSize: "0.9rem", fontWeight: 700, margin: "0 0 0.25rem 0" }}>فعالیت اخیر در مخزن</h4>
                <p style={{ fontSize: "0.85rem", color: "#475569", lineHeight: 1.5, margin: 0 }}>
                  {activeIntervention.evidence.recentActivity}
                </p>
              </div>

              <div>
                <h4 style={{ fontSize: "0.9rem", fontWeight: 700, margin: "0 0 0.25rem 0" }}>پیشنهاد سیستمی اقدام</h4>
                <div style={{ background: "#e0e7ff", padding: "0.75rem", borderRadius: "0.5rem", color: "#3730a3", fontSize: "0.85rem" }}>
                  {activeIntervention.recommendedAction}
                </div>
              </div>

              <div style={{ marginBlockStart: "1.5rem" }}>
                <button
                  type="button"
                  className={styles.actionBtnPrimary}
                  style={{ inlineSize: "100%" }}
                  onClick={() => setIsEvidenceDrawerOpen(false)}
                >
                  بازگشت به استودیوی اقدام
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 5. Parent Briefing Modal / Drawer */}
      {isParentBriefingOpen && (
        <div className={styles.drawerOverlay} onClick={() => setIsParentBriefingOpen(false)}>
          <div className={styles.drawerContent} onClick={(e) => e.stopPropagation()}>
            <div className={styles.drawerHeader}>
              <h3 style={{ margin: 0, fontSize: "1.1rem", fontWeight: 700 }}>
                پیش‌نویس گزارش برای والدین ({activeIntervention.studentName})
              </h3>
              <button
                type="button"
                className={styles.drawerCloseBtn}
                onClick={() => setIsParentBriefingOpen(false)}
              >
                ✕
              </button>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              <p style={{ fontSize: "0.85rem", color: "#475569", lineHeight: 1.6 }}>
                این گزارش با زبان غیرفنی تنظیم شده تا والد بتواند در منزل پشتیبانی لازم را ارائه دهد:
              </p>

              <div style={{ background: "#f8fafc", padding: "1rem", borderRadius: "0.5rem", border: "1px solid #e2e8f0", fontSize: "0.85rem", lineHeight: 1.6, color: "#1e293b" }}>
                <strong>ولی محترم {activeIntervention.studentName}،</strong><br />
                فرزند شما هم‌اکنون در حال توسعه پروژه «{activeIntervention.evidence.projectTitle}» است. 
                {activeIntervention.status === "RESOLVED"
                  ? " روند پیشرفت ایشان بسیار درخشان بوده و چالش‌های اخیر را با موفقیت پشت سر گذاشته است."
                  : ` ایشان در حال تمرین بر روی مبحث پیشرفته است. ما در مرکز هدایت همراه ایشان هستیم و تشویق شما در خانه در تداوم تلاش بسیار موثر خواهد بود.`}
              </div>

              <div style={{ display: "flex", gap: "0.5rem", marginBlockStart: "1rem" }}>
                <button
                  type="button"
                  className={styles.actionBtnPrimary}
                  style={{ flex: 1 }}
                  onClick={() => {
                    setIsParentBriefingOpen(false);
                    const briefingContent = `ولی محترم ${activeIntervention.studentName}، فرزند شما هم‌اکنون در حال توسعه پروژه «${activeIntervention.evidence.projectTitle}» است. ${activeIntervention.status === "RESOLVED" ? "روند پیشرفت ایشان بسیار درخشان بوده و چالش‌های اخیر را با موفقیت پشت سر گذاشته است." : "ایشان در حال تمرین بر روی مبحث پیشرفته است. ما در مرکز هدایت همراه ایشان هستیم و تشویق شما در خانه در تداوم تلاش بسیار موثر خواهد بود."}`;
                    if (activeIntervention.studentName.includes("علی")) {
                      updateSharedLearningState((prev) => ({
                        ...prev,
                        parentBridge: {
                          ...prev.parentBridge,
                          lastBriefing: briefingContent,
                          briefingTimestamp: "هم‌اکنون",
                        },
                      }));
                    }
                    showToast("گزارش والد با موفقیت به رصدخانه رشد ارسال شد.");
                  }}
                >
                  ارسال به رصدخانه والدین
                </button>
                <button
                  type="button"
                  className={styles.actionBtnSecondary}
                  onClick={() => setIsParentBriefingOpen(false)}
                >
                  انصراف
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
