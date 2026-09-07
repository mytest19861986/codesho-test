"use client";

import React, { useState } from "react";
import { AppShell, type NavigationItem } from "@/components/layout";
import styles from "./admin_learning.module.css";

export interface CurriculumItem {
  readonly id: string;
  readonly type: "course" | "lesson" | "assignment";
  readonly title: string;
  readonly code: string;
  readonly state: "draft" | "published" | "archived";
}

export interface AdminLearningProps {
  readonly initialItems: CurriculumItem[];
  readonly onTransition?: (id: string, action: "publish" | "archive") => void;
  readonly onCreateDraft?: (item: { type: string; code: string; title: string }) => void;
}

const navigationItems: NavigationItem[] = [
  { id: "admin-learning", label: "مدیریت آموزشی", href: "/admin/learning", icon: "⚙" },
];

function Brand() {
  return (
    <a className={styles.brand} href="/admin/learning">
      <span aria-hidden="true">⌁</span>
      <span>کُدشو - مدیریت سیستم</span>
    </a>
  );
}

export function AdminLearningScreen({
  initialItems,
  onTransition,
  onCreateDraft,
}: AdminLearningProps) {
  const [items, setItems] = useState<CurriculumItem[]>(initialItems);
  const [formType, setFormType] = useState<"course" | "lesson" | "assignment">("course");
  const [formCode, setFormCode] = useState<string>("");
  const [formTitle, setFormTitle] = useState<string>("");

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formCode.trim() || !formTitle.trim()) return;

    const newItem: CurriculumItem = {
      id: `draft-${Date.now()}`,
      type: formType,
      code: formCode,
      title: formTitle,
      state: "draft",
    };

    setItems((prev) => [...prev, newItem]);
    onCreateDraft?.({ type: formType, code: formCode, title: formTitle });
    setFormCode("");
    setFormTitle("");
  };

  const handleAction = (id: string, action: "publish" | "archive") => {
    onTransition?.(id, action);
    setItems((prev) =>
      prev.map((item) =>
        item.id === id
          ? { ...item, state: action === "publish" ? "published" : "archived" }
          : item
      )
    );
  };

  return (
    <AppShell
      activeItemId="admin-learning"
      brand={<Brand />}
      drawerCloseLabel="بستن منو"
      menuButtonLabel="باز کردن منوی ادمین"
      bottomNavigationItems={navigationItems}
      navigationItems={navigationItems}
      navigationLabel="ناوبری مدیریت"
      tone="teacher"
      profileSlot={<span aria-label="حساب مدیر" className={styles.profile}>م</span>}
    >
      <main className={styles.page} dir="rtl">
        <section aria-labelledby="admin-greeting" className={styles.hero}>
          <div>
            <p className={styles.eyebrow}>عملیات برنامه آموزشی (Curriculum Operations)</p>
            <h1 id="admin-greeting">مدیریت دوره‌ها و دروس کُدشو</h1>
            <p className={styles.heroMeta}>ایجاد پیش‌نویس، انتشار، مرتب‌سازی و بایگانی با حفظ تمامیت داده‌ها</p>
          </div>
        </section>

        <div className={styles.mainGrid}>
          {/* Create Draft Form */}
          <section aria-labelledby="create-draft-heading" className={styles.panel}>
            <h2 id="create-draft-heading" className={styles.sectionHeading}>ایجاد پیش‌نویس جدید</h2>
            <form onSubmit={handleCreate}>
              <div className={styles.formGroup}>
                <label htmlFor="entity-type">نوع محتوا:</label>
                <select
                  id="entity-type"
                  className={styles.select}
                  value={formType}
                  onChange={(e) => setFormType(e.target.value as "course" | "lesson" | "assignment")}
                >
                  <option value="course">دوره آموزشی (Course)</option>
                  <option value="lesson">درس آموزشی (Lesson)</option>
                  <option value="assignment">تکلیف عملی (Assignment)</option>
                </select>
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="entity-code">شناسه سیستمی (Code):</label>
                <input
                  id="entity-code"
                  type="text"
                  placeholder="مثال: py-advanced"
                  className={styles.input}
                  value={formCode}
                  onChange={(e) => setFormCode(e.target.value)}
                />
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="entity-title">عنوان فارسی:</label>
                <input
                  id="entity-title"
                  type="text"
                  placeholder="مثال: آموزش پایتون پیشرفته"
                  className={styles.input}
                  value={formTitle}
                  onChange={(e) => setFormTitle(e.target.value)}
                />
              </div>

              <button type="submit" className={styles.btnPrimary}>
                ایجاد پیش‌نویس (Draft)
              </button>
            </form>
          </section>

          {/* Curriculum List & Lifecycle Actions */}
          <section aria-labelledby="curriculum-list-heading" className={styles.panel}>
            <h2 id="curriculum-list-heading" className={styles.sectionHeading}>
              لیست محتوا و چرخه حیات ({items.length})
            </h2>

            <div className={styles.tableList}>
              {items.map((item) => (
                <div key={item.id} className={styles.tableItem}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                      <strong>{item.title}</strong>
                      <span
                        className={`${styles.badge} ${
                          item.state === "draft"
                            ? styles.badgeDraft
                            : item.state === "published"
                            ? styles.badgePublished
                            : styles.badgeArchived
                        }`}
                      >
                        {item.state === "draft"
                          ? "پیش‌نویس"
                          : item.state === "published"
                          ? "منتشر شده"
                          : "بایگانی شده"}
                      </span>
                    </div>
                    <small style={{ color: "#64748b" }}>
                      کد: {item.code} | نوع: {item.type}
                    </small>
                  </div>

                  <div style={{ display: "flex", gap: "0.5rem" }}>
                    {item.state === "draft" && (
                      <button
                        type="button"
                        className={`${styles.btnAction} ${styles.btnPublish}`}
                        onClick={() => handleAction(item.id, "publish")}
                      >
                        انتشار
                      </button>
                    )}
                    {item.state === "published" && (
                      <button
                        type="button"
                        className={`${styles.btnAction} ${styles.btnArchive}`}
                        onClick={() => handleAction(item.id, "archive")}
                      >
                        بایگانی
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </main>
    </AppShell>
  );
}
