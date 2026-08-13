import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

const screen = await readFile(new URL("./DashboardScreen.tsx", import.meta.url), "utf8");
const state = await readFile(new URL("./DashboardState.tsx", import.meta.url), "utf8");
const boundary = await readFile(new URL("./DashboardDataBoundary.tsx", import.meta.url), "utf8");

test("course controls are native keyboard controls with truthful selection state", () => {
  assert.match(screen, /<button[^>]+type="button"[^>]+aria-pressed=/);
  assert.match(screen, /aria-pressed=\{course\.id === model\.learning\.selectedCourseId\}/);
  assert.match(screen, /onClick=\{\(\) => onSelectCourse\?\.\(course\.id\)\}/);
  assert.doesNotMatch(screen, /tabIndex=\{-1\}/);
});

test("loading, empty, and failure transitions expose live announcements", () => {
  assert.match(state, /aria-live="polite"[^>]+className=\{styles\.stateGrid\}[^>]+role="status"/);
  assert.match(state, /state === "empty" \|\| state === "lessons-empty"/);
  assert.match(state, /aria-live="polite"/);
  assert.match(state, /role="status"/);
  assert.match(state, /styles\.emptyIcon/);
  assert.match(state, /aria-live=\{isFailure \? "assertive" : "polite"\}/);
  assert.match(state, /role=\{isFailure \? "alert" : "status"\}/);
  const emptyBranch = state.split('if (state === "empty" || state === "lessons-empty")')[1].split("  return")[0];
  assert.doesNotMatch(emptyBranch, /window\.location\.reload/);
});

test("RTL and stale selection boundaries remain explicit", () => {
  assert.match(screen, /<main className=\{styles\.page\} dir="rtl">/);
  assert.match(boundary, /AbortController/);
  assert.match(boundary, /let current = true/);
  assert.match(boundary, /current = false; controller\.abort\(\)/);
  assert.match(boundary, /selectedCourseId: courseId/);
});
