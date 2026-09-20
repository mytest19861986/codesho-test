import type { HomepageRoute } from "@/features/home/home.types";

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
    { id: "paths", label: "مسیرهای یادگیری", destination: available("/student") },
    { id: "parent", label: "پرتال والدین", destination: available("/parent") },
    { id: "mentor", label: "پرتال مربیان", destination: available("/mentor") },
    { id: "admin", label: "راهبری و حاکمیت", destination: available("/admin") },
    { id: "login", label: "ورود به پلتفرم", destination: available("/login") },
  ],
  sections: {
    hero: "enabled",
    trust: "enabled",
    learningPaths: "enabled",
    projects: "enabled",
    courses: "enabled",
    mentor: "enabled",
    testimonials: "omitted_until_permissioned",
    finalCta: "enabled",
    footer: "enabled",
  },
  assets: {
    nonLogoIllustrations: "generation_authorized",
    officialLogo: "awaiting_official_asset",
  },
  hero: {
    eyebrow: "پلتفرم تخصصی آموزش هوشمند برنامه‌نویسی",
    title: "کدشو: مسیر هوشمند تبدیل شدن به یک برنامه‌نویس واقعی",
    description: "ترکیب چالش‌های کدنویسی واقعی، تحلیل پیوسته روند رشد و همراهی دائمی AI Mentor در یک محیط شخصی‌سازی‌شده برای آمادگی بازار کار فناوری.",
    primaryAction: { id: "hero-start", label: "ورود به پلتفرم یادگیری", destination: available("/login") },
    secondaryAction: { id: "hero-paths", label: "مشاهده پرتال دانش‌آموز", destination: available("/student") },
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
  whyCodesho: {
    heading: "چرا کدشو؟ تفاوت یادگیری واقعی با آموزش سنتی",
    subheading: "ما صرفاً ویدیوهای آموزشی ضبط‌شده ارائه نمی‌دهیم؛ کدشو یک محیط عملیاتی زنده برای کشف استعداد و تسلط صنعتی است.",
    pillars: [
      {
        id: "personalized-path",
        title: "مسیر یادگیری هوشمند و تطبیقی",
        description: "سیستم هوش مصنوعی سطح مهارت، سرعت پیشرفت و نقاط ضعف شما را تحلیل کرده و چالش‌های بعدی را بر اساس نیاز واقعی شما تنظیم می‌کند.",
      },
      {
        id: "industry-projects",
        title: "پروژه‌های استاندارد صنعت نرم‌افزار",
        description: "به جای تمرین‌های تکراری و ابتدایی، سیستم‌های نرم‌افزاری واقعی و کاربردی بسازید که نمونه کار رسمی شما در بازار کار خواهند بود.",
      },
      {
        id: "ai-mentor-pair",
        title: "همراهی مداوم AI Mentor",
        description: "در هر لحظه از کدنویسی که با خطا یا ابهام مواجه شوید، مربی هوشمند در نقش Pair Programmer راهنمای گام‌به‌گام شماست.",
      },
      {
        id: "growth-transparency",
        title: "شفافیت و پایش عملکرد برای والدین",
        description: "پرتال اختصاصی والدین امکان رصد دقیق زمان تمرین، مهارت‌های اکتسابی و گزارش‌های پیشرفت تحصیلی فرزندان را فراهم می‌سازد.",
      },
    ],
  },
  rolePortals: {
    heading: "اکوسیستم سه پرتال یکپارچه کدشو",
    subheading: "کدشو محیطی هماهنگ میان فراگیران، خانواده‌ها و مربیان حرفه‌ای فراهم آورده است.",
    portals: [
      {
        id: "student-portal",
        title: "پرتال دانش‌آموز (Student)",
        description: "محیط اجرای چالش‌های کدنویسی، دریافت فوری بازخورد مربی هوشمند، شرکت در پروژه‌ها و جمع‌آوری امتیازهای مهارتی.",
        action: { id: "action-student", label: "ورود به پرتال دانش‌آموز", destination: available("/student") },
      },
      {
        id: "parent-portal",
        title: "پرتال والدین (Parent)",
        description: "داشبورد اختصاصی اولیا جهت پایش زمان صرف‌شده، سطح تمرکز، کارنامه‌های تحلیلی و اطمینان از رشد واقعی فرزند.",
        action: { id: "action-parent", label: "ورود به پرتال اولیا", destination: available("/parent") },
      },
      {
        id: "mentor-portal",
        title: "پرتال مربیان (Mentor)",
        description: "سامانه بازبینی فنی کدهای دانش‌آموزان، ثبت بازخوردهای تخصصی تکمیلی و راهبری مسیر شغلی فراگیران.",
        action: { id: "action-mentor", label: "ورود به پرتال مربیان", destination: available("/mentor") },
      },
    ],
  },
  learningPathsHeading: "مسیرهای یادگیری تخصصی",
  learningPaths: [
    {
      id: "frontend",
      title: "توسعه فرانت‌اند مدرن (Frontend)",
      description: "تسلط بر HTML, CSS, JavaScript, React و اصول رابط‌های کاربری تعاملی با هدایت پروژه‌محور.",
      action: { id: "path-frontend", label: "ورود و ثبت‌نام در مسیر", destination: available("/login") },
    },
    {
      id: "backend",
      title: "معماری سیستم و بک‌اند (Backend)",
      description: "طراحی APIهای مقیاس‌پذیر، پایگاه‌های داده رابطه‌ای و منطق کسب‌وکار با استاندارد Enterprise.",
      action: { id: "path-backend", label: "ورود و ثبت‌نام در مسیر", destination: available("/login") },
    },
    {
      id: "ai-engineering",
      title: "مهندسی هوش مصنوعی (AI Engineering)",
      description: "آشنایی با الگوریتم‌های هوشمند، مدل‌های یادگیری عمیق و کاربرد ابزارهای مدرن در توسعه نرم‌افزار.",
      action: { id: "path-ai-engineering", label: "ورود و ثبت‌نام در مسیر", destination: available("/login") },
    },
  ],
  mentor: {
    title: "منتور هوشمند کدشو؛ مربی اختصاصی شما در ۲۴ ساعت شبانه‌روز",
    descriptionStatus: "pending_transcription" as const,
    action: { id: "mentor-start", label: "شروع کار با مربی هوشمند", destination: available("/login") },
  },
  finalCta: {
    title: "آماده‌اید مسیر حرفه‌ای خود در برنامه‌نویسی را از امروز شروع کنید؟",
    primaryAction: { id: "final-start", label: "ورود به حساب کاربری", destination: available("/login") },
    secondaryAction: { id: "final-paths", label: "مشاهده پرتال دانش‌آموز", destination: available("/student") },
  },
} as const;
