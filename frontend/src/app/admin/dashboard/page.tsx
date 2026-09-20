import type { Metadata } from "next";
import Link from "next/link";
import { adminAlphaContent as copy } from "@/content/fa/admin.alpha";
import styles from "../admin.module.css";
import { IconLaptop, IconDocument, IconSettings, IconCheck, IconClose } from "@/components/ui";

export const metadata: Metadata = {
  title: `${copy.brand} | ${copy.dashboard.title}`,
  description: copy.dashboard.subtitle,
};

export default function AdminDashboardPage() {
  const d = copy.dashboard;
  const tenants = copy.tenants.items;
  const auditEvents = copy.audit.events.slice(0, 3);
  const sysMetrics = copy.system.metrics.slice(0, 3);

  return (
    <div className={styles.adminContainer}>
      {/* 1. Page Header */}
      <div className={styles.headerSection}>
        <div className={styles.noticeBanner}>
          <span>{copy.envNotice}</span>
        </div>
        <h1 className={styles.pageTitle}>{d.title}</h1>
        <p className={styles.pageSubtitle}>{d.subtitle}</p>
      </div>

      {/* 2. Quick Telemetry Stats */}
      <div className={styles.statsGrid}>
        {d.quickStats.map((stat, idx) => (
          <div key={idx} className={styles.statCard}>
            <span className={styles.statLabel}>{stat.label}</span>
            <span className={styles.statValue}>{stat.value}</span>
            <span className={styles.statChange}>{stat.change}</span>
          </div>
        ))}
      </div>

      {/* 3. Tenant Isolation Health Snapshot */}
      <div className={styles.tableWrapper}>
        <div style={{ padding: "1rem 1.25rem", borderBottom: "1px solid var(--line)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h2 style={{ fontSize: "1.125rem", margin: 0, fontWeight: 800 }}>{d.tenantHealthTitle}</h2>
          <Link href="/admin/tenants" className={styles.actionBtn}>
            مشاهده همه سازمان‌ها
          </Link>
        </div>
        <table className={styles.adminTable}>
          <thead>
            <tr>
              <th>{copy.tenants.tableHeaders.name}</th>
              <th>{copy.tenants.tableHeaders.domain}</th>
              <th>{copy.tenants.tableHeaders.status}</th>
              <th>{copy.tenants.tableHeaders.isolation}</th>
              <th>{copy.tenants.tableHeaders.health}</th>
              <th>{copy.tenants.tableHeaders.actions}</th>
            </tr>
          </thead>
          <tbody>
            {tenants.map((t) => (
              <tr key={t.id}>
                <td style={{ fontWeight: 700 }}>{t.name}</td>
                <td dir="ltr" style={{ textAlign: "right", color: "var(--muted)" }}>{t.domain}</td>
                <td>
                  <span className={`${styles.badge} ${t.status === "active" ? styles.badgeSuccess : styles.badgeWarning}`}>
                    {t.status === "active" ? "فعال" : "در حال راه‌اندازی"}
                  </span>
                </td>
                <td>
                  <span className={`${styles.badge} styles.badgeInfo`}>
                    {t.isolationLevel}
                  </span>
                </td>
                <td style={{ fontWeight: 700, color: t.healthScore >= 98 ? "#67c23a" : "#e6a23c" }}>
                  {t.healthScore}٪
                </td>
                <td>
                  <Link href="/admin/tenants" className={styles.actionBtn}>
                    پایش ایزولاسیون
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 4. Live Audit Alerts & System Telemetry Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "1.5rem" }}>
        {/* Audit Alerts */}
        <div className={styles.tableWrapper}>
          <div style={{ padding: "1rem 1.25rem", borderBottom: "1px solid var(--line)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h2 style={{ fontSize: "1rem", margin: 0, fontWeight: 800 }}>{d.auditAlertsTitle}</h2>
            <Link href="/admin/audit" className={styles.actionBtn}>
              لاگ کامل
            </Link>
          </div>
          <div style={{ padding: "0.5rem 1rem", display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            {auditEvents.map((ev) => (
              <div key={ev.id} style={{ display: "flex", flexDirection: "column", gap: "0.25rem", padding: "0.75rem", background: "#faf8fc", borderRadius: "8px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontWeight: 700, fontSize: "0.8125rem" }}>{ev.action}</span>
                  <span className={`${styles.badge} ${ev.status === "SUCCESS" ? styles.badgeSuccess : styles.badgeDanger}`}>
                    {ev.status}
                  </span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "var(--muted)" }}>
                  <span>{ev.actor}</span>
                  <span dir="ltr">{ev.timestampJalali}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* System Ops Status */}
        <div className={styles.tableWrapper}>
          <div style={{ padding: "1rem 1.25rem", borderBottom: "1px solid var(--line)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h2 style={{ fontSize: "1rem", margin: 0, fontWeight: 800 }}>{d.systemOpsTitle}</h2>
            <Link href="/admin/system" className={styles.actionBtn}>
              جزئیات موتور
            </Link>
          </div>
          <div style={{ padding: "0.5rem 1rem", display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            {sysMetrics.map((met) => (
              <div key={met.key} style={{ display: "flex", flexDirection: "column", gap: "0.25rem", padding: "0.75rem", background: "#faf8fc", borderRadius: "8px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontWeight: 700, fontSize: "0.8125rem" }}>{met.title}</span>
                  <span className={`${styles.badge} styles.badgeSuccess`}>
                    {met.value}
                  </span>
                </div>
                <div style={{ fontSize: "0.75rem", color: "var(--muted)" }}>
                  <span>{met.detail}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
