export interface MentorNav {
  readonly id: string;
  readonly label: string;
  readonly href: string;
}

export interface MentorAlphaContent {
  readonly brand: string;
  readonly tagline: string;
  readonly shell: {
    readonly searchPlaceholder: string;
    readonly searchShortcut: string;
    readonly notificationsLabel: string;
    readonly unreadCount: number;
    readonly roleLabel: string;
    readonly userName: string;
    readonly settingsLabel: string;
    readonly supportLabel: string;
    readonly sidebarPromoTitle: string;
    readonly sidebarPromoSubtitle: string;
    readonly sidebarPromoButton: string;
    readonly drawerCloseLabel: string;
    readonly menuButtonLabel: string;
    readonly navigationLabel: string;
  };
  readonly navigation: readonly MentorNav[];
  readonly overview: {
    readonly title: string;
    readonly heroBadge: string;
    readonly heroBadgeSecondary: string;
    readonly heroHeading: string;
    readonly heroSubtitle: string;
    readonly heroActionPrimary: string;
    readonly heroActionSecondary: string;
    readonly reviewConsoleTitle: string;
    readonly reviewConsoleSubtitle: string;
    readonly check1: string;
    readonly check2: string;
    readonly check3: string;
    readonly check4: string;
    readonly kpi1Title: string;
    readonly kpi1Value: string;
    readonly kpi1Sub: string;
    readonly kpi2Title: string;
    readonly kpi2Value: string;
    readonly kpi2Sub: string;
    readonly kpi3Title: string;
    readonly kpi3Value: string;
    readonly kpi3Sub: string;
    readonly kpi4Title: string;
    readonly kpi4Value: string;
    readonly kpi4Sub: string;
    readonly pendingQueueTitle: string;
    readonly pendingItem1Title: string;
    readonly pendingItem1Student: string;
    readonly pendingItem1Time: string;
    readonly pendingItem1Status: string;
    readonly pendingItem2Title: string;
    readonly pendingItem2Student: string;
    readonly pendingItem2Time: string;
    readonly pendingItem2Status: string;
    readonly feedbackFocusTitle: string;
    readonly feedbackFocusDesc: string;
    readonly feedbackComplianceLabel: string;
    readonly feedbackComplianceValue: string;
    readonly actionStartReview: string;
  };
}

export const mentorAlphaContent: MentorAlphaContent = {
  brand: "CodeSho",
  tagline: "میز کار مربیگری تخصصی",
  shell: {
    searchPlaceholder: "جستجوی کارآموزان، پروژه‌های نیازمند بازخورد، جلسات رفع اشکال...",
    searchShortcut: "Ctrl + K",
    notificationsLabel: "اعلان‌های بازخورد منتوری",
    unreadCount: 3,
    roleLabel: "منتور ارشد",
    userName: "مهندس سهراب رحیمی",
    settingsLabel: "تنظیمات تقویم و ساعات مشاوره",
    supportLabel: "پشتیبانی علمی و ارزیابی",
    sidebarPromoTitle: "قوانین بازخورد سازنده",
    sidebarPromoSubtitle: "رعایت استانداردهای کدنویسی و عدم تحقیر یا مقایسه منفی کارآموزان",
    sidebarPromoButton: "مشاهده شیوه‌نامه منتوری",
    drawerCloseLabel: "بستن منوی مربی",
    menuButtonLabel: "منوی میز کار منتور",
    navigationLabel: "ناوبری اصلی منتور",
  },
  navigation: [
    { id: "overview", label: "میز کار و صف بررسی", href: "/mentor" },
    { id: "reviews", label: "بازخورد پروژه‌ها", href: "/mentor/reviews" },
    { id: "students", label: "کارآموزان تحت هدایت", href: "/mentor/students" },
    { id: "sessions", label: "جلسات آنلاین", href: "/mentor/sessions" },
  ],
  overview: {
    title: "میز کار مربیگری و صف بررسی بازخوردها",
    heroBadge: "کنسول مربیگری",
    heroBadgeSecondary: "هدایت فنی هدفمند",
    heroHeading: "میز کار منتور: صف هدایت، بازخورد کد و ارزیابی پروژه‌ها",
    heroSubtitle: "بررسی مستقیم کدهای تحویلی، ارائه بازخورد دقیق مهندسی و هدایت گام‌به‌گام کارآموزان در یک محیط متمرکز و ایزوله.",
    heroActionPrimary: "شروع بررسی اولین پروژه صف",
    heroActionSecondary: "مشاهده برنامه جلسات امروز",
    reviewConsoleTitle: "اصول راهبری و منتورینگ CodeSho",
    reviewConsoleSubtitle: "ارزیابی فنی استاندارد بدون نمره‌دهی مقایسه‌ای مخرب",
    check1: "بازخورد فنی مبتنی بر Clean Code",
    check2: "پاسخگویی سریع به گره‌های یادگیری",
    check3: "راهنمایی بدون حل مستقیم مسائل",
    check4: "تأیید گام‌های مسیر شغلی کارآموز",
    kpi1Title: "پروژه‌های نیازمند بررسی",
    kpi1Value: "۴ پروژه",
    kpi1Sub: "اولویت بازخورد امروز",
    kpi2Title: "میانگین زمان پاسخگویی",
    kpi2Value: "۱.۸ ساعت",
    kpi2Sub: "بهتر از سقف استاندارد (۲ ساعت)",
    kpi3Title: "جلسات رفع اشکال هفته",
    kpi3Value: "۶ جلسه",
    kpi3Sub: "۲ جلسه باقی‌مانده امروز",
    kpi4Title: "شاخص کیفیت بازخورد",
    kpi4Value: "۹۸٪",
    kpi4Sub: "بر مبنای رضایت کارآموزان",
    pendingQueueTitle: "صف پروژه‌های منتظر بازخورد",
    pendingItem1Title: "پروژه ماشین‌حساب ماژولار با جاوااسکریپت",
    pendingItem1Student: "علی محمدی — شاخه learning/calc",
    pendingItem1Time: "۳۵ دقیقه پیش",
    pendingItem1Status: "نیازمند بازبینی کد",
    pendingItem2Title: "کامپوننت احراز هویت با استفاده از LocalStorage",
    pendingItem2Student: "سارا احمدی — شاخه auth/token-store",
    pendingItem2Time: "۲ ساعت پیش",
    pendingItem2Status: "پیش‌نویس بازخورد ثبت شده",
    feedbackFocusTitle: "سیاست نظارتی و راهبری مربیگری",
    feedbackFocusDesc: "تمامی تعاملات مربی با کارآموزان در بستر امن و ثبت‌شده CodeSho صورت می‌پذیرد تا کیفیت علمی و ایمنی محیط یادگیری تضمین شود.",
    feedbackComplianceLabel: "وضعیت پایبندی به منشور مربیگری:",
    feedbackComplianceValue: "۱۰۰٪ تاییدشده و دارای اعتبار فعال",
    actionStartReview: "ورود به محیط Code Review",
  },
};
