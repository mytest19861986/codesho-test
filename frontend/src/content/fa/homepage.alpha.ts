import type { HomepageAlphaContent } from "@/features/home/home.types";

const hidden = (route: "/login" | "/signup" | "/paths" | "/courses" | "/projects" | "/mentor") => ({
  route,
  status: "hidden_until_route_available" as const,
});

export const homepageAlphaContent = {
  brandName: "کدشو",
  navigation: [
    { id: "paths", label: "مسیرهای یادگیری", destination: hidden("/paths") },
    { id: "courses", label: "دوره‌ها", destination: hidden("/courses") },
    { id: "projects", label: "پروژه‌ها", destination: hidden("/projects") },
    { id: "mentor", label: "منتور", destination: hidden("/mentor") },
    { id: "login", label: "ورود", destination: hidden("/login") },
    { id: "signup", label: "ثبت‌نام", destination: hidden("/signup") },
  ],
  hero: {
    eyebrow: "یادگیری برنامه‌نویسی پروژه‌محور",
    title: "یاد بگیر، بساز و مسیر خودت را پیدا کن",
    description: "کدشو فضای یادگیری و ساخت پروژه برای شروع مسیر برنامه‌نویسی است.",
    primaryAction: { id: "hero-start", label: "شروع یادگیری", destination: hidden("/signup") },
    secondaryAction: { id: "hero-paths", label: "مشاهده مسیرها", destination: hidden("/paths") },
  },
  features: [
    { id: "project-based", title: "یادگیری پروژه‌محور", description: "مفاهیم را با ساخت پروژه تمرین کن." },
    { id: "guided", title: "راهنمایی گام‌به‌گام", description: "برای ادامهٔ مسیر، راهنمای روشن داشته باش." },
    { id: "practice", title: "تمرین عملی", description: "دانسته‌ها را در تمرین و پروژه به کار ببر." },
  ],
  learningPaths: [
    { id: "web", title: "مسیر وب", description: "برای آشنایی با ساخت تجربه‌های وب.", action: { id: "path-web", label: "دیدن مسیر", destination: hidden("/paths") } },
    { id: "backend", title: "مسیر بک‌اند", description: "برای شناخت منطق و سرویس‌های پشت یک محصول.", action: { id: "path-backend", label: "دیدن مسیر", destination: hidden("/paths") } },
    { id: "projects", title: "مسیر پروژه", description: "برای تبدیل تمرین‌ها به نمونه‌کارهای واقعی.", action: { id: "path-projects", label: "دیدن مسیر", destination: hidden("/projects") } },
  ],
  mentor: {
    eyebrow: "همراه یادگیری",
    title: "منتور کدشو",
    description: "در هر مرحله از یادگیری، برای پرسش و ادامهٔ مسیر همراهت هستیم.",
    action: { id: "mentor-start", label: "آشنایی با منتور", destination: hidden("/mentor") },
  },
} as const satisfies HomepageAlphaContent;
