"use client";

import { useState } from "react";
import Link from "next/link";
import { parentAlphaContent as copy } from "@/content/fa/parent.alpha";
import {
  Badge,
  IconSparkles,
  IconCheck,
  IconClose,
  IconShield,
  IconLaptop,
} from "@/components/ui";
import { useParentSearch } from "../ParentSearchContext";
import styles from "../../student/student.module.css";

export default function ParentConsentPage() {
  const o = copy.overview;
  const { searchQuery, selectedChild } = useParentSearch();
  const [consentOversight, setConsentOversight] = useState(true);
  const [consentPortfolio, setConsentPortfolio] = useState(true);
  const [consentMentorChat, setConsentMentorChat] = useState(true);
  const [savedNotice, setSavedNotice] = useState(false);

  const handleSave = () => {
    setSavedNotice(true);
    setTimeout(() => setSavedNotice(false), 3000);
  };

  return (
    <div className={styles.studentDashboard}>
      {/* 1. Hero Banner */}
      <section className={styles.heroBanner} aria-labelledby="consent-hero-heading">
        <div className={styles.heroContent}>
          <div className={styles.heroGreeting}>
            <div className={styles.heroBadgeRow}>
              <Badge variant="primary" className={styles.heroBadgeTranslucent}>حریم خصوصی و مجوزها</Badge>
              <Badge variant="outline" className={styles.heroBadgeDark}>سیاست‌های حاکمیتی و نظارتی</Badge>
            </div>
            <h1 id="consent-hero-heading" className={styles.heroHeading}>
              مدیریت رضایت‌نامه‌ها و کنترل دسترسی اولیا
            </h1>
            <p className={styles.heroSubtitle}>
              تعیین دقیق حدود دسترسی منتورها، نحوه انتشار نمونه‌کارها در پورتفولیو و پایش مستقیم ایمنی آموزشی فرزند شما ({selectedChild}).
            </p>
          </div>
          <div className={styles.heroButtons}>
            <button
              type="button"
              className={styles.heroPrimaryBtn}
              onClick={handleSave}
            >
              <IconSparkles aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>ذخیره تغییرات مجوزها</span>
            </button>
            <Link href="/parent" className={styles.heroSecondaryBtn} style={{ textDecoration: "none" }}>
              <IconLaptop aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>بازگشت به نمای کلی</span>
            </Link>
          </div>
        </div>

        <div className={styles.heroGraphicWrapper}>
          <div className={styles.heroGlassPanel}>
            <p className={styles.heroQuoteText}>«ایمنی یادگیری فرزند، اولویت اول»</p>
            <span className={styles.heroBrandMini}>ثبت تغییرات در دفتر کل بدون امکان جعل یا حذف</span>
            <div className={styles.heroChecklist}>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>حریم خصوصی تفکیک‌شده</span>
              </div>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>نظارت کامل والدین</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. Consent Items Card */}
      <section className={styles.cardPanel} aria-label="تنظیمات رضایت‌نامه‌ها">
        <div className={styles.panelHeader}>
          <h2 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
            <IconShield aria-hidden="true" />
            <span>مجوزهای نظارتی و فعالیت‌های مجاز</span>
          </h2>
          <Badge variant="primary">سیاست حاکمیتی فعال</Badge>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "var(--cs-space-4)" }}>
          {/* Permission 1 */}
          <div style={{
            background: "var(--cs-color-bg-base)",
            padding: "var(--cs-space-4)",
            borderRadius: "var(--cs-radius-control)",
            border: "var(--cs-border-width) solid var(--cs-color-border-subtle)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center"
          }}>
            <div>
              <strong style={{ display: "block", fontSize: "var(--cs-font-size-body)" }}>مجوز نظارت تحصیلی و پایش پیشرفت</strong>
              <span style={{ fontSize: "var(--cs-font-size-caption)", color: "var(--cs-color-text-secondary)" }}>
                امکان مشاهده ساعات مطالعه، تکالیف تحویل‌شده و وضعیت دوره‌ها توسط ولی
              </span>
            </div>
            <button
              type="button"
              className={styles.actionButton}
              style={{
                background: consentOversight ? "var(--cs-color-brand-primary)" : "var(--cs-color-bg-card)",
                color: consentOversight ? "#fff" : "var(--cs-color-text-primary)"
              }}
              onClick={() => setConsentOversight(!consentOversight)}
            >
              {consentOversight ? "مجوز فعال است" : "غیرفعال"}
            </button>
          </div>

          {/* Permission 2 */}
          <div style={{
            background: "var(--cs-color-bg-base)",
            padding: "var(--cs-space-4)",
            borderRadius: "var(--cs-radius-control)",
            border: "var(--cs-border-width) solid var(--cs-color-border-subtle)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center"
          }}>
            <div>
              <strong style={{ display: "block", fontSize: "var(--cs-font-size-body)" }}>مجوز گفتگو و جلسات آنلاین با منتور ارشد</strong>
              <span style={{ fontSize: "var(--cs-font-size-caption)", color: "var(--cs-color-text-secondary)" }}>
                برگزاری جلسات رفع اشکال با نظارت مستمر و ثبت متن و زمان جلسات
              </span>
            </div>
            <button
              type="button"
              className={styles.actionButton}
              style={{
                background: consentMentorChat ? "var(--cs-color-brand-primary)" : "var(--cs-color-bg-card)",
                color: consentMentorChat ? "#fff" : "var(--cs-color-text-primary)"
              }}
              onClick={() => setConsentMentorChat(!consentMentorChat)}
            >
              {consentMentorChat ? "مجوز فعال است" : "غیرفعال"}
            </button>
          </div>

          {/* Permission 3 */}
          <div style={{
            background: "var(--cs-color-bg-base)",
            padding: "var(--cs-space-4)",
            borderRadius: "var(--cs-radius-control)",
            border: "var(--cs-border-width) solid var(--cs-color-border-subtle)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center"
          }}>
            <div>
              <strong style={{ display: "block", fontSize: "var(--cs-font-size-body)" }}>مجوز انتشار پروژه‌ها در پورتفولیوی عمومی</strong>
              <span style={{ fontSize: "var(--cs-font-size-caption)", color: "var(--cs-color-text-secondary)" }}>
                امکان نمایش پروژه‌های تاییدشده کارآموز در صفحه پورتفولیو بدون افشای اطلاعات هویتی
              </span>
            </div>
            <button
              type="button"
              className={styles.actionButton}
              style={{
                background: consentPortfolio ? "var(--cs-color-brand-primary)" : "var(--cs-color-bg-card)",
                color: consentPortfolio ? "#fff" : "var(--cs-color-text-primary)"
              }}
              onClick={() => setConsentPortfolio(!consentPortfolio)}
            >
              {consentPortfolio ? "مجوز فعال است" : "غیرفعال"}
            </button>
          </div>
        </div>

        {savedNotice && (
          <div style={{
            marginBlockStart: "var(--cs-space-4)",
            background: "rgba(16, 185, 129, 0.12)",
            color: "var(--cs-color-success)",
            border: "1px solid rgba(16, 185, 129, 0.25)",
            borderRadius: "var(--cs-radius-control)",
            padding: "var(--cs-space-3)",
            fontSize: "var(--cs-font-size-caption)",
            display: "flex",
            alignItems: "center",
            gap: "var(--cs-space-2)"
          }}>
            <IconCheck aria-hidden="true" style={{ inlineSize: "1rem", blockSize: "1rem" }} />
            <span>تنظیمات و مجوزهای حریم خصوصی با موفقیت به‌روزرسانی و ثبت شد.</span>
          </div>
        )}
      </section>
    </div>
  );
}
