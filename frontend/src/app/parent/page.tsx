"use client";

import { useState } from "react";
import Link from "next/link";
import { parentAlphaContent as copy } from "@/content/fa/parent.alpha";
import {
  Badge,
  IconSparkles,
  IconChat,
  IconCheck,
  IconArrowUp,
  IconClock,
  IconDocument,
  IconFire,
  IconCalendar,
  IconShield,
  IconLaptop,
  IconClose,
} from "@/components/ui";
import { useParentSearch } from "./ParentSearchContext";
import styles from "../student/student.module.css";

interface Milestone {
  id: string;
  title: string;
  date: string;
  status: string;
  type: string;
}

const milestonesByChild: Record<string, Milestone[]> = {
  "علی محمدی (پایه دهم ریاضی)": [
    {
      id: "m-1",
      title: copy.overview.milestone1Title,
      date: copy.overview.milestone1Date,
      status: copy.overview.milestone1Status,
      type: "front-end"
    },
    {
      id: "m-2",
      title: copy.overview.milestone2Title,
      date: copy.overview.milestone2Date,
      status: copy.overview.milestone2Status,
      type: "programming"
    }
  ],
  "مریم محمدی (پایه هفتم)": [
    {
      id: "m-3",
      title: copy.overview.milestone3Title,
      date: copy.overview.milestone3Date,
      status: copy.overview.milestone3Status,
      type: "front-end"
    },
    {
      id: "m-4",
      title: copy.overview.milestone4Title,
      date: copy.overview.milestone4Date,
      status: copy.overview.milestone4Status,
      type: "python"
    }
  ]

};

export default function ParentOverviewPage() {
  const o = copy.overview;
  const {
    searchQuery,
    openWeeklyReportModal,
    setOpenWeeklyReportModal,
    openMentorChatModal,
    setOpenMentorChatModal,
    openConsentModal,
    setOpenConsentModal,
    selectedChild,
    setSelectedChild,
  } = useParentSearch();

  const [consentGranted, setConsentGranted] = useState(true);
  const [chatMessage, setChatMessage] = useState("");
  const [chatSent, setChatSent] = useState(false);

  // Keyboard accessibility: ESC closes any open modal
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      setOpenWeeklyReportModal(false);
      setOpenMentorChatModal(false);
      setOpenConsentModal(false);
    }
  };

  const currentMilestones = milestonesByChild[selectedChild] || milestonesByChild["علی محمدی (پایه دهم ریاضی)"];

  const filteredMilestones = currentMilestones.filter(m =>
    m.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    m.status.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className={styles.studentDashboard} onKeyDown={handleKeyDown} tabIndex={-1}>
      {/* 0. Page Context Header & Child Anchor */}
      <header className={styles.childSelectorBanner} aria-label={o.childSelectLabel}>
        <div className={styles.childSelectorInfo}>
          <span style={{ fontSize: "var(--cs-font-size-caption)", color: "var(--cs-color-text-secondary)", fontWeight: "var(--cs-font-weight-medium)" }}>
            {o.childSelectLabel}
          </span>
          <select
            value={selectedChild}
            onChange={(e) => setSelectedChild(e.target.value)}
            style={{
              fontSize: "var(--cs-font-size-body)",
              fontWeight: "var(--cs-font-weight-bold)",
              color: "var(--cs-color-text-primary)",
              background: "transparent",
              border: "1px solid var(--cs-color-border-subtle)",
              borderRadius: "var(--cs-radius-control)",
              padding: "0.25rem 0.5rem",
              cursor: "pointer"
            }}
            aria-label={o.childSelectLabel}
          >
            <option value={o.child1Option}>{o.child1Option}</option>
            <option value={o.child2Option}>{o.child2Option}</option>
          </select>
        </div>
        <Badge variant="primary" className={styles.childSelectorBadge}>
          <bdi dir="ltr">{o.selectedChildBadge}</bdi>
        </Badge>

      </header>

      {/* 1. Compact Product Briefing Band (Hero) */}
      <section className={styles.heroBanner} aria-labelledby="parent-hero-heading">
        <div className={styles.parentHeroBriefingBand}>
          <div className={styles.heroGreeting} style={{ maxWidth: "42rem" }}>
            <div className={styles.heroBadgeRow}>
              <Badge variant="primary" className={styles.heroBadgeTranslucent}>{o.heroBadge}</Badge>
              <Badge variant="outline" className={styles.heroBadgeDark}>{o.privacyAssuranceBadge}</Badge>
            </div>
            <h1 id="parent-hero-heading" className={styles.heroHeading} style={{ fontSize: "var(--cs-font-size-heading-xl)" }}>
              {o.heroHeading}
            </h1>
            <p className={styles.heroSubtitle}>
              <bdi dir="rtl">{o.heroSubtitle}</bdi>
            </p>
          </div>
          <div className={styles.heroButtons}>
            <button
              type="button"
              className={styles.heroPrimaryBtn}
              onClick={() => setOpenWeeklyReportModal(true)}
            >
              <IconSparkles aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>{o.heroActionPrimary}</span>
            </button>
          </div>
        </div>
      </section>

      {/* 2. 4 Disciplined KPI Metrics Grid */}
      <section className={styles.kpiGrid} aria-label={o.title}>
        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{o.kpi1Title}</span>
            <span className={styles.kpiValue}>{o.kpi1Value}</span>
            <span className={styles.kpiSub}>
              <IconArrowUp aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>{o.kpi1Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle1}`}>
              <IconClock aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{o.kpi2Title}</span>
            <span className={styles.kpiValue}>{o.kpi2Value}</span>
            <span className={styles.kpiSub}>
              <IconCheck aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>{o.kpi2Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle2}`}>
              <IconDocument aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{o.kpi3Title}</span>
            <span className={styles.kpiValue}>{o.kpi3Value}</span>
            <span className={styles.kpiSub}>
              <IconFire aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>{o.kpi3Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle3}`}>
              <IconCalendar aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{o.kpi4Title}</span>
            <span className={styles.kpiValue}>{o.kpi4Value}</span>
            <span className={styles.kpiSub}>
              <IconCheck aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>{o.kpi4Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle4}`}>
              <IconShield aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />
            </div>
          </div>
        </div>
      </section>

      {/* 3. Operational Workflow & Oversight Grid (Content-Weighted) */}
      <section className={styles.parentLowerGrid} aria-label={o.oversightGridAria}>
        {/* Recent Milestones */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h2 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <IconLaptop aria-hidden="true" />
              <span>{o.recentMilestonesTitle}</span>
            </h2>
            <Badge variant="success">{o.milestoneStatusApproved}</Badge>
          </div>

          {searchQuery && (
            <div style={{
              padding: "var(--cs-space-2) var(--cs-space-3)",
              background: "var(--cs-color-bg-base)",
              borderRadius: "var(--cs-radius-control)",
              fontSize: "var(--cs-font-size-caption)",
              color: "var(--cs-color-text-secondary)",
              display: "flex",
              justifyContent: "space-between"
            }}>
              <span>{`${o.filterPrefix} «${searchQuery}»`}</span>
              <span>{`${filteredMilestones.length} ${o.filterSuffixCount}`}</span>
            </div>

          )}

          <div className={styles.activityList}>
            {filteredMilestones.length > 0 ? (
              filteredMilestones.map((item, idx) => (
                <div key={item.id} className={styles.activityItem}>
                  <div className={`${styles.activityIconCircle} ${idx === 0 ? styles.kpiCircle1 : styles.kpiCircle2}`}>
                    <IconCheck aria-hidden="true" />
                  </div>
                  <div className={styles.activityContent} style={{ inlineSize: "100%" }}>
                    <p className={styles.activityDesc} style={{ fontWeight: "var(--cs-font-weight-bold)" }}>
                      <bdi dir="rtl">{item.title}</bdi>
                    </p>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <span className={styles.activityTime}>{item.date}</span>
                      <Badge variant="outline">{item.status}</Badge>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div style={{ textAlign: "center", padding: "var(--cs-space-6) var(--cs-space-4)", color: "var(--cs-color-text-muted)" }}>
                <p style={{ margin: 0, fontWeight: "var(--cs-font-weight-bold)" }}>{o.noSearchResults}</p>
              </div>
            )}
          </div>
        </div>

        {/* Consent & Oversight Management */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h2 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <IconShield aria-hidden="true" />
              <span>{o.safetyTitle}</span>
            </h2>
            <Badge variant="primary">{o.safetyBadge}</Badge>
          </div>
          <p className={styles.cardText}>{o.safetyDescription}</p>
          <div style={{
            background: "var(--cs-color-bg-base)",
            padding: "var(--cs-space-3) var(--cs-space-4)",
            borderRadius: "var(--cs-radius-control)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between"
          }}>
            <span style={{ fontSize: "var(--cs-font-size-caption)", color: "var(--cs-color-text-secondary)" }}>
              {o.consentStatusLabel}
            </span>
            <span style={{
              fontSize: "var(--cs-font-size-caption)",
              fontWeight: "var(--cs-font-weight-bold)",
              color: consentGranted ? "var(--cs-color-success-foreground)" : "var(--cs-color-danger-foreground)"
            }}>
              {consentGranted ? o.consentStatusValue : o.consentStatusDisabled}
            </span>
          </div>
          <div style={{ marginBlockStart: "auto", display: "flex", justifyContent: "flex-end" }}>
            <button
              className={`${styles.actionButton} ${styles.primaryActionButton}`}
              type="button"
              onClick={() => setOpenConsentModal(true)}
            >
              {o.actionManageConsent}
            </button>
          </div>
        </div>
      </section>


      {/* Modal 1: Weekly Progress Report */}

      {/* Modal 1: Weekly Progress Report */}
      {openWeeklyReportModal && (
        <div className={styles.modalBackdrop} onClick={() => setOpenWeeklyReportModal(false)}>
          <div className={styles.modalSheet} onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="report-modal-title">
            <div className={styles.modalHeader}>
              <h3 id="report-modal-title" className={styles.modalTitle}>
                <IconDocument aria-hidden="true" style={{ color: "var(--cs-color-brand-primary)" }} />
                <span>{o.weeklyReportModalTitle}</span>
              </h3>
              <button
                type="button"
                className={styles.modalCloseBtn}
                onClick={() => setOpenWeeklyReportModal(false)}
                aria-label={o.weeklyReportModalCloseAria}
              >
                <IconClose aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />
              </button>
            </div>

            <p style={{ margin: 0, fontSize: "var(--cs-font-size-body)", color: "var(--cs-color-text-secondary)" }}>
              <span>{o.weeklyReportChildPrefix}</span>
              <span>{selectedChild}</span>
              <span>{o.weeklyReportChildSuffix}</span>
            </p>

            <div style={{ display: "flex", flexDirection: "column", gap: "var(--cs-space-3)" }}>
              <div style={{ padding: "var(--cs-space-3)", background: "var(--cs-color-bg-base)", borderRadius: "var(--cs-radius-control)" }}>
                <strong>{o.weeklyReportMetric1Label}</strong>
                <span> {o.weeklyReportMetric1Value}</span>
              </div>
              <div style={{ padding: "var(--cs-space-3)", background: "var(--cs-color-bg-base)", borderRadius: "var(--cs-radius-control)" }}>
                <strong>{o.weeklyReportMetric2Label}</strong>
                <span> {o.weeklyReportMetric2Value}</span>
              </div>
              <div style={{ padding: "var(--cs-space-3)", background: "var(--cs-color-bg-base)", borderRadius: "var(--cs-radius-control)" }}>
                <strong>{o.weeklyReportMetric3Label}</strong>
                <span> {o.weeklyReportMetric3Value}</span>
              </div>
            </div>


            <div style={{ display: "flex", justifyContent: "flex-end", marginBlockStart: "var(--cs-space-3)" }}>
              <button
                type="button"
                className={`${styles.actionButton} ${styles.primaryActionButton}`}
                onClick={() => setOpenWeeklyReportModal(false)}
              >
                {o.weeklyReportCloseBtn}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal 2: Contact Mentor */}
      {openMentorChatModal && (
        <div className={styles.modalBackdrop} onClick={() => setOpenMentorChatModal(false)}>
          <div className={styles.modalSheet} onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="mentor-chat-modal-title">
            <div className={styles.modalHeader}>
              <h3 id="mentor-chat-modal-title" className={styles.modalTitle}>
                <IconChat aria-hidden="true" style={{ color: "var(--cs-color-brand-primary)" }} />
                <span>{o.mentorModalTitle}</span>
              </h3>
              <button
                type="button"
                className={styles.modalCloseBtn}
                onClick={() => setOpenMentorChatModal(false)}
                aria-label={o.mentorModalCloseAria}
              >
                <IconClose aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />
              </button>
            </div>

            <p style={{ margin: 0, fontSize: "var(--cs-font-size-body)", color: "var(--cs-color-text-secondary)" }}>
              <span>{o.mentorModalDesc}</span>
            </p>

            <textarea
              style={{
                inlineSize: "100%",
                minBlockSize: "5rem",
                padding: "var(--cs-space-3)",
                borderRadius: "var(--cs-radius-control)",
                border: "var(--cs-border-width) solid var(--cs-color-border-subtle)",
                background: "var(--cs-color-bg-base)",
                color: "var(--cs-color-text-primary)",
                fontFamily: "inherit",
                fontSize: "var(--cs-font-size-body)",
                resize: "vertical"
              }}
              placeholder={o.mentorModalPlaceholder}
              value={chatMessage}
              onChange={(e) => setChatMessage(e.target.value)}
            />

            {chatSent && (
              <div style={{
                background: "var(--cs-color-bg-base)",
                color: "var(--cs-color-success)",
                border: "var(--cs-border-width) solid var(--cs-color-border-subtle)",
                borderRadius: "var(--cs-radius-control)",
                padding: "var(--cs-space-3)",
                fontSize: "var(--cs-font-size-caption)",
                display: "flex",
                alignItems: "center",
                gap: "var(--cs-space-2)"
              }}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "1rem", blockSize: "1rem" }} />
                <span>{o.mentorModalSuccess}</span>
              </div>
            )}

            <div style={{ display: "flex", justifyContent: "flex-end", gap: "var(--cs-space-2)", marginBlockStart: "var(--cs-space-3)" }}>
              <button
                type="button"
                className={styles.actionButton}
                onClick={() => setOpenMentorChatModal(false)}
              >
                {o.mentorModalCancelBtn}
              </button>
              <button
                type="button"
                className={`${styles.actionButton} ${styles.primaryActionButton}`}
                onClick={() => setChatSent(true)}
              >
                {o.mentorModalSendBtn}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal 3: Consent & Privacy Policy Management */}
      {openConsentModal && (
        <div className={styles.modalBackdrop} onClick={() => setOpenConsentModal(false)}>
          <div className={styles.modalSheet} onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="consent-modal-title">
            <div className={styles.modalHeader}>
              <h3 id="consent-modal-title" className={styles.modalTitle}>
                <IconShield aria-hidden="true" style={{ color: "var(--cs-color-brand-primary)" }} />
                <span>{o.consentModalTitle}</span>
              </h3>
              <button
                type="button"
                className={styles.modalCloseBtn}
                onClick={() => setOpenConsentModal(false)}
                aria-label={o.consentModalCloseAria}
              >
                <IconClose aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />
              </button>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "var(--cs-space-3)", fontSize: "var(--cs-font-size-body)" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "var(--cs-space-2)", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={consentGranted}
                  onChange={(e) => setConsentGranted(e.target.checked)}
                  style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }}
                />
                <span>{o.consentModalItem1Title}</span>
              </label>

              <p style={{ margin: 0, fontSize: "var(--cs-font-size-caption)", color: "var(--cs-color-text-muted)", lineHeight: 1.6 }}>
                <span>{o.consentModalItem1Desc}</span>
              </p>
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", marginBlockStart: "var(--cs-space-3)" }}>
              <button
                type="button"
                className={`${styles.actionButton} ${styles.primaryActionButton}`}
                onClick={() => setOpenConsentModal(false)}
              >
                {o.consentModalConfirmBtn}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

