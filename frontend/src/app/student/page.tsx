"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  IconArrowUp,
  IconBrand,
  IconCalendar,
  IconChart,
  IconCheck,
  IconClose,
  IconDocument,
  IconFile,
  IconFire,
  IconGraduate,
  IconLaptop,
  IconShield,
  IconSparkles,
  IconStar,
  IconTarget,
  IconTrending,
} from "@/components/ui/Icons";
import { studentAlphaContent as copy } from "@/content/fa/student.alpha";
import { getSharedLearningState, SharedLearningState } from "@/data/sharedLearningLoop";
import styles from "./commandCenter.module.css";

export default function StudentDashboardPage() {
  const d = copy.dashboard;

  // Interactive drawer/modal states for live actions
  const [missionModalOpen, setMissionModalOpen] = useState(false);
  const [mentorDrawerOpen, setMentorDrawerOpen] = useState(false);
  const [projectDrawerOpen, setProjectDrawerOpen] = useState(false);
  const [missionCompleted, setMissionCompleted] = useState(false);
  const [loopState, setLoopState] = useState<SharedLearningState>(getSharedLearningState());

  useEffect(() => {
    const handleSync = () => {
      setLoopState(getSharedLearningState());
    };
    window.addEventListener("storage", handleSync);
    return () => window.removeEventListener("storage", handleSync);
  }, []);

  return (
    <div className={styles.commandCenter}>
      {/* 1. Learning Identity Header: Focus on growth story & status, not raw gaming stats */}
      <header className={styles.identityHeader}>
        <div className={styles.identityInfo}>
          <div className={styles.avatarBadge}>
            <IconGraduate className={styles.avatarIcon} />
          </div>
          <div className={styles.identityText}>
            <div className={styles.roleRankRow}>
              <span className={styles.levelTag}>پایتون پیشرفته • Python Explorer</span>
              <span className={styles.studentIdTag}>کد شناسه: CS-9804</span>
            </div>
            <h1 className={styles.welcomeHeading}>سلام علی عزیز؛ به مرکز فرماندهی یادگیری خوش آمدید</h1>
            <p className={styles.journeyNarrative}>
              شما <strong>۷ روز پیوسته</strong> است که با انضباط کدنویسی کرده‌اید. فقط یک چالش مهارتی تا رسیدن به رتبه <strong>Senior Learner</strong> باقی مانده است.
            </p>
          </div>
        </div>

        <div className={styles.identityBadges}>
          <div className={styles.badgeItem}>
            <div className={styles.badgeIconWrapperFire}>
              <IconFire className={styles.fireIcon} />
            </div>
            <div className={styles.badgeDetails}>
              <span className={styles.badgeVal}>۷ روز متوالی</span>
              <span className={styles.badgeLabel}>انضباط تمرین روزانه</span>
            </div>
          </div>

          <div className={styles.badgeItem}>
            <div className={styles.badgeIconWrapperStar}>
              <IconStar className={styles.starIcon} />
            </div>
            <div className={styles.badgeDetails}>
              <span className={styles.badgeVal}>سطح ۳ پیشرفته</span>
              <span className={styles.badgeLabel}>مسیر مهندسی نرم‌افزار</span>
            </div>
          </div>
        </div>
      </header>

      {/* 1.5. Parent Encouragement Ribbon (Cross-Role Journey 3) */}
      {loopState.parentBridge.parentEncouragementSent && (
        <aside className={styles.parentEncouragementBanner} aria-label="پیام تشویقی خانواده">
          <div className={styles.parentEncouragementIcon}>
            <IconStar />
          </div>
          <div className={styles.parentEncouragementContent}>
            <span className={styles.parentEncouragementLabel}>پیام خانواده از رصدخانه والدین:</span>
            <p className={styles.parentEncouragementText}>«{loopState.parentBridge.parentEncouragementMessage}»</p>
          </div>
        </aside>
      )}

      {/* 2. Today's Mission (Heart of the Command Center) */}
      <section className={styles.missionCard} aria-labelledby="mission-heading">
        <div className={styles.missionGlow} />
        <div className={styles.missionHeader}>
          <div className={styles.missionTag}>
            <IconTarget className={styles.missionTagIcon} />
            <span>مأموریت اولویت‌دار امروز</span>
          </div>
          <span className={styles.missionTimeEst}>تخمین زمان: ۲۰ دقیقه • ۵۰ امتیاز مهارت</span>
        </div>

        <div className={styles.missionBody}>
          <div className={styles.missionMain}>
            <h2 id="mission-heading" className={styles.missionTitle}>
              پیاده‌سازی بهینه الگوریتم جستجوی دودویی (Binary Search)
            </h2>
            <p className={styles.missionImportance}>
              <strong>چرا این مأموریت اهمیت دارد؟</strong> تسلط بر جستجوی لگاریتمی O(log n) پایه اساسی طراحی موتورهای جستجوی داده و بهینه‌سازی کوئری‌های مقیاس‌بزرگ در صنعت است.
            </p>

            <div className={styles.mentorHintBox}>
              <div className={styles.mentorHintHeader}>
                <IconSparkles className={styles.mentorHintIcon} />
                <span>راهنمای آغازین AI Mentor:</span>
              </div>
              <p className={styles.mentorHintText}>
                «در نظر داشته باشید که شرط خروج حلقه <code>while low &lt;= high</code> است. حتماً محاسبه نقطه میانی را برای جلوگیری از سرریز حافظه به شکل <code>mid = low + (high - low) // 2</code> بنویسید.»
              </p>
            </div>
          </div>

          <div className={styles.missionActionCol}>
            <button
              type="button"
              id="start-mission-btn"
              className={missionCompleted ? styles.missionBtnDone : styles.missionBtnAction}
              onClick={() => setMissionModalOpen(true)}
            >
              <IconBrand className={styles.btnIcon} />
              <span>{missionCompleted ? "مرور کد مأموریت تکمیل‌شده" : "ورود به محیط کدنویسی مأموریت"}</span>
            </button>
            <div className={styles.missionStatusIndicator}>
              <span className={missionCompleted ? styles.dotDone : styles.dotActive} />
              <span>{missionCompleted ? "مأموریت امروز با موفقیت ثبت شد" : "در انتظار اجرا و کامپایل کد"}</span>
            </div>
          </div>
        </div>
      </section>

      {/* 3. Core Grid: Active Project Workspace + AI Mentor Guidance Panel */}
      <div className={styles.coreGrid}>
        {/* Active Project Workspace */}
        <section className={styles.panelCard} aria-labelledby="project-workspace-heading">
          <header className={styles.panelHeader}>
            <div className={styles.panelTitleWrapper}>
              <IconLaptop className={styles.panelIcon} />
              <h2 id="project-workspace-heading" className={styles.panelTitle}>
                میزکار پروژه فعال (Active Project)
              </h2>
            </div>
            <span className={styles.statusPill}>مرحله ۳ از ۵</span>
          </header>

          <div className={styles.projectCardBody}>
            <div className={styles.projectMainInfo}>
              <h3 className={styles.projectTitle}>{loopState.activeProject.title}</h3>
              <p className={styles.projectDesc}>
                شاخه <code>{loopState.activeProject.branch}</code> • مایل‌استون: {loopState.activeProject.currentMilestone}
              </p>
            </div>

            <div className={styles.milestoneBlock}>
              <div className={styles.milestoneLabelRow}>
                <span>پیشرفت پروژه</span>
                <span className={styles.milestonePct}>{loopState.activeProject.progressPercentage}٪ تکمیل</span>
              </div>
              <div className={styles.progressTrack}>
                <div className={styles.progressBar} style={{ width: `${loopState.activeProject.progressPercentage}%` }} />
              </div>
            </div>

            <div className={styles.reviewStatusRow}>
              <div className={styles.reviewBadge}>
                <IconCheck className={styles.reviewCheckIcon} />
                <span>وضعیت هدایت مربی: {loopState.mentorIntervention.status === "RESOLVED" ? "تأییدشده و حل‌شده" : "در حال بازبینی و نظارت فعال"}</span>
              </div>
              <button
                type="button"
                id="inspect-project-btn"
                className={styles.projectActionBtn}
                onClick={() => setProjectDrawerOpen(true)}
              >
                بررسی لاگ تغییرات پروژه
              </button>
            </div>
          </div>
        </section>

        {/* AI Mentor Dedicated Guidance Panel */}
        <section className={styles.panelCard} aria-labelledby="mentor-panel-heading">
          <header className={styles.panelHeader}>
            <div className={styles.panelTitleWrapper}>
              <IconSparkles className={styles.panelIconAi} />
              <h2 id="mentor-panel-heading" className={styles.panelTitle}>
                یار یادگیری هوشمند (AI Mentor Guidance)
              </h2>
            </div>
            <span className={styles.onlineBadge}>آنلاین و پایشگر</span>
          </header>

          <div className={styles.mentorPanelBody}>
            <div className={styles.mentorSpeechBubble}>
              <div className={styles.mentorSpeechTop}>
                <span className={styles.mentorContextTag}>
                  {loopState.mentorIntervention.feedbacks.length > 0
                    ? `آخرین بازخورد (${loopState.mentorIntervention.feedbacks[0].timestamp})`
                    : "تحلیل آخرین تمرین"}
                </span>
              </div>
              <p className={styles.mentorFeedbackText}>
                «{loopState.mentorIntervention.feedbacks.length > 0
                  ? loopState.mentorIntervention.feedbacks[0].text
                  : loopState.mentorIntervention.recommendedAction}»
              </p>
            </div>

            <div className={styles.mentorActions}>
              <button
                type="button"
                id="open-mentor-dialog-btn"
                className={styles.mentorTalkBtn}
                onClick={() => setMentorDrawerOpen(true)}
              >
                <IconSparkles className={styles.btnMiniIcon} />
                <span>مشاهده توصیه تکمیلی و گفتگو با مربی</span>
              </button>
              <Link href="/student/coaching" className={styles.mentorHistoryLink}>
                تاریخچه جلسات راهنمایی ←
              </Link>
            </div>
          </div>
        </section>
      </div>

      {/* 4. Growth Engine & Skill Progression */}
      <section className={styles.panelCard} aria-labelledby="growth-engine-heading">
        <header className={styles.panelHeader}>
          <div className={styles.panelTitleWrapper}>
            <IconTrending className={styles.panelIcon} />
            <h2 id="growth-engine-heading" className={styles.panelTitle}>
              موتور تسلط بر مهارت‌ها (Skill Mastery Engine)
            </h2>
          </div>
          <Link href="/student/growth" className={styles.viewDetailsLink}>
            مشاهده کارنامه جامع مهارت‌ها
          </Link>
        </header>

        <div className={styles.skillsGrid}>
          <div className={styles.skillItemCard}>
            <div className={styles.skillItemHeader}>
              <span className={styles.skillName}>الگوریتم و حل مسئله</span>
              <span className={styles.skillScore}>۸۵٪ تسلط</span>
            </div>
            <div className={styles.progressTrack}>
              <div className={styles.progressBar} style={{ width: "85%", background: "var(--cs-color-brand-primary)" }} />
            </div>
            <span className={styles.skillInsight}>مرحله بعد: برنامه‌ریزی پویا (DP)</span>
          </div>

          <div className={styles.skillItemCard}>
            <div className={styles.skillItemHeader}>
              <span className={styles.skillName}>پایتون شی‌گرا (OOP)</span>
              <span className={styles.skillScore}>۹۰٪ تسلط</span>
            </div>
            <div className={styles.progressTrack}>
              <div className={styles.progressBar} style={{ width: "90%", background: "#10b981" }} />
            </div>
            <span className={styles.skillInsight}>تسلط کامل بر Inheritance و Polymorphism</span>
          </div>

          <div className={styles.skillItemCard}>
            <div className={styles.skillItemHeader}>
              <span className={styles.skillName}>کدنویسی تمیز و تست‌نویسی</span>
              <span className={styles.skillScore}>۷۲٪ تسلط</span>
            </div>
            <div className={styles.progressTrack}>
              <div className={styles.progressBar} style={{ width: "72%", background: "#f59e0b" }} />
            </div>
            <span className={styles.skillInsight}>توصیه: افزایش پوشش Unit Test در پروژه</span>
          </div>
        </div>
      </section>

      {/* Interactive Modal: Mission Code Workspace */}
      {missionModalOpen ? (
        <div className={styles.modalOverlay} role="dialog" aria-modal="true">
          <div className={styles.modalBox}>
            <div className={styles.modalHeader}>
              <div className={styles.modalTitleRow}>
                <IconLaptop className={styles.modalIcon} />
                <h3>محیط اجرای مأموریت: پیاده‌سازی Binary Search</h3>
              </div>
              <button
                type="button"
                className={styles.closeBtn}
                onClick={() => setMissionModalOpen(false)}
                aria-label="بستن پنجره"
              >
                <IconClose />
              </button>
            </div>
            <div className={styles.modalBody}>
              <div className={styles.codeEditorSimulation}>
                <p className={styles.editorComment}># مأموریت روزانه: تابع جستجوی دودویی را تکمیل کنید</p>
                <p>def binary_search(arr, target):</p>
                <p>&nbsp;&nbsp;&nbsp;&nbsp;low, high = 0, len(arr) - 1</p>
                <p>&nbsp;&nbsp;&nbsp;&nbsp;while low &lt;= high:</p>
                <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;mid = low + (high - low) // 2</p>
                <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if arr[mid] == target: return mid</p>
                <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;elif arr[mid] &lt; target: low = mid + 1</p>
                <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else: high = mid - 1</p>
                <p>&nbsp;&nbsp;&nbsp;&nbsp;return -1</p>
              </div>
              <div className={styles.simulationFeedback}>
                <IconCheck className={styles.feedbackCheck} />
                <span>تحلیل خودکار سینتکس: کامپایل موفق بدون خطا | تست با آرایه مرتب پاس شد.</span>
              </div>
            </div>
            <div className={styles.modalFooter}>
              <button
                type="button"
                className={styles.submitCodeBtn}
                onClick={() => {
                  setMissionCompleted(true);
                  setMissionModalOpen(false);
                }}
              >
                تأیید و ارسال نهایی مأموریت
              </button>
              <button
                type="button"
                className={styles.cancelBtn}
                onClick={() => setMissionModalOpen(false)}
              >
                بستن
              </button>
            </div>
          </div>
        </div>
      ) : null}

      {/* Interactive Drawer: AI Mentor Feedback Detail */}
      {mentorDrawerOpen ? (
        <div className={styles.modalOverlay} role="dialog" aria-modal="true">
          <div className={styles.drawerBox}>
            <div className={styles.modalHeader}>
              <div className={styles.modalTitleRow}>
                <IconSparkles className={styles.modalIcon} />
                <h3>تحلیل تخصصی AI Mentor</h3>
              </div>
              <button
                type="button"
                className={styles.closeBtn}
                onClick={() => setMentorDrawerOpen(false)}
                aria-label="بستن"
              >
                <IconClose />
              </button>
            </div>
            <div className={styles.modalBody}>
              <p className={styles.drawerSectionTitle}>نکات بهینه‌سازی الگوریتمی:</p>
              <ul className={styles.drawerList}>
                <li>استفاده از ساختارهای داده‌ای متناسب با نیاز O(1) به جای آرایه‌های متغیر.</li>
                <li>پیاده‌سازی مدیریت استثنا (Exception Handling) جهت جلوگیری از توقف برنامه در ورودی‌های نامعتبر.</li>
                <li>تمرین پیشنهادی بعدی: حل چالش چرخش آرایه مرتب (Rotated Array Search).</li>
              </ul>
            </div>
            <div className={styles.modalFooter}>
              <button
                type="button"
                className={styles.submitCodeBtn}
                onClick={() => setMentorDrawerOpen(false)}
              >
                متوجه شدم؛ بازگشت به داشبورد
              </button>
            </div>
          </div>
        </div>
      ) : null}

      {/* Interactive Drawer: Project Inspection */}
      {projectDrawerOpen ? (
        <div className={styles.modalOverlay} role="dialog" aria-modal="true">
          <div className={styles.drawerBox}>
            <div className={styles.modalHeader}>
              <div className={styles.modalTitleRow}>
                <IconLaptop className={styles.modalIcon} />
                <h3>لاگ وضعیت پروژه: ربات تحلیل داده ورزشی</h3>
              </div>
              <button
                type="button"
                className={styles.closeBtn}
                onClick={() => setProjectDrawerOpen(false)}
                aria-label="بستن"
              >
                <IconClose />
              </button>
            </div>
            <div className={styles.modalBody}>
              <div className={styles.timelineItem}>
                <span className={styles.timelineDate}>امروز</span>
                <p>مرحله ۳: ثبت و تأیید توابع تمیزکاری داده‌ها (Data Cleaning Pipeline).</p>
              </div>
              <div className={styles.timelineItem}>
                <span className={styles.timelineDate}>۲ روز پیش</span>
                <p>مرحله ۲: اتصال به وب‌سوکت شبیه‌سازی حسگر و دریافت داده‌های خام.</p>
              </div>
              <div className={styles.timelineItem}>
                <span className={styles.timelineDate}>۵ روز پیش</span>
                <p>مرحله ۱: ایجاد ساختار ریپازیتوری و تعریف معماری ماژولار پروژه.</p>
              </div>
            </div>
            <div className={styles.modalFooter}>
              <button
                type="button"
                className={styles.submitCodeBtn}
                onClick={() => setProjectDrawerOpen(false)}
              >
                بستن پنجره بازرسی
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
