"use client";

import { useState } from "react";
import Link from "next/link";
import { parentAlphaContent as copy } from "@/content/fa/parent.alpha";
import {
  Badge,
  IconSparkles,
  IconClock,
  IconCheck,
  IconClose,
  IconDocument,
  IconLaptop,
  IconShield,
  IconStar,
} from "@/components/ui";
import { useParentSearch } from "../ParentSearchContext";
import styles from "../../student/student.module.css";

export default function ParentFinancePage() {
  const o = copy.overview;
  const { searchQuery, selectedChild } = useParentSearch();
  const [openModal, setOpenModal] = useState(false);

  const transactions = [
    {
      id: "tx-1",
      title: "تمدید اشتراک فصلی دوره آموزش فرانت‌اند و هوش مصنوعی",
      date: "۱۵ مرداد ۱۴۰۵",
      amount: "رایگان (نسخه آزمایشی سنتتیک)",
      status: "پرداخت موفق",
      receiptId: "REC-2026-8812",
    },
    {
      id: "tx-2",
      title: "بسته مشاوره‌ای ویژه اولیا و پایش تحصیلی",
      date: "۱ تیر ۱۴۰۵",
      amount: "رایگان (طرح استعدادسنجی)",
      status: "فعال",
      receiptId: "REC-2026-7734",
    },
  ];

  const filteredTx = transactions.filter((t) =>
    t.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    t.receiptId.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className={styles.studentDashboard}>
      {/* 1. Hero Banner */}
      <section className={styles.heroBanner} aria-labelledby="finance-hero-heading">
        <div className={styles.heroContent}>
          <div className={styles.heroGreeting}>
            <div className={styles.heroBadgeRow}>
              <Badge variant="primary" className={styles.heroBadgeTranslucent}>وضعیت مالی و اشتراک</Badge>
              <Badge variant="outline" className={styles.heroBadgeDark}>شفافیت و امنیت تراکنش‌ها</Badge>
            </div>
            <h1 id="finance-hero-heading" className={styles.heroHeading}>
              مدیریت اشتراک آموزشی و رسیدهای مالی
            </h1>
            <p className={styles.heroSubtitle}>
              مشاهده اعتبار باقیمانده بسته آموزشی {selectedChild}، تاریخچه فاکتورها و جزئیات تمدید بدون ابهام یا هزینه‌های پنهان.
            </p>
          </div>
          <div className={styles.heroButtons}>
            <button
              type="button"
              className={styles.heroPrimaryBtn}
              onClick={() => setOpenModal(true)}
            >
              <IconSparkles aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>تمدید یا ارتقای اشتراک</span>
            </button>
            <Link href="/parent" className={styles.heroSecondaryBtn} style={{ textDecoration: "none" }}>
              <IconLaptop aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>بازگشت به نمای کلی</span>
            </Link>
          </div>
        </div>

        <div className={styles.heroGraphicWrapper}>
          <div className={styles.heroGlassPanel}>
            <p className={styles.heroQuoteText}>«شفافیت کامل در کلیه پرداخت‌ها»</p>
            <span className={styles.heroBrandMini}>صدور آنی فاکتور رسمی و ضمانت کیفیت آموزش</span>
            <div className={styles.heroChecklist}>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>اشتراک ۶۵ روزه فعال</span>
              </div>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>پشتیبانی مالی مستقیم</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. KPI Cards */}
      <section className={styles.kpiGrid} aria-label="وضعیت مالی">
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
              <IconShield aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>وضعیت پرداخت</span>
            <span className={styles.kpiValue}>تسویه‌شده</span>
            <span className={styles.kpiSub}>
              <IconCheck aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>بدون بدهی جاری</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle1}`}>
              <IconCheck aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>فاکتورهای رسمی صادرشده</span>
            <span className={styles.kpiValue}>۲ فاکتور</span>
            <span className={styles.kpiSub}>
              <IconClock aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>قابل دانلود پی‌دی‌اف</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle2}`}>
              <IconDocument aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>تضمین بازگشت وجه</span>
            <span className={styles.kpiValue}>۱۴ روز</span>
            <span className={styles.kpiSub}>
              <IconStar aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>سیاست مشتری‌مداری</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle3}`}>
              <IconStar aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>
      </section>

      {/* 3. Invoices List */}
      <section className={styles.cardPanel} aria-label="فاکتورها">
        <div className={styles.panelHeader}>
          <h2 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
            <IconDocument aria-hidden="true" />
            <span>رسیدها و تاریخچه فاکتورهای حساب</span>
          </h2>
          <Badge variant="primary">{filteredTx.length} رسید</Badge>
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
            <span>{filteredTx.length} نتیجه</span>
          </div>
        )}

        <div className={styles.activityList}>
          {filteredTx.map((tx, idx) => (
            <div key={tx.id} className={styles.activityItem}>
              <div className={`${styles.activityIconCircle} ${idx === 0 ? styles.kpiCircle1 : styles.kpiCircle2}`}>
                <IconDocument aria-hidden="true" />
              </div>
              <div className={styles.activityContent} style={{ inlineSize: "100%" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <p className={styles.activityDesc} style={{ fontWeight: "var(--cs-font-weight-bold)", margin: 0 }}>
                    {tx.title}
                  </p>
                  <Badge variant="success">{tx.status}</Badge>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBlockStart: "0.25rem" }}>
                  <span className={styles.activityTime}>شماره فاکتور: {tx.receiptId} • تاریخ: {tx.date}</span>
                  <span style={{ fontSize: "0.75rem", color: "var(--cs-color-brand-primary)", fontWeight: "bold" }}>{tx.amount}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Modal */}
      {openModal && (
        <div className={styles.modalBackdrop} onClick={() => setOpenModal(false)}>
          <div className={styles.modalSheet} onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="finance-modal-title">
            <div className={styles.modalHeader}>
              <h3 id="finance-modal-title" className={styles.modalTitle}>
                <IconShield aria-hidden="true" style={{ color: "var(--cs-color-brand-primary)" }} />
                <span>تمدید اشتراک آموزشی CodeSho</span>
              </h3>
              <button
                type="button"
                className={styles.modalCloseBtn}
                onClick={() => setOpenModal(false)}
                aria-label="بستن"
              >
                <IconClose aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />
              </button>
            </div>

            <p style={{ margin: 0, fontSize: "var(--cs-font-size-body)", color: "var(--cs-color-text-secondary)" }}>
              اشتراک فعلی فرزند شما تا ۶۵ روز آینده معتبر است و کلیه ماژول‌های آموزشی، منتورینگ و بازخورد پروژه‌ها فعال هستند.
            </p>

            <div style={{ display: "flex", justifyContent: "flex-end", marginBlockStart: "var(--cs-space-3)" }}>
              <button
                type="button"
                className={`${styles.actionButton} ${styles.primaryActionButton}`}
                onClick={() => setOpenModal(false)}
              >
                متوجه شدم
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
