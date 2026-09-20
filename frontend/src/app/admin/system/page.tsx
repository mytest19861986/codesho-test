import type { Metadata } from "next";
import { adminAlphaContent as copy } from "@/content/fa/admin.alpha";
import styles from "../admin.module.css";

export const metadata: Metadata = {
  title: `${copy.brand} | ${copy.system.title}`,
  description: copy.system.subtitle,
};

export default function AdminSystemPage() {
  const s = copy.system;

  return (
    <div className={styles.adminContainer}>
      <div className={styles.headerSection}>
        <div className={styles.noticeBanner}>
          <span>{copy.envNotice}</span>
        </div>
        <h1 className={styles.pageTitle}>{s.title}</h1>
        <p className={styles.pageSubtitle}>{s.subtitle}</p>
      </div>

      {/* System Engine Telemetry */}
      <h2 style={{ fontSize: "1.125rem", margin: "0.5rem 0 0", fontWeight: 800 }}>موتورهای زیرساخت و پردازش</h2>
      <div className={styles.statsGrid}>
        {s.metrics.map((m) => (
          <div key={m.key} className={styles.statCard}>
            <span className={styles.statLabel}>{m.title}</span>
            <span className={styles.statValue} style={{ fontSize: "1.125rem" }}>{m.value}</span>
            <span className={styles.pageSubtitle} style={{ fontSize: "0.75rem" }}>{m.detail}</span>
          </div>
        ))}
      </div>

      {/* Feature Flags & Pilot Controls */}
      <h2 style={{ fontSize: "1.125rem", margin: "1rem 0 0", fontWeight: 800 }}>کنترل پرچم‌های عملیاتی و پایلوت (Simulation)</h2>
      <div className={styles.tableWrapper}>
        <table className={styles.adminTable}>
          <thead>
            <tr>
              <th>عنوان ویژگی</th>
              <th>کلید پیکربندی</th>
              <th>سطح ریسک</th>
              <th>وضعیت فعلی</th>
              <th>شرح کاربرد</th>
              <th>تغییر وضعیت</th>
            </tr>
          </thead>
          <tbody>
            {s.flags.map((f) => (
              <tr key={f.id}>
                <td style={{ fontWeight: 800 }}>{f.name}</td>
                <td dir="ltr" style={{ textAlign: "right", fontFamily: "monospace", fontSize: "0.8125rem", color: "var(--purple)" }}>
                  {f.key}
                </td>
                <td>
                  <span className={`${styles.badge} ${f.riskLevel === "high" ? styles.badgeDanger : styles.badgeWarning}`}>
                    {f.riskLevel.toUpperCase()}
                  </span>
                </td>
                <td>
                  <span className={`${styles.badge} ${f.enabled ? styles.badgeSuccess : styles.badgeDanger}`}>
                    {f.enabled ? "فعال" : "غیرفعال"}
                  </span>
                </td>
                <td style={{ fontSize: "0.8125rem", color: "var(--muted)", maxWidth: "300px" }}>
                  {f.description}
                </td>
                <td>
                  <button type="button" className={styles.actionBtn}>
                    {f.enabled ? "غیرفعال‌سازی" : "فعال‌سازی"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
