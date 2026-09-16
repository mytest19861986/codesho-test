import type { ReactNode } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout";
import { studentAlphaContent as copy } from "@/content/fa/student.alpha";
import styles from "./student.module.css";

interface StudentLayoutProps {
  children: ReactNode;
}

export default function StudentLayout({ children }: StudentLayoutProps) {
  const navigationItems = copy.navigation.map((item) => ({
    id: item.id,
    label: item.label,
    href: item.href,
    icon: <span aria-hidden="true">{copy.indicators.bullet}</span>,
  }));

  const brandSlot = (
    <div className={styles.sidebarBrandArea}>
      <Link href="/student" className={styles.brandLogoTitle}>
        <span aria-hidden="true">{copy.icons.brandCode}</span>
        <span>{copy.brand}</span>
      </Link>
      <span className={styles.brandTagline}>{copy.tagline}</span>
    </div>
  );

  const headerSearchSlot = (
    <div className={styles.headerSearchWrapper}>
      <span aria-hidden="true" className={styles.searchIcon}>{copy.icons.search}</span>
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
        <span aria-hidden="true">{copy.icons.bell}</span>
        <span className={styles.notifBadge}>{copy.shell.unreadCount}</span>
      </button>
      <div className={styles.userProfileBadge}>
        <div className={styles.userInfo}>
          <span className={styles.userRole}>{copy.shell.roleLabel}</span>
          <span className={styles.userName}>{copy.shell.userName}</span>
        </div>
        <div className={styles.userAvatar} aria-hidden="true">
          <span>{copy.shell.userName.slice(0, 1)}</span>
        </div>
      </div>
    </div>
  );

  const sidebarSupplementarySlot = (
    <div className={styles.sidebarFooterLinks}>
      <Link href="/student" className={styles.sidebarUtilityLink}>
        <span aria-hidden="true">{copy.icons.settings}</span>
        <span>{copy.shell.settingsLabel}</span>
      </Link>
      <Link href="/student" className={styles.sidebarUtilityLink}>
        <span aria-hidden="true">{copy.icons.support}</span>
        <span>{copy.shell.supportLabel}</span>
      </Link>
    </div>
  );

  const sidebarFooterSlot = (
    <div className={styles.sidebarPromoCard}>
      <p className={styles.sidebarPromoTitle}>{copy.shell.sidebarPromoTitle}</p>
      <p className={styles.sidebarPromoSubtitle}>{copy.shell.sidebarPromoSubtitle}</p>
      <Link href="/student/learning" className={styles.sidebarPromoButton}>
        {copy.shell.sidebarPromoButton}
      </Link>
    </div>
  );

  return (
    <AppShell
      activeItemId="dashboard"
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
