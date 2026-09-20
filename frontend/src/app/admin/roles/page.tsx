"use client";

import { useState } from "react";
import { adminAlphaContent as copy } from "@/content/fa/admin.alpha";
import styles from "../admin.module.css";

export default function AdminRolesPage() {
  const r = copy.roles;
  const [selectedRole, setSelectedRole] = useState<string | null>(null);

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
                  <button
                    type="button"
                    className={styles.actionBtn}
                    onClick={() => setSelectedRole(selectedRole === role.id ? null : role.id)}
                  >
                    {selectedRole === role.id ? "بستن جزئیات" : r.tableHeaders.actions}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedRole && (
        <div className={styles.statCard} style={{ borderColor: "var(--purple)", background: "#fbf9fe", gap: "0.75rem" }}>
          <h2 style={{ fontSize: "1rem", margin: 0, fontWeight: 800, color: "var(--purple)" }}>
            ماتریس دسترسی و سیاست‌های امنیتی نقش ({selectedRole})
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "0.75rem", fontSize: "0.8125rem" }}>
            <div style={{ padding: "0.5rem", background: "#fff", borderRadius: "6px", border: "1px solid var(--line)" }}>
              <strong>دسترسی چندمستأجری:</strong> {selectedRole === "r-superadmin" ? "سراسری (Cross-tenant)" : "محدود به سازمان (Isolated)"}
            </div>
            <div style={{ padding: "0.5rem", background: "#fff", borderRadius: "6px", border: "1px solid var(--line)" }}>
              <strong>مجوزهای ثبت‌شده:</strong> {r.items.find(x => x.id === selectedRole)?.permissionsCount} مجوز فعال
            </div>
            <div style={{ padding: "0.5rem", background: "#fff", borderRadius: "6px", border: "1px solid var(--line)" }}>
              <strong>سطح تغییرناپذیری:</strong> {selectedRole === "r-superadmin" || selectedRole === "r-auditor" ? "سیستمی رزروشده" : "قابل تنظیم سازمانی"}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
