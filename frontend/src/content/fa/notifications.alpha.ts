export interface NotificationCopy {
  readonly title: string;
  readonly syntheticBadge: string;
  readonly noticeBanner: string;
  readonly emptyTitle: string;
  readonly emptyDescription: string;
  readonly markAllRead: string;
  readonly closeLabel: string;
  readonly feedLabel: string;
}

export const defaultNotificationCopy: NotificationCopy = {
  title: "اعلان‌ها",
  syntheticBadge: "شبیه‌سازی محیط توسعه",
  noticeBanner: "سرویس تحویل واقعی اعلان‌ها در این محیط فعال نیست. اعلان‌های زیر داده‌های شبیه‌سازی‌شده (Synthetic) جهت ارزیابی رابط کاربری هستند.",
  emptyTitle: "هیچ اعلان جدیدی وجود ندارد",
  emptyDescription: "تمام پیام‌ها و تغییرات وضعیت را بررسی کرده‌اید.",
  markAllRead: "علامت‌گذاری همه به‌عنوان خوانده‌شده",
  closeLabel: "بستن پنل اعلان‌ها",
  feedLabel: "فهرست اعلان‌ها",
};
