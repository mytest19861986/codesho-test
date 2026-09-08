import React, { useState } from "react";

export interface MentorQueueItem {
  id: string;
  assignmentTitle: string;
  assignmentCode: string;
  lessonTitle: string;
  studentName: string;
  content: string;
  state: "submitted" | "under_review" | "reviewed";
  submittedAt: string;
  feedback?: string;
  score?: number;
}

export interface MentorReviewQueueProps {
  submissions: MentorQueueItem[];
  mentorName: string;
  onClaim?: (submissionId: string) => void;
  onSubmitFeedback?: (submissionId: string, feedback: string, score: number) => void;
}

const queueBadgeMap: Record<string, { label: string; bg: string; color: string }> = {
  submitted: { label: "در انتظار بررسی", bg: "#fef3c7", color: "#b45309" },
  under_review: { label: "در حال تصحیح من", bg: "#eff6ff", color: "#1d4ed8" },
  reviewed: { label: "تکمیل و ثبت نمره", bg: "#f0fdf4", color: "#15803d" },
};

export const MentorReviewQueue: React.FC<MentorReviewQueueProps> = ({
  submissions,
  mentorName,
  onClaim,
  onSubmitFeedback,
}) => {
  const [items, setItems] = useState<MentorQueueItem[]>(submissions);
  const [feedbackTexts, setFeedbackTexts] = useState<Record<string, string>>({});
  const [scores, setScores] = useState<Record<string, number>>({});

  const handleClaim = (id: string) => {
    setItems((prev) =>
      prev.map((sub) => (sub.id === id ? { ...sub, state: "under_review" } : sub))
    );
    if (onClaim) onClaim(id);
  };

  const handleComplete = (id: string) => {
    const text = feedbackTexts[id] || "پاسخ مورد تایید است و ساختار کدنویسی دقیق می‌باشد.";
    const score = scores[id] !== undefined ? scores[id] : 100;
    setItems((prev) =>
      prev.map((sub) =>
        sub.id === id ? { ...sub, state: "reviewed", feedback: text, score } : sub
      )
    );
    if (onSubmitFeedback) onSubmitFeedback(id, text, score);
  };

  return (
    <div
      style={{
        background: "var(--cs-color-bg-surface, #ffffff)",
        border: "1px solid var(--cs-color-border-subtle, #e2e8f0)",
        borderRadius: "1rem",
        padding: "1.5rem",
        direction: "rtl",
      }}
      role="region"
      aria-labelledby="mentor-review-queue-heading"
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1.25rem",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <span style={{ fontSize: "1.25rem" }} aria-hidden="true">
            📋
          </span>
          <h3
            id="mentor-review-queue-heading"
            style={{
              margin: 0,
              fontSize: "1.125rem",
              fontWeight: 700,
              color: "var(--cs-color-text-primary, #0f172a)",
            }}
          >
            صف تکالیف و کارتابل بررسی منتور ({mentorName})
          </h3>
        </div>
        <span
          style={{
            fontSize: "0.8125rem",
            color: "var(--cs-color-text-muted, #64748b)",
          }}
        >
          {items.filter((s) => s.state !== "reviewed").length} مورد در انتظار
        </span>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {items.map((sub) => {
          const badge = queueBadgeMap[sub.state] || queueBadgeMap.submitted;
          return (
            <div
              key={sub.id}
              style={{
                border: "1px solid var(--cs-color-border-subtle, #f1f5f9)",
                borderRadius: "0.75rem",
                padding: "1rem",
                background: "var(--cs-color-bg-base, #f8fafc)",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                  marginBottom: "0.75rem",
                }}
              >
                <div>
                  <h4
                    style={{
                      margin: "0 0 0.25rem 0",
                      fontSize: "0.9375rem",
                      fontWeight: 700,
                      color: "var(--cs-color-text-primary, #0f172a)",
                    }}
                  >
                    {sub.assignmentTitle}
                  </h4>
                  <div
                    style={{
                      fontSize: "0.8125rem",
                      color: "var(--cs-color-text-muted, #64748b)",
                      display: "flex",
                      gap: "0.75rem",
                    }}
                  >
                    <span>ارسال‌کننده: {sub.studentName}</span>
                    <span>درس: {sub.lessonTitle}</span>
                    <span>زمان ارسال: {sub.submittedAt}</span>
                  </div>
                </div>
                <span
                  style={{
                    padding: "0.25rem 0.625rem",
                    borderRadius: "9999px",
                    fontSize: "0.75rem",
                    fontWeight: 600,
                    background: badge.bg,
                    color: badge.color,
                  }}
                >
                  {badge.label}
                </span>
              </div>

              {/* Code snippet */}
              <div
                style={{
                  background: "#1e293b",
                  color: "#f8fafc",
                  borderRadius: "0.5rem",
                  padding: "0.75rem",
                  fontFamily: "monospace",
                  fontSize: "0.8125rem",
                  direction: "ltr",
                  textAlign: "left",
                  overflowX: "auto",
                  marginBottom: "0.75rem",
                }}
              >
                <pre style={{ margin: 0 }}>{sub.content}</pre>
              </div>

              {/* Action area */}
              {sub.state === "submitted" && (
                <div style={{ display: "flex", justifyContent: "flex-end" }}>
                  <button
                    onClick={() => handleClaim(sub.id)}
                    style={{
                      padding: "0.375rem 1rem",
                      borderRadius: "0.5rem",
                      border: "none",
                      background: "var(--cs-color-primary, #2563eb)",
                      color: "#ffffff",
                      fontSize: "0.8125rem",
                      fontWeight: 600,
                      cursor: "pointer",
                    }}
                  >
                    شروع بررسی و پذیرش (Claim)
                  </button>
                </div>
              )}

              {sub.state === "under_review" && (
                <div
                  style={{
                    borderTop: "1px dashed var(--cs-color-border-subtle, #e2e8f0)",
                    paddingTop: "0.75rem",
                    marginTop: "0.5rem",
                  }}
                >
                  <label
                    htmlFor={`mentor-feedback-${sub.id}`}
                    style={{
                      display: "block",
                      fontSize: "0.8125rem",
                      fontWeight: 600,
                      marginBottom: "0.375rem",
                      color: "var(--cs-color-text-primary, #0f172a)",
                    }}
                  >
                    ثبت بازخورد آموزشی و نمره:
                  </label>
                  <textarea
                    id={`mentor-feedback-${sub.id}`}
                    rows={2}
                    value={feedbackTexts[sub.id] || ""}
                    onChange={(e) =>
                      setFeedbackTexts((prev) => ({ ...prev, [sub.id]: e.target.value }))
                    }
                    placeholder="نکات قوت، ایرادات و راهنمایی‌های لازم به دانش‌آموز..."
                    style={{
                      width: "100%",
                      padding: "0.5rem",
                      borderRadius: "0.375rem",
                      border: "1px solid var(--cs-color-border-subtle, #cbd5e1)",
                      fontSize: "0.8125rem",
                      marginBottom: "0.5rem",
                      boxSizing: "border-box",
                    }}
                  />
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                      <span style={{ fontSize: "0.8125rem" }}>نمره نهایی (از ۱۰۰):</span>
                      <input
                        type="number"
                        min="0"
                        max="100"
                        value={scores[sub.id] !== undefined ? scores[sub.id] : 100}
                        onChange={(e) =>
                          setScores((prev) => ({
                            ...prev,
                            [sub.id]: parseInt(e.target.value, 10) || 0,
                          }))
                        }
                        style={{
                          width: "60px",
                          padding: "0.25rem 0.5rem",
                          borderRadius: "0.375rem",
                          border: "1px solid #cbd5e1",
                          fontSize: "0.8125rem",
                        }}
                      />
                    </div>
                    <button
                      onClick={() => handleComplete(sub.id)}
                      style={{
                        padding: "0.375rem 1rem",
                        borderRadius: "0.5rem",
                        border: "none",
                        background: "#16a34a",
                        color: "#ffffff",
                        fontSize: "0.8125rem",
                        fontWeight: 600,
                        cursor: "pointer",
                      }}
                    >
                      تایید نهایی و ارسال بازخورد
                    </button>
                  </div>
                </div>
              )}

              {sub.state === "reviewed" && (
                <div
                  style={{
                    background: "#f0fdf4",
                    border: "1px solid #bbf7d0",
                    borderRadius: "0.375rem",
                    padding: "0.5rem 0.75rem",
                    color: "#166534",
                    fontSize: "0.8125rem",
                  }}
                >
                  <strong>بازخورد ثبت‌شده (نمره: {sub.score ?? 100}): </strong>
                  {sub.feedback || "تکمیل و تایید شد."}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
