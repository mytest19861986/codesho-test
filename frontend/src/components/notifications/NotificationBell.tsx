"use client";

import React, { useState } from "react";
import styles from "./notification_bell.module.css";

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  timestamp: string;
  isRead: boolean;
  type: "assignment" | "review" | "media" | "system";
}

const defaultNotifications: NotificationItem[] = [
  {
    id: "notif-1",
    title: "تکلیف منتشر شد",
    message: "پروژه ماشین‌حساب پایتون منتشر گردید و آماده ارسال است.",
    timestamp: "۱۰ دقیقه پیش",
    isRead: false,
    type: "assignment",
  },
  {
    id: "notif-2",
    title: "رسانه ضمیمه اضافه شد",
    message: "راهنمای سینتکس پایتون به درس مبانی متغیرها متصل شد.",
    timestamp: "۳۵ دقیقه پیش",
    isRead: false,
    type: "media",
  },
  {
    id: "notif-3",
    title: "بازخورد مربی ثبت شد",
    message: "کد ارسالی شما توسط مربی بررسی و نمره ۱۰۰ ثبت شد.",
    timestamp: "۲ ساعت پیش",
    isRead: true,
    type: "review",
  },
];

export function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false);
  const [items, setItems] = useState<NotificationItem[]>(defaultNotifications);

  const unreadCount = items.filter((i) => !i.isRead).length;

  const markAllAsRead = () => {
    setItems((prev) => prev.map((item) => ({ ...item, isRead: true })));
  };

  return (
    <div className={styles.container}>
      <button
        type="button"
        className={styles.bellButton}
        onClick={() => setIsOpen(!isOpen)}
        aria-label={`اعلان‌ها (${unreadCount} خوانده نشده)`}
        aria-expanded={isOpen}
      >
        <span aria-hidden="true" className={styles.bellIcon}>🔔</span>
        {unreadCount > 0 && <span className={styles.badge}>{unreadCount}</span>}
      </button>

      {isOpen && (
        <div className={styles.dropdown} role="region" aria-label="صندوق اعلان‌های درون‌برنامه‌ای">
          <div className={styles.header}>
            <h3 className={styles.title}>اعلان‌های سیستم</h3>
            {unreadCount > 0 && (
              <button
                type="button"
                className={styles.markReadBtn}
                onClick={markAllAsRead}
              >
                خواندن همه
              </button>
            )}
          </div>

          <div className={styles.list}>
            {items.length === 0 ? (
              <div className={styles.emptyState}>اعلانی وجود ندارد.</div>
            ) : (
              items.map((item) => (
                <div
                  key={item.id}
                  className={`${styles.item} ${item.isRead ? styles.itemRead : styles.itemUnread}`}
                >
                  <div className={styles.itemHeader}>
                    <strong className={styles.itemTitle}>{item.title}</strong>
                    <span className={styles.itemTime}>{item.timestamp}</span>
                  </div>
                  <p className={styles.itemMessage}>{item.message}</p>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
