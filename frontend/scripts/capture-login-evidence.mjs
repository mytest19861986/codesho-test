#!/usr/bin/env node

/**
 * Deterministic login evidence plan. Requires Playwright in the frontend
 * environment; this file intentionally does not install or select a browser.
 */

const VIEWPORTS = Object.freeze([
  ["mobile", 390, 844],
  ["tablet", 768, 1024],
  ["desktop", 1440, 900],
]);
const ARTIFACT_DIR = "artifacts/ui-login";
const BASE_URL = process.env.LOGIN_EVIDENCE_BASE_URL ?? "http://login-fixture.localhost";

function artifact(viewport, state) {
  return `${ARTIFACT_DIR}/login-${viewport}-${state}.png`;
}

async function waitForSuccessOutcome(page, initialUrl) {
  const origin = new URL(initialUrl).origin;
  const loginSuccess = page.waitForResponse(
    (response) => response.url().endsWith("/api/v1/auth/passcode/login/") && response.status() === 204,
    { timeout: 10_000 },
  ).then(() => "login-success");
  const sessionSuccess = page.waitForResponse(
    (response) => response.url().endsWith("/api/v1/auth/session/") && response.status() === 200,
    { timeout: 10_000 },
  ).then(() => "session-success");
  const passcodeChangeRedirect = page.waitForURL(
    (url) => url.origin === origin && url.href !== initialUrl && url.pathname === "/passcode-change",
    { timeout: 10_000 },
  ).then(() => "passcode-change");

  const outcome = await Promise.any([
    Promise.all([loginSuccess, sessionSuccess]).then(() => "login-success"),
    passcodeChangeRedirect,
  ]).catch(() => {
    throw new Error("success outcome was not observed within the bounded timeout");
  });
  const marker = page.locator('[aria-live="polite"]:visible').first();
  await marker.waitFor({ state: "visible", timeout: 5_000 });
  await page.waitForFunction(
    () => Boolean(document.querySelector('[aria-live="polite"]')?.textContent?.trim()),
    undefined,
    { timeout: 5_000 },
  );
  return outcome;
}

async function readRuntimeCredentials() {
  if (process.env.LOGIN_EVIDENCE_RUNTIME !== "1") return null;
  let input = "";
  process.stdin.setEncoding("utf8");
  for await (const chunk of process.stdin) input += chunk;
  const [username, passcode] = input.trimEnd().split(/\r?\n/, 2);
  if (!username || !passcode) throw new Error("runtime credentials must be supplied through stdin");
  return { username, passcode };
}

async function main() {
  let playwright;
  try {
    playwright = await import("playwright");
  } catch {
    throw new Error("Playwright is required; install the pinned frontend evidence dependency first");
  }
  const credentials = await readRuntimeCredentials();
  const browser = await playwright.chromium.launch({
    headless: true,
    ...(process.env.PLAYWRIGHT_EXECUTABLE_PATH
      ? { executablePath: process.env.PLAYWRIGHT_EXECUTABLE_PATH }
      : {}),
  });
  try {
    for (const [name, width, height] of VIEWPORTS) {
      const page = await browser.newPage({ viewport: { width, height } });
      await page.goto(`${BASE_URL}/login`, { waitUntil: "domcontentloaded" });
      await page.screenshot({ path: artifact(name, "initial"), fullPage: true });

      await page.getByRole("button", { name: /.+/ }).click();
      await page.screenshot({ path: artifact(name, "validation"), fullPage: true });

      await page.locator("#username").fill("evidence-user");
      await page.locator("#passcode").fill("1".repeat(6));
      await page.route("**/api/v1/auth/passcode/login/", async (route) =>
        new Promise((resolve) => setTimeout(async () => {
          await route.fulfill({ status: 204, body: "" });
          resolve();
        }, 500)),
      );
      const loading = page.getByRole("button", { name: /.+/ }).click();
      await page.screenshot({ path: artifact(name, "loading"), fullPage: true });
      await loading;

      if (credentials) {
        await page.unroute("**/api/v1/auth/passcode/login/");
        await page.locator("#username").fill(credentials.username);
        await page.locator("#passcode").fill(credentials.passcode);
        const initialUrl = page.url();
        const outcome = waitForSuccessOutcome(page, initialUrl);
        await page.getByRole("button", { name: /.+/ }).click();
        await outcome;
        await page.screenshot({ path: artifact(name, "success"), fullPage: true });
      }
      await page.close();
    }
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(`LOGIN_EVIDENCE_CAPTURE_FAILED: ${error.message}`);
  process.exitCode = 1;
});
