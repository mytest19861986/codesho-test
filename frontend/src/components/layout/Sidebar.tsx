import type { ReactNode } from "react";

import type { NavigationItem, ShellTone } from "./layout.types";
import styles from "./shell.module.css";

export interface SidebarProps {
  activeItemId: string;
  brand: ReactNode;
  navigationItems: NavigationItem[];
  navigationLabel: string;
  footerSlot?: ReactNode;
  supplementarySlot?: ReactNode;
  tone: ShellTone;
}

export function Sidebar({ activeItemId, brand, navigationItems, navigationLabel, footerSlot, supplementarySlot, tone }: SidebarProps) {
  return (
    <aside className={`${styles.sidebar} ${styles[`sidebar${tone[0].toUpperCase()}${tone.slice(1)}`]}`}>
      <div className={styles.sidebarBrand}>{brand}</div>
      <nav aria-label={navigationLabel}>
        <ul className={styles.navigationList}>
          {navigationItems.map((item) => (
            <li key={item.id}>
              <a
                aria-current={item.id === activeItemId ? "page" : undefined}
                className={`${styles.navigationLink} ${item.id === activeItemId ? styles.navigationLinkActive : ""}`}
                href={item.href}
              >
                <span aria-hidden="true" className={styles.navigationIcon}>{item.icon}</span>
                <span>{item.label}</span>
                {item.badge ? <span className={styles.navigationBadge}>{item.badge}</span> : null}
              </a>
            </li>
          ))}
        </ul>
      </nav>
      {supplementarySlot ? <div className={styles.sidebarSupplementarySlot}>{supplementarySlot}</div> : null}
      {footerSlot ? <div className={styles.sidebarFooterSlot}>{footerSlot}</div> : null}
    </aside>
  );
}
