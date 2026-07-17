import type { HomepageAlphaContent } from "../home.types";

import { LearningPathCard } from "./LearningPathCard";
import styles from "./learningPaths.module.css";

export interface LearningPathGridProps {
  readonly heading: HomepageAlphaContent["learningPathsHeading"];
  readonly paths: HomepageAlphaContent["learningPaths"];
}

export function LearningPathGrid({ heading, paths }: LearningPathGridProps) {
  return (
    <section className={styles.section}>
      <h2 className={styles.heading}>{heading}</h2>
      <div className={styles.grid}>
        {paths.map((path) => <LearningPathCard key={path.id} path={path} />)}
      </div>
    </section>
  );
}
