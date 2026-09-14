"use client";

import React, { useState } from "react";
import styles from "./operations.module.css";

export interface GateVerificationState {
  manager_authorization_signed: boolean;
  legal_privacy_review_cleared: boolean;
  legal_basis_or_consent: boolean;
  data_minimization_audited: boolean;
  tenant_authorization_isolated: boolean;
  access_control_verified: boolean;
  retention_policy_enforced: boolean;
  deletion_procedure_verified: boolean;
  offboarding_policy_verified: boolean;
  incident_readiness_tested: boolean;
  support_readiness_active: boolean;
  auditability_ledger_active: boolean;
  security_acceptance_cleared: boolean;
  anti_ranking_validated: boolean;
}

export interface ManagerDecisionCockpitProps {
  tenantName?: string;
  pilotCode: string;
  currentState: string;
  isSyntheticRehearsal: boolean;
  gates: GateVerificationState;
  onAuthorizeActivation?: () => void;
  onEmergencySuspension?: (reason: string) => void;
}

export const ManagerDecisionCockpit: React.FC<ManagerDecisionCockpitProps> = ({
  tenantName = "Synthetic Pilot Academy P6",
  pilotCode,
  currentState,
  isSyntheticRehearsal,
  gates,
  onAuthorizeActivation,
  onEmergencySuspension,
}) => {
  const [confirmModalOpen, setConfirmModalOpen] = useState(false);
  const [suspensionModalOpen, setSuspensionModalOpen] = useState(false);
  const [suspensionReason, setSuspensionReason] = useState("");
  const [firstConfirmChecked, setFirstConfirmChecked] = useState(false);
  const [secondConfirmChecked, setSecondConfirmChecked] = useState(false);

  const gateList: { key: keyof GateVerificationState; label: string; description: string }[] = [
    {
      key: "manager_authorization_signed",
      label: "مجوز رسمی مدیریت ارشد (امضای دوطرفه)",
      description: "تأییدیه نهایی و رسمی مدیریت ارشد مبنی بر پذیرش شرایط پایلوت",
    },
    {
      key: "legal_privacy_review_cleared",
      label: "تأییدیه حقوقی و حریم خصوصی",
      description: "انطباق کامل با قوانین پردازش و حفاظت از داده‌ها",
    },
    {
      key: "legal_basis_or_consent",
      label: "مبنای قانونی و رضایت‌نامه صریح",
      description: "ثبت رضایت‌نامه‌های اولیا و مبنای قانونی شفاف",
    },
    {
      key: "data_minimization_audited",
      label: "ممیزی کمینه‌سازی داده‌ها (Zero Real PII)",
      description: "عدم ذخیره‌سازی داده‌های حساس و ناشناس‌سازی حداکثری",
    },
    {
      key: "tenant_authorization_isolated",
      label: "جداسازی داده‌ها بر اساس مستأجر (RLS)",
      description: "اعمال قطعی Row-Level Security در دیتابیس",
    },
    {
      key: "access_control_verified",
      label: "کنترل دسترسی مبتنی بر نقش (RBAC/Scopes)",
      description: "اعمال محدودیت‌های اختیارات پرسنل و اپراتورها",
    },
    {
      key: "retention_policy_enforced",
      label: "سیاست نگهداری داده‌ها (Data Retention)",
      description: "تعریف بازه‌های مجاز ماندگاری و انقضای خودکار داده‌ها",
    },
    {
      key: "deletion_procedure_verified",
      label: "رویه امحا و Crypto-Shredding",
      description: "مکانیزم تضمین حذف و نابودی غیرقابل‌بازگشت کلیدها",
    },
    {
      key: "offboarding_policy_verified",
      label: "رویه خروج و قطع دسترسی (Offboarding)",
      description: "پروتکل خروج سازمان از پایلوت و تحویل اسناد",
    },
    {
      key: "incident_readiness_tested",
      label: "آمادگی مدیریت رخداد و حوادث امنیتی",
      description: "آزمون سناریوهای بحران، اعلان نقض داده و مهار آسیب",
    },
    {
      key: "support_readiness_active",
      label: "آمادگی تیم پشتیبانی و عملیات",
      description: "فعال بودن کانال‌های پشتیبانی و اپراتورهای معین",
    },
    {
      key: "auditability_ledger_active",
      label: "دفترکل تغییرناپذیر ممیزی (Auditability Ledger)",
      description: "ثبت غیرقابل‌دستکاری رویدادها در Outbox و لاگ‌های امنیتی",
    },
    {
      key: "security_acceptance_cleared",
      label: "پذیرش امنیتی و کنترل‌های دفاعی",
      description: "گذراندن بررسی‌های سخت‌گیرانه امنیتی بدون باگ مسدودکننده",
    },
    {
      key: "anti_ranking_validated",
      label: "اعتبارسنجی منع رتبه‌بندی عمومی و شفافیت AI",
      description: "جلوگیری قطعی از رده‌بندی مخرب دانش‌آموزان و تضمین شفافیت",
    },
  ];

  const satisfiedGatesCount = gateList.filter((g) => gates[g.key]).length;
  const isAllGatesSatisfied = satisfiedGatesCount === 14;
  const canDecide = currentState === "MANAGER_DECISION_REQUIRED" && isAllGatesSatisfied;

  const handleFinalAuthorization = () => {
    if (firstConfirmChecked && secondConfirmChecked && onAuthorizeActivation) {
      onAuthorizeActivation();
      setConfirmModalOpen(false);
    }
  };

  const handleSuspensionSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!suspensionReason.trim()) return;
    if (onEmergencySuspension) {
      onEmergencySuspension(suspensionReason);
      setSuspensionModalOpen(false);
      setSuspensionReason("");
    }
  };

  return (
    <main className={styles.container} lang="fa" dir="rtl">
      {/* Header */}
      <header className={styles.header}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
          <div>
            <h1 className={styles.title}>میز تصمیم‌گیری مدیریت ارشد (Controlled Pilot Admission)</h1>
            <p className={styles.subtitle}>
              سازمان مستأجر: <strong>{tenantName}</strong> | کد پایلوت:{" "}
              <bdi className={styles.bidiWrapper} dir="ltr">{pilotCode}</bdi>
            </p>
          </div>
          <div>
            <span
              className={styles.badge}
              style={{
                background: isSyntheticRehearsal ? "#dbeafe" : "#fef3c7",
                color: isSyntheticRehearsal ? "#1e40af" : "#92400e",
                padding: "0.5rem 1rem",
                borderRadius: "9999px",
                fontWeight: 700,
                fontSize: "0.875rem",
              }}
            >
              حالت محیط: {isSyntheticRehearsal ? "شبیه‌سازی سنتتیک (Synthetic Rehearsal)" : "🔒 پایلوت واقعی (Real Data Pilot)"}
            </span>
          </div>
        </div>
      </header>

      {/* Grid: 14 Pre-Admission Gates & FSM Cockpit */}
      <div className={styles.gridTwoCol}>
        {/* Column 1: 14 Immutable Pre-Admission Gate Domains */}
        <section className={styles.card} aria-labelledby="gates-heading">
          <div className={styles.cardHeader}>
            <h2 id="gates-heading" className={styles.cardTitle}>
              دروازه‌های ۱۴‌گانه پیش‌پذیرش پایلوت
            </h2>
            <span
              className={styles.badge}
              style={{
                background: isAllGatesSatisfied ? "#dcfce7" : "#fee2e2",
                color: isAllGatesSatisfied ? "#166534" : "#991b1b",
              }}
            >
              {satisfiedGatesCount} از ۱۴ تأیید شده
            </span>
          </div>

          <p style={{ fontSize: "0.875rem", color: "#64748b", marginBottom: "1rem" }}>
            هیچ سازمانی بدون ارضای قطعی و ۱۰۰٪ هر ۱۴ دروازه حق ورود به فاز فعال‌سازی پایلوت را ندارد.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            {gateList.map((g, idx) => {
              const satisfied = gates[g.key];
              return (
                <article
                  key={g.key}
                  style={{
                    display: "flex",
                    alignItems: "flex-start",
                    gap: "0.75rem",
                    padding: "0.875rem",
                    borderRadius: "0.75rem",
                    background: satisfied ? "#f0fdf4" : "#fff1f2",
                    border: `1px solid ${satisfied ? "#bbf7d0" : "#fecdd3"}`,
                  }}
                >
                  <span
                    aria-hidden="true"
                    style={{
                      fontSize: "1.25rem",
                      lineHeight: 1,
                      marginTop: "0.125rem",
                    }}
                  >
                    {satisfied ? "✅" : "⏳"}
                  </span>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <strong style={{ fontSize: "0.9375rem", color: satisfied ? "#166534" : "#9f1239" }}>
                        {idx + 1}. {g.label}
                      </strong>
                      <span
                        style={{
                          fontSize: "0.75rem",
                          fontWeight: 700,
                          color: satisfied ? "#15803d" : "#be123c",
                        }}
                      >
                        {satisfied ? "پذیرفته شد" : "معلق / ناقص"}
                      </span>
                    </div>
                    <p style={{ fontSize: "0.8125rem", color: "#475569", margin: "0.25rem 0 0 0" }}>
                      {g.description}
                    </p>
                  </div>
                </article>
              );
            })}
          </div>
        </section>

        {/* Column 2: FSM Progression & Manager Decision Controls */}
        <section className={styles.card} aria-labelledby="fsm-heading">
          <div className={styles.cardHeader}>
            <h2 id="fsm-heading" className={styles.cardTitle}>
              وضعیت چرخه حیات (FSM Lifecycle)
            </h2>
            <span
              className={styles.badge}
              style={{
                background: "#e0e7ff",
                color: "#3730a3",
              }}
            >
              وضعیت فعلی: <bdi className={styles.bidiWrapper} dir="ltr">{currentState}</bdi>
            </span>
          </div>

          <div style={{ marginBottom: "1.5rem" }}>
            <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "#1e293b", marginBottom: "0.75rem" }}>
              سقف تصمیم‌گیری دنیای واقعی (Real-World Cap)
            </h3>
            <div
              style={{
                padding: "1rem",
                borderRadius: "0.75rem",
                background: "#f8fafc",
                border: "1px solid #e2e8f0",
                fontSize: "0.875rem",
                lineHeight: 1.7,
                color: "#334155",
              }}
            >
              <p style={{ margin: 0 }}>
                حتی در صورت تأیید کامل دروازه‌های ۱۴‌گانه، فعال‌سازی پایلوت در محیط عملیاتی مستلزم صدور رسمی
                دستورالعمل از سوی فرمانده و امضای مستقل مدیر با احراز هویت دوعاملی است.
              </p>
            </div>
          </div>

          {/* Action Cockpit */}
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <button
              type="button"
              id="authorize-pilot-btn"
              disabled={!canDecide}
              onClick={() => setConfirmModalOpen(true)}
              className={styles.primaryBtn}
              style={{
                width: "100%",
                minHeight: "48px",
                opacity: canDecide ? 1 : 0.5,
                cursor: canDecide ? "pointer" : "not-allowed",
                background: canDecide ? "#059669" : "#94a3b8",
              }}
            >
              صدور مجوز نهایی فعال‌سازی پایلوت (Manager Authorization)
            </button>

            <button
              type="button"
              id="emergency-suspend-btn"
              onClick={() => setSuspensionModalOpen(true)}
              style={{
                width: "100%",
                minHeight: "48px",
                borderRadius: "0.75rem",
                fontWeight: 600,
                fontSize: "0.9375rem",
                cursor: "pointer",
                background: "#ffffff",
                color: "#dc2626",
                border: "1px solid #f87171",
                transition: "background 0.2s ease",
              }}
            >
              🛑 تعلیق اضطراری پایلوت (Emergency Suspension)
            </button>
          </div>
        </section>
      </div>

      {/* Two-Step Confirmation Modal for Manager Authorization */}
      {confirmModalOpen && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="confirm-modal-title"
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(15, 23, 42, 0.7)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
            padding: "1rem",
          }}
        >
          <div
            style={{
              background: "#ffffff",
              borderRadius: "1.25rem",
              maxWidth: "540px",
              width: "100%",
              padding: "2rem",
              boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
              direction: "rtl",
            }}
          >
            <h2 id="confirm-modal-title" style={{ fontSize: "1.25rem", fontWeight: 800, color: "#111827", marginBottom: "1rem" }}>
              تأییدیه دومرحله‌ای صدور مجوز پایلوت
            </h2>
            <p style={{ fontSize: "0.875rem", color: "#4b5563", lineHeight: 1.6, marginBottom: "1.25rem" }}>
              به عنوان مدیر ارشد، صدور مجوز پایلوت به منزله باز شدن پنجره پذیرش (Activation Window) خواهد بود.
              لطفاً موارد ذیل را تأیید فرمایید:
            </p>

            <div style={{ display: "flex", flexDirection: "column", gap: "0.875rem", marginBottom: "1.5rem" }}>
              <label style={{ display: "flex", alignItems: "flex-start", gap: "0.5rem", fontSize: "0.875rem", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  id="confirm-step-1"
                  checked={firstConfirmChecked}
                  onChange={(e) => setFirstConfirmChecked(e.target.checked)}
                  style={{ width: "20px", height: "20px", marginTop: "0.125rem" }}
                />
                <span>صحت و سقم بررسی‌های حقوقی، امنیتی، و انطباق حریم خصوصی را شخصاً بررسی و تصدیق می‌نمایم.</span>
              </label>
              <label style={{ display: "flex", alignItems: "flex-start", gap: "0.5rem", fontSize: "0.875rem", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  id="confirm-step-2"
                  checked={secondConfirmChecked}
                  onChange={(e) => setSecondConfirmChecked(e.target.checked)}
                  style={{ width: "20px", height: "20px", marginTop: "0.125rem" }}
                />
                <span>تأیید می‌کنم که مکانیزم تعلیق اضطراری و کلیدهای امحا (Crypto-Shredding) در دسترس و عملیاتی هستند.</span>
              </label>
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.75rem" }}>
              <button
                type="button"
                onClick={() => setConfirmModalOpen(false)}
                style={{
                  padding: "0.625rem 1.25rem",
                  borderRadius: "0.625rem",
                  border: "1px solid #d1d5db",
                  background: "#ffffff",
                  color: "#374151",
                  cursor: "pointer",
                  minHeight: "44px",
                }}
              >
                انصراف
              </button>
              <button
                type="button"
                id="submit-final-auth"
                disabled={!firstConfirmChecked || !secondConfirmChecked}
                onClick={handleFinalAuthorization}
                style={{
                  padding: "0.625rem 1.25rem",
                  borderRadius: "0.625rem",
                  border: "none",
                  background: firstConfirmChecked && secondConfirmChecked ? "#059669" : "#9ca3af",
                  color: "#ffffff",
                  fontWeight: 600,
                  cursor: firstConfirmChecked && secondConfirmChecked ? "pointer" : "not-allowed",
                  minHeight: "44px",
                }}
              >
                امضا و صدور مجوز
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Emergency Suspension Modal */}
      {suspensionModalOpen && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="suspend-modal-title"
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(15, 23, 42, 0.7)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
            padding: "1rem",
          }}
        >
          <div
            style={{
              background: "#ffffff",
              borderRadius: "1.25rem",
              maxWidth: "500px",
              width: "100%",
              padding: "2rem",
              boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
              direction: "rtl",
            }}
          >
            <h2 id="suspend-modal-title" style={{ fontSize: "1.25rem", fontWeight: 800, color: "#991b1b", marginBottom: "0.75rem" }}>
              دستور تعلیق اضطراری پایلوت
            </h2>
            <p style={{ fontSize: "0.875rem", color: "#4b5563", lineHeight: 1.6, marginBottom: "1rem" }}>
              با ثبت تعلیق، تمامی دسترسی‌های فعال بلافاصله مسدود و وضعیت چرخه به <bdi className={styles.bidiWrapper} dir="ltr">SUSPENDED</bdi> تغییر می‌یابد.
            </p>

            <form onSubmit={handleSuspensionSubmit}>
              <div className={styles.formGroup}>
                <label htmlFor="suspension-reason-input" className={styles.label}>
                  علت تعلیق اضطراری / گزارش نقض:
                </label>
                <textarea
                  id="suspension-reason-input"
                  className={styles.textarea}
                  value={suspensionReason}
                  onChange={(e) => setSuspensionReason(e.target.value)}
                  placeholder="دلیل مستند تعلیق را شرح دهید..."
                  required
                />
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.75rem" }}>
                <button
                  type="button"
                  onClick={() => setSuspensionModalOpen(false)}
                  style={{
                    padding: "0.625rem 1.25rem",
                    borderRadius: "0.625rem",
                    border: "1px solid #d1d5db",
                    background: "#ffffff",
                    color: "#374151",
                    cursor: "pointer",
                    minHeight: "44px",
                  }}
                >
                  انصراف
                </button>
                <button
                  type="submit"
                  id="confirm-emergency-suspend"
                  style={{
                    padding: "0.625rem 1.25rem",
                    borderRadius: "0.625rem",
                    border: "none",
                    background: "#dc2626",
                    color: "#ffffff",
                    fontWeight: 600,
                    cursor: "pointer",
                    minHeight: "44px",
                  }}
                >
                  تأیید و اجرای تعلیق فوری
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </main>
  );
};
export default ManagerDecisionCockpit;
