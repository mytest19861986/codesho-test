import React, { useState } from "react";

interface DiscussionReplyComposerProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (title: string, body: string, scopeType: "COHORT" | "LESSON") => Promise<void>;
  defaultScopeType?: "COHORT" | "LESSON";
  scopeTitle?: string;
}

export const DiscussionReplyComposer: React.FC<DiscussionReplyComposerProps> = ({
  isOpen,
  onClose,
  onSubmit,
  defaultScopeType = "COHORT",
  scopeTitle = "کوهورت جاری",
}) => {
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [scopeType, setScopeType] = useState<"COHORT" | "LESSON">(defaultScopeType);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !body.trim()) {
      setErrorMsg("لطفاً عنوان و متن پرسش را وارد فرمایید.");
      return;
    }

    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      await onSubmit(title, body, scopeType);
      setTitle("");
      setBody("");
      onClose();
    } catch {
      setErrorMsg("خطا در ایجاد پرسش. لطفاً ورودی‌های خود را بررسی نمایید.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="composer-modal-title"
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: "rgba(15, 23, 42, 0.6)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 9999,
        padding: "1rem",
        direction: "rtl",
      }}
    >
      <div
        style={{
          background: "#ffffff",
          borderRadius: "1rem",
          maxWidth: "600px",
          width: "100%",
          padding: "1.75rem",
          display: "flex",
          flexDirection: "column",
          gap: "1.25rem",
          boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h2 id="composer-modal-title" style={{ margin: 0, fontSize: "1.25rem", color: "#0f172a" }}>
            ✨ ایجاد گفتگو یا پرسش جدید
          </h2>
          <button
            type="button"
            onClick={onClose}
            style={{
              background: "transparent",
              border: "none",
              fontSize: "1.25rem",
              cursor: "pointer",
              color: "#64748b",
            }}
          >
            ✕
          </button>
        </div>

        <div
          style={{
            padding: "0.75rem 1rem",
            borderRadius: "0.5rem",
            background: "#eff6ff",
            border: "1px solid #bfdbfe",
            fontSize: "0.85rem",
            color: "#1e40af",
            lineHeight: 1.5,
          }}
        >
          🛡️ <strong>راهنمای تعامل جمعی کُدشو:</strong> پرسش شما پس از ارسال در حالت بررسی امنیتی قرار گرفته و برای هم‌کلاسی‌ها نمایش داده می‌شود. لطفاً از اشتراک‌گذاری اطلاعات شخصی خودداری نمایید.
        </div>

        {errorMsg && (
          <div
            style={{
              padding: "0.5rem 0.75rem",
              borderRadius: "0.375rem",
              background: "#fef2f2",
              border: "1px solid #fecaca",
              color: "#dc2626",
              fontSize: "0.85rem",
            }}
          >
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <div>
            <label
              htmlFor="thread-scope-select"
              style={{ display: "block", marginBottom: "0.35rem", fontSize: "0.9rem", fontWeight: 600, color: "#334155" }}
            >
              دامنه گفتگو:
            </label>
            <select
              id="thread-scope-select"
              value={scopeType}
              onChange={(e) => setScopeType(e.target.value as "COHORT" | "LESSON")}
              style={{
                width: "100%",
                padding: "0.6rem 0.75rem",
                borderRadius: "0.5rem",
                border: "1px solid #cbd5e1",
                fontSize: "0.9rem",
                fontFamily: "inherit",
              }}
            >
              <option value="COHORT">تالار گفتگوی کوهورت ({scopeTitle})</option>
              <option value="LESSON">پرسش و پاسخ مرتبط با درس جاری</option>
            </select>
          </div>

          <div>
            <label
              htmlFor="thread-title-input"
              style={{ display: "block", marginBottom: "0.35rem", fontSize: "0.9rem", fontWeight: 600, color: "#334155" }}
            >
              عنوان پرسش یا موضوع گفتگو:
            </label>
            <input
              id="thread-title-input"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="مثال: روش بهینه‌سازی حلقه بازگشتی در تمرین ۳"
              style={{
                width: "100%",
                padding: "0.6rem 0.75rem",
                borderRadius: "0.5rem",
                border: "1px solid #cbd5e1",
                fontSize: "0.9rem",
                fontFamily: "inherit",
                boxSizing: "border-box",
              }}
            />
          </div>

          <div>
            <label
              htmlFor="thread-body-textarea"
              style={{ display: "block", marginBottom: "0.35rem", fontSize: "0.9rem", fontWeight: 600, color: "#334155" }}
            >
              شرح کامل سؤال یا مسئله:
            </label>
            <textarea
              id="thread-body-textarea"
              rows={5}
              value={body}
              onChange={(e) => setBody(e.target.value)}
              placeholder="توضیحات، خطاهای مشاهده‌شده، یا نمونه کد مورد نظر را اینجا بنویسید..."
              style={{
                width: "100%",
                padding: "0.6rem 0.75rem",
                borderRadius: "0.5rem",
                border: "1px solid #cbd5e1",
                fontSize: "0.9rem",
                fontFamily: "inherit",
                resize: "vertical",
                boxSizing: "border-box",
              }}
            />
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.75rem", marginTop: "0.5rem" }}>
            <button
              type="button"
              onClick={onClose}
              style={{
                padding: "0.5rem 1rem",
                borderRadius: "0.5rem",
                border: "1px solid #cbd5e1",
                background: "#ffffff",
                color: "#475569",
                cursor: "pointer",
                fontWeight: 600,
                fontSize: "0.9rem",
              }}
            >
              انصراف
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              style={{
                padding: "0.5rem 1.25rem",
                borderRadius: "0.5rem",
                border: "none",
                background: isSubmitting ? "#cbd5e1" : "#0284c7",
                color: "#ffffff",
                cursor: isSubmitting ? "not-allowed" : "pointer",
                fontWeight: 600,
                fontSize: "0.9rem",
              }}
            >
              {isSubmitting ? "در حال ثبت..." : "ارسال برای بررسی"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
