import type { PublicFooterProps } from "./public-layout.types";
import styles from "./public-shell.module.css";

export function PublicFooter({ brand, groups, legalSlot, supportingSlot }: PublicFooterProps) {
  return (
    <footer className={styles.footer}>
      <div className={styles.footerInner}>
        <div className={styles.footerIntro}>
          <div className={styles.footerBrand}>{brand}</div>
          {supportingSlot ? <div className={styles.footerSupportingSlot}>{supportingSlot}</div> : null}
        </div>
        <div className={styles.footerGroups}>
          {groups.map((group) => (
            <section className={styles.footerGroup} key={group.id}>
              <h2 className={styles.footerGroupLabel}>{group.label}</h2>
              <ul className={styles.footerLinks}>
                {group.links.map((link) => <li key={link.id}><a href={link.href}>{link.label}</a></li>)}
              </ul>
            </section>
          ))}
        </div>
      </div>
      {legalSlot ? <div className={styles.footerLegal}>{legalSlot}</div> : null}
    </footer>
  );
}
