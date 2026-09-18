"use client";

import React, { useEffect, useRef } from "react";
import { IconBell, IconClose, IconCheck, IconClock, IconDocument } from "@/components/ui";
import { defaultNotificationCopy, type NotificationCopy } from "@/content/fa/notifications.alpha";
import styles from "@/app/student/student.module.css";

export interface DemoNotification {
  id: string;
  title: string;
  description: string;
  time: string;
  read: boolean;
  type: "info" | "success" | "warning";
  link?: string;
}

interface NotificationPopoverProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  notifications: DemoNotification[];
  onMarkAllAsRead?: () => void;
  roleTone?: "student" | "parent" | "mentor";
  copy?: NotificationCopy;
}

export function NotificationPopover({
  isOpen,
  onClose,
  title,
  notifications,
  onMarkAllAsRead,
  copy = defaultNotificationCopy,
}: NotificationPopoverProps) {
  const popoverRef = useRef<HTMLDivElement>(null);
  const displayTitle = title ?? copy.title;

  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.stopPropagation();
        onClose();
      }
    };

    const handleClickOutside = (e: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      ref={popoverRef}
      className={styles.notificationPopover}
      role="dialog"
      aria-modal="false"
      aria-label={displayTitle}
      id="notification-panel"
    >
      <div className={styles.notificationPopoverHeader}>
        <div className={styles.notificationPopoverTitleArea}>
          <IconBell aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
          <h4 className={styles.notificationPopoverTitle}>{displayTitle}</h4>
          <span className={styles.syntheticBadge}>{copy.syntheticBadge}</span>
        </div>
        <button
          type="button"
          onClick={onClose}
          className={styles.modalCloseBtn}
          aria-label={copy.closeLabel}
        >
          <IconClose aria-hidden="true" style={{ inlineSize: "1rem", blockSize: "1rem" }} />
        </button>
      </div>

      <div className={styles.notificationNoticeBanner}>
        <span style={{ fontSize: "var(--cs-font-size-caption)", color: "var(--cs-color-text-muted)" }}>
          {copy.noticeBanner}
        </span>
      </div>

      <div className={styles.notificationList} role="feed" aria-label={copy.feedLabel}>
        {notifications.length === 0 ? (
          <div className={styles.notificationEmptyState}>
            <IconDocument aria-hidden="true" style={{ inlineSize: "2rem", blockSize: "2rem", color: "var(--cs-color-text-muted)" }} />
            <p style={{ margin: 0, fontWeight: "var(--cs-font-weight-bold)" }}>{copy.emptyTitle}</p>
            <span style={{ fontSize: "var(--cs-font-size-caption)", color: "var(--cs-color-text-muted)" }}>
              {copy.emptyDescription}
            </span>
          </div>
        ) : (
          notifications.map((item) => (
            <div
              key={item.id}
              className={`${styles.notificationItem} ${item.read ? styles.notificationItemRead : styles.notificationItemUnread}`}
              tabIndex={0}
              role="article"
              aria-label={item.title}
            >
              <div className={styles.notificationItemHeader}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.375rem" }}>
                  {!item.read && <span className={styles.notificationUnreadDot} aria-hidden="true" />}
                  <span className={styles.notificationItemTitle}>{item.title}</span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "0.25rem", fontSize: "0.6875rem", color: "var(--cs-color-text-muted)" }}>
                  <IconClock aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
                  <span>{item.time}</span>
                </div>
              </div>
              <p className={styles.notificationItemDesc}>{item.description}</p>
            </div>
          ))
        )}
      </div>

      {notifications.length > 0 && onMarkAllAsRead && (
        <div className={styles.notificationPopoverFooter}>
          <button
            type="button"
            onClick={onMarkAllAsRead}
            className={styles.notificationMarkAllBtn}
          >
            <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem" }} />
            <span>{copy.markAllRead}</span>
          </button>
        </div>
      )}
    </div>
  );
}
