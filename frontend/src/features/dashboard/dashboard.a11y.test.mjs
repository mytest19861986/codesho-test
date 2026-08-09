import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const source = await readFile(new URL("./DashboardScreen.tsx", import.meta.url), "utf8");
const state = await readFile(new URL("./DashboardState.tsx", import.meta.url), "utf8");

test("dashboard exposes semantic landmarks and accessible states", () => {
  assert.match(source, /<main|AppShell/);
  assert.match(source, /aria-labelledby/);
  assert.match(source, /aria-hidden="true"/);
  assert.match(source, /DashboardState/);
  assert.match(state, /role="status"/);
  assert.doesNotMatch(source, /textAction/);
});

test("dashboard keeps demo data behind a typed fixture boundary", async () => {
  const fixture = await readFile(new URL("./dashboard.fixture.ts", import.meta.url), "utf8");
  assert.match(fixture, /DashboardModel/);
});
