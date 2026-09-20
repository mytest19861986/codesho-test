"use client";

import { useState } from "react";
import { adminAlphaContent as copy } from "@/content/fa/admin.alpha";
import styles from "../admin.module.css";

export default function AdminAuditPage() {
  const a = copy.audit;
  const [statusFilter, setStatusFilter] = useState<"ALL" | "SUCCESS" | "DENIED">("ALL");

  const filteredEvents = a.events.filter((ev) => {
    if (statusFilter === "ALL") return true;
    return ev.status === statusFilter;
  });

  return (
    <div className={styles.adminContainer}>
      <div className={styles.headerSection}>
        <div className={styles.noticeBanner}>
          <span>{copy.envNotice}</span>
        </div>
        <h1 className={styles.pageTitle}>{a.title}</h1>
        <p className={styles.pageSubtitle}>{a.subtitle}</p>
      </div>

      {/* Filter and Notice */}
      <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: "1rem" }}>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button
            type="button"
            className={styles.actionBtn}
            style={statusFilter === "ALL" ? { background: "#f3eafa", borderColor: "var(--purple)", color: "var(--purple)", fontWeight: 800 } : {}}
            onClick={() => setStatusFilter("ALL")}
          >
            همه رویدادها ({a.events.length})
          </button>
          <button
            type="button"
            className={styles.actionBtn}
            style={statusFilter === "SUCCESS" ? { background: "#f0f9eb", borderColor: "#67c23a", color: "#67c23a", fontWeight: 800 } : {}}
            onClick={() => setStatusFilter("SUCCESS")}
          >
            موفق ({a.events.filter(e => e.status === "SUCCESS").length})
          </button>
          <button
            type="button"
            className={styles.actionBtn}
            style={statusFilter === "DENIED" ? { background: "#fef0f0", borderColor: "#f56c6c", color: "#f56c6c", fontWeight: 800 } : {}}
            onClick={() => setStatusFilter("DENIED")}
          >
            رد شده / هشدار ({a.events.filter(e => e.status === "DENIED").length})
          </button>
        </div>
        <span style={{ fontSize: "0.75rem", color: "var(--muted)" }}>
          کلیه رکوردهای این جدول داده‌های شبیه‌سازی‌شده آزمایشی (Synthetic Data) هستند.
        </span>
      </div>

      <div className={styles.tableWrapper}>
        <table className={styles.adminTable}>
          <thead>
            <tr>
              <th>{a.headers.timestamp}</th>
              <th>{a.headers.actor}</th>
              <th>{a.headers.action}</th>
              <th>{a.headers.resource}</th>
              <th>{a.headers.ip}</th>
              <th>{a.headers.status}</th>
            </tr>
          </thead>
          <tbody>
            {filteredEvents.map((ev) => (
              <tr key={ev.id}>
                <td>
                  <div style={{ display: "flex", flexDirection: "column" }}>
                    <span dir="ltr" style={{ textAlign: "right", fontWeight: 700, fontSize: "0.8125rem" }}>
                      {ev.timestampJalali}
                    </span>
                    <span dir="ltr" style={{ textAlign: "right", fontSize: "0.75rem", color: "var(--muted)" }}>
                      {ev.timestampUtc} UTC
                    </span>
                  </div>
                </td>
                <td style={{ fontWeight: 600 }}>{ev.actor}</td>
                <td dir="ltr" style={{ textAlign: "right", fontFamily: "monospace", fontSize: "0.8125rem", color: "var(--purple)" }}>
                  {ev.action}
                </td>
                <td dir="ltr" style={{ textAlign: "right", fontSize: "0.8125rem" }}>
                  {ev.resource}
                </td>
                <td dir="ltr" style={{ textAlign: "right", color: "var(--muted)" }}>
                  {ev.ipAddress}
                </td>
                <td>
                  <span className={`${styles.badge} ${ev.status === "SUCCESS" ? styles.badgeSuccess : styles.badgeDanger}`}>
                    {ev.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
