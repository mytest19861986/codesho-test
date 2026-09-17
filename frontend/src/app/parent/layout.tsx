"use client";

import { type ReactNode, useEffect, useRef } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { AppShell } from "@/components/layout";
import {
  IconBrand,
  IconSearch,
  IconBell,
  IconSettings,
  IconSupport,
  IconChart,
  IconTrending,
  IconDocument,
  IconCheck,
  IconClose,
} from "@/components/ui";
import { parentAlphaContent as copy } from "@/content/fa/parent.alpha";
import { ParentSearchProvider, useParentSearch } from "./ParentSearchContext";
import styles from "../student/student.module.css";

interface ParentLayoutProps {
  children: ReactNode;
}

const navIcons: Record<string, ReactNode> = {
  overview: <IconChart aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />,
  progress: <IconTrending aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />,
  finance: <IconDocument aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />,
  consent: <IconCheck aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />,
};

function ParentLayoutInner({ children }: ParentLayoutProps) {
  const pathname = usePathname();
  const { searchQuery, setSearchQuery, setOpenConsentModal } = useParentSearch();
  const searchInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  let activeItemId = "overview";
  if (pathname.includes("/progress")) activeItemId = "progress";
  else if (pathname.includes("/finance")) activeItemId = "finance";
  else if (pathname.includes("/consent")) activeItemId = "consent";

  const navigationItems = copy.navigation.map((item) => ({
    id: item.id,
    label: item.label,
    href: item.href,
    icon: navIcons[item.id] || <IconChart aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />,
  }));

  const brandSlot = (
    <div className={styles.sidebarBrandArea}>
      <Link href="/parent" className={styles.brandLogoTitle}>
        <IconBrand aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
        <span>{copy.brand}</span>
      </Link>
      <span className={styles.brandTagline}>{copy.tagline}</span>
    </div>
  );

  const headerSearchSlot = (
    <div className={styles.headerSearchWrapper}>
      <IconSearch aria-hidden="true" className={styles.searchIcon} style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
      <input
        ref={searchInputRef}
        type="search"
        className={styles.searchInput}
        placeholder={copy.shell.searchPlaceholder}
        aria-label={copy.shell.searchPlaceholder}
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />
      {searchQuery ? (
        <button
          type="button"
          onClick={() => setSearchQuery("")}
          className={styles.searchClearBtn}
          aria-label="پاک کردن جستجو"
        >
          <IconClose aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem" }} />
        </button>
      ) : (
        <span className={styles.searchShortcut}>{copy.shell.searchShortcut}</span>
      )}
    </div>
  );

  const headerActionsSlot = (
    <div className={styles.headerActionsArea}>
      <button
        type="button"
        className={styles.notifButton}
        aria-label={copy.shell.notificationsLabel}
      >
        <IconBell aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />
        <span className={styles.notifBadge}>{copy.shell.unreadCount}</span>
      </button>
      <div className={styles.userProfileBadge}>
        <div className={styles.userInfo}>
          <span className={styles.userRole}>{copy.shell.roleLabel}</span>
          <span className={styles.userName}>{copy.shell.userName}</span>
        </div>
        <div className={styles.userAvatar} aria-hidden="true" style={{ background: "rgba(99, 102, 241, 0.15)", color: "#4f46e5" }}>
          <span>{copy.shell.userName.slice(0, 1)}</span>
        </div>
      </div>
    </div>
  );

  const sidebarSupplementarySlot = (
    <div className={styles.sidebarFooterLinks}>
      <Link href="/parent" className={styles.sidebarUtilityLink}>
        <IconSettings aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
        <span>{copy.shell.settingsLabel}</span>
      </Link>
      <Link href="/parent" className={styles.sidebarUtilityLink}>
        <IconSupport aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
        <span>{copy.shell.supportLabel}</span>
      </Link>
    </div>
  );

  const sidebarFooterSlot = (
    <div className={styles.sidebarPromoCard}>
      <p className={styles.sidebarPromoTitle}>{copy.shell.sidebarPromoTitle}</p>
      <p className={styles.sidebarPromoSubtitle}>{copy.shell.sidebarPromoSubtitle}</p>
      <button
        type="button"
        className={styles.sidebarPromoButton}
        onClick={() => setOpenConsentModal(true)}
      >
        {copy.shell.sidebarPromoButton}
      </button>
    </div>
  );

  return (
    <AppShell
      activeItemId={activeItemId}
      brand={brandSlot}
      bottomNavigationItems={navigationItems}
      drawerCloseLabel={copy.shell.drawerCloseLabel}
      menuButtonLabel={copy.shell.menuButtonLabel}
      navigationItems={navigationItems}
      navigationLabel={copy.shell.navigationLabel}
      headerPrimarySlot={headerSearchSlot}
      headerActionsSlot={headerActionsSlot}
      sidebarSupplementarySlot={sidebarSupplementarySlot}
      sidebarFooterSlot={sidebarFooterSlot}
      tone="learner"
    >
      {children}
    </AppShell>
  );
}

export default function ParentLayout({ children }: ParentLayoutProps) {
  return (
    <ParentSearchProvider>
      <ParentLayoutInner>{children}</ParentLayoutInner>
    </ParentSearchProvider>
  );
}
