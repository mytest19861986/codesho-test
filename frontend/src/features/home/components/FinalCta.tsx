import type { HomepageAlphaContent } from "../home.types";

import styles from "./finalCta.module.css";

export interface FinalCtaProps {
  readonly content: HomepageAlphaContent["finalCta"];
}

export function FinalCta({ content }: FinalCtaProps) {
  const actions = [content.primaryAction, content.secondaryAction].filter(
    (action) => action.destination.status === "available",
  );

  return (
    <section className={styles.section}>
      <div className={styles.panel}>
        <h2 className={styles.heading}>{content.title}</h2>
        {actions.length > 0 ? (
          <div className={styles.actions}>
            {actions.map((action) => (
              <a className={styles.action} href={action.destination.route} key={action.id}>{action.label}</a>
            ))}
          </div>
        ) : null}
      </div>
    </section>
  );
}
