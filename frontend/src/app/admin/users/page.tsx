"use client";

import { useState } from "react";
import { adminAlphaContent as copy } from "@/content/fa/admin.alpha";
import styles from "../admin.module.css";

export default function AdminUsersPage() {
  const u = copy.users;
  const [filter, setFilter] = useState<"all" | "active" | "pending">("all");
  const [search, setSearch] = useState("");
  const [selectedUser, setSelectedUser] = useState<string | null>(null);

  const filteredItems = u.items.filter((user) => {
    if (filter === "active" && user.status !== "active") return false;
    if (filter === "pending" && user.status !== "pending") return false;
    if (search.trim()) {
      const q = search.toLowerCase();
      return (
        user.fullName.toLowerCase().includes(q) ||
        user.email.toLowerCase().includes(q) ||
        user.role.toLowerCase().includes(q) ||
        user.tenantName.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div className={styles.adminContainer}>
      <div className={styles.headerSection}>
        <div className={styles.noticeBanner}>
          <span>{copy.envNotice}</span>
        </div>
        <h1 className={styles.pageTitle}>{u.title}</h1>
        <p className={styles.pageSubtitle}>{u.subtitle}</p>
      </div>

      {/* Filter and Search Controls */}
      <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", gap: "1rem", alignItems: "center" }}>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button
            type="button"
            className={styles.actionBtn}
            style={filter === "all" ? { background: "#f3eafa", borderColor: "var(--purple)", color: "var(--purple)", fontWeight: 800 } : {}}
            onClick={() => setFilter("all")}
          >
            {u.filters.all} ({u.items.length})
          </button>
          <button
            type="button"
            className={styles.actionBtn}
            style={filter === "active" ? { background: "#f3eafa", borderColor: "var(--purple)", color: "var(--purple)", fontWeight: 800 } : {}}
            onClick={() => setFilter("active")}
          >
            {u.filters.active} ({u.items.filter(x => x.status === "active").length})
          </button>
          <button
            type="button"
            className={styles.actionBtn}
            style={filter === "pending" ? { background: "#f3eafa", borderColor: "var(--purple)", color: "var(--purple)", fontWeight: 800 } : {}}
            onClick={() => setFilter("pending")}
          >
            {u.filters.pending} ({u.items.filter(x => x.status === "pending").length})
          </button>
        </div>

        <input
          type="search"
          placeholder="جستجوی کاربر بر اساس نام یا ایمیل..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className={styles.actionBtn}
          style={{ width: "260px", padding: "0.5rem 0.75rem", textAlign: "right" }}
        />
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
            {filteredItems.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ textAlign: "center", padding: "2rem", color: "var(--muted)" }}>
                  هیچ کاربری با فیلترهای جاری یافت نشد.
                </td>
              </tr>
            ) : (
              filteredItems.map((user) => (
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
                    <button
                      type="button"
                      className={styles.actionBtn}
                      onClick={() => setSelectedUser(selectedUser === user.id ? null : user.id)}
                    >
                      {selectedUser === user.id ? "بستن جزئیات" : "مدیریت دسترسی"}
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {selectedUser && (
        <div className={styles.statCard} style={{ borderColor: "var(--purple)", background: "#fbf9fe" }}>
          <h2 style={{ fontSize: "1rem", margin: 0, fontWeight: 800, color: "var(--purple)" }}>
            پیکربندی هویت و انتساب نقش (نمای شبیه‌سازی حاکمیتی)
          </h2>
          <p style={{ margin: 0, fontSize: "0.8125rem", color: "var(--muted)" }}>
            شناسه کاربر: <code dir="ltr">{selectedUser}</code> | تغییر وضعیت و لغو نشست‌ها در این پنل شبیه‌سازی بصری است و تغییرات بر روی بانک داده اصلی اثر واقعی ندارد.
          </p>
        </div>
      )}
    </div>
  );
}
