"use client";

import React from "react";
import { LearnerSkillGraphReadModel, StudentReflectionEntry } from "@/data/intelligenceTypes";

interface Props {
  skillGraph?: LearnerSkillGraphReadModel | null;
  reflections?: StudentReflectionEntry[];
}

export const StudentIntelligenceView: React.FC<Props> = ({ skillGraph, reflections }) => {
  if (!skillGraph) {
    return (
      <div style={{ padding: "1.5rem", textAlign: "center", color: "var(--text-muted)" }}>
        هنوز داده کافی برای نمایش صورت فلکی یادگیری وجود ندارد. با پیشروی در مایلستون‌ها، مفاهیم در این بخش روشن می‌شوند.
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem", direction: "rtl" }}>
      {/* 1. Skill Constellation View */}
      <section
        style={{
          background: "linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9))",
          borderRadius: "1rem",
          padding: "1.5rem",
          border: "1px solid rgba(255, 255, 255, 0.1)",
          boxShadow: "0 8px 32px rgba(0, 0, 0, 0.2)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
          <div>
            <h2 style={{ fontSize: "1.15rem", fontWeight: 700, margin: 0, color: "#f8fafc" }}>
              صورت فلکی شایستگی‌ها • Skill Constellation
            </h2>
            <p style={{ fontSize: "0.85rem", color: "#94a3b8", margin: "0.25rem 0 0 0" }}>
              نقشه مفاهیم اثبات‌شده بدون رتبه‌بندی یا امتیاز رقابتی؛ هر ستاره نشانه تسلط بر یک مفهوم مهندسی است.
            </p>
          </div>
          <span style={{ fontSize: "0.8rem", padding: "0.25rem 0.75rem", borderRadius: "9999px", background: "rgba(99, 102, 241, 0.2)", color: "#818cf8" }}>
            کد دانش‌آموز: {skillGraph.student_code}
          </span>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem" }}>
          {skillGraph.skills.map((skill) => {
            const isDemonstrated = skill.status === "DEMONSTRATED";
            return (
              <div
                key={skill.slug}
                style={{
                  background: isDemonstrated ? "rgba(16, 185, 129, 0.08)" : "rgba(255, 255, 255, 0.03)",
                  border: `1px solid ${isDemonstrated ? "rgba(16, 185, 129, 0.3)" : "rgba(255, 255, 255, 0.08)"}`,
                  borderRadius: "0.75rem",
                  padding: "1rem",
                  display: "flex",
                  flexDirection: "column",
                  gap: "0.5rem",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: "0.75rem", color: isDemonstrated ? "#34d399" : "#94a3b8", fontWeight: 600 }}>
                    {isDemonstrated ? "✨ اثبات‌شده در کد" : "⏳ در حال کاوش و یادگیری"}
                  </span>
                  <span style={{ fontSize: "0.7rem", color: "#64748b", textTransform: "uppercase" }}>{skill.category}</span>
                </div>
                <h3 style={{ fontSize: "0.95rem", fontWeight: 600, color: "#f1f5f9", margin: 0 }}>{skill.title}</h3>
                {skill.prerequisites.length > 0 && (
                  <div style={{ fontSize: "0.75rem", color: "#64748b" }}>
                    پیش‌نیاز: {skill.prerequisites.join("، ")}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* 2. Student Self-Discovery Journal */}
      {reflections && reflections.length > 0 && (
        <section
          style={{
            background: "rgba(15, 23, 42, 0.6)",
            borderRadius: "1rem",
            padding: "1.25rem",
            border: "1px solid rgba(255, 255, 255, 0.06)",
          }}
        >
          <h3 style={{ fontSize: "1rem", fontWeight: 600, margin: "0 0 0.75rem 0", color: "#e2e8f0" }}>
            دفترچه خوداندیشی و تأمل یادگیری
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            {reflections.map((r) => (
              <div
                key={r.reflection_id}
                style={{
                  background: "rgba(255, 255, 255, 0.03)",
                  borderRadius: "0.5rem",
                  padding: "0.75rem 1rem",
                  fontSize: "0.85rem",
                  color: "#cbd5e1",
                  borderRight: "3px solid #818cf8",
                }}
              >
                <p style={{ margin: 0 }}>{r.reflection_text}</p>
                <span style={{ fontSize: "0.7rem", color: "#64748b", display: "block", marginTop: "0.25rem" }}>
                  مایلستون: {r.milestone_slug}
                </span>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
};
