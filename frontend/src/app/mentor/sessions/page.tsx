"use client";

import { useState } from "react";
import Link from "next/link";
import { mentorAlphaContent as copy } from "@/content/fa/mentor.alpha";
import {
  Badge,
  IconSparkles,
  IconClock,
  IconLaptop,
  IconCheck,
  IconClose,
  IconChat,
  IconShield,
  IconCalendar,
} from "@/components/ui";
import { useMentorSearch } from "../MentorSearchContext";
import styles from "../../student/student.module.css";

interface SessionItem {
  id: string;
  title: string;
  student: string;
  time: string;
  duration: string;
  status: "ready" | "scheduled" | "completed";
  topic: string;
}

const initialSessions: SessionItem[] = [
  {
    id: "sess-1",
    title: "جلسه رفع اشکال معماری کامپوننت‌ها و هوک‌های سفارشی",
    student: "رضا حسینی",
    time: "۱۷:۰۰ الی ۱۷:۴۵",
    duration: "۴۵ دقیقه",
    status: "ready",
    topic: "بررسی چرخه حیات کامپوننت و مدیریت Effectها بدون نشت حافظه",
  },
  {
    id: "sess-2",
    title: "بررسی نهایی پروژه پورتفولیو و استقرار روی استیجینگ",
    student: "مریم کاظمی",
    time: "۱۹:۱۵ الی ۲۰:۰۰",
    duration: "۴۵ دقیقه",
    status: "scheduled",
    topic: "بررسی فرایند بیلد و تست یکپارچگی پیش از انتشار عمومی",
  },
  {
    id: "sess-3",
    title: "هدایت مسیر شغلی و تحلیل خطاهای کدنویسی Clean Code",
    student: "علی محمدی",
    time: "فردا ۱۰:۰۰ الی ۱۰:۴۵",
    duration: "۴۵ دقیقه",
    status: "scheduled",
    topic: "مرور ساختار کدنویسی ماژولار و تفکیک مسئولیت توابع",
  },
];

export default function MentorSessionsPage() {
  const { searchQuery } = useMentorSearch();
  const [selectedSession, setSelectedSession] = useState<SessionItem | null>(null);
  const [openModal, setOpenModal] = useState(false);

  const filteredSessions = initialSessions.filter((s) =>
    s.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.student.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.topic.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleOpenSession = (sess: SessionItem) => {
    setSelectedSession(sess);
    setOpenModal(true);
  };

  return (
    <div className={styles.studentDashboard}>
      {/* 1. Hero Banner */}
      <section className={styles.heroBanner} aria-labelledby="sessions-hero-heading">
        <div className={styles.heroContent}>
          <div className={styles.heroGreeting}>
            <div className={styles.heroBadgeRow}>
              <Badge variant="primary" className={styles.heroBadgeTranslucent}>جلسات آنلاین و مشاوره</Badge>
              <Badge variant="outline" className={styles.heroBadgeDark}>تقویم تعاملی مربیگری</Badge>
            </div>
            <h1 id="sessions-hero-heading" className={styles.heroHeading}>
              برنامه جلسات آنلاین رفع اشکال و هدایت کارآموزان
            </h1>
            <p className={styles.heroSubtitle}>
              مدیریت و پیگیری زمان‌بندی جلسات ویدیویی و صوتی مستقیم با کارآموزان برای گره‌گشایی از چالش‌های مفهومی و معماری.
            </p>
          </div>
          <div className={styles.heroButtons}>
            <Link href="/mentor/reviews" className={styles.heroPrimaryBtn} style={{ textDecoration: "none" }}>
              <IconSparkles aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>صف بررسی کد</span>
            </Link>
            <Link href="/mentor" className={styles.heroSecondaryBtn} style={{ textDecoration: "none" }}>
              <IconLaptop aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>بازگشت به میز کار</span>
            </Link>
          </div>
        </div>

        <div className={styles.heroGraphicWrapper}>
          <div className={styles.heroGlassPanel}>
            <p className={styles.heroQuoteText}>«رفع گره‌های یادگیری در زمان طلایی»</p>
            <span className={styles.heroBrandMini}>جلسات ضبط‌شده با رعایت استانداردهای ایمنی آموزش</span>
            <div className={styles.heroChecklist}>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>جلسات ۴۵ دقیقه‌ای متمرکز</span>
              </div>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>محیط تعاملی کدنویسی زنده</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. KPI Cards */}
      <section className={styles.kpiGrid} aria-label="شاخص‌های جلسات مربیگری">
        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>جلسات امروز</span>
            <span className={styles.kpiValue}>۲ جلسه</span>
            <span className={styles.kpiSub}>
              <IconClock aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>۱ جلسه آماده برگزاری</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle1}`}>
              <IconClock aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>کل جلسات این هفته</span>
            <span className={styles.kpiValue}>۶ جلسه</span>
            <span className={styles.kpiSub}>
              <IconCheck aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>پوشش ۱۰۰٪ درخواست‌ها</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle2}`}>
              <IconCalendar aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>میانگین رضایت از جلسات</span>
            <span className={styles.kpiValue}>۴.۹ از ۵</span>
            <span className={styles.kpiSub}>
              <IconCheck aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>کیفیت علمی تاییدشده</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle3}`}>
              <IconChat aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>محیط امن تعاملی</span>
            <span className={styles.kpiValue}>فعال</span>
            <span className={styles.kpiSub}>
              <IconShield aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>پایبندی به شیوه‌نامه</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle4}`}>
              <IconShield aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>
      </section>

      {/* 3. Sessions List Card */}
      <section className={styles.cardPanel} aria-label="تقویم جلسات">
        <div className={styles.panelHeader}>
          <h2 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
            <IconClock aria-hidden="true" />
            <span>جلسات هماهنگ‌شده با کارآموزان</span>
          </h2>
          <Badge variant="warning">{filteredSessions.length} جلسه برنامه‌ریزی‌شده</Badge>
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
            <span>فیلتر شده بر اساس: «{searchQuery}»</span>
            <span>{filteredSessions.length} نتیجه</span>
          </div>
        )}

        <div className={styles.activityList}>
          {filteredSessions.map((sess, idx) => (
            <div
              key={sess.id}
              className={styles.activityItem}
              style={{ cursor: "pointer", transition: "background var(--cs-motion-fast)" }}
              onClick={() => handleOpenSession(sess)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") handleOpenSession(sess); }}
              aria-label={`مشاهده جزئیات ${sess.title}`}
            >
              <div className={`${styles.activityIconCircle} ${idx === 0 ? styles.kpiCircle1 : styles.kpiCircle2}`}>
                <IconChat aria-hidden="true" />
              </div>
              <div className={styles.activityContent} style={{ inlineSize: "100%" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <p className={styles.activityDesc} style={{ fontWeight: "var(--cs-font-weight-bold)", margin: 0 }}>
                    {sess.title}
                  </p>
                  <Badge variant={sess.status === "ready" ? "primary" : "outline"}>
                    {sess.status === "ready" ? "آماده برگزاری" : "برنامه‌ریزی‌شده"}
                  </Badge>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBlockStart: "0.25rem" }}>
                  <span className={styles.activityTime}>کارآموز: {sess.student} • ساعت: {sess.time}</span>
                  <span style={{ fontSize: "0.75rem", color: "var(--cs-color-text-secondary)" }}>مدت: {sess.duration}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Modal: Session Details */}
      {openModal && selectedSession && (
        <div className={styles.modalBackdrop} onClick={() => setOpenModal(false)}>
          <div className={styles.modalSheet} onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="session-detail-title">
            <div className={styles.modalHeader}>
              <h3 id="session-detail-title" className={styles.modalTitle}>
                <IconClock aria-hidden="true" style={{ color: "var(--cs-color-brand-primary)" }} />
                <span>جزئیات جلسه: {selectedSession.title}</span>
              </h3>
              <button
                type="button"
                className={styles.modalCloseBtn}
                onClick={() => setOpenModal(false)}
                aria-label="بستن پنجره"
              >
                <IconClose aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />
              </button>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "var(--cs-space-3)" }}>
              <div style={{ background: "var(--cs-color-bg-base)", padding: "var(--cs-space-3)", borderRadius: "var(--cs-radius-control)" }}>
                <strong>کارآموز:</strong> <span>{selectedSession.student}</span>
              </div>
              <div style={{ background: "var(--cs-color-bg-base)", padding: "var(--cs-space-3)", borderRadius: "var(--cs-radius-control)" }}>
                <strong>زمان برگزاری:</strong> <span>{selectedSession.time} ({selectedSession.duration})</span>
              </div>
              <div style={{ background: "var(--cs-color-bg-base)", padding: "var(--cs-space-3)", borderRadius: "var(--cs-radius-control)" }}>
                <strong>موضوع و محور گفت‌وگو:</strong> <span>{selectedSession.topic}</span>
              </div>
              <div style={{ background: "var(--cs-color-bg-base)", padding: "var(--cs-space-3)", borderRadius: "var(--cs-radius-control)" }}>
                <strong>استاندارد جلسه:</strong> <span>ارائه سرنخ و راهنمایی مفهومی بدون حل مستقیم تکلیف برای دانش‌آموز</span>
              </div>
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", gap: "var(--cs-space-2)", marginBlockStart: "var(--cs-space-3)" }}>
              <button
                type="button"
                className={styles.actionButton}
                onClick={() => setOpenModal(false)}
              >
                بستن
              </button>
              <button
                type="button"
                className={`${styles.actionButton} ${styles.primaryActionButton}`}
                onClick={() => setOpenModal(false)}
              >
                ورود به اتاق جلسه آنلاین
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
