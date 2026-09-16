import type { Metadata } from "next";
import Link from "next/link";
import { studentAlphaContent as copy } from "@/content/fa/student.alpha";
import { Badge } from "@/components/ui";
import styles from "../student.module.css";

export const metadata: Metadata = {
  title: `${copy.brand} | ${copy.coaching.title}`,
  description: copy.coaching.description,
};

export default function StudentCoachingPage() {
  const c = copy.coaching;

  return (
    <div className={styles.studentDashboard}>
      <header className={styles.heroCard} aria-labelledby="coaching-title">
        <h1 id="coaching-title" className={styles.heroTitle}>
          {c.title}
        </h1>
        <p className={styles.heroWelcome}>{c.description}</p>
        <div className={styles.badgeRow}>
          <Badge variant="info">{c.sourceLabel}</Badge>
        </div>
      </header>

      <section className={styles.stateCard} aria-labelledby="advice-title">
        <h2 id="advice-title" className={styles.cardHeading}>
          {c.adviceTitle}
        </h2>
        <p className={styles.cardText}>{c.adviceText}</p>
        <div>
          <Link href="/student" className={styles.actionButton}>
            {c.actionPrompt}
          </Link>
        </div>
      </section>
    </div>
  );
}
