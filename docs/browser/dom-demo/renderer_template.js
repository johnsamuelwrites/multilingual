// Auto-generated renderer skeleton from multilingual WASM ABI manifest
//
// Exported functions (all numeric args/returns are f64):
//   __main() -> void
export const ABI_EXPORTS = {
  "__main": {
    "mode": "scalar_field",
    "stream_output": null
  }
};

export async function loadWasmModule(url, importsFactory) {
  const memoryRef = { current: null };
  const imports = importsFactory(memoryRef);
  const result = await WebAssembly.instantiateStreaming(fetch(url), imports);
  const exports = result.instance.exports;
  memoryRef.current = exports.memory || null;
  return { instance: result.instance, exports, memoryRef };
}

// Load the canonical bundle emitted by `build-wasm-bundle` from a directory URL.
export async function loadWasmBundle(baseUrl, importsFactory) {
  const bundleUrl = new URL('module.wasm', new URL(baseUrl, import.meta.url));
  return loadWasmModule(bundleUrl, importsFactory);
}

// Call any exported numeric function by name.
// args: array of numbers (f64).  Returns the f64 result, or undefined for void.
// Example: callFunction(exports, 'fibonacci', [10]) // => 55
export function callFunction(exports, name, args = []) {
  const fn = exports[name];
  if (!fn) throw new Error(`No export named '${name}'`);
  return fn(...args);
}

export function renderByMode(ctx, abiName, exports, args = []) {
  const abi = ABI_EXPORTS[abiName];
  if (!abi) throw new Error(`Unknown ABI export: ${abiName}`);
  if (abi.mode === 'scalar_field') {
    return callFunction(exports, abiName, args);
  }
  if (abi.mode === 'point_stream' || abi.mode === 'polyline') {
    const stream = abi.stream_output;
    if (!stream) throw new Error(`Missing stream metadata for ${abiName}`);
    const count = exports[stream.count_export]();
    return { count, writer: stream.writer_export };
  }
  throw new Error(`Unsupported render mode: ${abi.mode}`);
}