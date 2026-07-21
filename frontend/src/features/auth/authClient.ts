export type LoginResult = "success" | "must_change" | "invalid" | "rate_limited" | "unavailable" | "error";
export type PasscodeChangeResult = "success" | "expired" | "same_as_current" | "rate_limited" | "unavailable" | "invalid" | "error";

const csrfPath = "/api/v1/auth/csrf/";
const loginPath = "/api/v1/auth/passcode/login/";
const sessionPath = "/api/v1/auth/session/";
const passcodeChangePath = "/api/v1/auth/passcode/change/complete/";

function csrfToken(): string | null {
  return document.cookie.split(";").map((part) => part.trim()).find((part) => part.startsWith("csrftoken="))?.slice("csrftoken=".length) ?? null;
}

async function bootstrapCsrf(): Promise<boolean> {
  const response = await fetch(csrfPath, { credentials: "same-origin", headers: { Accept: "application/json" } });
  return response.ok && Boolean(csrfToken());
}

export async function login(username: string, passcode: string): Promise<LoginResult> {
  try {
    let bootstrapped = await bootstrapCsrf();
    if (!bootstrapped) bootstrapped = await bootstrapCsrf();
    if (!bootstrapped) return "error";

    const response = await fetch(loginPath, {
      method: "POST",
      credentials: "same-origin",
      headers: { Accept: "application/json", "Content-Type": "application/json", "X-CSRFToken": csrfToken() ?? "" },
      body: JSON.stringify({ username, passcode }),
    });
    if (response.status === 204) {
      const session = await fetch(sessionPath, { credentials: "same-origin", headers: { Accept: "application/json" } });
      return session.ok ? "success" : "error";
    }
    if (response.status === 401) return "invalid";
    if (response.status === 429) return "rate_limited";
    if (response.status === 503) return "unavailable";
    if (response.status === 403) {
      const payload = await response.json().catch(() => null) as { code?: string } | null;
      return payload?.code === "passcode_change_required" ? "must_change" : "invalid";
    }
    return "error";
  } catch {
    return "error";
  }
}

export async function completePasscodeChange(newPasscode: string): Promise<PasscodeChangeResult> {
  try {
    let bootstrapped = await bootstrapCsrf();
    if (!bootstrapped) bootstrapped = await bootstrapCsrf();
    if (!bootstrapped) return "error";
    const response = await fetch(passcodeChangePath, { method: "POST", credentials: "same-origin", headers: { Accept: "application/json", "Content-Type": "application/json", "X-CSRFToken": csrfToken() ?? "" }, body: JSON.stringify({ newPasscode }) });
    if (response.status === 204) return "success";
    if (response.status === 401) return "expired";
    if (response.status === 409) return "same_as_current";
    if (response.status === 429) return "rate_limited";
    if (response.status === 503) return "unavailable";
    return "invalid";
  } catch { return "error"; }
}

export function normalizePasscode(value: string): string {
  return value.replace(/[۰-۹]/g, (digit) => String(digit.charCodeAt(0) - 1776)).replace(/[٠-٩]/g, (digit) => String(digit.charCodeAt(0) - 1632));
}
