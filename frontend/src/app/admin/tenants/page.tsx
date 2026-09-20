"use client";

import { useState } from "react";
import { adminAlphaContent as copy } from "@/content/fa/admin.alpha";
import styles from "../admin.module.css";

export default function AdminTenantsPage() {
  const t = copy.tenants;
  const [inspectedTenant, setInspectedTenant] = useState<string | null>(null);

  return (
    <div className={styles.adminContainer}>
      <div className={styles.headerSection}>
        <div className={styles.noticeBanner}>
          <span>{copy.envNotice}</span>
        </div>
        <h1 className={styles.pageTitle}>{t.title}</h1>
        <p className={styles.pageSubtitle}>{t.subtitle}</p>
      </div>

      <div className={styles.tableWrapper}>
        <table className={styles.adminTable}>
          <thead>
            <tr>
              <th>{t.tableHeaders.name}</th>
              <th>{t.tableHeaders.domain}</th>
              <th>{t.tableHeaders.status}</th>
              <th>{t.tableHeaders.isolation}</th>
              <th>{t.tableHeaders.users}</th>
              <th>{t.tableHeaders.health}</th>
              <th>{t.tableHeaders.actions}</th>
            </tr>
          </thead>
          <tbody>
            {t.items.map((item) => (
              <tr key={item.id}>
                <td>
                  <div style={{ display: "flex", flexDirection: "column" }}>
                    <span style={{ fontWeight: 800 }}>{item.name}</span>
                    <span style={{ fontSize: "0.75rem", color: "var(--muted)" }}>{item.slug}</span>
                  </div>
                </td>
                <td dir="ltr" style={{ textAlign: "right", color: "var(--purple)", fontWeight: 600 }}>
                  {item.domain}
                </td>
                <td>
                  <span className={`${styles.badge} ${item.status === "active" ? styles.badgeSuccess : styles.badgeWarning}`}>
                    {item.status === "active" ? "فعال و عملیاتی" : "در حال پیکربندی"}
                  </span>
                </td>
                <td>
                  <span className={`${styles.badge} ${styles.badgeInfo}`}>
                    {item.isolationLevel}
                  </span>
                </td>
                <td style={{ fontWeight: 700 }}>{item.userCount} کاربر</td>
                <td style={{ fontWeight: 800, color: item.healthScore >= 98 ? "#67c23a" : "#e6a23c" }}>
                  {item.healthScore}٪
                </td>
                <td>
                  <button
                    type="button"
                    className={styles.actionBtn}
                    onClick={() => setInspectedTenant(inspectedTenant === item.id ? null : item.id)}
                  >
                    {inspectedTenant === item.id ? "بستن گزارش" : "بررسی تفکیک داده"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {inspectedTenant && (
        <div className={styles.statCard} style={{ borderColor: "var(--purple)", background: "#fbf9fe", gap: "0.75rem" }}>
          <h2 style={{ fontSize: "1rem", margin: 0, fontWeight: 800, color: "var(--purple)" }}>
            گزارش تفکیک چندمستأجری و انزوای داده‌ها ({inspectedTenant})
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "0.75rem", fontSize: "0.8125rem" }}>
            <div style={{ padding: "0.5rem", background: "#fff", borderRadius: "6px", border: "1px solid var(--line)" }}>
              <strong>روش ایزولاسیون:</strong> Postgres Row-Level Security (RLS) + Tenant Schema
            </div>
            <div style={{ padding: "0.5rem", background: "#fff", borderRadius: "6px", border: "1px solid var(--line)" }}>
              <strong>امنیت اتصال:</strong> Fail-closed Middleware (نشت داده = صفر)
            </div>
            <div style={{ padding: "0.5rem", background: "#fff", borderRadius: "6px", border: "1px solid var(--line)" }}>
              <strong>زمان آخرین بررسی:</strong> هم‌اکنون (شاخص سلامت پایدار)
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
