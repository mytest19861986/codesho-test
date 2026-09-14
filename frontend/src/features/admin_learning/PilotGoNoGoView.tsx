"use client";

import React, { useState } from "react";
import styles from "./enterprise_governance.module.css";

export interface GoNoGoControlItem {
  readonly id: string;
  readonly domain: string;
  readonly controlName: string;
  readonly status: "GO" | "NO_GO";
  readonly reason: string;
  readonly isHardStop: boolean;
}

export function PilotGoNoGoView() {
  const [filterDomain, setFilterDomain] = useState<string>("ALL");

  const controls: GoNoGoControlItem[] = [
    { id: "g-01", domain: "امنیت داده", controlName: "جداسازی کامل پایگاه‌داده با FORCE RLS", status: "GO", reason: "سیاست‌های ایزولاسیون مستأجر بدون امکان دور زدن اعمال شده‌اند", isHardStop: true },
    { id: "g-02", domain: "حریم خصوصی", controlName: "ممانعت مطلق از ورود داده واقعی کودکان", status: "GO", reason: "تطابق با سیاست REAL_CHILD_DATA: 0", isHardStop: true },
    { id: "g-03", domain: "اخلاق آموزشی", controlName: "ممانعت از رتبه‌بندی دانش‌آموزان", status: "GO", reason: "تطابق با سیاست STUDENT_RANKING: 0", isHardStop: true },
    { id: "g-04", domain: "حاکمیت اختیار", controlName: "تفکیک اختیارات دو نفره و منع اعطای خودسرانه", status: "GO", reason: "تطابق با DUAL_CUSTODY_BYPASS: DENY", isHardStop: true },
    { id: "g-05", domain: "استقرار سیستمی", controlName: "منع استقرار خودکار در محیط عملیاتی", status: "GO", reason: "تطابق با PRODUCTION_DEPLOY_AUTHORITY: 0", isHardStop: true },
    { id: "g-06", domain: "بازیابی رخداد", controlName: "سنجش بازیابی پشتیبان و PITR ساختگی", status: "GO", reason: "سناریوهای R11 و R12 با موفقیت ارزیابی شدند", isHardStop: false },
    { id: "g-07", domain: "تأییدیه مدیریت", controlName: "سقف حالت در دنیای واقعی: تایید مدیر انسانی", status: "GO", reason: "تطابق با REAL_WORLD_MAX_STATE: MANAGER_APPROVAL_REQUIRED", isHardStop: true },
  ];

  const filtered = filterDomain === "ALL" ? controls : controls.filter(c => c.domain === filterDomain);

  return (
    <div className={styles.container} style={{ gap: "1.5rem" }}>
      <div className={styles.header}>
        <h2 className={styles.title} id="go-no-go-heading">
          ماتریس کنترل تصميم‌گیری <bdi dir="ltr">Go / No-Go</bdi> فعال‌سازی پایلوت
        </h2>
        <p className={styles.subtitle}>
          سامانه اعتبارسنجی کنترل‌های حیاتی با رعایت اصول توقف قطعی (Hard Stop) و ضدرتبه‌بندی
        </p>
      </div>

      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
        {["ALL", "امنیت داده", "حریم خصوصی", "اخلاق آموزشی", "حاکمیت اختیار", "استقرار سیستمی", "بازیابی رخداد"].map((d) => (
          <button
            key={d}
            type="button"
            className={`${styles.tabBtn} ${filterDomain === d ? styles.tabBtnActive : ""}`}
            style={{ minHeight: "44px" }}
            onClick={() => setFilterDomain(d)}
          >
            {d === "ALL" ? "همه حوزه‌ها" : d}
          </button>
        ))}
      </div>

      <div className={styles.cardGrid}>
        {filtered.map((item) => (
          <article key={item.id} className={styles.card} aria-labelledby={`ctrl-${item.id}-title`}>
            <div className={styles.cardHeader}>
              <span className={`${styles.badge} ${item.status === "GO" ? styles.badgeActive : styles.badgeBlocking}`}>
                {item.status}
              </span>
              {item.isHardStop && (
                <span className={`${styles.badge} ${styles.badgeBlocking}`}>
                  توقف قطعی (Hard Stop)
                </span>
              )}
            </div>
            <h3 id={`ctrl-${item.id}-title`} className={styles.cardTitle}>
              {item.controlName}
            </h3>
            <div className={styles.cardMeta}>
              <span>حوزه ارزیابی: {item.domain}</span>
              <span>وضعیت شواهد: {item.reason}</span>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
