import {
  IconArrowUp,
  IconChart,
  IconCheck,
  IconGraduate,
  IconLaptop,
  IconShield,
  IconSparkles,
  IconStar,
  IconTarget,
  IconUser,
  IconUsers,
} from "@/components/ui/Icons";
import { homepageAlphaContent } from "@/content/fa/homepage.alpha";
import styles from "./valueSections.module.css";

export function WhyCodeshoSection() {
  const content = homepageAlphaContent.whyCodesho;
  const icons = [IconTarget, IconLaptop, IconSparkles, IconShield];

  return (
    <section className={styles.section} aria-labelledby="why-codesho-heading">
      <div className={styles.sectionHeader}>
        <div className={styles.tag}>
          <IconStar className={styles.tagIcon} />
          <span>ارزش‌های متمایز کدشو</span>
        </div>
        <h2 id="why-codesho-heading" className={styles.heading}>
          {content.heading}
        </h2>
        <p className={styles.subheading}>{content.subheading}</p>
      </div>

      <div className={styles.grid}>
        {content.pillars.map((pillar, idx) => {
          const IconComp = icons[idx % icons.length];
          return (
            <div key={pillar.id} className={styles.card}>
              <div className={styles.cardIconWrapper}>
                <IconComp className={styles.cardIcon} />
              </div>
              <h3 className={styles.cardTitle}>{pillar.title}</h3>
              <p className={styles.cardDescription}>{pillar.description}</p>
            </div>
          );
        })}
      </div>
    </section>
  );
}

export function RolePortalsSection() {
  const content = homepageAlphaContent.rolePortals;
  const portalIcons = [IconGraduate, IconUsers, IconUser];

  return (
    <section className={styles.sectionAlt} aria-labelledby="portals-heading">
      <div className={styles.sectionHeader}>
        <div className={styles.tag}>
          <IconLaptop className={styles.tagIcon} />
          <span>اکوسیستم یکپارچه آموزشی</span>
        </div>
        <h2 id="portals-heading" className={styles.heading}>
          {content.heading}
        </h2>
        <p className={styles.subheading}>{content.subheading}</p>
      </div>

      <div className={styles.portalGrid}>
        {content.portals.map((p, idx) => {
          const IconComp = portalIcons[idx % portalIcons.length];
          return (
            <div key={p.id} className={styles.portalCard}>
              <div className={styles.portalHeader}>
                <div className={styles.portalIconWrapper}>
                  <IconComp className={styles.portalIcon} />
                </div>
                <h3 className={styles.portalTitle}>{p.title}</h3>
              </div>
              <p className={styles.portalDescription}>{p.description}</p>
              <a href={p.action.destination.route} className={styles.portalAction}>
                <span>{p.action.label}</span>
                <span className={styles.arrowIcon}>←</span>
              </a>
            </div>
          );
        })}
      </div>
    </section>
  );
}
