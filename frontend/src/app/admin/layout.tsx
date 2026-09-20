"use client";

import { useState, type ReactNode } from "react";
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
  IconSparkles,
  IconTarget,
  IconClock,
} from "@/components/ui";
import { adminAlphaContent as copy } from "@/content/fa/admin.alpha";
import styles from "../student/student.module.css";

interface AdminLayoutProps {
  children: ReactNode;
}

const initialAdminNotifications: DemoNotification[] = [
  {
    id: "notif-a1",
    title: "مستأجر جدید در حال راه‌اندازی",
    description: "سازمان 'آموزشگاه عصر نوین' درخواست پیکربندی دامنه novin.codesho.ir را ثبت کرده است.",
    time: "۱۵ دقیقه پیش",
    read: false,
    type: "info",
  },
  {
    id: "notif-a2",
    title: "تست تمدید خودکار گواهی SSL",
    description: "شبیه‌سازی دوره‌ای تمدید گواهینامه Let's Encrypt با موفقیت ۱۰۰٪ کامل شد.",
    time: "۴۵ دقیقه پیش",
    read: true,
    type: "success",
  },
  {
    id: "notif-a3",
    title: "رویداد امنیتی دسترسی رد شده",
    description: "تلاش برای دسترسی غیرمجاز از آدرس IP ناشناس در لاگ‌های تغییرناپذیر ثبت گردید.",
    time: "۲ ساعت پیش",
    read: true,
    type: "warning",
  },
];

const navigationItems = [
  { id: "dashboard", label: copy.nav.dashboard, href: "/admin/dashboard", icon: <IconChart aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} /> },
  { id: "tenants", label: copy.nav.tenants, href: "/admin/tenants", icon: <IconLaptop aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} /> },
  { id: "users", label: copy.nav.users, href: "/admin/users", icon: <IconSparkles aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} /> },
  { id: "roles", label: copy.nav.roles, href: "/admin/roles", icon: <IconTarget aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} /> },
  { id: "audit", label: copy.nav.audit, href: "/admin/audit", icon: <IconDocument aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} /> },
  { id: "governance", label: copy.nav.governance, href: "/admin/governance", icon: <IconClock aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} /> },
  { id: "system", label: copy.nav.system, href: "/admin/system", icon: <IconSettings aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} /> },
];

export default function AdminLayout({ children }: AdminLayoutProps) {
  const pathname = usePathname();
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const [notifications, setNotifications] = useState<DemoNotification[]>(initialAdminNotifications);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const handleMarkAllRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  let activeItemId = "dashboard";
  if (pathname.includes("/tenants")) activeItemId = "tenants";
  else if (pathname.includes("/users")) activeItemId = "users";
  else if (pathname.includes("/roles")) activeItemId = "roles";
  else if (pathname.includes("/audit")) activeItemId = "audit";
  else if (pathname.includes("/governance")) activeItemId = "governance";
  else if (pathname.includes("/system")) activeItemId = "system";

  const brandSlot = (
    <div className={styles.sidebarBrandArea}>
      <Link href="/admin/dashboard" className={styles.brandLogoTitle}>
        <IconBrand aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
        <span>{copy.brand}</span>
      </Link>
      <span className={styles.brandTagline}>{copy.portalTitle}</span>
    </div>
  );

  const headerSearchSlot = (
    <div className={styles.headerSearchWrapper}>
      <IconSearch aria-hidden="true" className={styles.searchIcon} style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
      <input
        type="search"
        className={styles.searchInput}
        placeholder="جستجو در مدیریت... (Ctrl+K)"
        aria-label="جستجوی سامانه مدیریت"
      />
      <span className={styles.searchShortcut}>Ctrl+K</span>
    </div>
  );

  const headerActionsSlot = (
    <div className={styles.headerActionsArea}>
      <div className={styles.notifContainer}>
        <button
          type="button"
          className={styles.notifButton}
          aria-label={`اعلان‌ها (${unreadCount} خوانده‌نشده)`}
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
          title="اعلان‌های پنل مدیریت"
          notifications={notifications}
          onMarkAllAsRead={handleMarkAllRead}
          roleTone="mentor"
        />
      </div>
      <div className={styles.userProfileBadge}>
        <div className={styles.userInfo}>
          <span className={styles.userRole}>Superadmin</span>
          <span className={styles.userName}>راهبر ارشد سیستم</span>
        </div>
        <div className={`${styles.userAvatar} ${styles.mentorAvatar}`} aria-hidden="true">
          <span>م</span>
        </div>
      </div>
    </div>
  );

  const sidebarSupplementarySlot = (
    <div className={styles.sidebarFooterLinks}>
      <Link href="/admin/system" className={styles.sidebarUtilityLink}>
        <IconSettings aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
        <span>پایش سیستم</span>
      </Link>
      <Link href="/admin/governance" className={styles.sidebarUtilityLink}>
        <IconSupport aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
        <span>سیاست‌ها</span>
      </Link>
    </div>
  );

  const sidebarFooterSlot = (
    <div className={styles.sidebarPromoCard}>
      <p className={styles.sidebarPromoTitle}>محیط نظارت و راهبری</p>
      <p className={styles.sidebarPromoSubtitle}>{copy.envNotice}</p>
    </div>
  );

  return (
    <AppShell
      activeItemId={activeItemId}
      brand={brandSlot}
      bottomNavigationItems={navigationItems}
      drawerCloseLabel="بستن منو"
      menuButtonLabel="منوی ناوبری مدیریت"
      navigationItems={navigationItems}
      navigationLabel="بخش‌های مدیریت"
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
