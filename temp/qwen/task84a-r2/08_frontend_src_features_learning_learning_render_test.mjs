import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const typescript = require("typescript");

function loadComponent(source, exportedName, prelude) {
  const withoutImports = source.replace(/^import[^\n]*\n/gm, "");
  const compiled = typescript.transpileModule(`${prelude}\n${withoutImports}`, {
    compilerOptions: { jsx: typescript.JsxEmit.React, module: typescript.ModuleKind.CommonJS, target: typescript.ScriptTarget.ES2022 },
  }).outputText;
  const componentModule = { exports: {} };
  new Function("require", "module", "exports", "React", compiled)(require, componentModule, componentModule.exports, React);
  return componentModule.exports[exportedName];
}

const screenSource = await readFile(new URL("./LearningScreen.tsx", import.meta.url), "utf8");
const stateSource = await readFile(new URL("./LearningState.tsx", import.meta.url), "utf8");
const screenPrelude = `const styles = new Proxy({}, { get: () => "" }); const Card = ({ children }) => React.createElement("div", null, children); const AppShell = ({ children }) => React.createElement(React.Fragment, null, children); const LearningState = () => null;`;
const statePrelude = `const styles = new Proxy({}, { get: () => "" });`;
const LearningScreen = loadComponent(screenSource, "LearningScreen", screenPrelude);
const LearningState = loadComponent(stateSource, "LearningState", statePrelude);

const model = {
  courses: [{ id: "course-1", title: "آشنایی با وب", code: "WEB-1" }, { id: "course-2", title: "طراحی رابط", code: "UI-1" }],
  selectedCourseId: "course-1",
  lessons: [{ id: "lesson-1", title: "مبانی", code: "WEB-1-1", position: 1 }],
};

test("rendered learning disclosure has truthful stable relationships", () => {
  const html = renderToStaticMarkup(React.createElement(LearningScreen, { model, state: "ready" }));
  const buttons = [...html.matchAll(/<button\b([^>]*)>/g)].map((match) => match[1]);
  assert.equal(buttons.length, 2);
  assert.match(buttons[0], /aria-expanded="true"/);
  assert.match(buttons[0], /aria-controls="learning-lessons-course-1"/);
  assert.match(buttons[1], /aria-expanded="false"/);
  assert.doesNotMatch(buttons[1], /aria-controls/);
  assert.match(html, /id="learning-lessons-course-1"/);
  assert.doesNotMatch(html, /Learning space|Project-based learning|Published courses|>courses(?:<|\s)/);
  assert.match(html, /dir="rtl"/);
});

test("rendered learning states preserve authentication and retry semantics", () => {
  const unauthenticated = renderToStaticMarkup(React.createElement(LearningState, { state: "unauthenticated" }));
  const forbidden = renderToStaticMarkup(React.createElement(LearningState, { state: "forbidden" }));
  const notFound = renderToStaticMarkup(React.createElement(LearningState, { state: "parent-not-found" }));
  const invalid = renderToStaticMarkup(React.createElement(LearningState, { state: "invalid-request" }));
  const recoverable = renderToStaticMarkup(React.createElement(LearningState, { state: "recoverable-error" }));
  assert.match(unauthenticated, /href="\/login"/);
  assert.doesNotMatch(forbidden, /<button/);
  assert.doesNotMatch(notFound, /<button/);
  assert.doesNotMatch(invalid, /<button/);
  assert.match(recoverable, /<button/);
  assert.match(recoverable, /تلاش دوباره/);
});
