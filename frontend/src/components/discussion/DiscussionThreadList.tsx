import React from "react";

export interface DiscussionThreadItem {
  id: string;
  title: string;
  body: string;
  authorId: string;
  status: "PENDING" | "APPROVED" | "FLAGGED" | "REMOVED";
  isPinned: boolean;
  isLocked: boolean;
  repliesCount: number;
  scopeType: "COHORT" | "LESSON";
  scopeTitle: string;
  createdAt: string;
}

interface DiscussionThreadListProps {
  threads: DiscussionThreadItem[];
  selectedThreadId?: string;
  onSelectThread: (threadId: string) => void;
  onCreateNewThread?: () => void;
  isLoading?: boolean;
}

export const DiscussionThreadList: React.FC<DiscussionThreadListProps> = ({
  threads,
  selectedThreadId,
  onSelectThread,
  onCreateNewThread,
  isLoading = false,
}) => {
  return (
    <section
      aria-labelledby="discussions-list-heading"
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "1rem",
        direction: "rtl",
        width: "100%",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderBottom: "2px solid var(--cs-color-border-subtle, #e2e8f0)",
          paddingBottom: "0.75rem",
        }}
      >
        <div>
          <h2 id="discussions-list-heading" style={{ margin: 0, fontSize: "1.25rem", color: "#0f172a" }}>
            💬 تالار گفتگو و تعاملات یادگیری
          </h2>
          <p style={{ margin: "0.25rem 0 0 0", fontSize: "0.85rem", color: "#64748b" }}>
            فضای امن گفتگوی هم‌کلاسی‌ها، حل تمرین و بازخورد منتورها
          </p>
        </div>
        {onCreateNewThread && (
          <button
            type="button"
            onClick={onCreateNewThread}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "0.5rem",
              background: "#0284c7",
              color: "#ffffff",
              border: "none",
              fontWeight: 600,
              fontSize: "0.9rem",
              cursor: "pointer",
            }}
          >
            + ایجاد پرسش جدید
          </button>
        )}
      </div>

      {isLoading ? (
        <div style={{ textAlign: "center", padding: "2rem", color: "#64748b" }}>
          در حال بارگذاری گفتگوها...
        </div>
      ) : threads.length === 0 ? (
        <div
          style={{
            textAlign: "center",
            padding: "3rem 1.5rem",
            background: "#f8fafc",
            borderRadius: "0.75rem",
            border: "1px dashed #cbd5e1",
          }}
        >
          <span style={{ fontSize: "2.5rem" }} role="img" aria-label="خالی">
            📭
          </span>
          <h3 style={{ margin: "0.75rem 0 0.25rem 0", color: "#1e293b", fontSize: "1.1rem" }}>
            هنوز گفتگویی ایجاد نشده است
          </h3>
          <p style={{ margin: 0, fontSize: "0.85rem", color: "#64748b" }}>
            اولین نفری باشید که در این درس یا کوهورت سؤالی مطرح می‌کند!
          </p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {threads.map((t) => {
            const isSelected = selectedThreadId === t.id;
            return (
              <div
                key={t.id}
                onClick={() => onSelectThread(t.id)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    onSelectThread(t.id);
                  }
                }}
                style={{
                  padding: "1rem 1.25rem",
                  borderRadius: "0.75rem",
                  background: isSelected ? "#f0fdf4" : "#ffffff",
                  border: isSelected ? "2px solid #22c55e" : "1px solid #e2e8f0",
                  cursor: "pointer",
                  transition: "all 0.15s ease",
                  display: "flex",
                  flexDirection: "column",
                  gap: "0.5rem",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    {t.isPinned && (
                      <span
                        style={{
                          fontSize: "0.75rem",
                          padding: "0.15rem 0.5rem",
                          borderRadius: "0.25rem",
                          background: "#fef3c7",
                          color: "#92400e",
                          fontWeight: 700,
                        }}
                      >
                        📌 پین‌شده توسط منتور
                      </span>
                    )}
                    {t.status === "PENDING" && (
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
                        ⏳ در انتظار بررسی محتوا
                      </span>
                    )}
                    <span
                      style={{
                        fontSize: "0.75rem",
                        padding: "0.15rem 0.5rem",
                        borderRadius: "0.25rem",
                        background: "#e0f2fe",
                        color: "#0369a1",
                      }}
                    >
                      {t.scopeType === "COHORT" ? "کوهورت" : "درس"}:{" "}
                      <bdi dir="ltr">{t.scopeTitle}</bdi>
                    </span>
                  </div>
                  <span style={{ fontSize: "0.8rem", color: "#64748b" }}>
                    💬 {t.repliesCount} پاسخ
                  </span>
                </div>

                <h3 style={{ margin: 0, fontSize: "1.05rem", color: "#0f172a", fontWeight: 700 }}>
                  {t.title}
                </h3>

                <p
                  style={{
                    margin: 0,
                    fontSize: "0.9rem",
                    color: "#475569",
                    display: "-webkit-box",
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: "vertical",
                    overflow: "hidden",
                  }}
                >
                  {t.body}
                </p>

                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    fontSize: "0.75rem",
                    color: "#94a3b8",
                    marginTop: "0.25rem",
                  }}
                >
                  <span>
                    شناسه نویسنده: <bdi dir="ltr">{t.authorId.slice(0, 8)}...</bdi>
                  </span>
                  <span>{t.createdAt}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
};
