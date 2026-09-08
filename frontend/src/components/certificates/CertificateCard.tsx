"use client";

import React, { useState } from "react";

export interface CertificateData {
  id: string;
  certificateNumber: string;
  courseTitle: string;
  templateTitle: string;
  studentDisplayId: string;
  finalScore: string;
  issuedAtPersian: string;
  verificationHash: string;
  status: "ISSUED" | "REVOKED";
}

interface CertificateCardProps {
  certificate: CertificateData;
}

export const CertificateCard: React.FC<CertificateCardProps> = ({ certificate }) => {
  const [copied, setCopied] = useState(false);

  const handleCopyHash = async () => {
    try {
      await navigator.clipboard.writeText(certificate.verificationHash);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
    }
  };

  return (
    <article
      style={{
        background: "linear-gradient(135deg, #ffffff 0%, #fdfbf7 100%)",
        border: "2px solid #e2d9c8",
        boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.03)",
        borderRadius: "1.25rem",
        padding: "2rem",
        position: "relative",
        overflow: "hidden",
        direction: "rtl",
        fontFamily: "var(--cs-font-family-base, inherit)",
      }}
      aria-labelledby={`cert-title-${certificate.id}`}
    >
      {/* Decorative double-border line (Academic Dignity) */}
      <div
        style={{
          position: "absolute",
          top: "0.5rem",
          bottom: "0.5rem",
          right: "0.5rem",
          left: "0.5rem",
          border: "1px solid #d1c7b7",
          borderRadius: "0.85rem",
          pointerEvents: "none",
        }}
        aria-hidden="true"
      />

      {/* Header Banner */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.5rem" }}>
        <div>
          <span
            style={{
              display: "inline-block",
              padding: "0.25rem 0.75rem",
              borderRadius: "0.375rem",
              background: "#fef3c7",
              color: "#92400e",
              fontSize: "0.75rem",
              fontWeight: 700,
              marginBottom: "0.5rem",
            }}
          >
            گواهی رسمی پایان دوره آموزشی
          </span>
          <h3
            id={`cert-title-${certificate.id}`}
            style={{
              margin: "0",
              fontSize: "1.35rem",
              fontWeight: 800,
              color: "#1e293b",
            }}
          >
            {certificate.courseTitle}
          </h3>
          <p style={{ margin: "0.25rem 0 0 0", fontSize: "0.9rem", color: "#64748b" }}>
            {certificate.templateTitle}
          </p>
        </div>

        {/* Digital Verification Seal */}
        <div
          style={{
            width: "4rem",
            height: "4rem",
            borderRadius: "50%",
            border: "2px solid #b45309",
            background: "#fffbeb",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 2px 4px rgba(180, 83, 9, 0.15)",
          }}
          aria-label="نشان تأیید دیجیتال سیستم"
        >
          <span style={{ fontSize: "1.1rem" }} aria-hidden="true">🏅</span>
          <span style={{ fontSize: "0.6rem", fontWeight: 800, color: "#92400e" }}>تأییدشده</span>
        </div>
      </div>

      {/* Details Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "1rem",
          padding: "1rem",
          background: "rgba(241, 245, 249, 0.6)",
          borderRadius: "0.75rem",
          marginBottom: "1.5rem",
        }}
      >
        <div>
          <span style={{ display: "block", fontSize: "0.75rem", color: "#64748b" }}>شناسه فراگیر:</span>
          <span style={{ fontWeight: 700, color: "#334155" }}>
            <bdi dir="ltr">{certificate.studentDisplayId}</bdi>
          </span>
        </div>
        <div>
          <span style={{ display: "block", fontSize: "0.75rem", color: "#64748b" }}>نمره نهایی دستاورد:</span>
          <span style={{ fontWeight: 800, color: "#047857" }}>{certificate.finalScore}٪</span>
        </div>
        <div>
          <span style={{ display: "block", fontSize: "0.75rem", color: "#64748b" }}>تاریخ صدور رسمی:</span>
          <span style={{ fontWeight: 600, color: "#334155" }}>{certificate.issuedAtPersian}</span>
        </div>
        <div>
          <span style={{ display: "block", fontSize: "0.75rem", color: "#64748b" }}>شماره سریال گواهی:</span>
          <span style={{ fontWeight: 700, color: "#1e293b", fontFamily: "monospace" }}>
            <bdi dir="ltr">{certificate.certificateNumber}</bdi>
          </span>
        </div>
      </div>

      {/* Cryptographic Verification Digest Section */}
      <div
        style={{
          borderTop: "1px dashed #cbd5e1",
          paddingTop: "1rem",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "0.5rem",
        }}
      >
        <div style={{ flex: 1, minWidth: "220px" }}>
          <span style={{ display: "block", fontSize: "0.7rem", color: "#64748b" }}>
            هش اعتبارسنجی رمزنگاری‌شده (HMAC-SHA256):
          </span>
          <code
            style={{
              fontSize: "0.75rem",
              background: "#e2e8f0",
              padding: "0.2rem 0.5rem",
              borderRadius: "0.25rem",
              color: "#334155",
              display: "inline-block",
              maxWidth: "100%",
              overflow: "hidden",
              textOverflow: "ellipsis",
            }}
          >
            <bdi dir="ltr">{certificate.verificationHash}</bdi>
          </code>
        </div>

        <button
          onClick={handleCopyHash}
          style={{
            padding: "0.5rem 1rem",
            fontSize: "0.8rem",
            fontWeight: 600,
            borderRadius: "0.5rem",
            border: "1px solid #cbd5e1",
            background: copied ? "#dcfce7" : "#ffffff",
            color: copied ? "#15803d" : "#475569",
            cursor: "pointer",
            minHeight: "44px",
            minWidth: "44px",
            transition: "all 0.2s ease",
          }}
          aria-label="کپی هش اعتبارسنجی گواهی"
        >
          {copied ? "کپی شد ✓" : "کپی کد هش 📋"}
        </button>
      </div>
    </article>
  );
};
