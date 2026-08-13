import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";
import { Buffer } from "node:buffer";
import ts from "typescript";

const boundary = await readFile(new URL("./DashboardDataBoundary.tsx", import.meta.url), "utf8");
const screen = await readFile(new URL("./DashboardScreen.tsx", import.meta.url), "utf8");
const client = await readFile(new URL("../auth/authClient.ts", import.meta.url), "utf8");
const learningSource = await readFile(new URL("./learningClient.ts", import.meta.url), "utf8");
const compiledClient = ts.transpileModule(client, { compilerOptions: { module: ts.ModuleKind.ES2022, target: ts.ScriptTarget.ES2022 } }).outputText;
const authClient = await import(`data:text/javascript;base64,${Buffer.from(compiledClient).toString("base64")}`);
const compiledLearning = ts.transpileModule(learningSource, { compilerOptions: { module: ts.ModuleKind.ES2022, target: ts.ScriptTarget.ES2022 } }).outputText.replace(/from "\.\/dashboard\.types";/, "from \"data:text/javascript,export{}\";");
const learningClient = await import(`data:text/javascript;base64,${Buffer.from(compiledLearning).toString("base64")}`);

const courseId = "11111111-1111-4111-8111-111111111111";
const lessonId = "22222222-2222-4222-8222-222222222222";

test("dashboard reads the existing authenticated session contract", () => {
  assert.match(boundary, /getSession\(\)/);
  assert.match(boundary, /session\.user\.username/);
  assert.doesNotMatch(boundary, /fetch\(/);
  assert.match(client, /credentials: "same-origin"/);
  assert.match(client, /const sessionEndpoint = sessionPath/);
  assert.match(client, /userRecord\.id/);
  assert.match(client, /tenantRecord\.id/);
  assert.match(client, /tenantRecord\.role/);
  assert.match(client, /parseSessionContract/);
  assert.doesNotMatch(boundary, /dashboardFixture/);
  assert.match(boundary, /fetchCourses/);
  assert.match(boundary, /fetchLessons/);
});

test("course selection keeps button content valid and non-interactive", () => {
  assert.match(screen, /<button[^>]*aria-pressed=/);
  assert.doesNotMatch(screen, /<button[^>]*>[\s\S]*?<h[1-6][^>]*>/);
  assert.doesNotMatch(screen, /<button[^>]*>[\s\S]*?<p(?:\s|>)/);
  assert.doesNotMatch(screen, /<button[^>]*>[\s\S]*?<a(?:\s|>)/);
});

test("dashboard does not create a domain or mutation endpoint", () => {
  assert.doesNotMatch(boundary, /method:\s*["']POST|PUT|PATCH|DELETE/);
  assert.doesNotMatch(boundary, /localStorage|sessionStorage|document\.cookie/);
});

test("learning client enforces the bounded read contract and same-origin authority", async () => {
  const originalFetch = globalThis.fetch;
  const calls = [];
  try {
    globalThis.fetch = async (input, init) => { calls.push({ input, init }); return { ok: true, status: 200, json: async () => ({ results: [{ id: courseId, code: "C1", title: "Course", state: "published", tenant_id: "must-not-leak" }] }) }; };
    assert.deepEqual(await learningClient.fetchCourses(), [{ id: courseId, code: "C1", title: "Course", state: "published" }]);
    assert.equal(calls[0].input, "/api/v1/learning/courses/?page=1&page_size=20");
    assert.equal(calls[0].init.credentials, "same-origin");
    assert.equal(calls[0].init.headers.Accept, "application/json");
    assert.doesNotMatch(String(calls[0].input), /tenant|role|slug/i);

    globalThis.fetch = async (input, init) => { calls.push({ input, init }); return { ok: true, status: 200, json: async () => ({ results: [{ id: lessonId, code: "L1", title: "Lesson", position: 1, state: "published" }] }) }; };
    assert.deepEqual(await learningClient.fetchLessons(courseId), [{ id: lessonId, code: "L1", title: "Lesson", position: 1, state: "published" }]);
    assert.match(String(calls.at(-1).input), new RegExp(`/api/v1/learning/courses/${courseId}/lessons/\\?page=1&page_size=20$`));
  } finally { globalThis.fetch = originalFetch; }
});

test("learning client preserves typed status failures and rejects malformed data", async () => {
  const originalFetch = globalThis.fetch;
  try {
    for (const [status, kind] of [[400, "invalid-request"], [401, "unauthenticated"], [403, "forbidden"], [404, "parent-not-found"], [500, "recoverable"]]) {
      globalThis.fetch = async () => ({ ok: false, status, json: async () => ({}) });
      await assert.rejects(() => learningClient.fetchLessons(courseId), (error) => error.kind === kind);
    }

    globalThis.fetch = async () => ({ ok: true, status: 200, json: async () => ({ results: [{ id: "not-a-uuid", code: "C1", title: "Course", state: "published" }] }) });
    await assert.rejects(() => learningClient.fetchCourses(), (error) => error.kind === "recoverable");

    globalThis.fetch = async () => ({ ok: true, status: 200, json: async () => ({ results: [{ id: lessonId, code: "L1", title: "Lesson", position: 0, state: "published" }] }) });
    await assert.rejects(() => learningClient.fetchLessons(courseId), (error) => error.kind === "recoverable");

    globalThis.fetch = async () => ({ ok: true, status: 200, json: async () => ({ results: Array.from({ length: 21 }, (_, index) => ({ id: `${String(index + 1).padStart(8, "0")}-1111-4111-8111-111111111111`, code: `C${index}`, title: "Course", state: "published" })) }) });
    await assert.rejects(() => learningClient.fetchCourses(), (error) => error.kind === "recoverable");

    await assert.rejects(() => learningClient.fetchLessons("course-1"), (error) => error.kind === "invalid-request");
  } finally { globalThis.fetch = originalFetch; }
});

test("session parser fails closed for malformed and incomplete contracts", async () => {
  const valid = { authenticated: true, user: { id: "user-1", username: "student" }, tenant: { id: "tenant-1", slug: "school", role: "student" } };
  assert.deepEqual(authClient.parseSessionContract(valid), valid);
  for (const invalid of [
    "not-json",
    { ...valid, user: { ...valid.user, id: 42 } },
    { ...valid, tenant: { ...valid.tenant, id: undefined } },
    { ...valid, tenant: { ...valid.tenant, role: 7 } },
    { ...valid, authenticated: false },
  ]) assert.equal(authClient.parseSessionContract(invalid), null);
});

test("getSession fails closed for malformed, incomplete, and non-success responses", async () => {
  const valid = { authenticated: true, user: { id: "user-1", username: "student" }, tenant: { id: "tenant-1", slug: "school", role: "student" } };
  const originalFetch = globalThis.fetch;
  try {
    globalThis.fetch = async () => ({ ok: true, json: async () => valid });
    assert.deepEqual(await authClient.getSession(), valid);
    globalThis.fetch = async () => ({ ok: true, json: async () => { throw new SyntaxError("malformed"); } });
    assert.equal(await authClient.getSession(), null);
    globalThis.fetch = async () => ({ ok: true, json: async () => ({ ...valid, tenant: { ...valid.tenant, role: 7 } }) });
    assert.equal(await authClient.getSession(), null);
    globalThis.fetch = async () => ({ ok: false, json: async () => valid });
    assert.equal(await authClient.getSession(), null);
  } finally { globalThis.fetch = originalFetch; }
});
