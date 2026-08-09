import type { DashboardModel } from "./dashboard.types";

/** Synthetic presentation data only; replace with a reviewed read contract in Task78B. */
export const dashboardFixture: DashboardModel = {
  student: { displayName: "آرین", greeting: "امروز آماده‌ای یک قدم جلوتر بروی؟", className: "مسیر پایتون مقدماتی" },
  learning: { course: "پایتون برای حل مسئله", module: "ماژول ۳ · حلقه‌ها", lesson: "تمرین‌های تکرار و الگوها", progress: 64, totalUnits: 25, completedUnits: 16 },
  nextSession: { title: "کارگاه حل مسئله", date: "شنبه ۲۵ مرداد", time: "۱۷:۳۰", type: "جلسه زنده", status: "رزروشده" },
  momentum: { xp: 1240, rank: "کاوشگر کد", streak: 7 },
  assignment: { title: "ساخت الگوی ستاره‌ای", dueLabel: "تا ۲ روز دیگر", status: "در انتظار ارسال", actionLabel: "ادامه تمرین" },
  recommendation: { title: "چالش حلقه‌های تو در تو", reason: "برای تثبیت مهارت همین ماژول پیشنهاد شده است." },
  attention: ["بازخورد مربی برای تمرین قبلی آماده است.", "جلسه بعدی در تقویم تو رزرو شده است."],
};
