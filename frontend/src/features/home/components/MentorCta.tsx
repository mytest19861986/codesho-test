import type { HomepageAlphaContent } from "../home.types";

import styles from "./mentorCta.module.css";

export interface MentorCtaProps {
  readonly content: HomepageAlphaContent["mentor"];
}

export function MentorCta({ content }: MentorCtaProps) {
  const hasAvailableDestination = content.action.destination.status === "available";

  return (
    <section className={styles.section}>
      <div className={styles.panel}>
        <h2 className={styles.heading}>{content.title}</h2>
        {hasAvailableDestination ? (
          <a className={styles.action} href={content.action.destination.route}>{content.action.label}</a>
        ) : null}
      </div>
    </section>
  );
}
