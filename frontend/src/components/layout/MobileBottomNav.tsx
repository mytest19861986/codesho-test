import type { NavigationItem } from "./layout.types";
import styles from "./shell.module.css";

export interface MobileBottomNavProps {
  activeItemId: string;
  items: NavigationItem[];
  navigationLabel: string;
}

export function MobileBottomNav({ activeItemId, items, navigationLabel }: MobileBottomNavProps) {
  if (items.length > 5) {
    throw new Error("MobileBottomNav accepts at most five navigation items.");
  }

  return (
    <nav aria-label={navigationLabel} className={styles.bottomNavigation}>
      <ul className={styles.bottomNavigationList}>
        {items.map((item) => (
          <li key={item.id}>
            <a
              aria-current={item.id === activeItemId ? "page" : undefined}
              className={`${styles.bottomNavigationLink} ${item.id === activeItemId ? styles.bottomNavigationLinkActive : ""}`}
              href={item.href}
            >
              <span aria-hidden="true" className={styles.navigationIcon}>{item.icon}</span>
              <span>{item.label}</span>
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}
