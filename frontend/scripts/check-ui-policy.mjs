import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import ts from "typescript";

const LEGACY_FILES = new Set([
  "src/app/page.tsx",
  "src/app/styles.css",
  "src/app/ui-001.css",
]);
const PRODUCTION_DIRS = ["src/app", "src/components", "src/content", "src/i18n"];
const USER_FACING_ATTRIBUTES = new Set(["alt", "aria-description", "aria-label", "placeholder", "title"]);
const RAW_COLOR_PATTERNS = [
  /#[0-9a-f]{3,8}\b/i,
  /\b(?:rgb|rgba|hsl|hsla|oklch)\s*\(/i,
  /\b(?:linear|radial|conic)-gradient\s*\([^)]*(?:#|\b(?:rgb|rgba|hsl|hsla|oklch|white|black|red|blue|green)\b)/i,
];
const NAMED_COLOR_DECLARATION = /(?:^|[;{])\s*(?:color|background(?:-color|-image)?|border(?:-[\w-]+)?|outline(?:-color)?|box-shadow)\s*:\s*[^;{}]*(?:\b(?:white|black|red|blue|green|yellow|orange|purple|transparent)\b)/i;
const FORBIDDEN_IMPORT = /(?:^|[/\\])(?:fixtures?|mocks?|demo|preview)(?:[/\\]|$)/i;

function rootPath(root, relativePath) {
  return path.join(root, relativePath);
}

function relativePath(root, filePath) {
  return path.relative(root, filePath).replaceAll(path.sep, "/");
}

function sha256(filePath) {
  return crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex").toUpperCase();
}

function walkFiles(directory) {
  if (!fs.existsSync(directory)) return [];
  const files = [];
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const filePath = path.join(directory, entry.name);
    if (entry.isDirectory()) files.push(...walkFiles(filePath));
    else if (entry.isFile()) files.push(filePath);
  }
  return files;
}

function sourceFiles(root) {
  return PRODUCTION_DIRS.flatMap((directory) => walkFiles(rootPath(root, directory)))
    .filter((filePath) => /\.(?:css|js|jsx|mjs|ts|tsx)$/.test(filePath));
}

function report(violations, filePath, message) {
  violations.push(`${filePath}: ${message}`);
}

function scanRawColors(root, filePath, text, violations) {
  const relative = relativePath(root, filePath);
  if (LEGACY_FILES.has(relative)) return;
  for (const pattern of RAW_COLOR_PATTERNS) {
    if (pattern.test(text)) {
      report(violations, relative, `raw color syntax matched ${pattern}`);
      break;
    }
  }
  const cssWithoutTokens = text.replace(/var\([^)]*\)/g, "var-token");
  if (filePath.endsWith(".css") && NAMED_COLOR_DECLARATION.test(cssWithoutTokens)) {
    report(violations, relative, "named color in a CSS declaration");
  }
}

function scanJsx(root, filePath, text, violations) {
  const relative = relativePath(root, filePath);
  if (LEGACY_FILES.has(relative) || !/\.tsx$/.test(filePath)) return;
  const source = ts.createSourceFile(filePath, text, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
  function visit(node) {
    if (ts.isJsxText(node) && node.getText(source).trim()) {
      report(violations, relative, "non-empty JSXText must come from typed content or props");
    }
    if (ts.isJsxExpression(node)) {
      const expression = node.expression;
      if (expression && (ts.isStringLiteral(expression) || ts.isNoSubstitutionTemplateLiteral(expression))) {
        report(violations, relative, "display string literal in JSX must come from typed content or props");
      }
    }
    if (ts.isJsxAttribute(node) && USER_FACING_ATTRIBUTES.has(node.name.text)) {
      const initializer = node.initializer;
      if (initializer && ts.isStringLiteral(initializer)) {
        report(violations, relative, `literal user-facing JSX attribute ${node.name.text}`);
      }
    }
    ts.forEachChild(node, visit);
  }
  visit(source);
}

function scanProductionImports(root, filePath, text, violations) {
  const relative = relativePath(root, filePath);
  const source = ts.createSourceFile(filePath, text, ts.ScriptTarget.Latest, true, filePath.endsWith(".tsx") ? ts.ScriptKind.TSX : ts.ScriptKind.TS);
  function check(specifier) {
    if (specifier && FORBIDDEN_IMPORT.test(specifier)) {
      report(violations, relative, `production import uses forbidden fixture/mock/demo/preview path: ${specifier}`);
    }
  }
  function visit(node) {
    if (ts.isImportDeclaration(node) && ts.isStringLiteral(node.moduleSpecifier)) check(node.moduleSpecifier.text);
    if (ts.isImportEqualsDeclaration(node) && ts.isExternalModuleReference(node.moduleReference) && ts.isStringLiteral(node.moduleReference.expression)) check(node.moduleReference.expression.text);
    if (ts.isCallExpression(node) && node.expression.getText(source) === "require" && node.arguments.length === 1 && ts.isStringLiteral(node.arguments[0])) check(node.arguments[0].text);
    if (ts.isCallExpression(node) && node.expression.kind === ts.SyntaxKind.ImportKeyword && node.arguments.length === 1 && ts.isStringLiteral(node.arguments[0])) check(node.arguments[0].text);
    ts.forEachChild(node, visit);
  }
  visit(source);
}

function loadBaseline(root) {
  const filePath = rootPath(root, "ui-policy-baseline.json");
  if (!fs.existsSync(filePath)) return { legacy: {} };
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function verifyBaseline(root, baseline, violations) {
  const expected = baseline.legacy ?? {};
  for (const relative of LEGACY_FILES) {
    const filePath = rootPath(root, relative);
    if (!fs.existsSync(filePath)) {
      report(violations, relative, "baseline legacy file is missing");
    } else if (expected[relative] !== sha256(filePath)) {
      report(violations, relative, "legacy file SHA-256 differs from the approved baseline");
    }
  }
  for (const relative of Object.keys(expected)) {
    if (!LEGACY_FILES.has(relative)) report(violations, relative, "baseline contains an unapproved exemption");
  }
}

export function run(root = process.env.UI_POLICY_ROOT ?? path.resolve(import.meta.dirname, "..")) {
  const violations = [];
  const baseline = loadBaseline(root);
  verifyBaseline(root, baseline, violations);
  for (const filePath of sourceFiles(root)) {
    const text = fs.readFileSync(filePath, "utf8");
    scanRawColors(root, filePath, text, violations);
    scanJsx(root, filePath, text, violations);
    scanProductionImports(root, filePath, text, violations);
  }
  return { ok: violations.length === 0, violations };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const result = run();
  if (!result.ok) {
    console.error("UI policy gate failed:");
    for (const violation of result.violations) console.error(`- ${violation}`);
    process.exitCode = 1;
  } else {
    console.log("UI policy gate passed: no raw colors, marketing JSX literals, forbidden production imports, or baseline drift.");
  }
}
