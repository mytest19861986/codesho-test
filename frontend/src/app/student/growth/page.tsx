import type { Metadata } from "next";
import Link from "next/link";
import { studentAlphaContent as copy } from "@/content/fa/student.alpha";
import { Badge } from "@/components/ui";
import styles from "../student.module.css";

export const metadata: Metadata = {
  title: `${copy.brand} | ${copy.growth.title}`,
  description: copy.growth.description,
};

export default function StudentGrowthPage() {
  const g = copy.growth;

  return (
    <div className={styles.studentDashboard}>
      <header className={styles.heroCard} aria-labelledby="growth-title">
        <h1 id="growth-title" className={styles.heroTitle}>
          {g.title}
        </h1>
        <p className={styles.heroWelcome}>{g.description}</p>
      </header>

      <div className={styles.stateGrid}>
        <section className={styles.stateCard} aria-labelledby="skills-heading">
          <h2 id="skills-heading" className={styles.cardHeading}>
            {g.skillsTitle}
          </h2>
          <ul className={styles.listGroup}>
            <li className={styles.listItem}>
              <span className={styles.cardText}>{g.skill1}</span>
              <Badge variant="success">{copy.indicators.check}</Badge>
            </li>
            <li className={styles.listItem}>
              <span className={styles.cardText}>{g.skill2}</span>
              <Badge variant="success">{copy.indicators.check}</Badge>
            </li>
            <li className={styles.listItem}>
              <span className={styles.cardText}>{g.skill3}</span>
              <Badge variant="info">{copy.indicators.bullet}</Badge>
            </li>
          </ul>
        </section>

        <section className={styles.stateCard} aria-labelledby="milestones-heading">
          <h2 id="milestones-heading" className={styles.cardHeading}>
            {g.milestoneTitle}
          </h2>
          <ul className={styles.listGroup}>
            <li className={styles.listItem}>
              <span className={styles.cardText}>{g.milestone1}</span>
              <Badge variant="primary">{copy.indicators.step1}</Badge>
            </li>
            <li className={styles.listItem}>
              <span className={styles.cardText}>{g.milestone2}</span>
              <Badge variant="primary">{copy.indicators.step2}</Badge>
            </li>
          </ul>
          <Link href="/student" className={`${styles.actionButton} ${styles.secondaryAction}`}>
            {copy.learning.actionContinue}
          </Link>
        </section>
      </div>
    </div>
  );
}
