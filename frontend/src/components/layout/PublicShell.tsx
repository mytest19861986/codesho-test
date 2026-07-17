"use client";

import { useCallback, useState } from "react";

import { PublicFooter } from "./PublicFooter";
import { PublicHeader } from "./PublicHeader";
import type { PublicShellProps } from "./public-layout.types";
import styles from "./public-shell.module.css";

export function PublicShell({ actionSlot, activeItemId, brand, children, drawerCloseLabel, footerGroups, footerLegalSlot, footerSupportingSlot, menuButtonLabel, navigationItems, navigationLabel, utilitySlot }: PublicShellProps) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const handleDrawerClose = useCallback(() => setDrawerOpen(false), []);
  const handleDrawerOpen = useCallback(() => setDrawerOpen(true), []);

  return (
    <div className={styles.shell} dir="rtl">
      <PublicHeader actionSlot={actionSlot} activeItemId={activeItemId} brand={brand} drawerCloseLabel={drawerCloseLabel} drawerOpen={drawerOpen} menuButtonLabel={menuButtonLabel} navigationItems={navigationItems} navigationLabel={navigationLabel} onDrawerClose={handleDrawerClose} onDrawerOpen={handleDrawerOpen} utilitySlot={utilitySlot} />
      <main className={styles.content}>{children}</main>
      <PublicFooter brand={brand} groups={footerGroups} legalSlot={footerLegalSlot} supportingSlot={footerSupportingSlot} />
    </div>
  );
}
