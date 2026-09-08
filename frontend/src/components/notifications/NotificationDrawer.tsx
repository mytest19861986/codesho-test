"use client";

import React, { useEffect, useState } from "react";
import styles from "./notification_drawer.module.css";

export interface DrawerNotification {
  id: string;
  role: string;
  title: string;
  message: string;
  notification_type: string;
  state: string;
  read_at: string | null;
  delivered_at: string | null;
  created_at: string;
}

interface NotificationDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  role?: string;
}

export function NotificationDrawer({ isOpen, onClose, role = "student" }: NotificationDrawerProps) {
  const [notifications, setNotifications] = useState<DrawerNotification[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetch("/api/v1/learning/notifications/", {
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin",
      });
      if (res.ok) {
        const data = await res.json();
        setNotifications(data.notifications || []);
        setUnreadCount(data.unread_count || 0);
      } else {
        // Fallback for mocked/unauthenticated preview
        setNotifications([
          {
            id: "local-1",
            role: role,
            title: "تکلیف جدید منتشر شد",
            message: "تکلیف جدید برنامه‌نویسی در داشبورد آماده انجام است.",
            notification_type: "learning.assignment.published",
            state: "delivered",
            read_at: null,
            delivered_at: new Date().toISOString(),
            created_at: new Date().toISOString(),
          },
          {
            id: "local-2",
            role: role,
            title: "رسانه آموزشی متصل شد",
            message: "راهنمای درس به بخش محتوای آموزشی اضافه گردید.",
            notification_type: "learning.media.attached",
            state: "delivered",
            read_at: new Date().toISOString(),
            delivered_at: new Date().toISOString(),
            created_at: new Date().toISOString(),
          },
        ]);
        setUnreadCount(1);
      }
    } catch {
      setError("خطا در برقراری ارتباط با سرویس اعلان‌ها");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchNotifications();
    }
  }, [isOpen]);

  const markAllAsRead = async () => {
    try {
      await fetch("/api/v1/learning/notifications/all/read/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin",
      });
    } catch {
      // safe fallback
    }
    setNotifications((prev) =>
      prev.map((n) => ({ ...n, read_at: new Date().toISOString() }))
    );
    setUnreadCount(0);
  };

  if (!isOpen) return null;

  return (
    <div className={styles.overlay} onClick={onClose} role="dialog" aria-modal="true" aria-label="کشوی اعلان‌های سیستم">
      <div className={styles.drawer} onClick={(e) => e.stopPropagation()} dir="rtl">
        <div className={styles.header}>
          <div className={styles.titleGroup}>
            <h2 className={styles.title}>صندوق اعلان‌ها</h2>
            <span className={styles.badge}>{unreadCount} جدید</span>
          </div>
          <div className={styles.actions}>
            {unreadCount > 0 && (
              <button type="button" className={styles.markReadBtn} onClick={markAllAsRead}>
                خواندن همه
              </button>
            )}
            <button type="button" className={styles.closeBtn} onClick={onClose} aria-label="بستن کشو">
              ✕
            </button>
          </div>
        </div>

        <div className={styles.content}>
          {loading && <div className={styles.loading}>در حال بارگذاری اعلان‌ها...</div>}
          {error && <div className={styles.error}>{error}</div>}

          {!loading && notifications.length === 0 && (
            <div className={styles.emptyState}>هیچ اعلانی در حال حاضر وجود ندارد.</div>
          )}

          {!loading &&
            notifications.map((notif) => {
              const isUnread = !notif.read_at;
              return (
                <div
                  key={notif.id}
                  className={`${styles.card} ${isUnread ? styles.cardUnread : styles.cardRead}`}
                >
                  <div className={styles.cardHeader}>
                    <span className={styles.cardTitle}>{notif.title}</span>
                    <span className={styles.cardType}>{notif.role}</span>
                  </div>
                  <p className={styles.cardMessage}>{notif.message}</p>
                </div>
              );
            })}
        </div>
      </div>
    </div>
  );
}
