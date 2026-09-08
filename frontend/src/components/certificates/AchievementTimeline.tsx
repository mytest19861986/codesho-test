"use client";

import React from "react";

export interface TimelineItem {
  id: string;
  eventType: "COURSE_ENROLLED" | "LESSON_COMPLETED" | "ASSIGNMENT_REVIEWED" | "BADGE_AWARDED" | "CERTIFICATE_ISSUED";
  title: string;
  description: string;
  occurredAtPersian: string;
}

interface AchievementTimelineProps {
  items: TimelineItem[];
}

export const AchievementTimeline: React.FC<AchievementTimelineProps> = ({ items }) => {
  const getEventIcon = (type: TimelineItem["eventType"]) => {
    switch (type) {
      case "CERTIFICATE_ISSUED":
        return "🎓";
      case "BADGE_AWARDED":
        return "🎖️";
      case "ASSIGNMENT_REVIEWED":
        return "📝";
      case "LESSON_COMPLETED":
        return "✅";
      case "COURSE_ENROLLED":
        return "🚀";
      default:
        return "📌";
    }
  };

  return (
    <section
      style={{
        background: "#ffffff",
        border: "1px solid #e2e8f0",
        borderRadius: "1rem",
        padding: "1.5rem",
        direction: "rtl",
      }}
      aria-labelledby="timeline-title"
    >
      <h3
        id="timeline-title"
        style={{
          margin: "0 0 1.5rem 0",
          fontSize: "1.25rem",
          fontWeight: 700,
          color: "#1e293b",
          display: "flex",
          alignItems: "center",
          gap: "0.5rem",
        }}
      >
        <span>📈</span>
        <span>خط زمانی دستاوردهای آموزشی فراگیر</span>
      </h3>

      {items.length === 0 ? (
        <p style={{ color: "#64748b", fontSize: "0.9rem" }}>هنوز رویدادی ثبت نشده است.</p>
      ) : (
        <ol style={{ listStyle: "none", padding: 0, margin: 0, position: "relative" }}>
          {items.map((item, index) => {
            const isLast = index === items.length - 1;
            return (
              <li
                key={item.id}
                style={{
                  position: "relative",
                  paddingRight: "2.5rem",
                  paddingBottom: isLast ? "0" : "1.5rem",
                }}
              >
                {/* Vertical Timeline Line */}
                {!isLast && (
                  <div
                    style={{
                      position: "absolute",
                      right: "0.95rem",
                      top: "1.75rem",
                      bottom: "0",
                      width: "2px",
                      background: "#e2e8f0",
                    }}
                    aria-hidden="true"
                  />
                )}

                {/* Node Icon */}
                <div
                  style={{
                    position: "absolute",
                    right: "0",
                    top: "0",
                    width: "2rem",
                    height: "2rem",
                    borderRadius: "50%",
                    background: "#f1f5f9",
                    border: "2px solid #cbd5e1",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "0.9rem",
                  }}
                  aria-hidden="true"
                >
                  {getEventIcon(item.eventType)}
                </div>

                {/* Content Box */}
                <div
                  style={{
                    background: "#f8fafc",
                    border: "1px solid #e2e8f0",
                    borderRadius: "0.75rem",
                    padding: "0.85rem 1rem",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: "0.25rem" }}>
                    <h4 style={{ margin: 0, fontSize: "0.95rem", fontWeight: 700, color: "#1e293b" }}>
                      {item.title}
                    </h4>
                    <time style={{ fontSize: "0.75rem", color: "#64748b" }}>
                      {item.occurredAtPersian}
                    </time>
                  </div>
                  {item.description && (
                    <p style={{ margin: 0, fontSize: "0.85rem", color: "#475569" }}>
                      {item.description}
                    </p>
                  )}
                </div>
              </li>
            );
          })}
        </ol>
      )}
    </section>
  );
};
