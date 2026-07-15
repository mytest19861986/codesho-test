export default function Home() {
  return (
    <main className="shell">
      <section className="card" aria-labelledby="page-title">
        <span className="eyebrow">Sprint Zero</span>
        <h1 id="page-title">زیرساخت کدشو آماده ساخت است</h1>
        <p>
          این صفحه موقت فقط سلامت Next.js، راست‌به‌چپ بودن رابط و مسیر Same-Origin را
          تأیید می‌کند. طراحی محصول پس از تحویل Design System توسط Gemini جایگزین می‌شود.
        </p>
        <a href="/api/schema/swagger-ui/">مشاهده قرارداد API</a>
      </section>
    </main>
  );
}
