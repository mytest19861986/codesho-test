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

const navItems = [
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

  return (
    <AppShell
      sidebarBrand={{
        title: copy.brand,
        subtitle: copy.portalTitle,
        icon: <IconBrand aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />,
        href: "/admin/dashboard",
      }}
      navItems={navItems.map((item) => ({
        id: item.id,
        label: item.label,
        href: item.href,
        icon: item.icon,
        isActive: item.id === activeItemId,
      }))}
      sidebarFooter={
        <div style={{ padding: "0.75rem", fontSize: "0.75rem", color: "var(--muted)", textAlign: "center", borderTop: "1px solid var(--line)" }}>
          <span>{copy.envNotice}</span>
        </div>
      }
      topbarSearch={
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", background: "var(--paper)", border: "1px solid var(--line)", padding: "0.375rem 0.75rem", borderRadius: "8px", width: "260px" }}>
          <IconSearch aria-hidden="true" style={{ inlineSize: "1rem", blockSize: "1rem", color: "var(--muted)" }} />
          <input
            type="search"
            placeholder="جستجو در مدیریت... (Ctrl+K)"
            style={{ border: "none", outline: "none", background: "transparent", fontSize: "0.8125rem", width: "100%", fontFamily: "inherit" }}
            aria-label="جستجوی سامانه مدیریت"
          />
        </div>
      }
      topbarActions={
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", position: "relative" }}>
          <button
            type="button"
            className={styles.iconBtn}
            onClick={() => setIsNotifOpen((prev) => !prev)}
            aria-label={`اعلان‌ها (${unreadCount} خوانده‌نشده)`}
            aria-expanded={isNotifOpen}
            aria-haspopup="dialog"
            style={{ position: "relative" }}
          >
            <IconBell aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />
            {unreadCount > 0 && (
              <span className={styles.notifBadge} aria-hidden="true">
                {unreadCount}
              </span>
            )}
          </button>

          <NotificationPopover
            isOpen={isNotifOpen}
            onClose={() => setIsNotifOpen(false)}
            notifications={notifications}
            onMarkAllRead={handleMarkAllRead}
            ariaLabel="اعلان‌های پنل مدیریت"
          />

          <Link href="/admin/system" className={styles.iconBtn} aria-label="تنظیمات سیستم">
            <IconSettings aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem" }} />
          </Link>

          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.25rem 0.625rem", background: "#f3eafa", borderRadius: "8px", color: "var(--purple)", fontWeight: 700, fontSize: "0.8125rem" }}>
            <span>راهبر کل (Superadmin)</span>
          </div>
        </div>
      }
    >
      {children}
    </AppShell>
  );
}
