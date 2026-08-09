import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

const boundary = await readFile(new URL("./DashboardDataBoundary.tsx", import.meta.url), "utf8");
const client = await readFile(new URL("../auth/authClient.ts", import.meta.url), "utf8");

test("dashboard reads the existing authenticated session contract", () => {
  assert.match(boundary, /getSession\(\)/);
  assert.match(boundary, /session\.user\.username/);
  assert.doesNotMatch(boundary, /fetch\(/);
  assert.match(client, /credentials: "same-origin"/);
  assert.match(client, /const sessionEndpoint = sessionPath/);
});

test("dashboard does not create a domain or mutation endpoint", () => {
  assert.doesNotMatch(boundary, /method:\s*["']POST|PUT|PATCH|DELETE/);
  assert.doesNotMatch(boundary, /localStorage|sessionStorage|document\.cookie/);
});
