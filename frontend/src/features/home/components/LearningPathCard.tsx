import type { HomepageLearningPath } from "../home.types";

import styles from "./learningPaths.module.css";

export interface LearningPathCardProps {
  readonly path: HomepageLearningPath;
}

export function LearningPathCard({ path }: LearningPathCardProps) {
  const hasAvailableDestination = path.action.destination.status === "available";

  return (
    <article className={styles.card}>
      <h2 className={styles.cardTitle}>{path.title}</h2>
      <p className={styles.cardDescription}>{path.description}</p>
      {hasAvailableDestination ? (
        <a className={styles.cardAction} href={path.action.destination.route}>{path.action.label}</a>
      ) : null}
    </article>
  );
}
