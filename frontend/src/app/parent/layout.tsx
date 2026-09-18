"use client";

import { type ReactNode, useState, useEffect, useRef } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { AppShell, NotificationPopover, type DemoNotification } from "@/components/layout";
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

const initialParentNotifications: DemoNotification[] = [
  {
    id: "notif-p1",
    title: "ثبت بازخورد منتور برای علی",
    description: "منتور ارشد بازخورد پروژه ماشین‌حساب ماژولار را ثبت کرد: کدنویسی تمیز و استاندارد.",
    time: "۴۵ دقیقه پیش",
    read: false,
    type: "success",
  },
  {
    id: "notif-p2",
    title: "گزارش پیشرفت هفتگی آماده شد",
    description: "گزارش تحلیلی ساعت مطالعه و تسلط بر مباحث هفته برای علی محمدی آماده مشاهده است.",
    time: "۳ ساعت پیش",
    read: true,
    type: "info",
  },
];

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
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const [notifications, setNotifications] = useState<DemoNotification[]>(initialParentNotifications);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const handleMarkAllRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

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
          aria-label={copy.shell.searchPlaceholder}
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
      <div className={styles.notifContainer}>
        <button
          type="button"
          className={styles.notifButton}
          aria-label={copy.shell.notificationsLabel}
          aria-expanded={isNotifOpen}
          aria-haspopup="dialog"
          onClick={() => setIsNotifOpen((prev) => !prev)}
        >
          <IconBell aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />
          {unreadCount > 0 && <span className={styles.notifBadge}>{unreadCount}</span>}
        </button>
        <NotificationPopover
          isOpen={isNotifOpen}
          onClose={() => setIsNotifOpen(false)}
          title={copy.shell.notificationsLabel}
          notifications={notifications}
          onMarkAllAsRead={handleMarkAllRead}
          roleTone="parent"
        />
      </div>
      <div className={styles.userProfileBadge}>
        <div className={styles.userInfo}>
          <span className={styles.userRole}>{copy.shell.roleLabel}</span>
          <span className={styles.userName}>{copy.shell.userName}</span>
        </div>
        <div className={`${styles.userAvatar} ${styles.parentAvatar}`} aria-hidden="true">
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
