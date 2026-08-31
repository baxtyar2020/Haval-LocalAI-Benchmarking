"use strict";

const vm = require("node:vm");

function deepEqual(a, b) {
  if (a === b) return true;
  if (a === null || b === null) return false;
  if (typeof a !== typeof b) return false;
  if (Array.isArray(a) && Array.isArray(b)) {
    if (a.length !== b.length) return false;
    return a.every((val, i) => deepEqual(val, b[i]));
  }
  if (typeof a === "object" && typeof b === "object") {
    const keysA = Object.keys(a).sort();
    const keysB = Object.keys(b).sort();
    if (!deepEqual(keysA, keysB)) return false;
    return keysA.every((key) => deepEqual(a[key], b[key]));
  }
  return false;
}

function stripTypeAnnotations(code) {
  try {
    new vm.Script(`${code}\n;`);
    return code;
  } catch {
    // fall through
  }
  let result = code;
  result = result.replace(/^\s*(?:export\s+)?type\s+\w+(?:<[^>]*>)?\s*=\s*[^;]+;\s*$/gm, "");
  result = result.replace(/(function\s+\w+)\s*<[^>]+>/g, "$1");
  result = result.replace(/((?:const|let|var)\s+\w+\s*=\s*)<[^>]+>\s*\(/g, "$1(");
  result = result.replace(/\)\s*:\s*(?:[^=>{,()]|<[^>]*>)+(?=\s*\{)/g, ")");
  result = result.replace(/\)\s*:\s*(?:[^=>{,()]|<[^>]*>)+(?=\s*=>)/g, ")");
  result = result.replace(/((?:const|let|var)\s+\w+)\s*:\s*(?:[^=;]|<[^>]*>)+(?=\s*=)/g, "$1");
  result = result.replace(/\s+as\s+(?:\w+(?:<[^>]*>)?(?:\[\])*)/g, "");
  result = result.replace(/(\w)!\./g, "$1.");
  try {
    new vm.Script(`${result}\n;`);
    return result;
  } catch {
    return code;
  }
}

function extractCodeBlock(text, preferredFunctionName) {
  const fenced = text.match(/```(?:javascript|js|typescript|ts)?\s*\n([\s\S]*?)```/i);
  if (fenced) return fenced[1].trim();
  const generic = text.match(/```\s*\n([\s\S]*?)```/);
  if (generic) return generic[1].trim();
  if (preferredFunctionName) {
    const escaped = preferredFunctionName.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const named = text.match(new RegExp(`function\\s+${escaped}\\s*\\([^)]*\\)\\s*\\{`));
    if (named) {
      const start = named.index;
      let depth = 0;
      for (let i = text.indexOf("{", start); i < text.length; i++) {
        if (text[i] === "{") depth++;
        else if (text[i] === "}") {
          depth--;
          if (depth === 0) return text.slice(start, i + 1).trim();
        }
      }
    }
  }
  return String(text || "").trim();
}

function runTestsInSandbox(code, task, sandboxTimeoutMs) {
  const total = Array.isArray(task.tests) ? task.tests.length : 0;
  const VALID_ID = /^[a-zA-Z_$][a-zA-Z0-9_$]*$/;
  if (!VALID_ID.test(task.functionName || "")) {
    return { passed: 0, total };
  }
  let passed = 0;
  try {
    const noop = () => {};
    const sandbox = Object.create(null);
    sandbox.console = Object.freeze({
      log: noop,
      info: noop,
      warn: noop,
      error: noop,
      debug: noop,
      trace: noop,
    });
    const context = vm.createContext(sandbox, {
      codeGeneration: { strings: false, wasm: false },
    });
    const script = new vm.Script(
      `${code}\nglobalThis.__testFn = typeof ${task.functionName} === "function" ? ${task.functionName} : undefined;`
    );
    script.runInContext(context, { timeout: sandboxTimeoutMs });
    if (typeof sandbox.__testFn !== "function") {
      return { passed: 0, total };
    }
    for (const test of task.tests) {
      try {
        const testInputJson = JSON.stringify(structuredClone(test.input));
        const testScript = new vm.Script(`__testFn(...${testInputJson})`);
        const result = testScript.runInContext(context, { timeout: sandboxTimeoutMs });
        if (deepEqual(result, test.expected)) passed++;
      } catch {
        // test failed or timed out
      }
    }
  } catch {
    // compile/run failed
  }
  return { passed, total };
}

let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => {
  input += chunk;
});
process.stdin.on("end", () => {
  try {
    const payload = JSON.parse(input || "{}");
    const task = payload.task || {};
    const raw = typeof payload.text === "string" ? payload.text : payload.code || "";
    const code = stripTypeAnnotations(extractCodeBlock(raw, task.functionName));
    const timeoutMs = typeof payload.sandboxTimeoutMs === "number" ? payload.sandboxTimeoutMs : 5000;
    process.stdout.write(JSON.stringify(runTestsInSandbox(code, task, timeoutMs)));
  } catch (err) {
    process.stdout.write(
      JSON.stringify({
        passed: 0,
        total: 0,
        error: err instanceof Error ? err.message : String(err),
      })
    );
  }
});
