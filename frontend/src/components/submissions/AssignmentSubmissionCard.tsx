import React, { useState } from "react";

export interface AssignmentItem {
  id: string;
  code: string;
  title: string;
  lessonTitle: string;
  dueDate: string;
  maxScore: number;
  submissionState: "draft" | "submitted" | "under_review" | "reviewed";
  currentContent?: string;
  feedback?: string;
  score?: number;
}

export interface AssignmentSubmissionCardProps {
  assignments: AssignmentItem[];
  onSubmitSolution?: (assignmentId: string, content: string) => void;
}

const stateBadgeMap: Record<string, { label: string; bg: string; color: string }> = {
  draft: { label: "پیش‌نویس", bg: "#f1f5f9", color: "#475569" },
  submitted: { label: "تحویل داده شده", bg: "#eff6ff", color: "#1d4ed8" },
  under_review: { label: "در حال بررسی منتور", bg: "#fef3c7", color: "#b45309" },
  reviewed: { label: "تصحیح شده و تایید نهایی", bg: "#f0fdf4", color: "#15803d" },
};

export const AssignmentSubmissionCard: React.FC<AssignmentSubmissionCardProps> = ({
  assignments,
  onSubmitSolution,
}) => {
  const [selectedId, setSelectedId] = useState<string>(assignments[0]?.id || "");
  const [contentDrafts, setContentDrafts] = useState<Record<string, string>>({});
  const [submittedStatus, setSubmittedStatus] = useState<Record<string, boolean>>({});

  const activeAssignment = assignments.find((a) => a.id === selectedId) || assignments[0];

  const handleTextChange = (id: string, text: string) => {
    setContentDrafts((prev) => ({ ...prev, [id]: text }));
  };

  const handleSubmit = (id: string) => {
    const text = contentDrafts[id] || activeAssignment?.currentContent || "";
    if (!text.trim()) return;
    setSubmittedStatus((prev) => ({ ...prev, [id]: true }));
    if (onSubmitSolution) {
      onSubmitSolution(id, text);
    }
  };

  if (!assignments || assignments.length === 0) {
    return (
      <div
        style={{
          background: "var(--cs-color-bg-surface, #ffffff)",
          border: "1px solid var(--cs-color-border-subtle, #e2e8f0)",
          borderRadius: "1rem",
          padding: "1.5rem",
          direction: "rtl",
          textAlign: "center",
          color: "var(--cs-color-text-muted, #64748b)",
        }}
      >
        هیچ تکلیفی در حال حاضر وجود ندارد.
      </div>
    );
  }

  const isAlreadySubmitted =
    submittedStatus[activeAssignment.id] ||
    activeAssignment.submissionState === "submitted" ||
    activeAssignment.submissionState === "under_review" ||
    activeAssignment.submissionState === "reviewed";

  const badge = stateBadgeMap[activeAssignment.submissionState] || stateBadgeMap.draft;

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
      aria-labelledby="student-assignments-heading"
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
            📝
          </span>
          <h3
            id="student-assignments-heading"
            style={{
              margin: 0,
              fontSize: "1.125rem",
              fontWeight: 700,
              color: "var(--cs-color-text-primary, #0f172a)",
            }}
          >
            تکالیف و پروژه‌های عملی من
          </h3>
        </div>
        <span
          style={{
            fontSize: "0.8125rem",
            color: "var(--cs-color-text-muted, #64748b)",
          }}
        >
          {assignments.length} تکلیف فعال
        </span>
      </div>

      {/* Tabs */}
      <div
        style={{
          display: "flex",
          gap: "0.5rem",
          marginBottom: "1.25rem",
          overflowX: "auto",
          paddingBottom: "0.25rem",
        }}
        role="tablist"
        aria-label="فهرست تکالیف"
      >
        {assignments.map((asgn) => {
          const isSelected = asgn.id === activeAssignment.id;
          return (
            <button
              key={asgn.id}
              role="tab"
              aria-selected={isSelected}
              onClick={() => setSelectedId(asgn.id)}
              style={{
                padding: "0.5rem 0.875rem",
                borderRadius: "0.5rem",
                border: isSelected
                  ? "1px solid var(--cs-color-primary, #2563eb)"
                  : "1px solid var(--cs-color-border-subtle, #e2e8f0)",
                background: isSelected
                  ? "var(--cs-color-primary-subtle, #eff6ff)"
                  : "var(--cs-color-bg-base, #f8fafc)",
                color: isSelected
                  ? "var(--cs-color-primary, #2563eb)"
                  : "var(--cs-color-text-secondary, #334155)",
                fontWeight: isSelected ? 700 : 500,
                fontSize: "0.875rem",
                cursor: "pointer",
                whiteSpace: "nowrap",
                transition: "all 0.15s ease",
              }}
            >
              {asgn.title}
            </button>
          );
        })}
      </div>

      {/* Active Assignment Details & Submission Box */}
      <div
        style={{
          border: "1px solid var(--cs-color-border-subtle, #f1f5f9)",
          borderRadius: "0.75rem",
          padding: "1.25rem",
          background: "var(--cs-color-bg-base, #f8fafc)",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            marginBottom: "1rem",
          }}
        >
          <div>
            <h4
              style={{
                margin: "0 0 0.375rem 0",
                fontSize: "1rem",
                fontWeight: 700,
                color: "var(--cs-color-text-primary, #0f172a)",
              }}
            >
              {activeAssignment.title}
            </h4>
            <div
              style={{
                fontSize: "0.8125rem",
                color: "var(--cs-color-text-muted, #64748b)",
                display: "flex",
                gap: "1rem",
              }}
            >
              <span>درس مربوطه: {activeAssignment.lessonTitle}</span>
              <span>مهلت تحویل: {activeAssignment.dueDate}</span>
              <span>حداکثر نمره: {activeAssignment.maxScore}</span>
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

        {/* Feedback Display if Reviewed */}
        {activeAssignment.feedback && (
          <div
            style={{
              margin: "1rem 0",
              padding: "1rem",
              background: "#f0fdf4",
              border: "1px solid #bbf7d0",
              borderRadius: "0.5rem",
              color: "#166534",
            }}
          >
            <div style={{ fontWeight: 700, marginBottom: "0.25rem" }}>
              بازخورد منتور (نمره دریافت شده: {activeAssignment.score ?? 100} از {activeAssignment.maxScore}):
            </div>
            <div style={{ fontSize: "0.875rem" }}>{activeAssignment.feedback}</div>
          </div>
        )}

        {/* Text Area for Submission */}
        <div style={{ marginTop: "1rem" }}>
          <label
            htmlFor={`solution-input-${activeAssignment.id}`}
            style={{
              display: "block",
              fontSize: "0.875rem",
              fontWeight: 600,
              marginBottom: "0.5rem",
              color: "var(--cs-color-text-primary, #0f172a)",
            }}
          >
            پاسخ یا کد راهکار شما:
          </label>
          <textarea
            id={`solution-input-${activeAssignment.id}`}
            rows={4}
            disabled={isAlreadySubmitted}
            value={
              contentDrafts[activeAssignment.id] !== undefined
                ? contentDrafts[activeAssignment.id]
                : activeAssignment.currentContent || ""
            }
            onChange={(e) => handleTextChange(activeAssignment.id, e.target.value)}
            placeholder="کد یا توضیحات پاسخ خود را در این بخش وارد نمایید..."
            style={{
              width: "100%",
              padding: "0.75rem",
              borderRadius: "0.5rem",
              border: "1px solid var(--cs-color-border-subtle, #cbd5e1)",
              fontFamily: "monospace",
              fontSize: "0.875rem",
              direction: "ltr",
              textAlign: "left",
              background: isAlreadySubmitted ? "#f8fafc" : "#ffffff",
              color: "#0f172a",
              boxSizing: "border-box",
            }}
          />
        </div>

        {/* Submit Button */}
        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            marginTop: "1rem",
          }}
        >
          <button
            onClick={() => handleSubmit(activeAssignment.id)}
            disabled={isAlreadySubmitted}
            style={{
              padding: "0.5rem 1.25rem",
              borderRadius: "0.5rem",
              border: "none",
              background: isAlreadySubmitted ? "#94a3b8" : "var(--cs-color-primary, #2563eb)",
              color: "#ffffff",
              fontWeight: 600,
              fontSize: "0.875rem",
              cursor: isAlreadySubmitted ? "not-allowed" : "pointer",
              transition: "background 0.15s ease",
            }}
          >
            {isAlreadySubmitted ? "پاسخ ثبت شده است ✓" : "ارسال نهایی تکلیف"}
          </button>
        </div>
      </div>
    </div>
  );
};
