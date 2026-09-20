import type { Metadata } from "next";
import Link from "next/link";
import { adminAlphaContent as copy } from "@/content/fa/admin.alpha";
import styles from "../admin.module.css";

export const metadata: Metadata = {
  title: `${copy.brand} | ${copy.tenants.title}`,
  description: copy.tenants.subtitle,
};

export default function AdminTenantsPage() {
  const t = copy.tenants;

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
                  <button type="button" className={styles.actionBtn}>
                    بررسی تفکیک داده
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
