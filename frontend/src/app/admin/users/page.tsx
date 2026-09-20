import type { Metadata } from "next";
import { adminAlphaContent as copy } from "@/content/fa/admin.alpha";
import styles from "../admin.module.css";

export const metadata: Metadata = {
  title: `${copy.brand} | ${copy.users.title}`,
  description: copy.users.subtitle,
};

export default function AdminUsersPage() {
  const u = copy.users;

  return (
    <div className={styles.adminContainer}>
      <div className={styles.headerSection}>
        <div className={styles.noticeBanner}>
          <span>{copy.envNotice}</span>
        </div>
        <h1 className={styles.pageTitle}>{u.title}</h1>
        <p className={styles.pageSubtitle}>{u.subtitle}</p>
      </div>

      {/* Filter Tabs */}
      <div style={{ display: "flex", gap: "0.5rem", borderBottom: "1px solid var(--line)", paddingBottom: "0.75rem" }}>
        <button type="button" className={styles.actionBtn} style={{ background: "#f3eafa", borderColor: "var(--purple)", color: "var(--purple)" }}>
          {u.filters.all} (۴)
        </button>
        <button type="button" className={styles.actionBtn}>
          {u.filters.active} (۳)
        </button>
        <button type="button" className={styles.actionBtn}>
          {u.filters.pending} (۱)
        </button>
      </div>

      <div className={styles.tableWrapper}>
        <table className={styles.adminTable}>
          <thead>
            <tr>
              <th>{u.tableHeaders.user}</th>
              <th>{u.tableHeaders.role}</th>
              <th>{u.tableHeaders.tenant}</th>
              <th>{u.tableHeaders.status}</th>
              <th>{u.tableHeaders.mfa}</th>
              <th>{u.tableHeaders.lastLogin}</th>
              <th>{u.tableHeaders.actions}</th>
            </tr>
          </thead>
          <tbody>
            {u.items.map((user) => (
              <tr key={user.id}>
                <td>
                  <div style={{ display: "flex", flexDirection: "column" }}>
                    <span style={{ fontWeight: 800 }}>{user.fullName}</span>
                    <span dir="ltr" style={{ textAlign: "right", fontSize: "0.75rem", color: "var(--muted)" }}>
                      {user.email}
                    </span>
                  </div>
                </td>
                <td>
                  <span className={`${styles.badge} ${styles.badgeInfo}`}>
                    {user.role}
                  </span>
                </td>
                <td style={{ fontWeight: 600 }}>{user.tenantName}</td>
                <td>
                  <span className={`${styles.badge} ${user.status === "active" ? styles.badgeSuccess : styles.badgeWarning}`}>
                    {user.status === "active" ? "فعال" : "در انتظار تایید"}
                  </span>
                </td>
                <td>
                  <span className={`${styles.badge} ${user.mfaEnabled ? styles.badgeSuccess : styles.badgeDanger}`}>
                    {user.mfaEnabled ? "فعال (TOTP)" : "غیرفعال"}
                  </span>
                </td>
                <td style={{ fontSize: "0.8125rem", color: "var(--muted)" }}>{user.lastLogin}</td>
                <td>
                  <button type="button" className={styles.actionBtn}>
                    مدیریت دسترسی
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
