"use client";

import type { ReactNode } from "react";
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
  IconDocument,
  IconLaptop,
  IconClock,
} from "@/components/ui";
import { mentorAlphaContent as copy } from "@/content/fa/mentor.alpha";
import styles from "../student/student.module.css";

interface MentorLayoutProps {
  children: ReactNode;
}

const navIcons: Record<string, ReactNode> = {
  overview: <IconChart aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />,
  reviews: <IconDocument aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />,
  students: <IconLaptop aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />,
  sessions: <IconClock aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />,
};

export default function MentorLayout({ children }: MentorLayoutProps) {
  const pathname = usePathname();

  let activeItemId = "overview";
  if (pathname.includes("/reviews")) activeItemId = "reviews";
  else if (pathname.includes("/students")) activeItemId = "students";
  else if (pathname.includes("/sessions")) activeItemId = "sessions";

  const navigationItems = copy.navigation.map((item) => ({
    id: item.id,
    label: item.label,
    href: item.href,
    icon: navIcons[item.id] || <IconChart aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />,
  }));

  const brandSlot = (
    <div className={styles.sidebarBrandArea}>
      <Link href="/mentor" className={styles.brandLogoTitle}>
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
        type="search"
        className={styles.searchInput}
        placeholder={copy.shell.searchPlaceholder}
        aria-label={copy.shell.searchPlaceholder}
        readOnly
      />
      <span className={styles.searchShortcut}>{copy.shell.searchShortcut}</span>
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
        <div className={styles.userAvatar} aria-hidden="true" style={{ background: "rgba(16, 185, 129, 0.15)", color: "#059669" }}>
          <span>{copy.shell.userName.slice(0, 1)}</span>
        </div>
      </div>
    </div>
  );

  const sidebarSupplementarySlot = (
    <div className={styles.sidebarFooterLinks}>
      <Link href="/mentor" className={styles.sidebarUtilityLink}>
        <IconSettings aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
        <span>{copy.shell.settingsLabel}</span>
      </Link>
      <Link href="/mentor" className={styles.sidebarUtilityLink}>
        <IconSupport aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
        <span>{copy.shell.supportLabel}</span>
      </Link>
    </div>
  );

  const sidebarFooterSlot = (
    <div className={styles.sidebarPromoCard}>
      <p className={styles.sidebarPromoTitle}>{copy.shell.sidebarPromoTitle}</p>
      <p className={styles.sidebarPromoSubtitle}>{copy.shell.sidebarPromoSubtitle}</p>
      <button type="button" className={styles.sidebarPromoButton}>
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
      tone="mentor"
    >
      {children}
    </AppShell>
  );
}
