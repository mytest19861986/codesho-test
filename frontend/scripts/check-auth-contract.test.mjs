import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";

const page = fs.readFileSync(new URL("../src/app/login/page.tsx", import.meta.url), "utf8");
const client = fs.readFileSync(new URL("../src/features/auth/authClient.ts", import.meta.url), "utf8");
const styles = fs.readFileSync(new URL("../src/app/login/login.module.css", import.meta.url), "utf8");
const source = `${page}\n${client}`;

test("login route exposes only the approved passcode flow", () => {
  assert.match(page, /type="password"/);
  assert.match(page, /autoComplete="current-password"/);
  assert.match(page, /aria-live="polite"/);
  assert.match(page, /htmlFor="username"/);
  assert.match(page, /htmlFor="passcode"/);
  assert.doesNotMatch(source, /localStorage|sessionStorage|window\.location|router\.|href=/);
  assert.doesNotMatch(source, /signup|recovery|forgot|remember|social|google|github/i);
  assert.match(styles, /min-inline-size:\s*0/);
  assert.match(styles, /max-inline-size:\s*100%/);
  assert.match(styles, /overflow-x:\s*hidden/);
});

test("auth client performs bounded same-origin CSRF and session sequence", () => {
  assert.ok(client.indexOf('fetch(csrfPath') < client.indexOf('method: "POST"'));
  assert.match(client, /credentials: "same-origin"/);
  assert.match(client, /X-CSRFToken/);
  assert.match(client, /response\.status === 204/);
  assert.ok(client.indexOf("fetch(sessionPath") > client.indexOf("response.status === 204"));
  assert.match(client, /normalizePasscode/);
});
