"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
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
  IconDocument,
  IconLaptop,
  IconClock,
  IconClose,
} from "@/components/ui";
import { mentorAlphaContent as copy } from "@/content/fa/mentor.alpha";
import { MentorSearchProvider, useMentorSearch } from "./MentorSearchContext";
import styles from "../student/student.module.css";

interface MentorLayoutProps {
  children: ReactNode;
}

const initialMentorNotifications: DemoNotification[] = [
  {
    id: "notif-m1",
    title: "پروژه جدید برای بررسی",
    description: "کارآموز علی محمدی کد پروژه ماشین‌حساب ماژولار را جهت بررسی فنی ارسال کرد.",
    time: "۳۵ دقیقه پیش",
    read: false,
    type: "info",
  },
  {
    id: "notif-m2",
    title: "جلسه آنلاین رفع اشکال",
    description: "جلسه رفع اشکال با سارا احمدی تا ۲۰ دقیقه دیگر آغاز می‌شود.",
    time: "۱ ساعت پیش",
    read: true,
    type: "warning",
  },
];

const navIcons: Record<string, ReactNode> = {
  overview: <IconChart aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />,
  reviews: <IconDocument aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />,
  students: <IconLaptop aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />,
  sessions: <IconClock aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />,
};

function MentorLayoutInner({ children }: MentorLayoutProps) {
  const pathname = usePathname();
  const { searchQuery, setSearchQuery, setOpenGuideModal } = useMentorSearch();
  const searchInputRef = useRef<HTMLInputElement>(null);
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const [notifications, setNotifications] = useState<DemoNotification[]>(initialMentorNotifications);

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
          className={styles.searchClearBtn}
          onClick={() => setSearchQuery("")}
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
          roleTone="mentor"
        />
      </div>
      <div className={styles.userProfileBadge}>
        <div className={styles.userInfo}>
          <span className={styles.userRole}>{copy.shell.roleLabel}</span>
          <span className={styles.userName}>{copy.shell.userName}</span>
        </div>
        <div className={`${styles.userAvatar} ${styles.mentorAvatar}`} aria-hidden="true">
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
      <button
        type="button"
        className={styles.sidebarPromoButton}
        onClick={() => setOpenGuideModal(true)}
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
      tone="mentor"
    >
      {children}
    </AppShell>
  );
}

export default function MentorLayout({ children }: MentorLayoutProps) {
  return (
    <MentorSearchProvider>
      <MentorLayoutInner>{children}</MentorLayoutInner>
    </MentorSearchProvider>
  );
}
