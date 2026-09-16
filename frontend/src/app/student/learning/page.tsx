import type { Metadata } from "next";
import Link from "next/link";
import { studentAlphaContent as copy } from "@/content/fa/student.alpha";
import { Badge } from "@/components/ui";
import styles from "../student.module.css";

export const metadata: Metadata = {
  title: `${copy.brand} | ${copy.learning.title}`,
  description: copy.learning.description,
};

export default function StudentLearningPage() {
  const l = copy.learning;

  return (
    <div className={styles.studentDashboard}>
      <header className={styles.heroCard} aria-labelledby="learning-title">
        <h1 id="learning-title" className={styles.heroTitle}>
          {l.title}
        </h1>
        <p className={styles.heroWelcome}>{l.description}</p>
        <div className={styles.badgeRow}>
          <Badge variant="primary">{l.currentPath}</Badge>
        </div>
      </header>

      <section className={styles.stateCard} aria-labelledby="modules-title">
        <h2 id="modules-title" className={styles.cardHeading}>
          {copy.dashboard.activeLearningTitle}
        </h2>
        <ul className={styles.listGroup}>
          <li className={styles.listItem}>
            <span className={styles.cardText}>{l.module1Title}</span>
            <Badge variant="success">{l.module1Status}</Badge>
          </li>
          <li className={styles.listItem}>
            <span className={styles.cardText}>{l.module2Title}</span>
            <Badge variant="warning">{l.module2Status}</Badge>
          </li>
          <li className={styles.listItem}>
            <span className={styles.cardText}>{l.module3Title}</span>
            <Badge variant="danger">{l.module3Status}</Badge>
          </li>
        </ul>
        <div style={{ marginTop: "1rem" }}>
          <Link href="/student" className={styles.actionButton}>
            {l.actionContinue}
          </Link>
        </div>
      </section>
    </div>
  );
}
