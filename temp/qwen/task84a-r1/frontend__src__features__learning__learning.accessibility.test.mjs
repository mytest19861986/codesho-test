import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";
const source = await readFile(new URL("./LearningScreen.tsx", import.meta.url), "utf8");
test("learning workspace is RTL and uses keyboard-native controls", () => { assert.match(source, /dir=\"rtl\"/); assert.match(source, /<button type=\"button\"/); assert.match(source, /aria-label=\"درس‌های دوره\"/); assert.doesNotMatch(source, /tabIndex=\"-1\"/); });
