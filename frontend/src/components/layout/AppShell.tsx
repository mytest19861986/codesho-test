"use client";

import { useCallback, useRef, useState } from "react";

import { AppHeader } from "./AppHeader";
import { MobileBottomNav } from "./MobileBottomNav";
import { NavigationDrawer } from "./NavigationDrawer";
import type { AppShellProps } from "./layout.types";
import { Sidebar } from "./Sidebar";
import styles from "./shell.module.css";

export function AppShell({
  activeItemId,
  brand,
  children,
  drawerCloseLabel,
  headerActionsSlot,
  headerPrimarySlot,
  menuButtonLabel,
  navigationItems,
  navigationLabel,
  profileSlot,
  sidebarFooterSlot,
  sidebarSupplementarySlot,
  tone,
}: AppShellProps) {
  if (navigationItems.length > 5) {
    throw new Error("AppShell accepts at most five navigation items for mobile navigation.");
  }
  const [drawerOpen, setDrawerOpen] = useState(false);
  const menuButtonRef = useRef<HTMLButtonElement>(null);
  const handleClose = useCallback(() => setDrawerOpen(false), []);

  return (
    <div className={`${styles.shell} ${styles[`shell${tone[0].toUpperCase()}${tone.slice(1)}`]}`} dir="rtl">
      <Sidebar
        activeItemId={activeItemId}
        brand={brand}
        navigationItems={navigationItems}
        navigationLabel={navigationLabel}
        footerSlot={sidebarFooterSlot}
        supplementarySlot={sidebarSupplementarySlot}
        tone={tone}
      />
      <div className={styles.shellMain}>
        <AppHeader
          brand={brand}
          headerActionsSlot={headerActionsSlot}
          headerPrimarySlot={headerPrimarySlot}
          isDrawerOpen={drawerOpen}
          menuButtonLabel={menuButtonLabel}
          menuButtonRef={menuButtonRef}
          onMenuOpen={() => setDrawerOpen(true)}
          profileSlot={profileSlot}
          tone={tone}
        />
        <main className={styles.shellContent}>{children}</main>
      </div>
      <MobileBottomNav activeItemId={activeItemId} items={navigationItems} navigationLabel={navigationLabel} />
      <NavigationDrawer
        activeItemId={activeItemId}
        closeLabel={drawerCloseLabel}
        items={navigationItems}
        label={navigationLabel}
        onClose={handleClose}
        open={drawerOpen}
        triggerRef={menuButtonRef}
      />
    </div>
  );
}
