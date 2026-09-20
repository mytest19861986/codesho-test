export interface AdminNotification {
  id: string;
  title: string;
  description: string;
  time: string;
  read: boolean;
  type: "info" | "warning" | "error" | "success";
}

export interface AdminTenantItem {
  id: string;
  name: string;
  slug: string;
  domain: string;
  status: "active" | "suspended" | "provisioning";
  isolationLevel: string;
  userCount: number;
  healthScore: number;
  lastActive: string;
}

export interface AdminUserItem {
  id: string;
  fullName: string;
  email: string;
  role: "superadmin" | "tenant_admin" | "auditor" | "compliance_officer";
  tenantName: string;
  status: "active" | "suspended" | "pending";
  lastLogin: string;
  mfaEnabled: boolean;
}

export interface AdminRoleItem {
  id: string;
  roleName: string;
  roleCode: string;
  description: string;
  userCount: number;
  permissionsCount: number;
  systemReserved: boolean;
  scope: string;
}

export interface AdminAuditEvent {
  id: string;
  actor: string;
  action: string;
  resource: string;
  ipAddress: string;
  timestampUtc: string;
  timestampJalali: string;
  status: "SUCCESS" | "DENIED" | "SECURITY_ALERT";
  severity: "low" | "medium" | "high";
  tenantContext: string;
}

export interface AdminSystemMetric {
  key: string;
  title: string;
  value: string;
  status: "optimal" | "warning" | "critical";
  detail: string;
}

export interface AdminFeatureFlag {
  id: string;
  name: string;
  key: string;
  enabled: boolean;
  description: string;
  riskLevel: "low" | "medium" | "high";
}

export const adminAlphaContent = {
  brand: "کدشو",
  portalTitle: "سامانه مدیریت و حاکمیت مرکزی",
  envNotice: "محیط نظارت و راهبری (داده‌های شبیه‌سازی‌شده - Synthetic Data Only)",
  
  nav: {
    dashboard: "داشبورد حاکمیتی",
    users: "مدیریت کاربران و نقش‌ها",
    roles: "ماتریس دسترسی (RBAC)",
    tenants: "سازمان‌ها و مستأجرها",
    audit: "ردیابی امنیتی و رویدادها",
    governance: "سیاست‌ها و انطباق",
    system: "پایش سیستم و پایلوت",
  },

  dashboard: {
    title: "میز فرماندهی و تله‌متری حاکمیتی",
    subtitle: "نظارت زنده بر سلامت چندمستأجری، رویدادهای امنیتی و بار کاری سامانه",
    quickStats: [
      { label: "سازمان‌های فعال", value: "۴ سازمان", change: "+۱ در ماه جاری" },
      { label: "کاربران سیستمی", value: "۲۸۴ کاربر", change: "۹۹.۲٪ فعال" },
      { label: "نرخ موفقیت تراکنش‌ها", value: "۱۰۰٪", change: "بدون نقض ایزولاسیون" },
      { label: "وضعیت پایلوت", value: "پایدار (Staging)", change: "نسخه 00dc640" },
    ],
    tenantHealthTitle: "وضعیت ایزولاسیون سازمان‌ها",
    auditAlertsTitle: "آخرین رویدادهای نظارتی",
    systemOpsTitle: "وضعیت زیرساخت و کش",
  },

  tenants: {
    title: "مدیریت سازمان‌ها و ایزولاسیون",
    subtitle: "پایش تفکیک داده‌ها و تنظیمات اختصاصی هر سازمان آموزشی",
    tableHeaders: {
      name: "نام سازمان",
      domain: "دامنه اختصاصی",
      status: "وضعیت سرویس",
      isolation: "سطح ایزولاسیون",
      users: "تعداد کاربران",
      health: "شاخص سلامت",
      actions: "عملیات",
    },
    items: [
      {
        id: "t-central",
        name: "کدشو مرکزی (Core)",
        slug: "codesho-central",
        domain: "central.codesho.ir",
        status: "active",
        isolationLevel: "Multi-tenant RLS (Fail-closed)",
        userCount: 142,
        healthScore: 100,
        lastActive: "هم‌اکنون",
      },
      {
        id: "t-alborz",
        name: "دبیرستان نمونه البرز",
        slug: "alborz-school",
        domain: "alborz.codesho.ir",
        status: "active",
        isolationLevel: "Tenant Schema + RLS",
        userCount: 68,
        healthScore: 98,
        lastActive: "۱۰ دقیقه پیش",
      },
      {
        id: "t-nokhbegan",
        name: "کانون نخبگان آینده",
        slug: "nokhbegan-center",
        domain: "nokhbegan.codesho.ir",
        status: "active",
        isolationLevel: "Tenant Schema + RLS",
        userCount: 54,
        healthScore: 99,
        lastActive: "۲۵ دقیقه پیش",
      },
      {
        id: "t-asrnovin",
        name: "آموزشگاه عصر نوین",
        slug: "asr-novin-academy",
        domain: "novin.codesho.ir",
        status: "provisioning",
        isolationLevel: "Tenant Schema + RLS",
        userCount: 20,
        healthScore: 95,
        lastActive: "۱ ساعت پیش",
      },
    ] as AdminTenantItem[],
  },

  users: {
    title: "مدیریت کاربران و انتساب دسترسی",
    subtitle: "تعیین وضعیت چرخه حیات کاربران، تایید هویت دو مرحله‌ای و تخصیص نقش",
    filters: {
      all: "همه کاربران",
      active: "فعال",
      suspended: "معلق",
      pending: "در انتظار بررسی",
    },
    tableHeaders: {
      user: "کاربر",
      role: "نقش سیستمی",
      tenant: "سازمان مستقر",
      status: "وضعیت",
      mfa: "ورود دو مرحله‌ای",
      lastLogin: "آخرین ورود",
      actions: "مدیریت",
    },
    items: [
      {
        id: "u-101",
        fullName: "دکتر مهران علوی",
        email: "m.alavi@admin.codesho.ir",
        role: "superadmin",
        tenantName: "کدشو مرکزی (Core)",
        status: "active",
        lastLogin: "امروز ۱۴:۴۵",
        mfaEnabled: true,
      },
      {
        id: "u-102",
        fullName: "مهندس سارا رضوانی",
        email: "s.rezvani@admin.codesho.ir",
        role: "tenant_admin",
        tenantName: "دبیرستان نمونه البرز",
        status: "active",
        lastLogin: "امروز ۱۳:۲۰",
        mfaEnabled: true,
      },
      {
        id: "u-103",
        fullName: "احسان کاظمی",
        email: "e.kazemi@compliance.codesho.ir",
        role: "auditor",
        tenantName: "کدشو مرکزی (Core)",
        status: "active",
        lastLogin: "دیروز ۱۸:۱۰",
        mfaEnabled: true,
      },
      {
        id: "u-104",
        fullName: "فاطمه شریفی",
        email: "f.sharifi@alborz.codesho.ir",
        role: "compliance_officer",
        tenantName: "دبیرستان نمونه البرز",
        status: "pending",
        lastLogin: "بدون ورود",
        mfaEnabled: false,
      },
    ] as AdminUserItem[],
  },

  roles: {
    title: "ماتریس سطوح دسترسی (RBAC)",
    subtitle: "پیکربندی حدود اختیارات، سیاست‌های امنیتی و تفکیک وظایف سازمانی",
    tableHeaders: {
      role: "عنوان نقش",
      code: "شناسه نقش",
      description: "شرح وظایف و حدود اختیارات",
      scope: "محدوده اعتبار",
      usersCount: "تعداد کاربران",
      actions: "ویرایش سیاست",
    },
    items: [
      {
        id: "r-superadmin",
        roleName: "مدیر ارشد حاکمیتی (Superadmin)",
        roleCode: "ROLE_SUPERADMIN",
        description: "دسترسی نامحدود سیستمی به پیکربندی کلان، مدیریت مستأجرها و زیرساخت",
        userCount: 2,
        permissionsCount: 48,
        systemReserved: true,
        scope: "Global System",
      },
      {
        id: "r-tenantadmin",
        roleName: "راهبر سازمان (Tenant Admin)",
        roleCode: "ROLE_TENANT_ADMIN",
        description: "مدیریت کاربران، دوره‌ها و تنظیمات همان سازمان بدون دسترسی به سایر مستأجرها",
        userCount: 14,
        permissionsCount: 28,
        systemReserved: false,
        scope: "Tenant Bound",
      },
      {
        id: "r-auditor",
        roleName: "ممیز امنیتی مستقل (Auditor)",
        roleCode: "ROLE_SECURITY_AUDITOR",
        description: "دسترسی فقط‌خواندنی به لاگ‌های تغییرناپذیر، تله‌متری و تحلیل نقض امنیت",
        userCount: 3,
        permissionsCount: 12,
        systemReserved: true,
        scope: "Cross-tenant Readonly",
      },
      {
        id: "r-compliance",
        roleName: "افسر انطباق و حریم خصوصی (Compliance)",
        roleCode: "ROLE_COMPLIANCE_OFFICER",
        description: "بررسی رضایت‌نامه‌های والدین، موافقت‌نامه‌های حریم کودکان و انقضای داده‌ها",
        userCount: 5,
        permissionsCount: 16,
        systemReserved: false,
        scope: "Policy & Consent",
      },
    ] as AdminRoleItem[],
  },

  audit: {
    title: "ردیابی رویدادها و ممیزی امنیتی",
    subtitle: "تایم‌لاین تغییرناپذیر رویدادهای حساس، تغییرات دسترسی و تراکنش‌های سیستمی",
    headers: {
      timestamp: "زمان ثبت (UTC / جلالی)",
      actor: "عامل رویداد",
      action: "عملیات",
      resource: "منبع مقصد",
      ip: "آدرس شبکه",
      status: "نتیجه ممیزی",
    },
    events: [
      {
        id: "aud-901",
        actor: "m.alavi@admin.codesho.ir",
        action: "TENANT_CONTEXT_SWITCH",
        resource: "tenant:alborz-school",
        ipAddress: "192.168.10.45",
        timestampUtc: "2026-09-20 11:20:15",
        timestampJalali: "۱۴۰۵/۰۶/۲۹ - ۱۴:۵۰",
        status: "SUCCESS",
        severity: "low",
        tenantContext: "codesho-central",
      },
      {
        id: "aud-902",
        actor: "system:certbot-agent",
        action: "TLS_CERTIFICATE_RENEW_DRY_RUN",
        resource: "domain:codesho.ir",
        ipAddress: "127.0.0.1",
        timestampUtc: "2026-09-20 11:15:00",
        timestampJalali: "۱۴۰۵/۰۶/۲۹ - ۱۴:۴۵",
        status: "SUCCESS",
        severity: "low",
        tenantContext: "system",
      },
      {
        id: "aud-903",
        actor: "guest@anonymous",
        action: "UNAUTHORIZED_ADMIN_ACCESS_ATTEMPT",
        resource: "route:/admin/users",
        ipAddress: "185.12.34.89",
        timestampUtc: "2026-09-20 10:45:10",
        timestampJalali: "۱۴۰۵/۰۶/۲۹ - ۱۴:۱۵",
        status: "DENIED",
        severity: "high",
        tenantContext: "none",
      },
      {
        id: "aud-904",
        actor: "s.rezvani@admin.codesho.ir",
        action: "USER_STATUS_UPDATE",
        resource: "user:f.sharifi",
        ipAddress: "10.0.4.12",
        timestampUtc: "2026-09-20 09:30:22",
        timestampJalali: "۱۴۰۵/۰۶/۲۹ - ۱۳:۰۰",
        status: "SUCCESS",
        severity: "medium",
        tenantContext: "alborz-school",
      },
    ] as AdminAuditEvent[],
  },

  governance: {
    title: "سیاست‌های حاکمیتی، رضایت اولیا و حریم داده",
    subtitle: "تنظیم ضوابط سخت‌گیرانه برای حفاظت از داده‌های کودکان، دوره‌های نگهداری و انطباق قانونی",
    policies: [
      {
        id: "pol-1",
        title: "الزام ثبت رضایت الکترونیک والدین",
        description: "هیچ کودک زیر ۱۳ سال نمی‌تواند بدون تایید هویت و رضایت دیجیتال ولی در دوره‌ها شرکت کند.",
        status: "فعال و اجباری",
        enforcement: "Fail-closed (دسترسی بدون رضایت مسدود می‌شود)",
      },
      {
        id: "pol-2",
        title: "سیاست انقضا و پاک‌سازی داده‌های غیرفعال",
        description: "اطلاعات لاگ‌های احراز هویت پس از ۹۰ روز به صورت خودکار بایگانی غیرقابل دسترس می‌شوند.",
        status: "فعال",
        enforcement: "وظیفه دوره‌ای Celery Beat",
      },
      {
        id: "pol-3",
        title: "جداسازی فیزیکی/منطقی اسناد مالی و فاکتورها",
        description: "مبالغ به واحد خرد ریال و زمان‌ها به صورت UTC ثبت شده و هرگز قابل ویرایش پس از صدور نیستند.",
        status: "تغییرناپذیر (Immutable)",
        enforcement: "Database Constraints",
      },
    ],
  },

  system: {
    title: "وضعیت عملیاتی سرور و پرچم‌های پایلوت",
    subtitle: "پایش پارامترهای موتور اجرای پایتون، ریدیس، صف وظایف سلری و کنترل ویژگی‌ها",
    metrics: [
      {
        key: "db_pool",
        title: "استخر اتصالات دیتابیس (PostgreSQL)",
        value: "۲۴ / ۱۰۰ فعال",
        status: "optimal",
        detail: "زمان پاسخ میانگین: ۱.۲ میلی‌ثانیه",
      },
      {
        key: "redis_cache",
        title: "کش توزیع‌شده ریدیس (Redis 7)",
        value: "نرخ اصابت ۹۸.۴٪",
        status: "optimal",
        detail: "حافظه مصرفی: ۱۸ مگابایت",
      },
      {
        key: "celery_latency",
        title: "تاخیر صف سلری (Celery Beat & Worker)",
        value: "۰ ثانیه تاخیر",
        status: "optimal",
        detail: "تسک‌های پردازش‌شده در ۲۴ ساعت: ۴,۲۸۰",
      },
      {
        key: "nginx_upstream",
        title: "پروکسی معکوس هاست (Host Nginx)",
        value: "Active (Proxy -> 18080)",
        status: "optimal",
        detail: "وضعیت گواهی SSL: معتبر (۸۹ روز مانده)",
      },
    ] as AdminSystemMetric[],
    flags: [
      {
        id: "flag-1",
        name: "حالت پایلوت محدود (Limited Pilot Mode)",
        key: "PILOT_STAGING_STRICT",
        enabled: true,
        description: "محدود کردن دسترسی‌های عمومی و جلوگیری از ثبت‌نام‌های ناشناس",
        riskLevel: "medium",
      },
      {
        id: "flag-2",
        name: "پرداخت واقعی (Real Payments Provider)",
        key: "FEATURE_REAL_PAYMENTS",
        enabled: false,
        description: "غیرفعال در محیط آزمایش؛ تمامی تراکنش‌ها به صورت ماک انجام می‌پذیرد",
        riskLevel: "high",
      },
      {
        id: "flag-3",
        name: "اطلاع‌رسانی پیامکی واقعی (Real SMS Notifications)",
        key: "FEATURE_REAL_SMS",
        enabled: false,
        description: "پیامک‌های کد تایید در محیط تست لاگ می‌شوند و ارسال واقعی ندارند",
        riskLevel: "high",
      },
    ] as AdminFeatureFlag[],
  },
};
