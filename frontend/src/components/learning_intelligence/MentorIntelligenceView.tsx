"use client";

import React from "react";
import { MentorIntelligenceDossierReadModel } from "@/data/intelligenceTypes";

interface Props {
  dossier?: MentorIntelligenceDossierReadModel | null;
}

export const MentorIntelligenceView: React.FC<Props> = ({ dossier }) => {
  if (!dossier) {
    return (
      <div style={{ padding: "1.5rem", textAlign: "center", color: "var(--text-muted)" }}>
        هنوز شواهد کافی برای تحلیل مربی ثبت نشده است.
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem", direction: "rtl" }}>
      {/* 1. Pedagogical Dossier Card */}
      <section
        style={{
          background: "linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.95))",
          borderRadius: "1rem",
          padding: "1.5rem",
          border: "1px solid rgba(255, 255, 255, 0.1)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
          <div>
            <h2 style={{ fontSize: "1.1rem", fontWeight: 700, margin: 0, color: "#f8fafc" }}>
              دوسیه شواهد پداگوژیکال • {dossier.display_name} ({dossier.student_code})
            </h2>
            <p style={{ fontSize: "0.85rem", color: "#94a3b8", margin: "0.25rem 0 0 0" }}>
              تحلیل شواهد یادگیری و استقامت در حل مسئله؛ این بخش جایگزین قضاوت مربی نیست، بلکه تقویت‌کننده تفکر مربی است.
            </p>
          </div>
        </div>

        {/* Evidence Trace Linkage */}
        <div style={{ background: "rgba(0, 0, 0, 0.3)", borderRadius: "0.5rem", padding: "0.75rem", marginBottom: "1rem" }}>
          <span style={{ fontSize: "0.75rem", color: "#818cf8", fontWeight: 600, display: "block", marginBottom: "0.25rem" }}>
            ردپای شواهد مستند (Evidence Trace):
          </span>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
            {dossier.evidence_trace.map((trace, idx) => (
              <span key={idx} style={{ fontSize: "0.75rem", color: "#cbd5e1", background: "rgba(255, 255, 255, 0.05)", padding: "0.2rem 0.5rem", borderRadius: "4px" }}>
                {trace}
              </span>
            ))}
          </div>
        </div>

        {/* Pedagogical Observations */}
        <div style={{ marginBottom: "1.25rem" }}>
          <h3 style={{ fontSize: "0.9rem", color: "#e2e8f0", margin: "0 0 0.5rem 0" }}>مشاهدات یادگیری:</h3>
          <ul style={{ margin: 0, paddingRight: "1.25rem", color: "#cbd5e1", fontSize: "0.85rem", lineHeight: 1.6 }}>
            {dossier.pedagogical_summary.map((sum, idx) => (
              <li key={idx}>{sum}</li>
            ))}
          </ul>
        </div>

        {/* 2. Socratic Prompts Launcher */}
        <div style={{ background: "rgba(99, 102, 241, 0.08)", border: "1px solid rgba(99, 102, 241, 0.2)", borderRadius: "0.75rem", padding: "1rem" }}>
          <span style={{ fontSize: "0.85rem", fontWeight: 600, color: "#a5b4fc", display: "block", marginBottom: "0.5rem" }}>
            پرسش‌های پیشنهادی سقراطی (عمق‌بخشی به تفکر بدون لو دادن پاسخ کد):
          </span>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            {dossier.suggested_socratic_prompts.map((prompt, idx) => (
              <div
                key={idx}
                style={{
                  background: "rgba(15, 23, 42, 0.6)",
                  padding: "0.6rem 0.8rem",
                  borderRadius: "0.5rem",
                  fontSize: "0.85rem",
                  color: "#f1f5f9",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <span>💬 {prompt}</span>
                <button
                  type="button"
                  style={{
                    background: "#4f46e5",
                    color: "white",
                    border: "none",
                    borderRadius: "0.35rem",
                    padding: "0.3rem 0.6rem",
                    fontSize: "0.75rem",
                    cursor: "pointer",
                  }}
                  onClick={() => alert(`پرسش سقراطی در چت ارسال شد:\n${prompt}`)}
                >
                  طرح در گفتگو
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* 3. Non-Alarmist Learning Signal */}
        {dossier.friction_signal && dossier.friction_signal.is_active && (
          <div
            style={{
              marginTop: "1rem",
              background: "rgba(245, 158, 11, 0.08)",
              border: "1px solid rgba(245, 158, 11, 0.3)",
              borderRadius: "0.5rem",
              padding: "0.75rem",
              fontSize: "0.85rem",
              color: "#fbbf24",
            }}
          >
            <strong>💡 سیگنال یادگیری (Learning Signal):</strong> {dossier.friction_signal.suggested_mentor_action}
          </div>
        )}
      </section>
    </div>
  );
};
