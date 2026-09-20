"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  IconGraduate,
  IconSparkles,
  IconCheck,
  IconLaptop,
  IconShield,
  IconTrending,
  IconClose,
  IconChat,
  IconTarget,
  IconStar,
  IconFire,
} from "@/components/ui/Icons";
import { getSharedLearningState, updateSharedLearningState, SharedLearningState } from "@/data/sharedLearningLoop";
import styles from "./observatory.module.css";

interface ChildProfile {
  id: string;
  name: string;
  grade: string;
  level: string;
  growthStatus: string;
  briefingHeadline: string;
  observation: string;
  insight: string;
  parentAction: string;
  activeProjectTitle: string;
  activeProjectDesc: string;
  activeProjectProgress: number;
  activeProjectMilestone: string;
  safetyMetrics: {
    title: string;
    desc: string;
    status: string;
  }[];
  skills: {
    pillar: string;
    score: number;
    meaning: string;
  }[];
}

const childProfiles: Record<string, ChildProfile> = {
  ali: {
    id: "ali",
    name: "علی محمدی",
    grade: "پایه دهم ریاضی",
    level: "پایتون پیشرفته • مهندسی نرم‌افزار",
    growthStatus: "در حال اوج‌گیری و پیشرفت مستمر • انگیزه بالا",
    briefingHeadline: "پشت سر گذاشتن موفق چالش الگوریتم‌های پیچیده",
    observation: "علی در هفته جاری روی بهینه‌سازی الگوریتم‌های جستجو و ساختارهای داده کار کرد و بدون تسلیم شدن، باگ محاسباتی را برطرف نمود.",
    insight: "قدرت حل مسئله و تاب‌آوری او در مواجهه با چالش‌های فنی دشوار رشد چشمگیری داشته است.",
    parentAction: "امشب از او بخواهید معماری پروژه ربات ورزشی‌اش را برایتان توضیح دهد؛ گوش دادن به استدلال او اعتمادبه‌نفسش را تثبیت می‌کند.",
    activeProjectTitle: "ربات هوشمند تحلیل داده‌های ورزشی (Python Data Engine)",
    activeProjectDesc: "توسعه خط لوله تمیزکاری و فیلتر داده‌های حسگرهای حرکتی با معماری شی‌گرا و ماژولار.",
    activeProjectProgress: 70,
    activeProjectMilestone: "پیاده‌سازی موفق فیلترهای آماری O(1)",
    safetyMetrics: [
      {
        title: "تعادل ساعات یادگیری",
        desc: "تمرین‌ها در ساعات عصر انجام شده و هیچ فعالیت فشرده شبانه ثبت نشده است.",
        status: "کاملاً سالم و متوازن",
      },
      {
        title: "حریم خصوصی و تعاملات",
        desc: "محیط مکالمات با مربی کاملاً پایش‌شده، امن و در چهارچوب اخلاقی سامانه است.",
        status: "ایزوله و محافظت‌شده",
      },
      {
        title: "بهداشت دیجیتال و تمرکز",
        desc: "پایداری یادگیری پیوسته بدون پرش مکرر بین تب‌ها یا حواس‌پرتی بصری.",
        status: "تمرکز عالی (۹۴٪)",
      },
    ],
    skills: [
      {
        pillar: "حل مسئله و تفکر تحلیلی",
        score: 85,
        meaning: "تسلط بر تفکیک مسائل بزرگ به گام‌های کوچک الگوریتمی",
      },
      {
        pillar: "پشتکار و تعهد به اتمام",
        score: 92,
        meaning: "تکمیل منظم مأموریت‌های روزانه بدون وقفه تحصیلی",
      },
      {
        pillar: "طراحی ساختاریافته (مهندسی)",
        score: 80,
        meaning: "رعایت استانداردهای کدنویسی تمیز و نام‌گذاری استاندارد",
      },
    ],
  },
  maryam: {
    id: "maryam",
    name: "مریم محمدی",
    grade: "پایه هفتم",
    level: "برنامه‌نویسی مقدماتی و وب • خلاقیت دیجیتال",
    growthStatus: "در مرحله کشف استعداد و شکوفایی خلاقیت",
    briefingHeadline: "خلق اولین صفحه وب تعاملی و داستان‌گویی دیجیتال",
    observation: "مریم با ترکیب رنگ‌ها و استایل‌های CSS توانست یک صفحه وب جذاب برای معرفی حیوانات خانگی طراحی کند.",
    insight: "ارتباط میان هنر بصری و منطق کدنویسی به خوبی در ذهن او شکل گرفته و شوق یادگیری بسیار بالایی دارد.",
    parentAction: "صفحه وبی که مریم طراحی کرده را در گوشی خود با هم ببینید و خلاقیت او را در انتخاب تم بصری تحسین کنید.",
    activeProjectTitle: "آلبوم تعاملی دانشنامه طبیعت (HTML & Modern CSS)",
    activeProjectDesc: "طراحی رابط کاربری ریسپانسیو با انیمیشن‌های CSS و چیدمان مدرن Flexbox.",
    activeProjectProgress: 60,
    activeProjectMilestone: "ایجاد کارت‌های تعاملی و استایل‌های هاور",
    safetyMetrics: [
      {
        title: "تعادل ساعات یادگیری",
        desc: "میانگین روزانه ۳۵ دقیقه تمرین مفید بدون خستگی چشم.",
        status: "بسیار متناسب با رده سنی",
      },
      {
        title: "حریم خصوصی و تعاملات",
        desc: "پرتال کودک و نوجوان با محافظت حداکثری و تاییدیه سرپرست.",
        status: "امنیت کامل",
      },
      {
        title: "شادی و نشاط یادگیری",
        desc: "بازخوردهای ثبت‌شده حاکی از تجربه لذت‌بخش و بدون استرس است.",
        status: "نشاط کامل",
      },
    ],
    skills: [
      {
        pillar: "خلاقیت و ذوق بصری",
        score: 90,
        meaning: "استفاده هارمونیک از رنگ‌ها و هارمونی المان‌های بصری",
      },
      {
        pillar: "دقت در جزییات و نظم",
        score: 78,
        meaning: "بستن صحیح تگ‌ها و ساختاربندی تمیز درخت DOM",
      },
      {
        pillar: "کنجکاوی در کشف ابزارها",
        score: 88,
        meaning: "علاقه به آزمایش ویژگی‌های جدید CSS و افکت‌های مدرن",
      },
    ],
  },
};

export default function ParentDashboardPage() {
  const [selectedChildKey, setSelectedChildKey] = useState<"ali" | "maryam">("ali");
  const child = childProfiles[selectedChildKey];

  // Interactive drawer and modal states
  const [encourageModalOpen, setEncourageModalOpen] = useState(false);
  const [mentorDrawerOpen, setMentorDrawerOpen] = useState(false);
  const [projectDrawerOpen, setProjectDrawerOpen] = useState(false);

  // Encouragement interaction state
  const [customMsg, setCustomMsg] = useState("");
  const [msgSent, setMsgSent] = useState(false);
  const [loopState, setLoopState] = useState<SharedLearningState>(getSharedLearningState());

  useEffect(() => {
    const handleSync = () => {
      setLoopState(getSharedLearningState());
    };
    window.addEventListener("storage", handleSync);
    return () => window.removeEventListener("storage", handleSync);
  }, []);

  const presets = [
    `«${child.name} عزیز، تلاش و پشتکار این هفته‌ات در حل چالش‌ها واقعاً برای من الهام‌بخش بود. بهت افتخار می‌کنم!»`,
    `«خداقوت قهرمان من! پیشرفت پروژه‌ات رو دیدم، امشب با اشتیاق منتظرم برام توضیح بدی چطور ساختیش.»`,
    `«استمرار و انضباط روزانه‌ات نشان از آینده درخشانت دارد. همیشه پشتت هستم!»`,
  ];

  const handleSendEncouragement = () => {
    const messageToSend = customMsg.trim() || presets[0];
    if (selectedChildKey === "ali") {
      updateSharedLearningState((prev) => ({
        ...prev,
        parentBridge: {
          ...prev.parentBridge,
          parentEncouragementSent: true,
          parentEncouragementMessage: messageToSend,
        },
      }));
    }
    setMsgSent(true);
    setTimeout(() => {
      setMsgSent(false);
      setEncourageModalOpen(false);
      setCustomMsg("");
    }, 1800);
  };

  return (
    <div className={styles.observatory}>
      {/* 1. Child Anchor & Growth Snapshot */}
      <header className={styles.childGrowthHeader}>
        <div className={styles.childGrowthInfo}>
          <div className={styles.childAvatar}>
            <IconGraduate className={styles.childAvatarIcon} />
          </div>
          <div className={styles.childDetails}>
            <div className={styles.childPillsRow}>
              <span className={styles.childTag}>{child.grade} • {child.level}</span>
              <span className={styles.safetyIndicatorTag}>{child.growthStatus}</span>
            </div>
            <h1 className={styles.childNameHeading}>رصدخانه رشد تحصیلی {child.name}</h1>
            <p className={styles.growthSummaryText}>
              نگاهی جامع به روند یادگیری، سلامت روان و دستاوردهای فرزند شما با نظارت مربیان CodeSho.
            </p>
          </div>
        </div>

        {/* Ergonomic Touch Tabs to switch between children */}
        <div className={styles.childTabsControl} role="tablist" aria-label="انتخاب فرزند">
          <button
            type="button"
            role="tab"
            aria-selected={selectedChildKey === "ali"}
            className={`${styles.childTabBtn} ${selectedChildKey === "ali" ? styles.childTabActive : ""}`}
            onClick={() => setSelectedChildKey("ali")}
          >
            علی (پایه دهم)
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={selectedChildKey === "maryam"}
            className={`${styles.childTabBtn} ${selectedChildKey === "maryam" ? styles.childTabActive : ""}`}
            onClick={() => setSelectedChildKey("maryam")}
          >
            مریم (پایه هفتم)
          </button>
        </div>
      </header>

      {/* 2. Weekly Mentor Briefing (Hero of Observatory) */}
      <section className={styles.mentorBriefingCard} aria-labelledby="briefing-heading">
        <div className={styles.briefingGlow} />
        <div className={styles.briefingHeader}>
          <div className={styles.briefingTag}>
            <IconSparkles className={styles.briefingTagIcon} />
            <span>گزارش هفتگی مربی (Weekly Mentor Briefing)</span>
          </div>
          <span className={styles.briefingDate}>
            {selectedChildKey === "ali" && loopState.parentBridge.briefingTimestamp
              ? `به‌روزرسانی: ${loopState.parentBridge.briefingTimestamp} • منتور ارشد`
              : "به‌روزرسانی: دیروز ساعت ۲۰:۰۰ • منتور ارشد"}
          </span>
        </div>

        <div className={styles.briefingBody}>
          <div className={styles.briefingMain}>
            <h2 id="briefing-heading" className={styles.briefingHeadline}>
              {child.briefingHeadline}
            </h2>

            <div className={styles.observationStepBlock}>
              <div className={styles.observationRow}>
                <IconCheck className={`${styles.stepIcon} ${styles.stepIconBlue}`} />
                <div>
                  <span className={styles.observationLabel}>مشاهده عینی مربی:</span>
                  <span className={styles.observationVal}>
                    {selectedChildKey === "ali" && loopState.parentBridge.lastBriefing
                      ? loopState.parentBridge.lastBriefing
                      : child.observation}
                  </span>
                </div>
              </div>

              <div className={styles.observationRow}>
                <IconStar className={`${styles.stepIcon} ${styles.stepIconYellow}`} />
                <div>
                  <span className={styles.observationLabel}>تحلیل مهارتی و رشد:</span>
                  <span className={styles.observationVal}>{child.insight}</span>
                </div>
              </div>

              <div className={styles.observationRow}>
                <IconFire className={`${styles.stepIcon} ${styles.stepIconGreen}`} />
                <div>
                  <span className={styles.observationLabel}>اقدام پیشنهادی برای والد:</span>
                  <span className={styles.observationVal}><strong>{child.parentAction}</strong></span>
                </div>
              </div>
            </div>
          </div>

          <div className={styles.briefingActionCol}>
            <button
              type="button"
              id="open-encourage-modal-btn"
              className={styles.encourageBtnAction}
              onClick={() => setEncourageModalOpen(true)}
            >
              <IconChat className={styles.briefingTagIcon} />
              <span>ارسال پیام تحسین و تشویق به فرزند</span>
            </button>
            <button
              type="button"
              id="open-mentor-briefing-btn"
              className={styles.viewBriefingDetailBtn}
              onClick={() => setMentorDrawerOpen(true)}
            >
              مشاهده یادداشت تکمیلی مربی
            </button>
          </div>
        </div>
      </section>

      {/* 3. Core Grid: Active Project Observatory + Healthy Habits Guard */}
      <div className={styles.coreGrid}>
        {/* Active Project Observatory */}
        <section className={styles.panelCard} aria-labelledby="project-obs-heading">
          <header className={styles.panelHeader}>
            <div className={styles.panelTitleWrapper}>
              <IconLaptop className={styles.panelIcon} />
              <h2 id="project-obs-heading" className={styles.panelTitle}>
                رصدخانه پروژه‌های واقعی (Project Lens)
              </h2>
            </div>
            <span className={styles.statusBadge}>پروژه فعال</span>
          </header>

          <div className={styles.projectObservatoryBody}>
            <h3 className={styles.projectHeadline}>{child.activeProjectTitle}</h3>
            <p className={styles.projectExplanation}>{child.activeProjectDesc}</p>

            <div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", marginBottom: "0.375rem" }}>
                <span style={{ color: "#475569" }}>مرحله: {child.activeProjectMilestone}</span>
                <span style={{ fontWeight: 700, color: "#0284c7" }}>{child.activeProjectProgress}٪ تکمیل</span>
              </div>
              <div className={styles.progressTrack}>
                <div className={styles.progressBar} style={{ width: `${child.activeProjectProgress}%` }} />
              </div>
            </div>

            <div className={styles.evidenceActionRow}>
              <span style={{ fontSize: "0.75rem", color: "#059669", fontWeight: 600 }}>
                شواهد فنی تأییدشده در مخزن
              </span>
              <button
                type="button"
                id="inspect-project-evidence-btn"
                className={styles.evidenceBtn}
                onClick={() => setProjectDrawerOpen(true)}
              >
                بررسی شواهد و دستاورد پروژه
              </button>
            </div>
          </div>
        </section>

        {/* Safety & Healthy Habits Guard */}
        <section className={styles.panelCard} aria-labelledby="health-guard-heading">
          <header className={styles.panelHeader}>
            <div className={styles.panelTitleWrapper}>
              <IconShield className={styles.panelIconShield} />
              <h2 id="health-guard-heading" className={styles.panelTitle}>
                پایش سلامت یادگیری و امنیت (Healthy Habits)
              </h2>
            </div>
            <span className={styles.statusBadge}>امنیت تأییدشده</span>
          </header>

          <div className={styles.healthGuardBody}>
            {child.safetyMetrics.map((m, idx) => (
              <div key={idx} className={styles.healthMetricItem}>
                <div className={styles.healthMetricLabel}>
                  <span className={styles.healthMetricTitle}>{m.title}</span>
                  <span className={styles.healthMetricDesc}>{m.desc}</span>
                </div>
                <span className={styles.healthMetricStatus}>{m.status}</span>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* 4. Skill Development Map */}
      <section className={styles.panelCard} aria-labelledby="skills-map-heading">
        <header className={styles.panelHeader}>
          <div className={styles.panelTitleWrapper}>
            <IconTrending className={styles.panelIcon} />
            <h2 id="skills-map-heading" className={styles.panelTitle}>
              نقشه رشد مهارت‌های بنیادین (Skill Development Map)
            </h2>
          </div>
          <span style={{ fontSize: "0.75rem", color: "#64748b" }}>
            سنجش مهارت‌ها بر مبنای خروجی کار عملی
          </span>
        </header>

        <div className={styles.skillsMapGrid}>
          {child.skills.map((s, idx) => (
            <div key={idx} className={styles.skillPillarCard}>
              <div className={styles.skillPillarHeader}>
                <span>{s.pillar}</span>
                <span className={styles.skillPillarScore}>{s.score}٪ تسلط</span>
              </div>
              <div className={styles.progressTrack}>
                <div className={styles.progressBar} style={{ width: `${s.score}%` }} />
              </div>
              <span className={styles.skillPillarMeaning}>{s.meaning}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Interactive Modal 1: Encouragement Sender */}
      {encourageModalOpen && (
        <div className={styles.modalOverlay} role="dialog" aria-modal="true" aria-labelledby="encourage-modal-title">
          <div className={styles.modalBox}>
            <div className={styles.modalHeader}>
              <div className={styles.modalTitleRow}>
                <IconChat className={styles.modalIcon} />
                <h3 id="encourage-modal-title">ارسال پیام حمایت و تشویق برای {child.name}</h3>
              </div>
              <button
                type="button"
                className={styles.closeBtn}
                onClick={() => setEncourageModalOpen(false)}
                aria-label="بستن پنجره"
              >
                <IconClose />
              </button>
            </div>

            <div className={styles.modalBody}>
              {msgSent ? (
                <div className={styles.sentSuccessBanner}>
                  پیام محبت‌آمیز شما با موفقیت در مرکز فرماندهی یادگیری فرزند ثبت و نمایش داده شد.
                </div>
              ) : (
                <>
                  <p style={{ margin: 0, fontSize: "0.8125rem", color: "#475569" }}>
                    یک پیام از پیش‌آماده را انتخاب کنید یا دل‌نوشته شخصی خود را برای فرزندتان بنویسید:
                  </p>

                  <div className={styles.encouragementPresetList}>
                    {presets.map((p, i) => (
                      <button
                        key={i}
                        type="button"
                        className={styles.presetBtn}
                        onClick={() => setCustomMsg(p)}
                      >
                        {p}
                      </button>
                    ))}
                  </div>

                  <textarea
                    id="encourage-msg-input"
                    className={styles.customTextarea}
                    placeholder="یا متن دلخواه خود را اینجا تایپ کنید..."
                    value={customMsg}
                    onChange={(e) => setCustomMsg(e.target.value)}
                  />
                </>
              )}
            </div>

            <div className={styles.modalFooter}>
              {!msgSent && (
                <>
                  <button
                    type="button"
                    id="submit-encourage-btn"
                    className={styles.sendActionBtn}
                    onClick={handleSendEncouragement}
                  >
                    ارسال به داشبورد فرزند
                  </button>
                  <button
                    type="button"
                    className={styles.cancelBtn}
                    onClick={() => setEncourageModalOpen(false)}
                  >
                    انصراف
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Interactive Drawer 2: Mentor Briefing Detail */}
      {mentorDrawerOpen && (
        <div className={styles.modalOverlay} role="dialog" aria-modal="true" aria-labelledby="drawer-mentor-title">
          <div className={styles.drawerBox}>
            <div className={styles.modalHeader}>
              <div className={styles.modalTitleRow}>
                <IconSparkles className={styles.modalIcon} />
                <h3 id="drawer-mentor-title">یادداشت تفصیلی مربی برای اولیا</h3>
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
              <div style={{ fontSize: "0.8125rem", color: "#334155", lineHeight: 1.6, display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                <p><strong>والد گرامی،</strong></p>
                <p>
                  در شیوه آموزشی CodeSho، ارزش یادگیری در مواجهه با چالش‌های فنی نهفته است. در تمرین‌های این هفته، {child.name} با صبر و تمرکز، خطاهای کامپایلر را تحلیل کرد و به جای درخواست کمک زودهنگام، منطق را خودش بازنویسی نمود.
                </p>
                <div style={{ background: "#f8fafc", padding: "0.75rem", borderRadius: "0.5rem", border: "1px solid #e2e8f0" }}>
                  <strong>پیشنهاد مربی برای گفتگوی خانوادگی:</strong>
                  <p style={{ margin: "0.375rem 0 0 0" }}>
                    از ایجاد حس رقابت یا مقایسه با دیگران خودداری فرمایید؛ تمرکز روی بهبود مستمر خود دانش‌آموز باعث تثبیت انگیزه درونی در برنامه‌نویسی می‌شود.
                  </p>
                </div>
              </div>
            </div>

            <div className={styles.modalFooter}>
              <button
                type="button"
                className={styles.sendActionBtn}
                onClick={() => setMentorDrawerOpen(false)}
              >
                متوجه شدم؛ بازگشت
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Interactive Drawer 3: Project Evidence Drawer */}
      {projectDrawerOpen && (
        <div className={styles.modalOverlay} role="dialog" aria-modal="true" aria-labelledby="drawer-project-title">
          <div className={styles.drawerBox}>
            <div className={styles.modalHeader}>
              <div className={styles.modalTitleRow}>
                <IconLaptop className={styles.modalIcon} />
                <h3 id="drawer-project-title">دستاوردها و شواهد ملموس پروژه</h3>
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
              <div style={{ fontSize: "0.8125rem", color: "#334155", lineHeight: 1.6, display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                <div style={{ borderInlineStart: "3px solid #0284c7", paddingInlineStart: "0.75rem" }}>
                  <strong>مسئله و صورت پروژه:</strong>
                  <p style={{ margin: 0 }}>پردازش داده‌های سرعت و کالری حسگرها و استخراج الگوهای رفتاری کاربر.</p>
                </div>

                <div style={{ borderInlineStart: "3px solid #059669", paddingInlineStart: "0.75rem" }}>
                  <strong>راه‌حل ساخته‌شده توسط دانش‌آموز:</strong>
                  <p style={{ margin: 0 }}>پیاده‌سازی کلاس‌های مستقل، مدیریت استثناها و بهینه‌سازی سرعت واکشی داده‌ها.</p>
                </div>

                <div style={{ borderInlineStart: "3px solid #f59e0b", paddingInlineStart: "0.75rem" }}>
                  <strong>مهارت تقویت‌شده در دنیای واقعی:</strong>
                  <p style={{ margin: 0 }}>توانایی درک داده‌های عددی مقیاس بزرگ و تفکر معماری ماژولار.</p>
                </div>
              </div>
            </div>

            <div className={styles.modalFooter}>
              <button
                type="button"
                className={styles.sendActionBtn}
                onClick={() => setProjectDrawerOpen(false)}
              >
                بستن پنجره شواهد
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
