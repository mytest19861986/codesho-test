"use client";

import { FormEvent, useRef, useState } from "react";

import { authAlphaContent as copy } from "@/content/fa/auth.alpha";
import { login, normalizePasscode } from "@/features/auth/authClient";

import styles from "./login.module.css";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [passcode, setPasscode] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const messageRef = useRef<HTMLDivElement>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    const normalized = normalizePasscode(passcode);
    if (!username) return setMessage(copy.usernameRequired);
    if (!normalized) return setMessage(copy.passcodeRequired);
    if (!/^\d{6}$/.test(normalized)) return setMessage(copy.passcodeInvalid);
    setBusy(true);
    const result = await login(username, normalized);
    setBusy(false);
    const next = result === "success" ? copy.success : result === "must_change" ? copy.mustChange : result === "invalid" ? copy.invalidCredentials : result === "rate_limited" ? copy.tooManyAttempts : result === "unavailable" ? copy.unavailable : copy.bootstrapFailed;
    setMessage(next);
    messageRef.current?.focus();
    if (result === "success") setPasscode("");
    if (result === "must_change") window.location.assign("/passcode-change");
  }

  return <main className={styles.page}>
    <section className={styles.card} aria-labelledby="login-title">
      <p className={styles.brand}>{copy.brand}</p>
      <h1 id="login-title">{copy.title}</h1>
      <form onSubmit={submit} noValidate>
        <label className={styles.field} htmlFor="username"><span>{copy.usernameLabel}</span><input id="username" name="username" autoComplete="username" value={username} onChange={(event) => setUsername(event.target.value)} /></label>
        <label className={styles.field} htmlFor="passcode"><span>{copy.passcodeLabel}</span><input id="passcode" name="passcode" type="password" inputMode="numeric" autoComplete="current-password" maxLength={6} value={passcode} onChange={(event) => setPasscode(normalizePasscode(event.target.value))} /></label>
        <div className={styles.message} aria-live="polite" tabIndex={-1} ref={messageRef}>{message}</div>
        <button className={styles.submit} type="submit" disabled={busy}>{copy.submit}</button>
      </form>
    </section>
  </main>;
}
