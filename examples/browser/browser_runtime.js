//
// SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
//
// SPDX-License-Identifier: GPL-3.0-or-later
//

import { createWasiImports, createDomImports, readStringResult } from "./host_shim.js";
import { ABI_EXPORTS, callFunction, loadWasmBundle } from "./renderer_template.js";

function appendLine(outputElement, line) {
  outputElement.textContent += `${line}\n`;
}

export async function loadBrowserBundle({
  baseUrl = "./",
  outputElement,
  inputProvider = null,
  // Optional factory: (memRef) => extra import object merged with WASI imports.
  // Use createDomImports(memRef) here to enable the DOM bridge.
  extraImportsFactory = null,
} = {}) {
  if (!outputElement) {
    throw new Error("outputElement is required");
  }

  const outputCallback = (line) => appendLine(outputElement, line);
  const { instance, exports, memoryRef } = await loadWasmBundle(
    baseUrl,
    (memRef) => {
      const wasiImports = createWasiImports(memRef, outputCallback, inputProvider);
      const extra = extraImportsFactory ? extraImportsFactory(memRef) : {};
      return { ...wasiImports, ...extra };
    },
  );

  function resetOutput() {
    outputElement.textContent = "";
  }

  function resetRuntime() {
    if (exports.__ml_reset) {
      exports.__ml_reset();
    }
  }

  function runMain() {
    resetOutput();
    resetRuntime();
    if (exports.__main) {
      exports.__main();
    }
  }

  function callExport(name, args = []) {
    const abi = ABI_EXPORTS[name];
    const result = callFunction(exports, name, args);
    if (abi?.return_type === "str") {
      return readStringResult(exports, result);
    }
    return result;
  }

  return {
    instance,
    exports,
    memoryRef,
    abi: ABI_EXPORTS,
    runMain,
    callExport,
    callableExports() {
      return Object.keys(exports).filter(
        (key) =>
          typeof exports[key] === "function"
          && !key.startsWith("__")
          && key !== "memory",
      );
    },
  };
}
