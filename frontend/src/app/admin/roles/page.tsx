import type { Metadata } from "next";
import { adminAlphaContent as copy } from "@/content/fa/admin.alpha";
import styles from "../admin.module.css";

export const metadata: Metadata = {
  title: `${copy.brand} | ${copy.roles.title}`,
  description: copy.roles.subtitle,
};

export default function AdminRolesPage() {
  const r = copy.roles;

  return (
    <div className={styles.adminContainer}>
      <div className={styles.headerSection}>
        <div className={styles.noticeBanner}>
          <span>{copy.envNotice}</span>
        </div>
        <h1 className={styles.pageTitle}>{r.title}</h1>
        <p className={styles.pageSubtitle}>{r.subtitle}</p>
      </div>

      <div className={styles.tableWrapper}>
        <table className={styles.adminTable}>
          <thead>
            <tr>
              <th>{r.tableHeaders.role}</th>
              <th>{r.tableHeaders.code}</th>
              <th>{r.tableHeaders.description}</th>
              <th>{r.tableHeaders.scope}</th>
              <th>{r.tableHeaders.usersCount}</th>
              <th>{r.tableHeaders.actions}</th>
            </tr>
          </thead>
          <tbody>
            {r.items.map((role) => (
              <tr key={role.id}>
                <td style={{ fontWeight: 800 }}>{role.roleName}</td>
                <td dir="ltr" style={{ textAlign: "right", fontFamily: "monospace", fontSize: "0.8125rem", color: "var(--purple)" }}>
                  {role.roleCode}
                </td>
                <td style={{ fontSize: "0.8125rem", maxWidth: "320px", lineHeight: "1.6" }}>
                  {role.description}
                </td>
                <td>
                  <span className={`${styles.badge} ${role.systemReserved ? styles.badgeDanger : styles.badgeInfo}`}>
                    {role.scope}
                  </span>
                </td>
                <td style={{ fontWeight: 700 }}>{role.userCount} کاربر</td>
                <td>
                  <button type="button" className={styles.actionBtn}>
                    {r.tableHeaders.actions}
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
