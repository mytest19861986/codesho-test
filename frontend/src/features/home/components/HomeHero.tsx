import {
  IconBrand,
  IconChart,
  IconCheck,
  IconFire,
  IconLaptop,
  IconSparkles,
  IconStar,
  IconTarget,
} from "@/components/ui/Icons";
import type { HomepageAlphaContent } from "../home.types";
import styles from "./homeHero.module.css";

export interface HomeHeroProps {
  readonly content: HomepageAlphaContent["hero"];
}

export function HomeHero({ content }: HomeHeroProps) {
  const actions = [content.primaryAction, content.secondaryAction].filter(
    (action) => action.destination.status === "available",
  );

  return (
    <section aria-labelledby="homepage-hero-title" className={styles.hero}>
      <div className={styles.copy}>
        <div className={styles.badge}>
          <IconSparkles className={styles.badgeIcon} />
          <span>{content.eyebrow}</span>
        </div>
        <h1 className={styles.title} id="homepage-hero-title">
          {content.title}
        </h1>
        <p className={styles.description}>{content.description}</p>
        {actions.length > 0 ? (
          <div className={styles.actions}>
            {actions.map((action, idx) => (
              <a
                className={idx === 0 ? styles.actionPrimary : styles.actionSecondary}
                href={action.destination.route}
                key={action.id}
              >
                {action.label}
              </a>
            ))}
          </div>
        ) : null}

        <div className={styles.trustBadges}>
          <div className={styles.trustItem}>
            <IconCheck className={styles.trustCheck} />
            <span>منتورینگ اختصاصی هوش مصنوعی</span>
          </div>
          <div className={styles.trustItem}>
            <IconCheck className={styles.trustCheck} />
            <span>پروژه‌های استاندارد صنعت</span>
          </div>
          <div className={styles.trustItem}>
            <IconCheck className={styles.trustCheck} />
            <span>پایش پیوسته برای اولیا</span>
          </div>
        </div>
      </div>

      {/* Live Interactive Learning Platform Mockup replacing generic robot image */}
      <div className={styles.media}>
        <div className={styles.mockupContainer} aria-label="داشبورد تعاملی آموزش و کدنویسی کدشو">
          {/* Mockup Header / Window Controls */}
          <div className={styles.windowHeader}>
            <div className={styles.windowDots}>
              <span className={styles.dotRed} />
              <span className={styles.dotYellow} />
              <span className={styles.dotGreen} />
            </div>
            <div className={styles.windowTitle}>
              <IconBrand className={styles.brandMiniIcon} />
              <span>CodeSho Workspace — Live AI Pair Session</span>
            </div>
            <div className={styles.liveStatus}>
              <span className={styles.statusPulse} />
              <span>AI Online</span>
            </div>
          </div>

          {/* Mockup Main Workspace Grid */}
          <div className={styles.workspaceBody}>
            {/* Left: Code Editor Pane */}
            <div className={styles.editorPane}>
              <div className={styles.paneHeader}>
                <IconLaptop className={styles.paneIcon} />
                <span>main.py — پروژه تحلیل داده دانش‌آموز</span>
              </div>
              <div className={styles.codeSnippet}>
                <p><span className={styles.kw}>async def</span> <span className={styles.fn}>analyze_student_growth</span>(learner_id):</p>
                <p>&nbsp;&nbsp;skills = <span className={styles.kw}>await</span> tracker.get_mastery(learner_id)</p>
                <p>&nbsp;&nbsp;<span className={styles.comment}># AI Mentor feedback integrated in real-time</span></p>
                <p>&nbsp;&nbsp;feedback = mentor.evaluate_code(skills.latest_patch)</p>
                <p>&nbsp;&nbsp;<span className={styles.kw}>return</span> feedback.next_challenge()</p>
              </div>

              {/* Real-time Telemetry Bar */}
              <div className={styles.editorFooter}>
                <span className={styles.syntaxOk}>
                  <IconCheck className={styles.smallIcon} /> سینتکس معتبر
                </span>
                <span className={styles.testOk}>
                  <IconTarget className={styles.smallIcon} /> تمام تست‌ها پاس شدند
                </span>
              </div>
            </div>

            {/* Right: AI Mentor & Mastery Widget */}
            <div className={styles.assistantPane}>
              <div className={styles.mentorCard}>
                <div className={styles.mentorHeader}>
                  <div className={styles.mentorAvatar}>
                    <IconSparkles className={styles.sparkleIcon} />
                  </div>
                  <div>
                    <h2 className={styles.mentorName}>AI Mentor Feedback</h2>
                    <p className={styles.mentorSubtitle}>همراه یادگیری در لحظه</p>
                  </div>
                </div>
                <div className={styles.mentorMessage}>
                  <p>«کد شما بسیار بهینه است! الگوریتم مرتب‌سازی با پیچیدگی زمانی O(n log n) پیاده‌سازی شده. برای چالش بعد آماده‌اید؟»</p>
                </div>
              </div>

              {/* Progress & Growth Mini-Stats */}
              <div className={styles.progressCard}>
                <div className={styles.progressItem}>
                  <div className={styles.statLabel}>
                    <IconChart className={styles.statIcon} />
                    <span>روند تسلط الگوریتمی</span>
                  </div>
                  <div className={styles.progressBarWrapper}>
                    <div className={styles.progressBar} style={{ width: "88%" }} />
                  </div>
                  <span className={styles.statVal}>۸۸٪</span>
                </div>

                <div className={styles.metricRow}>
                  <div className={styles.metricBadge}>
                    <IconFire className={styles.fireIcon} />
                    <span>۱۴ روز زنجیره تمرین</span>
                  </div>
                  <div className={styles.metricBadge}>
                    <IconStar className={styles.starIcon} />
                    <span>سطح ۴ پیشرفته</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
