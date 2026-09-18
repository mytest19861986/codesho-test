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
  IconGraduate,
  IconChat,
  IconTrending,
  IconLaptop,
  IconClose,
} from "@/components/ui";
import { studentAlphaContent as copy } from "@/content/fa/student.alpha";
import { StudentSearchProvider, useStudentSearch } from "./StudentSearchContext";
import styles from "./student.module.css";

interface StudentLayoutProps {
  children: ReactNode;
}

const initialStudentNotifications: DemoNotification[] = [
  {
    id: "notif-s1",
    title: "ثبت بازخورد منتور",
    description: "منتور کد پروژه ماشین‌حساب ماژولار شما را بررسی و بازخورد جدید ثبت کرد.",
    time: "۲۰ دقیقه پیش",
    read: false,
    type: "info",
  },
  {
    id: "notif-s2",
    title: "تکمیل موفقیت‌آمیز گام یادگیری",
    description: "گام مبانی توابع در جاوااسکریپت با موفقیت ثبت و تایید شد.",
    time: "۲ ساعت پیش",
    read: false,
    type: "success",
  },
];

const navIcons: Record<string, ReactNode> = {
  dashboard: <IconChart aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />,
  learning: <IconGraduate aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />,
  coaching: <IconChat aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />,
  growth: <IconTrending aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />,
  portfolio: <IconLaptop aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />,
};

function StudentLayoutInner({ children }: StudentLayoutProps) {
  const pathname = usePathname();
  const { searchQuery, setSearchQuery } = useStudentSearch();
  const searchInputRef = useRef<HTMLInputElement>(null);
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const [notifications, setNotifications] = useState<DemoNotification[]>(initialStudentNotifications);

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

  // Dynamically determine active item based on current route
  let activeItemId = "dashboard";
  if (pathname.includes("/learning")) activeItemId = "learning";
  else if (pathname.includes("/coaching")) activeItemId = "coaching";
  else if (pathname.includes("/growth")) activeItemId = "growth";
  else if (pathname.includes("/portfolio")) activeItemId = "portfolio";

  const navigationItems = copy.navigation.map((item) => ({
    id: item.id,
    label: item.label,
    href: item.href,
    icon: navIcons[item.id] || navIcons.dashboard,
  }));

  const brandSlot = (
    <div className={styles.sidebarBrandArea}>
      <Link href="/student" className={styles.brandLogoTitle}>
        <IconBrand aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
        <span>{copy.brand}</span>
      </Link>
      <span className={styles.brandTagline}>{copy.tagline}</span>
    </div>
  );

  const headerSearchSlot = (
    <div className={styles.headerSearchArea}>
      <IconSearch
        aria-hidden="true"
        className={styles.searchIcon}
        style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }}
      />
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
          roleTone="student"
        />
      </div>
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
        <IconSettings aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
        <span>{copy.shell.settingsLabel}</span>
      </Link>
      <Link href="/student" className={styles.sidebarUtilityLink}>
        <IconSupport aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
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

export default function StudentLayout({ children }: StudentLayoutProps) {
  return (
    <StudentSearchProvider>
      <StudentLayoutInner>{children}</StudentLayoutInner>
    </StudentSearchProvider>
  );
}
