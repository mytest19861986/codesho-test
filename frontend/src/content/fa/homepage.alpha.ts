import type { HomepageAlphaContent, HomepageRoute } from "@/features/home/home.types";

const hidden = (route: HomepageRoute) => ({
  route,
  status: "hidden_until_route_available" as const,
});

export const homepageAlphaContent = {
  brandName: "CodeSho",
  navigation: [
    { id: "paths", label: "مسیرهای یادگیری", destination: hidden("/paths") },
    { id: "courses", label: "دوره‌ها", destination: hidden("/courses") },
    { id: "projects", label: "پروژه‌ها", destination: hidden("/projects") },
    { id: "mentor", label: "منتور هوشمند", destination: hidden("/mentor") },
    { id: "login", label: "ورود", destination: hidden("/login") },
    { id: "signup", label: "شروع رایگان", destination: hidden("/signup") },
  ],
  sections: {
    hero: "enabled",
    trust: "hidden_until_verified_data",
    learningPaths: "enabled",
    projects: "hidden_until_verified_data",
    courses: "hidden_until_verified_data",
    mentor: "enabled",
    testimonials: "omitted_until_permissioned",
    finalCta: "enabled",
    footer: "hidden_until_route_available",
  },
  assets: {
    nonLogoIllustrations: "generation_authorized",
    officialLogo: "awaiting_official_asset",
  },
  hero: {
    eyebrow: "آکادمی برنامه‌نویسی با منتور هوشمند",
    title: "با هوش مصنوعی، سریع‌تر برنامه‌نویس حرفه‌ای شو",
    description: "CodeSho مسیر یادگیری ساختاریافته، پروژه‌های واقعی و منتور هوشمند را ترکیب کرده تا مهارت‌های موردنیاز بازار کار را سریع‌تر و هوشمندانه‌تر به تو برساند.",
    primaryAction: { id: "hero-start", label: "شروع یادگیری رایگان", destination: hidden("/signup") },
    secondaryAction: { id: "hero-paths", label: "مشاهده مسیرها", destination: hidden("/paths") },
  },
  learningPaths: [
    { id: "frontend", title: "مسیر فرانت‌اند", description: "توسعه رابط کاربری مدرن و تعاملی", action: { id: "path-frontend", label: "مشاهده مسیر", destination: hidden("/paths") } },
    { id: "backend", title: "مسیر بک‌اند", description: "ساخت APIها و سیستم‌های مقیاس‌پذیر و پایدار", action: { id: "path-backend", label: "مشاهده مسیر", destination: hidden("/paths") } },
    { id: "ai-engineering", title: "مسیر مهندسی هوش مصنوعی", description: "ساخت مدل‌های هوشمند و کاربردهای AI", action: { id: "path-ai-engineering", label: "مشاهده مسیر", destination: hidden("/paths") } },
  ],
  mentor: {
    title: "منتور هوشمند CodeSho، همیشه کنار تو",
    descriptionStatus: "pending_transcription",
    action: { id: "mentor-start", label: "شروع گفتگو با منتور", destination: hidden("/mentor") },
  },
  finalCta: {
    title: "آماده‌ای مسیر حرفه‌ای خودت را شروع کنی؟",
    primaryAction: { id: "final-start", label: "شروع یادگیری رایگان", destination: hidden("/signup") },
    secondaryAction: { id: "final-paths", label: "مشاهده مسیرها", destination: hidden("/paths") },
  },
} as const satisfies HomepageAlphaContent;
