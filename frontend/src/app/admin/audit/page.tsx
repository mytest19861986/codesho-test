import type { Metadata } from "next";
import { adminAlphaContent as copy } from "@/content/fa/admin.alpha";
import styles from "../admin.module.css";

export const metadata: Metadata = {
  title: `${copy.brand} | ${copy.audit.title}`,
  description: copy.audit.subtitle,
};

export default function AdminAuditPage() {
  const a = copy.audit;

  return (
    <div className={styles.adminContainer}>
      <div className={styles.headerSection}>
        <div className={styles.noticeBanner}>
          <span>{copy.envNotice}</span>
        </div>
        <h1 className={styles.pageTitle}>{a.title}</h1>
        <p className={styles.pageSubtitle}>{a.subtitle}</p>
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
            {a.events.map((ev) => (
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
