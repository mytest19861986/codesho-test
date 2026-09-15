"use client";

import React, { useState } from "react";
import styles from "./enterprise_governance.module.css";

export interface GoNoGoControlItem {
  readonly id: string;
  readonly domain: string;
  readonly controlName: string;
  readonly status: "GO" | "NO_GO" | "DEFER";
  readonly reason: string;
  readonly isHardStop: boolean;
}

export function PilotGoNoGoView() {
  const [filterDomain, setFilterDomain] = useState<string>("ALL");

  const controls: GoNoGoControlItem[] = [
    { id: "g-01", domain: "امنیت داده", controlName: "جداسازی کامل پایگاه‌داده با FORCE RLS", status: "GO", reason: "سیاست‌های ایزولاسیون مستأجر بدون امکان دور زدن اعمال شده‌اند", isHardStop: true },
    { id: "g-02", domain: "حریم خصوصی", controlName: "ممانعت مطلق از ورود داده واقعی کودکان (REAL_CHILD_DATA: 0)", status: "GO", reason: "سیاست سنتتیک خالص تأیید شده و بدون نقض است", isHardStop: true },
    { id: "g-03", domain: "اخلاق آموزشی", controlName: "ممانعت مطلق از رتبه‌بندی دانش‌آموزان (STUDENT_RANKING: 0)", status: "GO", reason: "قوانین عدم رتبه‌بندی و عدم مقایسه نمرات اعتبارسنجی شد", isHardStop: true },
    { id: "g-04", domain: "حاکمیت اختیار", controlName: "تفکیک اختیارات دو نفره و منع اعطای خودسرانه", status: "GO", reason: "Dual-custody بدون اجازه self-approval فعال است", isHardStop: true },
    { id: "g-05", domain: "استقرار سیستمی", controlName: "منع استقرار خودکار در محیط عملیاتی (PRODUCTION: LOCKED)", status: "GO", reason: "سیاست PRODUCTION_DEPLOY_AUTHORITY: 0 رعایت شده است", isHardStop: true },
    { id: "g-06", domain: "بازیابی رخداد", controlName: "سنجش بازیابی پشتیبان و PITR ساختگی", status: "GO", reason: "سناریوهای مانور بازیابی با موفقیت پشت سر گذاشته شدند", isHardStop: false },
    { id: "g-07", domain: "تصمیم مدیریت", controlName: "تصمیم‌گیری انسانی انحصاری مدیر (HUMAN_MANAGER_ONLY)", status: "GO", reason: "عامل‌های خودکار یا هوش مصنوعی فاقد حق صدور تصمیم هستند", isHardStop: true },
    { id: "g-08", domain: "تازگی شواهد", controlName: "گیت انقضا و تازگی شواهد ۱۲ گانه (Freshness Gate)", status: "GO", reason: "تمامی شواهد بازه اعتبار کمتر از ۲۴ ساعت دارند", isHardStop: true },
    { id: "g-09", domain: "تاییدیه‌های شاخص", controlName: "قفل بازه پنجره فعال‌سازی و انقضای زمان‌مند", status: "GO", reason: "بازه زمانی و انقضای توکن به طور دقیق ثبت شده است", isHardStop: false },
    { id: "g-10", domain: "تک‌بار مصرفی", controlName: "پیشگیری از حملات بازپخش توکن (Single-Use Nonce)", status: "GO", reason: "نانس توکن پس از اولین مصرف ابطال می‌گردد", isHardStop: true },
    { id: "g-11", domain: "ایزولاسیون توکن", controlName: "ممانعت از انتقال توکن میان مستأجرها (Non-Transferable)", status: "GO", reason: "توکن به کد پایلوت و هویت مستأجر متصل است", isHardStop: true },
    { id: "g-12", domain: "یکپارچگی اسکوپ", controlName: "اعتبارسنجی هش استاندارد پارامترها (Scope Hash)", status: "GO", reason: "دستکاری پارامترهای پایلوت به طور خودکار مسدود می‌شود", isHardStop: true },
    { id: "g-13", domain: "امحای داده ساختگی", controlName: "رمزنگاری امحای داده و صدور رسید غیرقابل‌تغییر (GLM F5)", status: "GO", reason: "مکانیزم پاکسازی سنتتیک و انتشار رسید امضا شده فعال است", isHardStop: true },
    { id: "g-14", domain: "دفترکل تغییرناپذیر", controlName: "ثبت رویدادهای ممیزی غیرقابل‌حذف (Immutable Audit Log)", status: "GO", reason: "مجوزهای UPDATE و DELETE در دیتابیس لغو شده‌اند", isHardStop: true },
  ];

  const filtered = filterDomain === "ALL" ? controls : controls.filter(c => c.domain === filterDomain);

  return (
    <div className={styles.container} style={{ gap: "1.5rem" }}>
      <div className={styles.header}>
        <h2 className={styles.title} id="go-no-go-heading">
          ماتریس کنترل تصميم‌گیری فاز ۷ <bdi dir="ltr">Go / No-Go / Defer</bdi> فعال‌سازی پایلوت
        </h2>
        <p className={styles.subtitle}>
          اتاق کنترل ۱۴ گانه تصمیم‌گیری مدیر انسانی با ثبت دفترکل تغییرناپذیر و گیت‌های توقف قطعی (Hard Stop)
        </p>
      </div>

      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
        {["ALL", "امنیت داده", "حریم خصوصی", "اخلاق آموزشی", "حاکمیت اختیار", "استقرار سیستمی", "تصمیم مدیریت", "تازگی شواهد"].map((d) => (
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
              <span className={`${styles.badge} ${
                item.status === "GO" ? styles.badgeActive : item.status === "NO_GO" ? styles.badgeBlocking : styles.badgeAdvisory
              }`}>
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

