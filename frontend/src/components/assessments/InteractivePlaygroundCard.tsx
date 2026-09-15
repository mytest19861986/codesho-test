"use client";

import React, { useState } from "react";
import { TestEvaluationPanel, TestCaseEvaluation } from "./TestEvaluationPanel";

export interface CodeAssessmentDetail {
  id: string;
  lessonId: string;
  language: string;
  starterCode: string;
  timeoutSeconds: number;
  memoryLimitMb: number;
  testcases: {
    id: string;
    input: string;
    expectedOutput: string;
    weight: number;
    isHidden: boolean;
  }[];
}

interface Props {
  assessment?: CodeAssessmentDetail;
}

export const InteractivePlaygroundCard: React.FC<Props> = ({ assessment }) => {
  const [code, setCode] = useState<string>(
    assessment?.starterCode ||
      'def solution(a, b):\n    # برنامه خود را بنویسید\n    return a + b\n\n# آزمون دستی:\nprint("نتیجه:", solution(3, 4))'
  );
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<"console" | "tests">("console");
  const [consoleOutput, setConsoleOutput] = useState<string>(
    "خروجی اجرای زنده کد در این بخش نمایش داده خواهد شد..."
  );
  const [testResults, setTestResults] = useState<TestCaseEvaluation[]>([]);
  const [score, setScore] = useState<number | null>(null);

  const handleRunPlayground = async () => {
    setIsRunning(true);
    setActiveTab("console");
    setConsoleOutput("در حال ارسال کد به محیط ایزوله سندباکس (Ephemeral Sandbox)...");

    // Simulate safe API call to /api/v1/learning/playground/run/
    setTimeout(() => {
      setIsRunning(false);
      try {
        if (code.includes("import os") || code.includes("subprocess")) {
          setConsoleOutput(
            "خطای امنیتی سندباکس: استفاده از ماژول‌های سیستمی و دسترسی به هاست مسدود است.\nSecurityViolation: Blocked syscall."
          );
        } else {
          setConsoleOutput(
            `کد با موفقیت در محیط ایزوله اجرا شد.\nزمان اجرا: 42ms | مصرف حافظه: 18MB\nخروجی برنامه:\nنتیجه: 7\n[Sandbox Exit Code 0]`
          );
        }
      } catch {
        setConsoleOutput("خطا در اجرای کد در سندباکس.");
      }
    }, 800);
  };

  const handleSubmitEvaluation = async () => {
    setIsSubmitting(true);
    setActiveTab("tests");

    setTimeout(() => {
      setIsSubmitting(false);
      const isCorrect = code.includes("return a + b") || code.includes("return a+b");
      const mockResults: TestCaseEvaluation[] = [
        {
          id: "tc-1",
          input: "2 3",
          expectedOutput: "5",
          actualOutput: isCorrect ? "5" : "0",
          isPassed: isCorrect,
          weight: 50,
          isHidden: false,
        },
        {
          id: "tc-2",
          input: "10 20",
          expectedOutput: "30",
          actualOutput: isCorrect ? "30" : "0",
          isPassed: isCorrect,
          weight: 50,
          isHidden: true,
        },
      ];
      setTestResults(mockResults);
      setScore(isCorrect ? 100 : 0);
    }, 1200);
  };

  return (
    <div
      style={{
        background: "var(--cs-color-bg-surface, #ffffff)",
        border: "1px solid var(--cs-color-border-subtle, #e2e8f0)",
        borderRadius: "1rem",
        overflow: "hidden",
        boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.05)",
        marginBottom: "2rem",
      }}
      data-testid="interactive-code-playground"
    >
      {/* Header Bar */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "1rem 1.5rem",
          background: "#0f172a",
          color: "#f8fafc",
          direction: "rtl",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <span style={{ fontSize: "1.25rem" }}>💻</span>
          <div>
            <h3 style={{ margin: 0, fontSize: "1.1rem", fontWeight: 700 }}>
              محیط تعاملی کدنویسی و ارزیابی خودکار (Code Playground)
            </h3>
            <span style={{ fontSize: "0.75rem", color: "#94a3b8" }}>
              ایزولاسیون سندباکس: شبکه Deny-All | سقف حافظه ۲۵۶MB | زمان اجرا ۵s
            </span>
          </div>
        </div>

        <div style={{ display: "flex", gap: "0.75rem" }}>
          <button
            type="button"
            onClick={handleRunPlayground}
            disabled={isRunning || isSubmitting}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "0.5rem",
              background: "#334155",
              color: "#ffffff",
              border: "1px solid #475569",
              cursor: isRunning ? "not-allowed" : "pointer",
              fontWeight: 600,
              display: "flex",
              alignItems: "center",
              gap: "0.35rem",
            }}
          >
            {isRunning ? "در حال اجرا..." : "▶ اجرای آزمایشی (Dry-Run)"}
          </button>
          <button
            type="button"
            onClick={handleSubmitEvaluation}
            disabled={isRunning || isSubmitting}
            style={{
              padding: "0.5rem 1.25rem",
              borderRadius: "0.5rem",
              background: "#10b981",
              color: "#ffffff",
              border: "none",
              cursor: isSubmitting ? "not-allowed" : "pointer",
              fontWeight: 600,
              display: "flex",
              alignItems: "center",
              gap: "0.35rem",
            }}
          >
            {isSubmitting ? "در حال داوری..." : "🚀 ثبت و ارزیابی نهایی"}
          </button>
        </div>
      </div>

      {/* Editor & Console Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          minHeight: "360px",
          background: "#1e293b",
        }}
      >
        {/* Code Editor (LTR) */}
        <div
          style={{
            borderLeft: "1px solid #334155",
            display: "flex",
            flexDirection: "column",
            direction: "ltr",
          }}
        >
          <div
            style={{
              padding: "0.5rem 1rem",
              background: "#1e293b",
              borderBottom: "1px solid #334155",
              color: "#94a3b8",
              fontSize: "0.8rem",
              display: "flex",
              justifyContent: "space-between",
            }}
          >
            <span>Python 3.13 (Isolated Sandbox)</span>
            <span>UTF-8</span>
          </div>
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            style={{
              flex: 1,
              background: "#0f172a",
              color: "#e2e8f0",
              fontFamily: "monospace",
              fontSize: "0.95rem",
              padding: "1rem",
              border: "none",
              outline: "none",
              resize: "none",
              lineHeight: "1.6",
            }}
            aria-label="کد پایتون برای ارزیابی"
            spellCheck={false}
          />
        </div>

        {/* Output Console & Test Results Panel */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            background: "#090d16",
            color: "#f8fafc",
          }}
        >
          {/* Tabs */}
          <div
            style={{
              display: "flex",
              borderBottom: "1px solid #1e293b",
              background: "#111827",
              direction: "rtl",
            }}
          >
            <button
              type="button"
              onClick={() => setActiveTab("console")}
              style={{
                padding: "0.6rem 1.2rem",
                background: activeTab === "console" ? "#1e293b" : "transparent",
                color: activeTab === "console" ? "#38bdf8" : "#94a3b8",
                border: "none",
                cursor: "pointer",
                fontWeight: 600,
                borderBottom: activeTab === "console" ? "2px solid #38bdf8" : "none",
              }}
            >
              کنسول خروجی ترمینال
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("tests")}
              style={{
                padding: "0.6rem 1.2rem",
                background: activeTab === "tests" ? "#1e293b" : "transparent",
                color: activeTab === "tests" ? "#38bdf8" : "#94a3b8",
                border: "none",
                cursor: "pointer",
                fontWeight: 600,
                borderBottom: activeTab === "tests" ? "2px solid #38bdf8" : "none",
              }}
            >
              نتایج تست‌کیس‌ها {score !== null && `(${score}٪)`}
            </button>
          </div>

          {/* Tab Content */}
          <div style={{ flex: 1, padding: "1rem", overflowY: "auto" }}>
            {activeTab === "console" ? (
              <pre
                style={{
                  margin: 0,
                  fontFamily: "monospace",
                  fontSize: "0.85rem",
                  color: "#a5f3fc",
                  whiteSpace: "pre-wrap",
                  direction: "ltr",
                }}
              >
                {consoleOutput}
              </pre>
            ) : (
              <TestEvaluationPanel testResults={testResults} score={score} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
