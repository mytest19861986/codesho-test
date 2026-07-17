"use client";

import { useRef } from "react";

import { PublicNavigationDrawer } from "./PublicNavigationDrawer";
import type { PublicHeaderProps } from "./public-layout.types";
import styles from "./public-shell.module.css";

export function PublicHeader({ actionSlot, activeItemId, brand, drawerCloseLabel, drawerOpen, menuButtonLabel, navigationItems, navigationLabel, onDrawerClose, onDrawerOpen, utilitySlot }: PublicHeaderProps) {
  const menuButtonRef = useRef<HTMLButtonElement>(null);

  return (
    <header className={styles.header}>
      <div className={styles.headerInner}>
        {utilitySlot || actionSlot ? (
          <div className={styles.headerControls}>
            {utilitySlot ? <div className={styles.utilitySlot}>{utilitySlot}</div> : null}
            {actionSlot ? <div className={styles.actionSlot}>{actionSlot}</div> : null}
          </div>
        ) : null}
        <nav aria-label={navigationLabel} className={styles.desktopNavigation}>
          <ul className={styles.desktopNavigationList}>
            {navigationItems.map((item) => (
              <li key={item.id}>
                <a aria-current={item.id === activeItemId ? "page" : undefined} className={`${styles.desktopNavigationLink} ${item.id === activeItemId ? styles.desktopNavigationLinkActive : ""}`} href={item.href}>{item.label}</a>
              </li>
            ))}
          </ul>
        </nav>
        <div className={styles.headerBrand}>{brand}</div>
        <button aria-controls="codesho-public-navigation-drawer" aria-expanded={drawerOpen} aria-label={menuButtonLabel} className={styles.menuButton} onClick={onDrawerOpen} ref={menuButtonRef} type="button">
          <span aria-hidden="true" className={styles.menuIcon}><i /><i /><i /></span>
        </button>
      </div>
      <PublicNavigationDrawer activeItemId={activeItemId} closeLabel={drawerCloseLabel} items={navigationItems} label={navigationLabel} onClose={onDrawerClose} open={drawerOpen} triggerRef={menuButtonRef} />
    </header>
  );
}
