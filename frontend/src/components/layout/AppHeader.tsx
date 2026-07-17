"use client";

import type { ReactNode, RefObject } from "react";

import type { ShellTone } from "./layout.types";
import styles from "./shell.module.css";

export interface AppHeaderProps {
  brand: ReactNode;
  headerActionsSlot?: ReactNode;
  headerPrimarySlot?: ReactNode;
  isDrawerOpen: boolean;
  menuButtonLabel: string;
  menuButtonRef: RefObject<HTMLButtonElement | null>;
  onMenuOpen: () => void;
  profileSlot?: ReactNode;
  tone: ShellTone;
}

export function AppHeader({
  brand,
  headerActionsSlot,
  headerPrimarySlot,
  isDrawerOpen,
  menuButtonLabel,
  menuButtonRef,
  onMenuOpen,
  profileSlot,
  tone,
}: AppHeaderProps) {
  return (
    <header className={`${styles.header} ${styles[`header${tone[0].toUpperCase()}${tone.slice(1)}`]}`}>
      <button
        aria-controls="codesho-navigation-drawer"
        aria-expanded={isDrawerOpen}
        aria-label={menuButtonLabel}
        className={styles.menuButton}
        onClick={onMenuOpen}
        ref={menuButtonRef}
        type="button"
      >
        <span aria-hidden="true" className={styles.menuIcon}><i /><i /><i /></span>
      </button>
      <div className={styles.headerBrand}>{brand}</div>
      {headerActionsSlot || profileSlot ? (
        <div className={styles.headerActions}>
          {headerActionsSlot ? <div className={styles.headerActionsSlot}>{headerActionsSlot}</div> : null}
          {profileSlot ? <div className={styles.profileSlot}>{profileSlot}</div> : null}
        </div>
      ) : null}
      {headerPrimarySlot ? <div className={styles.headerPrimarySlot}>{headerPrimarySlot}</div> : null}
    </header>
  );
}
