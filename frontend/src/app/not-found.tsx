import type { Metadata } from "next";
import Link from "next/link";
import { authAlphaContent as copy } from "@/content/fa/auth.alpha";
import styles from "./login/login.module.css";

export const metadata: Metadata = {
  title: `${copy.brand} | ${copy.notFoundTitle}`,
  description: copy.notFoundDesc,
};

export default function NotFound() {
  return (
    <main className={styles.page}>
      <section className={styles.card} aria-labelledby="not-found-title">
        <p className={styles.brand}>{copy.brand}</p>
        <h1 id="not-found-title">{copy.notFoundTitle}</h1>
        <p className={styles.message}>{copy.notFoundDesc}</p>
        <Link className={styles.submit} href="/">
          {copy.backHome}
        </Link>
      </section>
    </main>
  );
}
