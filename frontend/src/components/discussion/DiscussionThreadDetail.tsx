import React, { useState } from "react";
import { DiscussionThreadItem } from "./DiscussionThreadList";

export interface DiscussionCommentItem {
  id: string;
  threadId: string;
  parentId: string | null;
  authorId: string;
  body: string;
  status: "PENDING" | "APPROVED" | "FLAGGED" | "REMOVED";
  isMentorEndorsed: boolean;
  endorsedById: string | null;
  endorsedAt: string | null;
  createdAt: string;
}

interface DiscussionThreadDetailProps {
  thread: DiscussionThreadItem;
  comments: DiscussionCommentItem[];
  currentUserId: string;
  currentUserRole: "STUDENT" | "MENTOR" | "STAFF" | "ADMIN";
  onAddReply: (body: string, parentId?: string) => Promise<void>;
  onEndorseComment?: (commentId: string) => Promise<void>;
  onPinThread?: (isPinned: boolean) => Promise<void>;
  onModerate?: (action: "APPROVE" | "FLAG" | "REMOVE" | "RESTORE", targetId: string, isComment: boolean) => void;
  onBackToList?: () => void;
}

export const DiscussionThreadDetail: React.FC<DiscussionThreadDetailProps> = ({
  thread,
  comments,
  currentUserId,
  currentUserRole,
  onAddReply,
  onEndorseComment,
  onPinThread,
  onModerate,
  onBackToList,
}) => {
  const [replyBody, setReplyBody] = useState("");
  const [replyingToParentId, setReplyingToParentId] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submissionFeedback, setSubmissionFeedback] = useState<string | null>(null);

  const canModerate = ["MENTOR", "STAFF", "ADMIN"].includes(currentUserRole);

  const handleSubmitReply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!replyBody.trim()) return;

    setIsSubmitting(true);
    setSubmissionFeedback(null);
    try {
      await onAddReply(replyBody, replyingToParentId || undefined);
      setReplyBody("");
      setReplyingToParentId(null);
      setSubmissionFeedback("پاسخ شما با موفقیت ارسال شد و پس از تأیید تیم آموزش برای هم‌کلاسی‌ها نمایش داده می‌شود.");
    } catch {
      setSubmissionFeedback("خطا در ارسال پاسخ. لطفاً مجدداً تلاش فرمایید.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Group comments into parent -> children (2-level hierarchy)
  const rootComments = comments.filter((c) => !c.parentId);
  const getChildReplies = (parentId: string) => comments.filter((c) => c.parentId === parentId);

  return (
    <article
      aria-labelledby="thread-detail-title"
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "1.25rem",
        direction: "rtl",
        width: "100%",
      }}
    >
      {onBackToList && (
        <button
          type="button"
          onClick={onBackToList}
          style={{
            alignSelf: "flex-start",
            padding: "0.4rem 0.8rem",
            borderRadius: "0.375rem",
            border: "1px solid #cbd5e1",
            background: "#ffffff",
            cursor: "pointer",
            fontSize: "0.85rem",
            color: "#475569",
          }}
        >
          ← بازگشت به لیست گفتگوها
        </button>
      )}

      {/* Main Thread Card */}
      <div
        style={{
          padding: "1.5rem",
          borderRadius: "1rem",
          background: "#ffffff",
          border: "1px solid #e2e8f0",
          display: "flex",
          flexDirection: "column",
          gap: "1rem",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
            {thread.isPinned && (
              <span
                style={{
                  fontSize: "0.8rem",
                  padding: "0.2rem 0.6rem",
                  borderRadius: "0.375rem",
                  background: "#fef3c7",
                  color: "#92400e",
                  fontWeight: 700,
                }}
              >
                📌 پین‌شده توسط منتور
              </span>
            )}
            {thread.status === "PENDING" && (
              <span
                style={{
                  fontSize: "0.8rem",
                  padding: "0.2rem 0.6rem",
                  borderRadius: "0.375rem",
                  background: "#ffedd5",
                  color: "#c2410c",
                  fontWeight: 700,
                }}
              >
                ⏳ در انتظار تأیید ایمنی محتوا
              </span>
            )}
            {thread.isLocked && (
              <span
                style={{
                  fontSize: "0.8rem",
                  padding: "0.2rem 0.6rem",
                  borderRadius: "0.375rem",
                  background: "#f1f5f9",
                  color: "#475569",
                  fontWeight: 700,
                }}
              >
                🔒 رشته بسته شده است
              </span>
            )}
            <span
              style={{
                fontSize: "0.8rem",
                padding: "0.2rem 0.6rem",
                borderRadius: "0.375rem",
                background: "#e0f2fe",
                color: "#0369a1",
              }}
            >
              {thread.scopeType === "COHORT" ? "کوهورت" : "درس"}:{" "}
              <bdi dir="ltr">{thread.scopeTitle}</bdi>
            </span>
          </div>

          {canModerate && (
            <div style={{ display: "flex", gap: "0.5rem" }}>
              {onPinThread && (
                <button
                  type="button"
                  onClick={() => onPinThread(!thread.isPinned)}
                  style={{
                    padding: "0.35rem 0.75rem",
                    borderRadius: "0.375rem",
                    border: "1px solid #cbd5e1",
                    background: "#ffffff",
                    fontSize: "0.8rem",
                    cursor: "pointer",
                  }}
                >
                  {thread.isPinned ? "حذف پین" : "📌 پین به بالا"}
                </button>
              )}
              {onModerate && thread.status === "PENDING" && (
                <button
                  type="button"
                  onClick={() => onModerate("APPROVE", thread.id, false)}
                  style={{
                    padding: "0.35rem 0.75rem",
                    borderRadius: "0.375rem",
                    border: "none",
                    background: "#16a34a",
                    color: "#ffffff",
                    fontSize: "0.8rem",
                    cursor: "pointer",
                    fontWeight: 600,
                  }}
                >
                  ✓ تأیید و انتشار
                </button>
              )}
            </div>
          )}
        </div>

        <h1 id="thread-detail-title" style={{ margin: 0, fontSize: "1.35rem", color: "#0f172a" }}>
          {thread.title}
        </h1>

        <div
          style={{
            fontSize: "0.95rem",
            color: "#334155",
            lineHeight: 1.7,
            whiteSpace: "pre-wrap",
            background: "#f8fafc",
            padding: "1rem",
            borderRadius: "0.5rem",
            border: "1px solid #f1f5f9",
          }}
        >
          {thread.body}
        </div>

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            fontSize: "0.8rem",
            color: "#64748b",
            borderTop: "1px solid #f1f5f9",
            paddingTop: "0.75rem",
          }}
        >
          <span>
            نویسنده: <bdi dir="ltr">{thread.authorId.slice(0, 8)}...</bdi>
          </span>
          <span>تاریخ ایجاد: {thread.createdAt}</span>
        </div>
      </div>

      {/* Reply Input Form */}
      {!thread.isLocked && (
        <form
          onSubmit={handleSubmitReply}
          style={{
            padding: "1.25rem",
            borderRadius: "0.75rem",
            background: "#ffffff",
            border: "1px solid #e2e8f0",
            display: "flex",
            flexDirection: "column",
            gap: "0.75rem",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <label htmlFor="reply-composer-textarea" style={{ fontWeight: 700, fontSize: "0.95rem", color: "#0f172a" }}>
              {replyingToParentId ? "💬 ارسال پاسخ در زیر پیام منتخب" : "✍️ افزودن پاسخ جدید به گفتگو"}
            </label>
            {replyingToParentId && (
              <button
                type="button"
                onClick={() => setReplyingToParentId(null)}
                style={{
                  background: "transparent",
                  border: "none",
                  color: "#ef4444",
                  fontSize: "0.8rem",
                  cursor: "pointer",
                }}
              >
                انصراف از پاسخ مستقیم ✕
              </button>
            )}
          </div>

          <p style={{ margin: 0, fontSize: "0.8rem", color: "#64748b" }}>
            🛡️ یادآوری ایمنی: پاسخ‌ها ابتدا در وضعیت «در انتظار تأیید» قرار می‌گیرند تا استانداردهای آموزشی رعایت گردد.
          </p>

          <textarea
            id="reply-composer-textarea"
            rows={3}
            value={replyBody}
            onChange={(e) => setReplyBody(e.target.value)}
            placeholder="پاسخ یا تحلیل خود را با رعایت احترام و اصول آموزشی بنویسید..."
            style={{
              padding: "0.75rem",
              borderRadius: "0.5rem",
              border: "1px solid #cbd5e1",
              fontSize: "0.9rem",
              fontFamily: "inherit",
              resize: "vertical",
              outline: "none",
            }}
          />

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            {submissionFeedback && (
              <span style={{ fontSize: "0.85rem", color: "#16a34a", fontWeight: 600 }}>
                {submissionFeedback}
              </span>
            )}
            <button
              type="submit"
              disabled={isSubmitting || !replyBody.trim()}
              style={{
                marginRight: "auto",
                padding: "0.5rem 1.25rem",
                borderRadius: "0.5rem",
                background: isSubmitting || !replyBody.trim() ? "#cbd5e1" : "#0284c7",
                color: "#ffffff",
                border: "none",
                fontWeight: 600,
                fontSize: "0.9rem",
                cursor: isSubmitting || !replyBody.trim() ? "not-allowed" : "pointer",
              }}
            >
              {isSubmitting ? "در حال ارسال..." : "ارسال پاسخ"}
            </button>
          </div>
        </form>
      )}

      {/* Comment Tree Hierarchy (2 Levels) */}
      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <h2 style={{ margin: "0.5rem 0 0 0", fontSize: "1.1rem", color: "#0f172a" }}>
          نظرات و پاسخ‌های هم‌کلاسی‌ها ({comments.length})
        </h2>

        {rootComments.length === 0 ? (
          <div style={{ padding: "1.5rem", textAlign: "center", background: "#f8fafc", borderRadius: "0.5rem", color: "#64748b", fontSize: "0.9rem" }}>
            هنوز پاسخی به این پرسش ثبت نشده است. شما اولین پاسخ را بنویسید!
          </div>
        ) : (
          rootComments.map((root) => {
            const childReplies = getChildReplies(root.id);
            return (
              <div
                key={root.id}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "0.75rem",
                  padding: "1rem 1.25rem",
                  borderRadius: "0.75rem",
                  background: root.isMentorEndorsed ? "#f0fdf4" : "#ffffff",
                  border: root.isMentorEndorsed ? "1px solid #86efac" : "1px solid #e2e8f0",
                }}
              >
                {/* Root Comment Header */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    {root.isMentorEndorsed && (
                      <span
                        style={{
                          fontSize: "0.75rem",
                          padding: "0.15rem 0.5rem",
                          borderRadius: "0.25rem",
                          background: "#dcfce7",
                          color: "#166534",
                          fontWeight: 700,
                        }}
                      >
                        ✓ تأییدشده توسط منتور به عنوان پاسخ الگو
                      </span>
                    )}
                    {root.status === "PENDING" && (
                      <span
                        style={{
                          fontSize: "0.75rem",
                          padding: "0.15rem 0.5rem",
                          borderRadius: "0.25rem",
                          background: "#ffedd5",
                          color: "#c2410c",
                          fontWeight: 700,
                        }}
                      >
                        ⏳ در انتظار تأیید
                      </span>
                    )}
                    <span style={{ fontSize: "0.8rem", color: "#475569" }}>
                      نویسنده: <bdi dir="ltr">{root.authorId.slice(0, 8)}...</bdi>
                    </span>
                  </div>

                  {canModerate && onEndorseComment && !root.isMentorEndorsed && root.status === "APPROVED" && (
                    <button
                      type="button"
                      onClick={() => onEndorseComment(root.id)}
                      style={{
                        padding: "0.25rem 0.6rem",
                        borderRadius: "0.25rem",
                        border: "1px solid #86efac",
                        background: "#ffffff",
                        color: "#166534",
                        fontSize: "0.75rem",
                        fontWeight: 600,
                        cursor: "pointer",
                      }}
                    >
                      ⭐ علامت‌گذاری به عنوان پاسخ برتر
                    </button>
                  )}
                </div>

                <div style={{ fontSize: "0.9rem", color: "#1e293b", lineHeight: 1.6, whiteSpace: "pre-wrap" }}>
                  {root.body}
                </div>

                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "0.75rem", color: "#94a3b8" }}>
                  <span>{root.createdAt}</span>
                  {!thread.isLocked && (
                    <button
                      type="button"
                      onClick={() => setReplyingToParentId(root.id)}
                      style={{
                        background: "transparent",
                        border: "none",
                        color: "#0284c7",
                        cursor: "pointer",
                        fontSize: "0.8rem",
                        fontWeight: 600,
                      }}
                    >
                      ↩ پاسخ به این نظر
                    </button>
                  )}
                </div>

                {/* Level 2 Child Replies */}
                {childReplies.length > 0 && (
                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: "0.5rem",
                      marginTop: "0.5rem",
                      marginRight: "1.5rem",
                      borderRight: "2px solid #e2e8f0",
                      paddingRight: "1rem",
                    }}
                  >
                    {childReplies.map((reply) => (
                      <div
                        key={reply.id}
                        style={{
                          padding: "0.75rem 1rem",
                          borderRadius: "0.5rem",
                          background: "#f8fafc",
                          border: "1px solid #f1f5f9",
                          display: "flex",
                          flexDirection: "column",
                          gap: "0.25rem",
                        }}
                      >
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "#64748b" }}>
                          <span>
                            پاسخ‌دهنده: <bdi dir="ltr">{reply.authorId.slice(0, 8)}...</bdi>
                          </span>
                          <span>{reply.createdAt}</span>
                        </div>
                        <div style={{ fontSize: "0.85rem", color: "#334155", lineHeight: 1.5 }}>
                          {reply.body}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </article>
  );
};
