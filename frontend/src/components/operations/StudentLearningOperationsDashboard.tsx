"use client";

import React, { useState } from "react";
import styles from "./operations.module.css";

export interface ReflectionItem {
  id: string;
  promptType: string;
  content: string;
  moodSentiment: string;
  createdAt: string;
  mentorFeedback?: string;
}

export interface GoalItem {
  id: string;
  title: string;
  domain: string;
  status: "DRAFT" | "ACTIVE" | "ACHIEVED" | "PAUSED" | "ARCHIVED" | "SUPERSEDED";
  actionSteps: { order: number; text: string; completed: boolean }[];
}

export interface GrowthSuggestionItem {
  id: string;
  action: string;
  rationale: string;
  evidenceCode: string;
  status: string;
}

interface StudentLearningOperationsDashboardProps {
  studentName?: string;
  reflections: ReflectionItem[];
  goals: GoalItem[];
  suggestions: GrowthSuggestionItem[];
  onSubmitReflection?: (content: string, promptType: string) => void;
}

export const StudentLearningOperationsDashboard: React.FC<StudentLearningOperationsDashboardProps> = ({
  studentName = "دانش‌آموز کوشا",
  reflections,
  goals,
  suggestions,
  onSubmitReflection,
}) => {
  const [reflectionText, setReflectionText] = useState("");
  const [promptType, setPromptType] = useState("WEEKLY_REVIEW");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!reflectionText.trim()) return;
    if (onSubmitReflection) {
      onSubmitReflection(reflectionText, promptType);
      setReflectionText("");
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "ACTIVE":
        return <span className={`${styles.badge} ${styles.badgeActive}`}>فعال در حال یادگیری</span>;
      case "ACHIEVED":
        return <span className={`${styles.badge} ${styles.badgeSuccess}`}>دستیابی موفق</span>;
      case "PAUSED":
        return <span className={`${styles.badge} ${styles.badgePaused}`}>مکث بدون قضاوت</span>;
      default:
        return <span className={`${styles.badge}`}>{status}</span>;
    }
  };

  return (
    <div className={styles.container} data-testid="p3-vs14-operations-dashboard">
      <header className={styles.header}>
        <h1 className={styles.title}>عملیات یادگیری، بازتاب فردی و اهداف رشد</h1>
        <p className={styles.subtitle}>
          فضای امن و اختصاصی {studentName} برای ثبت تأملات یادگیری، گام‌های عملیاتی هدف‌گذاری شخصی و دریافت پیشنهادات کمکی رشد بدون هرگونه رتبه‌بندی کلاسی.
        </p>
      </header>

      <div className={styles.gridTwoCol}>
        {/* Column 1: Learning Reflection Journal */}
        <section className={styles.card} aria-labelledby="reflection-heading">
          <div className={styles.cardHeader}>
            <h2 id="reflection-heading" className={styles.cardTitle}>
              ژورنال بازتاب یادگیری (Reflection Journal)
            </h2>
            <span className={`${styles.badge} ${styles.badgeSuccess}`}>عاملیت ۱۰۰٪ یادگیرنده</span>
          </div>

          <form onSubmit={handleSubmit} className={styles.formGroup}>
            <label htmlFor="reflection-type" className={styles.label}>
              محور بازتاب یادگیری
            </label>
            <select
              id="reflection-type"
              className={styles.textarea}
              style={{ minHeight: "44px", height: "44px", padding: "0 0.75rem" }}
              value={promptType}
              onChange={(e) => setPromptType(e.target.value)}
            >
              <option value="WEEKLY_REVIEW">بازنگری هفتگی یادگیری</option>
              <option value="MILESTONE_RETROSPECTIVE">عطف به مایلستون و تسلط جدید</option>
              <option value="OBSTACLE_ANALYSIS">تحلیل چالش و نحوه عبور از موانع</option>
              <option value="FREE_REFLECTION">بازتاب آزادانه و خودارزیابی</option>
            </select>

            <label htmlFor="reflection-content" className={styles.label} style={{ marginTop: "1rem" }}>
              متن تأمل و تحلیل شخصی شما
            </label>
            <textarea
              id="reflection-content"
              className={styles.textarea}
              placeholder="در این مرحله چه مفهومی را عمیق‌تر درک کردید؟ چه موانعی بود و چگونه حل کردید؟..."
              value={reflectionText}
              onChange={(e) => setReflectionText(e.target.value)}
              required
            />

            <button type="submit" className={styles.primaryBtn} style={{ marginTop: "1rem" }}>
              ثبت بازتاب در ژورنال شخصی
            </button>
          </form>

          <div className={styles.reflectionList} style={{ marginTop: "2rem" }}>
            {reflections.map((refl) => (
              <article key={refl.id} className={styles.reflectionItem}>
                <div className={styles.reflectionMeta}>
                  <span>محور: {refl.promptType}</span>
                  <span>{refl.createdAt}</span>
                </div>
                <p className={styles.reflectionContent}>{refl.content}</p>
                {refl.mentorFeedback && (
                  <aside
                    style={{
                      marginTop: "1rem",
                      padding: "0.75rem 1rem",
                      background: "#eff6ff",
                      borderRadius: "0.75rem",
                      borderRight: "3px solid #3b82f6",
                    }}
                  >
                    <strong style={{ display: "block", color: "#1d4ed8", fontSize: "0.875rem", marginBottom: "0.25rem" }}>
                      بازخورد ارزنده‌ی مربی:
                    </strong>
                    <span style={{ fontSize: "0.875rem", color: "#1e3a8a" }}>{refl.mentorFeedback}</span>
                  </aside>
                )}
              </article>
            ))}
          </div>
        </section>

        {/* Column 2: Personal Goals & AI Suggestions */}
        <section className={styles.card} aria-labelledby="goals-heading">
          <div className={styles.cardHeader}>
            <h2 id="goals-heading" className={styles.cardTitle}>
              اهداف یادگیری شخصی و طرح‌های اقدام
            </h2>
            <span className={`${styles.badge} ${styles.badgeActive}`}>حداکثر ۵ هدف همزمان</span>
          </div>

          <div className={styles.goalList}>
            {goals.map((goal) => (
              <div key={goal.id} className={styles.goalItem}>
                <div className={styles.goalHeader}>
                  <h3 className={styles.goalTitle}>{goal.title}</h3>
                  {getStatusBadge(goal.status)}
                </div>
                <div style={{ fontSize: "0.8125rem", color: "#64748b", marginBottom: "0.5rem" }}>
                  دامنه: <bdi className={styles.bidiWrapper} dir="ltr">{goal.domain}</bdi>
                </div>
                {goal.actionSteps.length > 0 && (
                  <div className={styles.actionStepList}>
                    {goal.actionSteps.map((step) => (
                      <div key={step.order} className={styles.actionStep}>
                        <span>گام {step.order}: {step.text}</span>
                        <span>{step.completed ? "✅ انجام شد" : "⏳ در جریان"}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* AI-Assisted Non-Authoritative Suggestions Box */}
          {suggestions.length > 0 && (
            <aside className={styles.suggestionBox} aria-label="پیشنهادات دستیار هوشمند رشد">
              <div className={styles.suggestionHeader}>
                <h3 style={{ fontSize: "1.0625rem", fontWeight: 700, color: "#86198f" }}>
                  پیشنهاد هوشمند کمکی برای رشد
                </h3>
                <span className={`${styles.badge} ${styles.badgeAdvisory}`}>غیرمقتدر و مشورتی (Advisory)</span>
              </div>
              {suggestions.map((sugg) => (
                <div key={sugg.id} style={{ marginBottom: "1rem" }}>
                  <p className={styles.suggestionAction}>💡 اقدام پیشنهادی: {sugg.action}</p>
                  <p className={styles.suggestionRationale}>{sugg.rationale}</p>
                  <div style={{ fontSize: "0.8125rem", color: "#a21caf", marginTop: "0.5rem" }}>
                    مبنای استنادی (Explainable Code): <bdi className={styles.bidiWrapper} dir="ltr">{sugg.evidenceCode}</bdi>
                  </div>
                </div>
              ))}
            </aside>
          )}
        </section>
      </div>
    </div>
  );
};
