import Image from "next/image";

import type { HomepageAlphaContent } from "../home.types";
import styles from "./homeHero.module.css";

export interface HomeHeroProps {
  readonly content: HomepageAlphaContent["hero"];
}

export function HomeHero({ content }: HomeHeroProps) {
  const actions = [content.primaryAction, content.secondaryAction].filter(
    (action) => action.destination.status === "available",
  );

  return (
    <section aria-labelledby="homepage-hero-title" className={styles.hero}>
      <div className={styles.copy}>
        <p className={styles.eyebrow}>{content.eyebrow}</p>
        <h1 className={styles.title} id="homepage-hero-title">{content.title}</h1>
        <p className={styles.description}>{content.description}</p>
        {actions.length > 0 ? (
          <div className={styles.actions}>
            {actions.map((action) => (
              <a className={styles.action} href={action.destination.route} key={action.id}>{action.label}</a>
            ))}
          </div>
        ) : null}
      </div>
      <div className={styles.media}>
        <Image alt={content.illustration.alt} className={styles.image} height={content.illustration.height} priority src={content.illustration.src} width={content.illustration.width} />
      </div>
    </section>
  );
}
