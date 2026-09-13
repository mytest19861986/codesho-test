"use client";

import React, { useState } from "react";
import { AppShell, type NavigationItem } from "@/components/layout";
import styles from "./enterprise_governance.module.css";

export interface StaffAssignmentItem {
  readonly id: string;
  readonly roleName: string;
  readonly scopeType: string;
  readonly isActive: boolean;
  readonly validUntil?: string;
}

export interface RetentionPolicyItem {
  readonly id: string;
  readonly category: string;
  readonly retentionDays: number;
  readonly dispositionAction: string;
  readonly isActive: boolean;
}

export interface PilotControlItem {
  readonly id: string;
  readonly code: string;
  readonly category: string;
  readonly description: string;
  readonly isBlocking: boolean;
  readonly evidenceStatus: string;
}

const navItems: NavigationItem[] = [
  { id: "admin-learning", label: "مدیریت آموزشی", href: "/admin/learning", icon: "⚙" },
  { id: "admin-governance", label: "مرکز کنترل و حاکمیت سازمانی", href: "/admin/governance", icon: "🛡" },
];

export function EnterpriseGovernanceScreen() {
  const [activeTab, setActiveTab] = useState<"delegated_admin" | "data_lifecycle" | "pilot_readiness" | "pilot_operations">("pilot_readiness");
  const [rollbackConfirmationModal, setRollbackConfirmationModal] = useState<boolean>(false);
  const [rollbackInputText, setRollbackInputText] = useState<string>("");

  const syntheticAssignments: StaffAssignmentItem[] = [
    { id: "a-1", roleName: "مدیر راهبری داده", scopeType: "TENANT_WIDE", isActive: true, validUntil: "1403/12/29" },
    { id: "a-2", roleName: "ناظر امنیت پایلوت", scopeType: "RESOURCE_SCOPED", isActive: true, validUntil: "1404/06/31" },
  ];

  const syntheticPolicies: RetentionPolicyItem[] = [
    { id: "p-1", category: "سوابق تمرین و ارزیابی کد", retentionDays: 1095, dispositionAction: "ANONYMIZE", isActive: true },
    { id: "p-2", category: "لاگ‌های نشست و رویدادهای سیستمی", retentionDays: 365, dispositionAction: "DESTROY", isActive: true },
  ];

  const syntheticControls: PilotControlItem[] = [
    { id: "c-1", code: "SEC-PRIV-01", category: "کنترل دسترسی", description: "اعمال حاکمیت تفکیک اختیارات دو نفره و منع اعطای خودسرانه", isBlocking: true, evidenceStatus: "VERIFIED" },
    { id: "c-2", code: "DATA-HOLD-02", category: "چرخه عمر داده", description: "منع مطلق امحای سوابق دارای هولد فعال حقوقی", isBlocking: true, evidenceStatus: "VERIFIED" },
    { id: "c-3", code: "ETHIC-RANK-03", category: "انطباق اخلاقی", description: "منع رتبه‌بندی عمومی دانش‌آموزان و لیدربورد مقایسه‌ای", isBlocking: true, evidenceStatus: "VERIFIED" },
    { id: "c-4", code: "GATE-ADVISORY-04", category: "آمادگی پایلوت", description: "ارزیابی مشورتی گیت پایلوت بدون اختیار دپلوی خودکار", isBlocking: false, evidenceStatus: "ATTESTED" },
  ];

  return (
    <AppShell navigationItems={navItems} activeNavigationId="admin-governance">
      <div className={styles.container}>
        <header className={styles.header}>
          <h1 className={styles.title}>مرکز کنترل، حاکمیت سازمانی و آمادگی پایلوت (P3-VS26 - VS28)</h1>
          <p className={styles.subtitle}>
            نظارت عالیه بر تفکیک اختیارات دو نفره، هولدهای حقوقی و چرخه عمر داده، و ارزیابی مشورتی گیت‌های پایلوت پلتفرم کُدشو
          </p>
        </header>

        <div className={styles.noticeBox}>
          <strong>اصل استقلال و مشورتی بودن گیت:</strong> گیت آمادگی پایلوت کاملاً مستقل، نظارتی و مشورتی است و فاقد اختیار دپلویمنت خودکار به محیط عملیاتی است (`PRODUCTION_DEPLOY_AUTHORITY: 0`). تمام داده‌ها کاملاً مصنوعی و عاری از هرگونه هویت واقعی یا رتبه‌بندی دانش‌آموزان است.
        </div>

        <nav className={styles.tabs} aria-label="بخش‌های حاکمیت سازمانی">
          <button
            type="button"
            className={`${styles.tabBtn} ${activeTab === "pilot_readiness" ? styles.tabBtnActive : ""}`}
            onClick={() => setActiveTab("pilot_readiness")}
          >
            گیت‌ها و کنترل‌های آمادگی پایلوت (VS28)
          </button>
          <button
            type="button"
            className={`${styles.tabBtn} ${activeTab === "pilot_operations" ? styles.tabBtnActive : ""}`}
            onClick={() => setActiveTab("pilot_operations")}
          >
            عملیات پایلوت، کاندیدای انتشار و رخدادها (فاز ۴)
          </button>
          <button
            type="button"
            className={`${styles.tabBtn} ${activeTab === "delegated_admin" ? styles.tabBtnActive : ""}`}
            onClick={() => setActiveTab("delegated_admin")}
          >
            تفویض اختیارات و دسترسی دومنظوره (VS26)
          </button>
          <button
            type="button"
            className={`${styles.tabBtn} ${activeTab === "data_lifecycle" ? styles.tabBtnActive : ""}`}
            onClick={() => setActiveTab("data_lifecycle")}
          >
            چرخه عمر داده و هولد حقوقی (VS27)
          </button>
        </nav>

        {activeTab === "pilot_readiness" && (
          <section className={styles.cardGrid} aria-label="کنترل‌های آمادگی پایلوت">
            {syntheticControls.map((ctrl) => (
              <article key={ctrl.id} className={styles.card}>
                <div className={styles.cardHeader}>
                  <span className={`${styles.badge} ${ctrl.isBlocking ? styles.badgeBlocking : styles.badgeAdvisory}`}>
                    {ctrl.isBlocking ? "قفل‌کننده پایلوت" : "مشورتی"}
                  </span>
                  <span className={`${styles.badge} ${styles.badgeActive}`}>
                    {ctrl.evidenceStatus}
                  </span>
                </div>
                <h2 className={styles.cardTitle}>{ctrl.code}: {ctrl.category}</h2>
                <div className={styles.cardMeta}>
                  <span>{ctrl.description}</span>
                  <span>تأییدیه دیجیتال: SHA-256 رمزنگاری شده</span>
                </div>
                <button type="button" className={styles.actionBtn}>
                  مشاهده شواهد کنترل
                </button>
              </article>
            ))}
          </section>
        )}

        {activeTab === "delegated_admin" && (
          <section className={styles.cardGrid} aria-label="تخصیص‌های راهبری">
            {syntheticAssignments.map((assign) => (
              <article key={assign.id} className={styles.card}>
                <div className={styles.cardHeader}>
                  <span className={`${styles.badge} ${assign.isActive ? styles.badgeActive : styles.badgePending}`}>
                    {assign.isActive ? "فعال" : "معلق"}
                  </span>
                </div>
                <h2 className={styles.cardTitle}>{assign.roleName}</h2>
                <div className={styles.cardMeta}>
                  <span>دامنه اختیارات: {assign.scopeType}</span>
                  {assign.validUntil && <span>اعتبار تا: {assign.validUntil}</span>}
                  <span>قاعده دومنظوره: کنترل تایید دو نفره برقرار است</span>
                </div>
                <button type="button" className={styles.actionBtn}>
                  بازبینی دسترسی
                </button>
              </article>
            ))}
          </section>
        )}

        {activeTab === "data_lifecycle" && (
          <section className={styles.cardGrid} aria-label="پالیسی‌های نگهداری داده">
            {syntheticPolicies.map((pol) => (
              <article key={pol.id} className={styles.card}>
                <div className={styles.cardHeader}>
                  <span className={`${styles.badge} ${pol.isActive ? styles.badgeActive : styles.badgePending}`}>
                    {pol.isActive ? "پالیسی جاری" : "غیرفعال"}
                  </span>
                </div>
                <h2 className={styles.cardTitle}>{pol.category}</h2>
                <div className={styles.cardMeta}>
                  <span>دوره نگهداری قانونی: {pol.retentionDays} روز</span>
                  <span>اقدام انقضا: {pol.dispositionAction === "ANONYMIZE" ? "گمنام‌سازی قطعی" : "امحای ایمن"}</span>
                  <span>وضعیت هولد حقوقی: بررسی خودکار قبل از امحا</span>
                </div>
                <button type="button" className={styles.actionBtn}>
                  بررسی سوابق امحا
                </button>
              </article>
            ))}
          </section>
        )}
        {activeTab === "pilot_operations" && (
          <section className={styles.cardGrid} aria-label="عملیات پایلوت و کاندیدای انتشار">
            <article className={styles.card}>
              <div className={styles.cardHeader}>
                <span className={`${styles.badge} ${styles.badgeActive}`}>
                  CANDIDATE_TAGGED
                </span>
                <span className={`${styles.badge} ${styles.badgeAdvisory}`}>
                  پایلوت غیرعملیاتی
                </span>
              </div>
              <h2 className={styles.cardTitle}>
                کاندیدای انتشار: <bdi dir="ltr">v4.0.0-rc1</bdi>
              </h2>
              <div className={styles.cardMeta}>
                <span>هش کامیت مصوب: <bdi dir="ltr">a6bc0d9</bdi></span>
                <span>اختیار پروداکشن: <bdi dir="ltr">PRODUCTION_DEPLOY_AUTHORITY: 0</bdi></span>
                <span>تاییدیه دومنظوره: الزامی برای ارتقا به پایلوت</span>
              </div>
              <button
                type="button"
                className={styles.actionBtn}
                onClick={() => setRollbackConfirmationModal(true)}
              >
                اجرای رول‌بک اضطراری با تایید اصطکاکی
              </button>
            </article>

            <article className={styles.card}>
              <div className={styles.cardHeader}>
                <span className={`${styles.badge} ${styles.badgeBlocking}`}>
                  SEV2 - فعال
                </span>
                <span className={`${styles.badge} ${styles.badgePending}`}>
                  در حال بررسی
                </span>
              </div>
              <h2 className={styles.cardTitle}>
                رخداد عملیاتی: <bdi dir="ltr">INC-2026-042</bdi>
              </h2>
              <div className={styles.cardMeta}>
                <span>شرح: بررسی تاخیر صف سنتتیک ورکر‌های بک‌اند</span>
                <span>حریم خصوصی: عاری از هرگونه هویت واقعی یا PII</span>
                <span>سوابق پس از رخداد (PIR): تغییرناپذیر در دیتابیس</span>
              </div>
              <button type="button" className={styles.actionBtn}>
                مشاهده فرآیند تریاژ
              </button>
            </article>

            <article className={styles.card}>
              <div className={styles.cardHeader}>
                <span className={`${styles.badge} ${styles.badgeActive}`}>
                  PLANNED
                </span>
                <span className={`${styles.badge} ${styles.badgeAdvisory}`}>
                  موجودیت ساختگی
                </span>
              </div>
              <h2 className={styles.cardTitle}>
                برنامه فعال‌سازی مستأجر پایلوت
              </h2>
              <div className={styles.cardMeta}>
                <span>کد طرح: <bdi dir="ltr">PLAN-SYNTH-P4</bdi></span>
                <span>مدرسه هدف: دبیرستان نمونه ساختگی الف</span>
                <span>سیاست ضدرتبه‌بندی: <bdi dir="ltr">STUDENT_RANKING: 0</bdi> برقرار است</span>
              </div>
              <button type="button" className={styles.actionBtn}>
                بررسی چک‌لیست آنبوردینگ
              </button>
            </article>

            {rollbackConfirmationModal && (
              <div
                role="dialog"
                aria-modal="true"
                aria-labelledby="rollback-dialog-title"
                style={{
                  position: "fixed",
                  inset: 0,
                  backgroundColor: "rgba(0,0,0,0.6)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  zIndex: 50,
                  padding: "1rem",
                }}
              >
                <div
                  style={{
                    backgroundColor: "#ffffff",
                    borderRadius: "0.75rem",
                    maxWidth: "480px",
                    width: "100%",
                    padding: "1.5rem",
                    display: "flex",
                    flexDirection: "column",
                    gap: "1rem",
                    direction: "rtl",
                    boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
                  }}
                >
                  <h3 id="rollback-dialog-title" style={{ fontSize: "1.25rem", fontWeight: 700, color: "#991b1b" }}>
                    تایید اصطکاکی بازگشت به نسخه پیشین (Rollback)
                  </h3>
                  <p style={{ fontSize: "0.9rem", color: "#475569", lineHeight: 1.6 }}>
                    این یک اقدام اصطکاکی دو مرحله‌ای جهت پیشگیری از خطای انسانی است (N4-13). جهت تأیید رول‌بک به نسخه پیشین، لطفاً عبارت <bdi dir="ltr"><strong>CONFIRM-ROLLBACK</strong></bdi> را در کادر زیر تایپ نمایید:
                  </p>
                  <input
                    type="text"
                    value={rollbackInputText}
                    onChange={(e) => setRollbackInputText(e.target.value)}
                    placeholder="CONFIRM-ROLLBACK"
                    aria-label="تایپ عبارت تایید رول‌بک"
                    style={{
                      padding: "0.75rem",
                      borderRadius: "0.375rem",
                      border: "1px solid #cbd5e1",
                      fontSize: "1rem",
                      direction: "ltr",
                      textAlign: "center",
                      minHeight: "44px",
                    }}
                  />
                  <div style={{ display: "flex", gap: "0.75rem", justifyContent: "flex-end" }}>
                    <button
                      type="button"
                      onClick={() => {
                        setRollbackConfirmationModal(false);
                        setRollbackInputText("");
                      }}
                      style={{
                        padding: "0.5rem 1rem",
                        borderRadius: "0.375rem",
                        border: "1px solid #cbd5e1",
                        background: "#ffffff",
                        cursor: "pointer",
                        minHeight: "44px",
                        minWidth: "44px",
                      }}
                    >
                      انصراف
                    </button>
                    <button
                      type="button"
                      disabled={rollbackInputText !== "CONFIRM-ROLLBACK"}
                      onClick={() => {
                        alert("دستور رول‌بک با موفقیت به FSM پایلوت ارسال گردید.");
                        setRollbackConfirmationModal(false);
                        setRollbackInputText("");
                      }}
                      style={{
                        padding: "0.5rem 1.25rem",
                        borderRadius: "0.375rem",
                        border: "none",
                        backgroundColor: rollbackInputText === "CONFIRM-ROLLBACK" ? "#991b1b" : "#cbd5e1",
                        color: "#ffffff",
                        cursor: rollbackInputText === "CONFIRM-ROLLBACK" ? "pointer" : "not-allowed",
                        minHeight: "44px",
                        minWidth: "44px",
                        fontWeight: 600,
                      }}
                    >
                      تایید و اجرای رول‌بک
                    </button>
                  </div>
                </div>
              </div>
            )}
          </section>
        )}
      </div>
    </AppShell>
  );
}
