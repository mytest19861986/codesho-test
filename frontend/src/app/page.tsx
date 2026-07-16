type IconName = "rocket" | "target" | "shield" | "brain" | "spark" | "code";

const paths = [
  { icon: "🚀", title: "Frontend Developer", text: "HTML, CSS, JavaScript و React", tone: "purple" },
  { icon: "◉", title: "AI Engineer", text: "Python، ML و هوش مصنوعی", tone: "lilac" },
  { icon: "⚒", title: "Full Stack Developer", text: "Python و توسعه وب کامل", tone: "cyan" },
];

const projects = [
  ["▦", "اپلیکیشن آب‌وهوا", "React و API"],
  ["▤", "داشبورد مدیریت داده", "React و Chart.js"],
  ["☷", "چت هوشمند", "OpenAI API"],
  ["▧", "فروشگاه اینترنتی", "Next.js و Redux"],
];

function Mark({ name }: { name: IconName }) {
  const glyphs: Record<IconName, string> = {
    rocket: "↗", target: "◎", shield: "♢", brain: "✿", spark: "✦", code: "</>",
  };
  return <span className={`mark mark-${name}`} aria-hidden="true">{glyphs[name]}</span>;
}

export default function Home() {
  return (
    <main>
      <section className="hero-wrap" aria-labelledby="hero-title">
        <nav className="topbar" aria-label="ناوبری اصلی">
          <a className="brand" href="#top" aria-label="کدشو، صفحه اصلی"><span>◉</span> کدشو</a>
          <div className="nav-links">
            <a href="#courses">دوره‌ها</a><a href="#paths">مسیرهای یادگیری</a><a href="#projects">پروژه‌ها</a>
            <a href="#mentor">منتور هوش مصنوعی</a><a href="#footer">درباره ما</a>
          </div>
          <a className="nav-login" href="#courses">ثبت نام</a>
        </nav>

        <div className="hero" id="top">
          <div className="hero-copy">
            <h1 id="hero-title">از کد تا محصول واقعی<br />با قدرت <em>AI</em></h1>
            <p>یادگیری برنامه‌نویسی، ساخت پروژه واقعی و<br />همراهی با مربی هوشمند.</p>
            <div className="hero-actions"><a className="button primary" href="#paths">شروع یادگیری رایگان</a><a className="button ghost" href="#paths">مشاهده مسیرها</a></div>
            <div className="stats" aria-label="آمار کدشو"><div><b>+۲۵,۰۰۰</b><span>دانشجو</span></div><div><b>+۵۰۰</b><span>پروژه واقعی</span></div><div><b>+۱۸۰</b><span>دوره آموزشی</span></div></div>
          </div>
          <div className="device-stage" aria-label="نمایش کدنویسی و پنل یادگیری">
            <div className="stage-grid" />
            <div className="laptop"><div className="laptop-screen"><i /><code>const learn = async () =&gt; &#123;<br />&nbsp; await build(<b>&quot;future&quot;</b>);<br />&nbsp; return <b>success</b>;<br />&#125;</code><div className="terminal-lines"><span /><span /><span /></div></div><div className="laptop-base" /></div>
            <div className="phone"><small>09:41</small><div className="phone-code">&lt;/&gt;<br /><b>شروع</b><br />یادگیری</div><button type="button">ادامه</button></div>
            <div className="mini-panel"><span>پیشرفت امروز</span><strong>۸۵٪</strong><div><i /></div></div>
          </div>
          <aside className="mentor-float"><Mark name="brain" /><div><b>منتور هوشمند AI</b><span>راهنمایی قدم‌به‌قدم، پاسخ فوری و<br />شخصی‌سازی مسیر یادگیری</span></div></aside>
        </div>
      </section>

      <section className="why section" id="courses" aria-labelledby="why-title">
        <h2 id="why-title">چرا کدشو؟</h2>
        <div className="benefits">
          <article><Mark name="shield" /><h3>Security</h3><b>اپلیکیشن امن</b><p>پایدار، امن و پشتیبانی تخصصی</p><span className="benefit-art shield-art" aria-hidden="true">♢</span></article>
          <article><Mark name="code" /><h3>Backend</h3><b>با ساخت پروژه واقعی</b><p>تمرین عملی، انتقال از کد به بازار</p><span className="benefit-art backend-art" aria-hidden="true">▤</span></article>
          <article><Mark name="target" /><h3>Projects</h3><b>با ساخت پروژه محور</b><p>منتور هوشمند، تمرین اختصاصی</p><span className="benefit-art target-art" aria-hidden="true">◎</span></article>
          <article><Mark name="rocket" /><h3>Learning</h3><b>یادگیری پروژه محور</b><p>یادگیری عمیق، ساخت و بازار</p><span className="benefit-art rocket-art" aria-hidden="true">↗</span></article>
        </div>
      </section>

      <section className="paths section" id="paths" aria-labelledby="paths-title">
        <div className="section-heading"><h2 id="paths-title">Learning Paths</h2><p>مهارت‌هایی که تو را مسیر مسیر شغلی واقعی می‌برند</p></div>
        <div className="path-grid">{paths.map((path) => <article className={`path-card ${path.tone}`} key={path.title}><span className="path-icon">{path.icon}</span><h3>{path.title}</h3><p>{path.text}</p><div className="path-bottom"><span>سطح مبتدی</span><i><b /></i><span>Progress</span></div></article>)}</div>
        <div className="dots" aria-label="اسلاید دوم از سه"><button aria-label="اسلاید اول" /><button className="active" aria-label="اسلاید دوم" /><button aria-label="اسلاید سوم" /></div>
      </section>

      <section className="projects section" id="projects" aria-labelledby="projects-title">
        <div className="projects-head"><div><h2 id="projects-title">پروژه‌هایی که در مسیر یادگیری می‌سازی</h2><p>با پروژه‌های واقعی، نمونه‌کار قابل ارائه بساز</p></div><div className="arrows"><button aria-label="پروژه قبلی">‹</button><button aria-label="پروژه بعدی">›</button></div></div>
        <div className="project-grid">{projects.map(([symbol, title, subtitle], index) => <article className={`project-card project-${index + 1}`} key={title}><div className="project-shot"><span>{symbol}</span><i /><i /><i /></div><h3>{title}</h3><p>{subtitle}</p></article>)}</div>
      </section>

      <section className="mentor section" id="mentor" aria-labelledby="mentor-title">
        <div className="mentor-lights" /><div className="mentor-copy"><p className="kicker">همیشه کنار تو</p><h2 id="mentor-title">مربی هوشمند <em>AI</em></h2><p>هر زمان که نیاز داشتی، مربی هوشمند کدشو کنار توست؛ از رفع خطا تا راهنمایی در ساخت پروژه.</p><ul><li>پاسخ سریع به سؤال‌ها</li><li>راهنمایی گام‌به‌گام</li><li>بررسی و تحلیل کد</li></ul><a className="button primary" href="#top">با AI شروع کن</a></div>
        <div className="mentor-visual"><div className="editor"><div className="editor-top"><span /><span /><span /></div><code>function <b>createProject</b>() &#123;<br />&nbsp; const idea = <i>&apos;your future&apos;</i>;<br />&nbsp; return <b>build</b>(idea);<br />&#125;</code><div className="editor-message">عالیه! حالا این بخش را اضافه کن.</div></div><div className="chat-bubble">سلام! چطور می‌تونم کمکت کنم؟</div></div>
      </section>

      <footer id="footer"><div className="footer-brand"><a className="brand" href="#top"><span>◉</span> کدشو</a><p>یادگیری برنامه‌نویسی با ساخت پروژه واقعی</p></div><div><h3>کدشو</h3><a href="#courses">دوره‌ها</a><a href="#paths">مسیرها</a><a href="#projects">پروژه‌ها</a></div><div><h3>منابع</h3><a href="#mentor">منتور AI</a><a href="#projects">مقاله‌ها</a><a href="#footer">درباره ما</a></div><div><h3>ارتباط</h3><a href="mailto:hello@codesho.ir">hello@codesho.ir</a><a href="#footer">تلگرام</a><a href="#footer">اینستاگرام</a></div></footer>
    </main>
  );
}
