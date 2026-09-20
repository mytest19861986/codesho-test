"use client";

import { useState } from "react";
import Link from "next/link";
import { mentorAlphaContent as copy } from "@/content/fa/mentor.alpha";
import {
  Badge,
  IconSparkles,
  IconDocument,
  IconLaptop,
  IconCheck,
  IconClock,
  IconShield,
  IconClose,
  IconArrowUp,
} from "@/components/ui";
import { useMentorSearch } from "../MentorSearchContext";
import styles from "../../student/student.module.css";

interface StudentItem {
  id: string;
  name: string;
  grade: string;
  course: string;
  progress: number;
  lastActive: string;
  pendingReviews: number;
  avatar: string;
  status: "active" | "needs_attention" | "completed_module";
}

const initialStudents: StudentItem[] = [
  {
    id: "std-1",
    name: "علی محمدی",
    grade: "پایه دهم ریاضی",
    course: "توسعه فرانت‌اند با جاوااسکریپت",
    progress: 78,
    lastActive: "۳۵ دقیقه پیش",
    pendingReviews: 1,
    avatar: "ع",
    status: "active",
  },
  {
    id: "std-2",
    name: "سارا احمدی",
    grade: "پایه یازدهم تجربی",
    course: "مفاهیم وب و امنیت هویت",
    progress: 65,
    lastActive: "۲ ساعت پیش",
    pendingReviews: 1,
    avatar: "س",
    status: "active",
  },
  {
    id: "std-3",
    name: "رضا اکبری",
    grade: "پایه دهم ریاضی",
    course: "اصول طراحی رابط کاربری دسترسی‌پذیر",
    progress: 90,
    lastActive: "۳ ساعت پیش",
    pendingReviews: 1,
    avatar: "ر",
    status: "completed_module",
  },
  {
    id: "std-4",
    name: "مهسا کریمی",
    grade: "پایه دوازدهم ریاضی",
    course: "طراحی فرم‌ها و اعتبارسنجی مدرن",
    progress: 42,
    lastActive: "دیروز",
    pendingReviews: 1,
    avatar: "م",
    status: "needs_attention",
  },
  {
    id: "std-5",
    name: "حسین باقری",
    grade: "پایه نهم",
    course: "مبانی وب و پایتون مقدماتی",
    progress: 55,
    lastActive: "۲ روز پیش",
    pendingReviews: 0,
    avatar: "ح",
    status: "active",
  },
];

export default function MentorStudentsPage() {
  const o = copy.overview;
  const { searchQuery } = useMentorSearch();
  const [selectedStudent, setSelectedStudent] = useState<StudentItem | null>(null);
  const [openModal, setOpenModal] = useState(false);

  const filteredStudents = initialStudents.filter((s) =>
    s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.course.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.grade.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleOpenStudent = (std: StudentItem) => {
    setSelectedStudent(std);
    setOpenModal(true);
  };

  return (
    <div className={styles.studentDashboard}>
      {/* 1. Hero Banner */}
      <section className={styles.heroBanner} aria-labelledby="students-hero-heading">
        <div className={styles.heroContent}>
          <div className={styles.heroGreeting}>
            <div className={styles.heroBadgeRow}>
              <Badge variant="primary" className={styles.heroBadgeTranslucent}>کارآموزان تحت هدایت</Badge>
              <Badge variant="outline" className={styles.heroBadgeDark}>پایش رشد و توانمندی فنی</Badge>
            </div>
            <h1 id="students-hero-heading" className={styles.heroHeading}>
              فهرست کارآموزان فعال و وضعیت پیشرفت مهارتی
            </h1>
            <p className={styles.heroSubtitle}>
              مشاهده پرونده آموزشی، روند تکمیل تکالیف، آخرین زمان فعالیت و ارزیابی استمرار یادگیری کارآموزان تحت راهبری.
            </p>
          </div>
          <div className={styles.heroButtons}>
            <Link href="/mentor/reviews" className={styles.heroPrimaryBtn} style={{ textDecoration: "none" }}>
              <IconSparkles aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>مشاهده صف بازخوردها</span>
            </Link>
            <Link href="/mentor" className={styles.heroSecondaryBtn} style={{ textDecoration: "none" }}>
              <IconLaptop aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>بازگشت به میز کار</span>
            </Link>
          </div>
        </div>

        <div className={styles.heroGraphicWrapper}>
          <div className={styles.heroGlassPanel}>
            <p className={styles.heroQuoteText}>«هدایت متناسب با توانمندی هر کارآموز»</p>
            <span className={styles.heroBrandMini}>راهبری بدون تبعیض و بدون رتبه‌بندی مقایسه‌ای</span>
            <div className={styles.heroChecklist}>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>پایش نرخ ماندگاری یادگیری</span>
              </div>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>بررسی پروژه‌های تحویلی</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. KPI Cards */}
      <section className={styles.kpiGrid} aria-label="شاخص‌های پایش کارآموزان">
        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>کل کارآموزان فعال</span>
            <span className={styles.kpiValue}>۵ نفر</span>
            <span className={styles.kpiSub}>
              <IconCheck aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>ظرفیت راهبری استاندارد</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle1}`}>
              <IconLaptop aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>میانگین پیشرفت مهارتی</span>
            <span className={styles.kpiValue}>۶۸٪</span>
            <span className={styles.kpiSub}>
              <IconArrowUp aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>+۸٪ در دو هفته گذشته</span>
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
            <span className={styles.kpiLabel}>پروژه‌های در انتظار بازخورد</span>
            <span className={styles.kpiValue}>۴ مورد</span>
            <span className={styles.kpiSub}>
              <IconClock aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>نیازمند رسیدگی امروز</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle3}`}>
              <IconDocument aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>پایبندی به استانداردهای مربیگری</span>
            <span className={styles.kpiValue}>۱۰۰٪</span>
            <span className={styles.kpiSub}>
              <IconShield aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>تاییدیه اخلاق حرفه‌ای</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle4}`}>
              <IconShield aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>
      </section>

      {/* 3. Students List Card */}
      <section className={styles.cardPanel} aria-label="فهرست پرونده کارآموزان">
        <div className={styles.panelHeader}>
          <h2 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
            <IconLaptop aria-hidden="true" />
            <span>پرونده آموزشی و مهارت‌آموزی کارآموزان</span>
          </h2>
          <Badge variant="primary">{filteredStudents.length} کارآموز</Badge>
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
            <span>{filteredStudents.length} نتیجه</span>
          </div>
        )}

        <div className={styles.activityList}>
          {filteredStudents.map((s, idx) => (
            <div
              key={s.id}
              className={styles.activityItem}
              style={{ cursor: "pointer", transition: "background var(--cs-motion-fast)" }}
              onClick={() => handleOpenStudent(s)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") handleOpenStudent(s); }}
              aria-label={`مشاهده وضعیت ${s.name}`}
            >
              <div className={`${styles.activityIconCircle} ${idx % 2 === 0 ? styles.kpiCircle1 : styles.kpiCircle2}`}>
                <span style={{ fontWeight: "bold" }}>{s.avatar}</span>
              </div>
              <div className={styles.activityContent} style={{ inlineSize: "100%" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <p className={styles.activityDesc} style={{ fontWeight: "var(--cs-font-weight-bold)", margin: 0 }}>
                    {s.name} <span style={{ fontSize: "0.75rem", color: "var(--cs-color-text-secondary)" }}>({s.grade})</span>
                  </p>
                  <Badge variant={s.status === "completed_module" ? "success" : s.status === "needs_attention" ? "warning" : "outline"}>
                    {s.status === "completed_module" ? "تکمیل ماژول" : s.status === "needs_attention" ? "نیازمند پیگیری" : "در حال یادگیری"}
                  </Badge>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBlockStart: "0.25rem" }}>
                  <span className={styles.activityTime}>{s.course} • آخرین فعالیت: {s.lastActive}</span>
                  <span style={{ fontSize: "0.75rem", color: "var(--cs-color-brand-primary)", fontWeight: "bold" }}>پیشرفت: {s.progress}٪</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Modal: Student Detail View */}
      {openModal && selectedStudent && (
        <div className={styles.modalBackdrop} onClick={() => setOpenModal(false)}>
          <div className={styles.modalSheet} onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="student-modal-title">
            <div className={styles.modalHeader}>
              <h3 id="student-modal-title" className={styles.modalTitle}>
                <IconLaptop aria-hidden="true" style={{ color: "var(--cs-color-brand-primary)" }} />
                <span>پرونده آموزشی: {selectedStudent.name}</span>
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
                <strong>دوره آموزشی فعال:</strong> <span>{selectedStudent.course}</span>
              </div>
              <div style={{ background: "var(--cs-color-bg-base)", padding: "var(--cs-space-3)", borderRadius: "var(--cs-radius-control)" }}>
                <strong>پایه تحصیلی:</strong> <span>{selectedStudent.grade}</span>
              </div>
              <div style={{ background: "var(--cs-color-bg-base)", padding: "var(--cs-space-3)", borderRadius: "var(--cs-radius-control)" }}>
                <strong>درصد پیشرفت سرفصل‌ها:</strong> <span>{selectedStudent.progress}٪</span>
              </div>
              <div style={{ background: "var(--cs-color-bg-base)", padding: "var(--cs-space-3)", borderRadius: "var(--cs-radius-control)" }}>
                <strong>آخرین بازخورد منتور:</strong> <span>تایید گام Clean Code و رعایت اصول کامپوننت‌نویسی</span>
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
              <Link
                href="/mentor/reviews"
                className={`${styles.actionButton} ${styles.primaryActionButton}`}
                style={{ textDecoration: "none" }}
              >
                بررسی پروژه‌های کارآموز
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
