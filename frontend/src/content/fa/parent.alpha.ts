export const parentAlphaContent = {
  brand: "CodeSho",
  tagline: "همراهی آگاهانه، آینده مطمئن",
  shell: {
    drawerCloseLabel: "بستن منوی اولیا",
    menuButtonLabel: "باز کردن منوی ناوبری",
    navigationLabel: "ناوبری پورتال اولیا",
    roleLabel: "ولی دانش‌آموز",
    userName: "رضا محمدی (سرپرست)",
    logoutLabel: "خروج از حساب",
    searchPlaceholder: "جستجوی گزارش‌ها، دوره‌ها، پرداخت‌ها و ...",
    searchShortcut: "Ctrl + K",
    notificationsLabel: "اعلان‌های نظارتی",
    unreadCount: "۱",
    settingsLabel: "تنظیمات حریم خصوصی",
    supportLabel: "ارتباط با مشاور",
    sidebarPromoTitle: "مشاوره اختصاصی تحصیلی",
    sidebarPromoSubtitle: "گفتگوی تخصصی با مشاوران CodeSho",
    sidebarPromoButton: "درخواست مشاوره",
  },
  navigation: [
    { id: "overview", label: "نمای کلی و نظارت", href: "/parent" },
    { id: "progress", label: "گزارش پیشرفت فرزند", href: "/parent/progress" },
    { id: "finance", label: "وضعیت مالی و اشتراک", href: "/parent/finance" },
    { id: "consent", label: "رضایت‌نامه‌ها و حریم", href: "/parent/consent" },
  ],
  overview: {
    title: "پنل نظارت و همراهی اولیا",
    childSelectLabel: "انتخاب فرزند فعال:",
    child1Option: "علی محمدی (پایه دهم ریاضی)",
    child2Option: "مریم محمدی (پایه هفتم)",
    selectedChildName: "علی محمدی (دانش‌آموز پایه دهم)",
    selectedChildBadge: "احراز هویت شده (Synthetic)",

    heroBadge: "نظارت شفاف و امن",
    heroHeading: "گزارش عملکرد و وضعیت یادگیری فرزند شما",
    heroSubtitle: "CodeSho با تفکیک کامل حریم خصوصی، امکان پایش دقیق استمرار مطالعه، کیفیت انجام تکالیف و تعامل با منتور را برای اولیا فراهم می‌کند.",
    heroActionPrimary: "مشاهده گزارش جامع هفته",
    heroActionSecondary: "گفتگو با مشاور تحصیلی",
    
    // Panel glass items
    oversightQuote: "«آرامش خاطر والدین با شفافیت کامل مسیر رشد»",
    oversightNote: "محیط نظارتی ایمن و تفکیک‌شده (Role Isolation)",
    check1: "استمرار مطالعه هفتگی پایدار",
    check2: "تاییدیه امنیتی فعالیت‌ها",
    check3: "عدم مقایسه یا رتبه‌بندی مخرب",
    check4: "پشتیبانی فعال مشاوران",

    // 4 KPI Cards for Parents
    kpi1Title: "ساعات یادگیری ماهانه",
    kpi1Value: "۴۸ ساعت",
    kpi1Sub: "۱۰ ساعت بالاتر از میانگین هدف",

    kpi2Title: "تکالیف تحویل‌شده",
    kpi2Value: "۲۴ پروژه",
    kpi2Sub: "۱۰۰٪ تاییدیه کیفی مربی",

    kpi3Title: "استمرار مطالعه متوالی",
    kpi3Value: "۱۲ روز",
    kpi3Sub: "بدون وقفه تحصیلی",

    kpi4Title: "اعتبار اشتراک آموزشی",
    kpi4Value: "۶۵ روز",
    kpi4Sub: "بسته یادگیری فرانت‌اند",

    // Middle Sections
    weeklyTrendTitle: "روند استمرار یادگیری در ماه جاری",
    weeklyTrendSubtitle: "ساعات تمرین و کدنویسی به تفکیک هفته",
    
    recentMilestonesTitle: "نقاط عطف و دستاوردهای ثبت‌شده",
    milestoneStatusApproved: "تأییدشده",
    milestone1Title: "تکمیل پروژه ماشین حساب مدولار",
    milestone1Date: "۲ روز پیش",
    milestone1Status: "تایید منتور ارشد",
    milestone2Title: "پایان فصل مفاهیم State در React",
    milestone2Date: "۵ روز پیش",
    milestone2Status: "نمره عالی در آزمون مفهومی",
    milestone3Title: "تکمیل پروژه طراحی صفحات وب با HTML و CSS",
    milestone3Date: "دیروز",
    milestone3Status: "تأیید مربی",
    milestone4Title: "آشنایی با متغیرها و حلقه‌ها در پایتون مقدماتی",
    milestone4Date: "۴ روز پیش",
    milestone4Status: "در حال بررسی",


    // Filter and empty states
    filterPrefix: "فیلتر شده بر اساس:",
    filterSuffixCount: "مورد",
    noSearchResults: "نتیجه‌ای برای جستجو یافت نشد",

    // Consent and Safety Section
    safetyTitle: "حریم خصوصی و مجوزهای اولیا",
    safetyBadge: "سیاست حاکمیتی",
    safetyDescription: "تمامی دسترسی‌ها، ارتباطات با منتورها و انتشار نمونه‌کارها در محیط ایزوله و منوط به سیاست‌های حاکمیتی سامانه است.",
    consentStatusLabel: "مجوز نظارت تحصیلی:",
    consentStatusValue: "فعال و ثبت‌شده در دفتر کل",
    consentStatusDisabled: "غیرفعال (محدودشده توسط والد)",
    actionManageConsent: "مدیریت مجوزها و دسترسی‌ها",

    // Operational Modal 1: Weekly Report
    weeklyReportModalTitle: "کارنامه و گزارش تحلیلی پیشرفت هفتگی",
    weeklyReportModalCloseAria: "بستن گزارش",
    weeklyReportChildPrefix: "گزارش عملکرد فرزند گرامی شما (",
    weeklyReportChildSuffix: ") در هفته جاری:",
    weeklyReportMetric1Label: "زمان یادگیری متمرکز:",
    weeklyReportMetric1Value: "۱۲ ساعت و ۴۵ دقیقه (افزایش ۱۵٪ نسبت به هفته قبل)",
    weeklyReportMetric2Label: "تمرین‌های کدنویسی تکمیل‌شده:",
    weeklyReportMetric2Value: "۸ پروژه کوچک و ۱ ارزیابی میان‌دوره",
    weeklyReportMetric3Label: "تاییدیه سلامت و اخلاق تعاملی:",
    weeklyReportMetric3Value: "۱۰۰٪ بدون هیچ‌گونه هشدار یا نقض قوانین",
    weeklyReportCloseBtn: "بستن کارنامه",

    // Operational Modal 2: Contact Mentor / Consultation
    mentorModalTitle: "درخواست مشاوره و گفتگوی اختصاصی",
    mentorModalCloseAria: "بستن گفتگو",
    mentorModalDesc: "پیام یا درخواست مشاوره خود پیرامون روند تحصیلی را ثبت نمایید:",
    mentorModalSuccess: "پیام شما برای تیم مشاوره و منتورینگ ارسال گردید و حداکثر ظرف ۴ ساعت پاسخ داده خواهد شد.",
    mentorModalPlaceholder: "پرسش یا یادداشت نظارتی خود را اینجا بنویسید...",
    mentorModalSendBtn: "ارسال پیام به مشاور",
    mentorModalCancelBtn: "انصراف",

    // Operational Modal 3: Consent Management
    consentModalTitle: "تنظیمات حریم خصوصی و مجوزهای نظارت اولیا",
    consentModalCloseAria: "بستن پنجره مجوزها",
    consentModalItem1Title: "مجوز مشاهده روزانه ساعت مطالعه و تکالیف",
    consentModalItem1Desc: "امکان رویت دقیق تایم‌لاین و خروجی تمرینات ثبت‌شده در محیط یادگیری",
    consentModalItem2Title: "دریافت پیامک هشدارهای عدم استمرار مطالعه",
    consentModalItem2Desc: "ارسال اعلان در صورت عدم فعالیت تحصیلی بیش از ۳ روز متوالی",
    consentModalConfirmBtn: "تأیید و ذخیره تغییرات",
    consentModalCancelBtn: "انصراف",
    privacyAssuranceBadge: "حریم خصوصی تضمین‌شده",
    oversightGridAria: "روند و دستاوردها",
  }
};

