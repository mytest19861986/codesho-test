"use client";

import React, { useState } from "react";
import styles from "./enterprise_governance.module.css";

export interface PilotLifecycleItem {
  readonly id: string;
  readonly pilotCode: string;
  readonly state: string;
  readonly isSyntheticMode: boolean;
  readonly isProductionTarget: boolean;
  readonly prerequisitesSatisfied: boolean;
}

export function PilotActivationControlBoard() {
  const [frictionalModal, setFrictionalModal] = useState<boolean>(false);
  const [frictionalInput, setFrictionalInput] = useState<string>("");
  const [selectedAction, setSelectedAction] = useState<string>("ROLLBACK");
  const [noticeMessage, setNoticeMessage] = useState<string>("");

  const syntheticPilots: PilotLifecycleItem[] = [
    {
      id: "pilot-1",
      pilotCode: "synth-school-alpha",
      state: "MANAGER_APPROVAL_REQUIRED",
      isSyntheticMode: true,
      isProductionTarget: false,
      prerequisitesSatisfied: true,
    },
    {
      id: "pilot-2",
      pilotCode: "synth-school-beta",
      state: "PREREQUISITES_PENDING",
      isSyntheticMode: true,
      isProductionTarget: false,
      prerequisitesSatisfied: false,
    },
    {
      id: "pilot-3",
      pilotCode: "synth-school-gamma",
      state: "SUSPENDED",
      isSyntheticMode: true,
      isProductionTarget: false,
      prerequisitesSatisfied: true,
    },
  ];

  const handleActionClick = (action: string) => {
    setSelectedAction(action);
    setFrictionalModal(true);
    setFrictionalInput("");
  };

  const handleConfirmFrictional = () => {
    if (frictionalInput === "CONFIRM-ROLLBACK") {
      setNoticeMessage("اقدام اصطکاکی با موفقیت ثبت شد و به FSM پایلوت ارسال گردید.");
      setFrictionalModal(false);
      setFrictionalInput("");
    }
  };

  return (
    <div className={styles.container} style={{ gap: "1.5rem" }}>
      <div className={styles.header}>
        <h2 className={styles.title} id="pilot-control-board-heading">
          داشبورد راهبری و فعال‌سازی پایلوت کنترل‌شده (فاز ۵)
        </h2>
        <p className={styles.subtitle}>
          سامانه نظارت بر ماشین حالت ۱۰ مرحله‌ای، حاکمیت تفکیک اختیارات دو نفره و گیت ۱۱ گانه ورود داده
        </p>
      </div>

      <div className={styles.noticeBox} role="status">
        <strong>وضعیت حاکمیت ران‌تایم:</strong> سقف مرحله در دنیای واقعی: <bdi dir="ltr">MANAGER_APPROVAL_REQUIRED</bdi> | 
        اختیار استقرار در محیط پروداکشن: <bdi dir="ltr">0</bdi> | رتبه‌بندی دانش‌آموز: <bdi dir="ltr">STUDENT_RANKING: 0</bdi>
      </div>

      {noticeMessage && (
        <div style={{ padding: "0.75rem", backgroundColor: "#dcfce7", color: "#166534", borderRadius: "0.375rem" }} role="alert">
          {noticeMessage}
        </div>
      )}

      <div className={styles.cardGrid}>
        {syntheticPilots.map((p) => (
          <article key={p.id} className={styles.card} aria-labelledby={`pilot-${p.id}-title`}>
            <div className={styles.cardHeader}>
              <span className={`${styles.badge} ${p.state === "SUSPENDED" ? styles.badgeBlocking : styles.badgeActive}`}>
                {p.state}
              </span>
              <span className={`${styles.badge} ${styles.badgeAdvisory}`}>
                سنتتیک ۱۰۰٪
              </span>
            </div>
            <h3 id={`pilot-${p.id}-title`} className={styles.cardTitle}>
              کد شناسایی: <bdi dir="ltr">{p.pilotCode}</bdi>
            </h3>
            <div className={styles.cardMeta}>
              <span>گیت پیش‌نیازها: {p.prerequisitesSatisfied ? "۱۱ از ۱۱ تایید شده" : "در انتظار تکمیل چک‌لیست"}</span>
              <span>حالت اجرا: محیط شبیه‌سازی ساختگی (Synthetic Sandbox)</span>
              <span>ایمنی پروداکشن: <bdi dir="ltr">is_production_target: false</bdi></span>
            </div>
            <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
              <button
                type="button"
                className={styles.actionBtn}
                style={{ minHeight: "44px", minWidth: "44px" }}
                onClick={() => handleActionClick("ROLLBACK")}
              >
                رول‌بک اصطکاکی
              </button>
            </div>
          </article>
        ))}
      </div>

      {frictionalModal && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="frictional-dialog-title"
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
            <h3 id="frictional-dialog-title" style={{ fontSize: "1.25rem", fontWeight: 700, color: "#991b1b" }}>
              تایید اصطکاکی دو مرحله‌ای ({selectedAction})
            </h3>
            <p style={{ fontSize: "0.9rem", color: "#475569", lineHeight: 1.6 }}>
              جهت اعمال عملیات حساس بر روی FSM پایلوت، لطفاً عبارت <bdi dir="ltr"><strong>CONFIRM-ROLLBACK</strong></bdi> را در کادر زیر وارد فرمایید:
            </p>
            <input
              type="text"
              value={frictionalInput}
              onChange={(e) => setFrictionalInput(e.target.value)}
              placeholder="CONFIRM-ROLLBACK"
              aria-label="کادر ورود عبارت تایید اصطکاکی"
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
                onClick={() => setFrictionalModal(false)}
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
                disabled={frictionalInput !== "CONFIRM-ROLLBACK"}
                onClick={handleConfirmFrictional}
                style={{
                  padding: "0.5rem 1.25rem",
                  borderRadius: "0.375rem",
                  border: "none",
                  backgroundColor: frictionalInput === "CONFIRM-ROLLBACK" ? "#991b1b" : "#cbd5e1",
                  color: "#ffffff",
                  cursor: frictionalInput === "CONFIRM-ROLLBACK" ? "pointer" : "not-allowed",
                  minHeight: "44px",
                  minWidth: "44px",
                  fontWeight: 600,
                }}
              >
                تایید اصطکاکی نهایی
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
