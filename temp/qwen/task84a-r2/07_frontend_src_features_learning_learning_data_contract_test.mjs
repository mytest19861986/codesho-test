import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

const screen = await readFile(new URL("./LearningScreen.tsx", import.meta.url), "utf8");
const boundary = await readFile(new URL("./LearningDataBoundary.tsx", import.meta.url), "utf8");
const page = await readFile(new URL("../../app/learning/page.tsx", import.meta.url), "utf8");

test("learning has a dedicated route and reuses read contracts", () => { assert.match(page, /LearningDataBoundary/); assert.match(boundary, /fetchCourses/); assert.match(boundary, /fetchLessons/); assert.doesNotMatch(boundary, /POST|PUT|PATCH|DELETE|localStorage|tenant_id/); });
test("learning navigation and disclosure contracts are present", () => { assert.match(screen, /href: "\/learning"/); assert.match(screen, /href: "\/dashboard"/); assert.match(screen, /aria-expanded=/); assert.match(screen, /aria-controls/); assert.doesNotMatch(screen, /aria-pressed/); assert.match(screen, /role="status"/); });
