import type { Metadata } from "next";
import { adminAlphaContent as copy } from "@/content/fa/admin.alpha";
import styles from "../admin.module.css";

export const metadata: Metadata = {
  title: `${copy.brand} | ${copy.governance.title}`,
  description: copy.governance.subtitle,
};

export default function AdminGovernancePage() {
  const g = copy.governance;

  return (
    <div className={styles.adminContainer}>
      <div className={styles.headerSection}>
        <div className={styles.noticeBanner}>
          <span>{copy.envNotice}</span>
        </div>
        <h1 className={styles.pageTitle}>{g.title}</h1>
        <p className={styles.pageSubtitle}>{g.subtitle}</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "1.25rem" }}>
        {g.policies.map((pol) => (
          <div key={pol.id} className={styles.statCard} style={{ gap: "0.75rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h2 style={{ fontSize: "1rem", margin: 0, fontWeight: 800 }}>{pol.title}</h2>
              <span className={`${styles.badge} styles.badgeSuccess`}>
                {pol.status}
              </span>
            </div>
            <p style={{ margin: 0, fontSize: "0.8125rem", color: "var(--muted)", lineHeight: "1.7" }}>
              {pol.description}
            </p>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid var(--line)", paddingTop: "0.75rem", fontSize: "0.75rem" }}>
              <span style={{ color: "var(--muted)" }}>ضمانت اجرا:</span>
              <span style={{ fontWeight: 700, color: "var(--purple)" }}>{pol.enforcement}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
