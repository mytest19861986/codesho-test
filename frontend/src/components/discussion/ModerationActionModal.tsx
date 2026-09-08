import React, { useState } from "react";

interface ModerationActionModalProps {
  isOpen: boolean;
  targetId: string;
  targetType: "THREAD" | "COMMENT";
  targetPreview: string;
  onClose: () => void;
  onConfirmAction: (
    action: "APPROVE" | "FLAG" | "REMOVE" | "RESTORE",
    reason: string,
    note: string
  ) => Promise<void>;
}

export const ModerationActionModal: React.FC<ModerationActionModalProps> = ({
  isOpen,
  targetId,
  targetType,
  targetPreview,
  onClose,
  onConfirmAction,
}) => {
  const [action, setAction] = useState<"APPROVE" | "FLAG" | "REMOVE" | "RESTORE">("APPROVE");
  const [reason, setReason] = useState("");
  const [note, setNote] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reason.trim()) {
      setErrorMsg("ذکر دلیل نظارتی برای ثبت در لاگ ممیزی تغییرناپذیر الزامی است.");
      return;
    }

    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      await onConfirmAction(action, reason, note);
      onClose();
    } catch {
      setErrorMsg("خطا در اعمال اقدام نظارتی.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="moderation-modal-title"
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: "rgba(15, 23, 42, 0.65)",
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
          maxWidth: "540px",
          width: "100%",
          padding: "1.5rem",
          display: "flex",
          flexDirection: "column",
          gap: "1rem",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h2 id="moderation-modal-title" style={{ margin: 0, fontSize: "1.2rem", color: "#0f172a" }}>
            ⚖️ نظارت و ممیزی محتوای آموزشی
          </h2>
          <button
            type="button"
            onClick={onClose}
            style={{ background: "transparent", border: "none", fontSize: "1.2rem", cursor: "pointer" }}
          >
            ✕
          </button>
        </div>

        <div
          style={{
            padding: "0.75rem",
            borderRadius: "0.5rem",
            background: "#f8fafc",
            border: "1px solid #e2e8f0",
            fontSize: "0.85rem",
            color: "#475569",
          }}
        >
          <div>
            <strong>هدف:</strong> {targetType === "THREAD" ? "رشته گفتگو" : "نظر/پاسخ"} (<bdi dir="ltr">{targetId.slice(0, 8)}</bdi>)
          </div>
          <div style={{ marginTop: "0.25rem", fontStyle: "italic" }}>"{targetPreview}"</div>
        </div>

        {errorMsg && (
          <div style={{ padding: "0.5rem", borderRadius: "0.375rem", background: "#fef2f2", color: "#dc2626", fontSize: "0.85rem" }}>
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "0.85rem" }}>
          <div>
            <label htmlFor="moderation-action-select" style={{ display: "block", marginBottom: "0.3rem", fontSize: "0.85rem", fontWeight: 600 }}>
              نوع اقدام:
            </label>
            <select
              id="moderation-action-select"
              value={action}
              onChange={(e) => setAction(e.target.value as "APPROVE" | "FLAG" | "REMOVE" | "RESTORE")}
              style={{ width: "100%", padding: "0.5rem", borderRadius: "0.375rem", border: "1px solid #cbd5e1" }}
            >
              <option value="APPROVE">✓ تأیید و انتشار عمومی (Approve)</option>
              <option value="FLAG">🚩 نشانه‌گذاری جهت بررسی دقیق‌تر (Flag)</option>
              <option value="REMOVE">🗑️ حذف از دید دانش‌آموزان (Remove)</option>
              <option value="RESTORE">↩ بازگردانی توسط استاف (Restore)</option>
            </select>
          </div>

          <div>
            <label htmlFor="moderation-reason-input" style={{ display: "block", marginBottom: "0.3rem", fontSize: "0.85rem", fontWeight: 600 }}>
              دلیل رسمی (الزامی):
            </label>
            <input
              id="moderation-reason-input"
              type="text"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="مثال: انطباق با معیارهای آموزشی کُدشو"
              style={{ width: "100%", padding: "0.5rem", borderRadius: "0.375rem", border: "1px solid #cbd5e1", boxSizing: "border-box" }}
            />
          </div>

          <div>
            <label htmlFor="moderation-note-textarea" style={{ display: "block", marginBottom: "0.3rem", fontSize: "0.85rem", fontWeight: 600 }}>
              یادداشت محرمانه ممیزی (اختیاری):
            </label>
            <textarea
              id="moderation-note-textarea"
              rows={2}
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="یادداشت‌های داخلی منتورها..."
              style={{ width: "100%", padding: "0.5rem", borderRadius: "0.375rem", border: "1px solid #cbd5e1", boxSizing: "border-box" }}
            />
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem", marginTop: "0.5rem" }}>
            <button
              type="button"
              onClick={onClose}
              style={{ padding: "0.4rem 0.8rem", borderRadius: "0.375rem", border: "1px solid #cbd5e1", background: "#ffffff", cursor: "pointer" }}
            >
              انصراف
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              style={{
                padding: "0.4rem 1rem",
                borderRadius: "0.375rem",
                border: "none",
                background: "#0f172a",
                color: "#ffffff",
                cursor: isSubmitting ? "not-allowed" : "pointer",
                fontWeight: 600,
              }}
            >
              {isSubmitting ? "در حال ثبت لاگ..." : "ثبت ممیزی"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
