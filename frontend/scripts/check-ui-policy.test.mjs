import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { run } from "./check-ui-policy.mjs";

const LEGACY = ["src/app/page.tsx", "src/app/styles.css", "src/app/ui-001.css"];

function hash(content) {
  return crypto.createHash("sha256").update(content).digest("hex").toUpperCase();
}

function fixture() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "codesho-ui-policy-"));
  for (const relative of LEGACY) {
    const filePath = path.join(root, relative);
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    fs.writeFileSync(filePath, `legacy ${relative}\n`);
  }
  fs.mkdirSync(path.join(root, "src/components"), { recursive: true });
  fs.mkdirSync(path.join(root, "src/styles"), { recursive: true });
  const baseline = Object.fromEntries(LEGACY.map((relative) => {
    const content = fs.readFileSync(path.join(root, relative));
    return [relative, hash(content)];
  }));
  fs.writeFileSync(path.join(root, "ui-policy-baseline.json"), JSON.stringify({ version: 1, legacy: baseline }));
  return root;
}

function write(root, relative, content) {
  const filePath = path.join(root, relative);
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, content);
}

test("raw HEX in a component fails", () => {
  const root = fixture();
  write(root, "src/components/Bad.tsx", "export const Bad = () => <div style={{color: '#fff'}}>x</div>;");
  assert.equal(run(root).ok, false);
});

test("rgb and direct gradient syntax fail", () => {
  const root = fixture();
  write(root, "src/components/Bad.css", ".bad { color: rgb(1 2 3); background: linear-gradient(red, blue); }");
  assert.equal(run(root).ok, false);
});

test("named color in a CSS declaration fails", () => {
  const root = fixture();
  write(root, "src/components/Bad.css", ".bad { color: red; }");
  assert.equal(run(root).ok, false);
});

test("marketing JSX literal fails", () => {
  const root = fixture();
  write(root, "src/components/Bad.tsx", "export const Bad = () => <section>شروع یادگیری</section>;");
  assert.equal(run(root).ok, false);
});

test("fixture/mock import fails", () => {
  const root = fixture();
  write(root, "src/components/Bad.tsx", "import data from '../fixtures/home.json'; export const Bad = () => <div>{data}</div>;");
  assert.equal(run(root).ok, false);
});

test("legacy hash mutation fails", () => {
  const root = fixture();
  fs.appendFileSync(path.join(root, "src/app/page.tsx"), "changed\n");
  assert.equal(run(root).ok, false);
});

test("token-layer colors and props pass", () => {
  const root = fixture();
  write(root, "src/styles/tokens.css", ":root { --brand: #5d26df; }");
  write(root, "src/components/Good.tsx", "export const Good = ({label}: {label: string}) => <span>{label}</span>;");
  assert.equal(run(root).ok, true);
});

test("current repository passes the policy baseline", () => {
  const repositoryRoot = path.resolve(import.meta.dirname, "..");
  const result = run(repositoryRoot);
  assert.deepEqual(result, { ok: true, violations: [] });
});
