import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

const source = await readFile(new URL("./LearningScreen.tsx", import.meta.url), "utf8");

test("learning workspace is RTL and uses keyboard-native disclosure controls", () => {
  assert.match(source, /dir="rtl"/);
  assert.match(source, /<button type="button"/);
  assert.match(source, /aria-expanded=/);
  assert.match(source, /aria-controls/);
  assert.match(source, /aria-label="درس‌های دوره"/);
  assert.doesNotMatch(source, /aria-pressed/);
  assert.doesNotMatch(source, /tabIndex="-1"/);
});
