import type { HomepageAlphaContent, HomepageRoute } from "@/features/home/home.types";

const hidden = (route: HomepageRoute) => ({
  route,
  status: "hidden_until_route_available" as const,
});

const available = (route: HomepageRoute) => ({
  route,
  status: "available" as const,
});

export const homepageAlphaContent = {
  brandName: "CodeSho",
  shell: {
    drawerCloseLabel: "بستن منوی اصلی",
    menuButtonLabel: "باز کردن منوی اصلی",
    navigationLabel: "ناوبری اصلی",
  },
  navigation: [
    { id: "paths", label: "مسیرهای یادگیری", destination: hidden("/paths") },
    { id: "courses", label: "دوره‌ها", destination: hidden("/courses") },
    { id: "projects", label: "پروژه‌ها", destination: hidden("/projects") },
    { id: "mentor", label: "منتور هوشمند", destination: hidden("/mentor") },
    { id: "login", label: "ورود", destination: available("/login") },
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
    primaryAction: { id: "hero-start", label: "ورود به پلتفرم", destination: available("/login") },
    secondaryAction: { id: "hero-paths", label: "مشاهده مسیرها", destination: hidden("/paths") },
    illustration: {
      id: "home-hero-ai-coding-alpha",
      src: "/assets/home/hero-ai-coding-alpha.png",
      width: 1448,
      height: 1086,
      format: "png",
      background: "solid",
      presentation: "decorative",
      alt: "",
      approvalStatus: "alpha_approved",
      productionRights: "pending_metadata_review",
      sourceKind: "employer_supplied_ai_generated",
      provider: null,
      model: null,
      referenceUse: "none_reported_not_independently_verified",
    },
  },
  learningPaths: [
    { id: "frontend", title: "مسیر فرانت‌اند", description: "توسعه رابط کاربری مدرن و تعاملی", action: { id: "path-frontend", label: "ورود به مسیر", destination: available("/login") } },
    { id: "backend", title: "مسیر بک‌اند", description: "ساخت APIها و سیستم‌های مقیاس‌پذیر و پایدار", action: { id: "path-backend", label: "ورود به مسیر", destination: available("/login") } },
    { id: "ai-engineering", title: "مسیر مهندسی هوش مصنوعی", description: "ساخت مدل‌های هوشمند و کاربردهای AI", action: { id: "path-ai-engineering", label: "ورود به مسیر", destination: available("/login") } },
  ],
  learningPathsHeading: "مسیرهای یادگیری",
  mentor: {
    title: "منتور هوشمند CodeSho، همیشه کنار تو",
    descriptionStatus: "pending_transcription",
    action: { id: "mentor-start", label: "ورود و گفتگو با منتور", destination: available("/login") },
  },
  finalCta: {
    title: "آماده‌ای مسیر حرفه‌ای خودت را شروع کنی؟",
    primaryAction: { id: "final-start", label: "ورود به پلتفرم", destination: available("/login") },
    secondaryAction: { id: "final-paths", label: "مشاهده مسیرها", destination: hidden("/paths") },
  },
} as const satisfies HomepageAlphaContent;
