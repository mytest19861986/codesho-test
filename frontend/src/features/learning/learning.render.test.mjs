import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { JSDOM } from "jsdom";

const require = createRequire(import.meta.url);
const React = require("react");
const { act } = React;
const ReactDOMClient = require("react-dom/client");
const typescript = require("typescript");

function loadComponent(source, exportedName, prelude) {
  const withoutImports = source.replace(/^import[^\n]*\n/gm, "");
  const compiled = typescript.transpileModule(`${prelude}\n${withoutImports}`, {
    compilerOptions: {
      jsx: typescript.JsxEmit.React,
      module: typescript.ModuleKind.CommonJS,
      target: typescript.ScriptTarget.ES2022,
    },
  }).outputText;
  const componentModule = { exports: {} };
  new Function("require", "module", "exports", "React", compiled)(require, componentModule, componentModule.exports, React);
  return componentModule.exports[exportedName];
}

function installDom() {
  const dom = new JSDOM("<!doctype html><html><body></body></html>", { url: "https://codesho.test/learning" });
  globalThis.window = dom.window;
  globalThis.document = dom.window.document;
  Object.defineProperty(globalThis, "navigator", { configurable: true, value: dom.window.navigator });
  globalThis.HTMLElement = dom.window.HTMLElement;
  globalThis.Node = dom.window.Node;
  globalThis.IS_REACT_ACT_ENVIRONMENT = true;
  return dom;
}

async function render(component, props) {
  const container = document.createElement("div");
  document.body.replaceChildren(container);
  const root = ReactDOMClient.createRoot(container);
  await act(async () => {
    root.render(React.createElement(component, props));
  });
  return { container, root };
}

const screenSource = await readFile(new URL("./LearningScreen.tsx", import.meta.url), "utf8");
const stateSource = await readFile(new URL("./LearningState.tsx", import.meta.url), "utf8");
const screenPrelude = `const styles = new Proxy({}, { get: () => "" }); const Card = ({ children }) => React.createElement("div", null, children); const AppShell = ({ children }) => React.createElement(React.Fragment, null, children); const LearningState = () => null;`;
const statePrelude = `const styles = new Proxy({}, { get: () => "" });`;
const LearningScreen = loadComponent(screenSource, "LearningScreen", screenPrelude);
const LearningState = loadComponent(stateSource, "LearningState", statePrelude);
const model = {
  courses: [
    { id: "course-1", title: "آشنایی با وب", code: "WEB-1" },
    { id: "course-2", title: "طراحی رابط", code: "UI-1" },
  ],
  selectedCourseId: "course-1",
  lessons: [{ id: "lesson-1", title: "مبانی", code: "WEB-1-1", position: 1 }],
};

installDom();

test("rendered learning disclosure has truthful stable DOM relationships", async () => {
  const { container, root } = await render(LearningScreen, { model, state: "ready" });
  const buttons = [...container.querySelectorAll("button")];
  assert.equal(buttons.length, 2);
  assert.equal(buttons[0].getAttribute("aria-expanded"), "true");
  const controlsId = buttons[0].getAttribute("aria-controls");
  assert.ok(controlsId);
  assert.ok(container.querySelector(`#${controlsId}`));
  assert.equal(buttons[1].getAttribute("aria-expanded"), "false");
  assert.equal(buttons[1].hasAttribute("aria-controls"), false);
  assert.ok(document.getElementById("learning-lessons-course-1"));
  assert.equal(container.querySelector('[dir="rtl"]') !== null, true);
  assert.equal(container.textContent.includes("Learning space"), false);
  assert.equal(container.textContent.includes("Project-based learning"), false);
  assert.equal(container.textContent.includes("Published courses"), false);
  await act(async () => root.unmount());
});

test("rendered learning states preserve authentication and retry semantics", async () => {
  const cases = [
    ["unauthenticated", "/login", false],
    ["forbidden", null, false],
    ["parent-not-found", null, false],
    ["invalid-request", null, false],
    ["recoverable-error", null, true],
  ];
  for (const [state, href, hasRetry] of cases) {
    const { container, root } = await render(LearningState, { state });
    if (href) assert.equal(container.querySelector(`a[href="${href}"]`) !== null, true);
    assert.equal(container.querySelector('button') !== null, hasRetry);
    if (hasRetry) assert.equal(container.textContent.includes("تلاش دوباره"), true);
    await act(async () => root.unmount());
  }
});
