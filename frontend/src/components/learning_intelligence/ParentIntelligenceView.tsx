"use client";

import React from "react";
import { ParentInsightReadModel } from "@/data/intelligenceTypes";

interface Props {
  parentInsight?: ParentInsightReadModel | null;
}

export const ParentIntelligenceView: React.FC<Props> = ({ parentInsight }) => {
  if (!parentInsight) {
    return (
      <div style={{ padding: "1.5rem", textAlign: "center", color: "var(--text-muted)" }}>
        هنوز بینش جدیدی برای این مرحله ثبت نشده است.
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem", direction: "rtl" }}>
      {/* 1. Empathetic Growth Banner */}
      <section
        style={{
          background: "linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.95))",
          borderRadius: "1rem",
          padding: "1.5rem",
          border: "1px solid rgba(255, 255, 255, 0.1)",
        }}
      >
        <div style={{ marginBottom: "1rem" }}>
          <span style={{ fontSize: "0.8rem", color: "#34d399", fontWeight: 600, display: "block", marginBottom: "0.25rem" }}>
            🌱 رشد فردی و اخلاقی در مسیر کدنویسی
          </span>
          <h2 style={{ fontSize: "1.1rem", fontWeight: 700, margin: 0, color: "#f8fafc" }}>
            گزارش پیشرفت و بالندگی فرزند شما
          </h2>
        </div>

        <p style={{ fontSize: "0.95rem", color: "#cbd5e1", lineHeight: 1.7, margin: "0 0 1.25rem 0" }}>
          {parentInsight.developmental_translation}
        </p>

        {/* 2. Home Conversation Cues */}
        <div
          style={{
            background: "rgba(16, 185, 129, 0.08)",
            border: "1px solid rgba(16, 185, 129, 0.2)",
            borderRadius: "0.75rem",
            padding: "1rem",
          }}
        >
          <span style={{ fontSize: "0.85rem", fontWeight: 600, color: "#6ee7b7", display: "block", marginBottom: "0.5rem" }}>
            💡 سرنخ‌های گفتگوی صمیمانه در منزل (Home Conversation Cues):
          </span>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            {parentInsight.home_support_cues.map((cue, idx) => (
              <div
                key={idx}
                style={{
                  background: "rgba(15, 23, 42, 0.6)",
                  padding: "0.6rem 0.8rem",
                  borderRadius: "0.5rem",
                  fontSize: "0.85rem",
                  color: "#f1f5f9",
                }}
              >
                🤝 {cue}
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};
