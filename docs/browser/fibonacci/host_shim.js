// Auto-generated WASI shim from multilingual WASM ABI manifest
//
// Requires: wasi_snapshot_preview1.{fd_write, fd_read}
// For production use, prefer a full WASI polyfill such as:
//   npm install @bjorn3/browser_wasi_shim
//
// Minimal inline shim (line-buffers stdout; fd_read returns EOF in browser):
export function createWasiImports(
  memoryRef = { current: null },
  outputCallback = (line) => console.log(line),
  inputProvider = null,
) {
  const textDecoder = new TextDecoder('utf-8');
  const textEncoder = new TextEncoder();
  let stdoutBuf = '';
  function flushLine() {
    let nl;
    while ((nl = stdoutBuf.indexOf('\n')) !== -1) {
      outputCallback(stdoutBuf.slice(0, nl));
      stdoutBuf = stdoutBuf.slice(nl + 1);
    }
  }
  const wasi_snapshot_preview1 = {
    fd_write(fd, iovsPtr, iovsLen, nwrittenPtr) {
      if (fd !== 1 && fd !== 2) return 8;
      const mem = memoryRef.current;
      if (!mem) return 8;
      const view = new DataView(mem.buffer);
      let written = 0;
      for (let i = 0; i < iovsLen; i++) {
        const ptr = view.getUint32(iovsPtr + i * 8, true);
        const len = view.getUint32(iovsPtr + i * 8 + 4, true);
        stdoutBuf += textDecoder.decode(new Uint8Array(mem.buffer, ptr, len));
        written += len;
      }
      flushLine();
      view.setUint32(nwrittenPtr, written, true);
      return 0;
    },
    fd_read(fd, iovsPtr, iovsLen, nreadPtr) {
      // Browser stub: calls inputProvider() if provided, else returns EOF.
      if (fd !== 0) return 8;
      const mem = memoryRef.current;
      if (!mem || !inputProvider) {
        new DataView(mem.buffer).setUint32(nreadPtr, 0, true);
        return 0;
      }
      const line = (inputProvider() ?? '') + '\n';
      const encoded = textEncoder.encode(line);
      const view = new DataView(mem.buffer);
      const ptr = view.getUint32(iovsPtr, true);
      const len = view.getUint32(iovsPtr + 4, true);
      const nread = Math.min(encoded.length, len);
      new Uint8Array(mem.buffer, ptr, nread).set(encoded.subarray(0, nread));
      view.setUint32(nreadPtr, nread, true);
      return 0;
    },
    args_sizes_get(argcPtr, argvBufSizePtr) {
      // Browser stub: reports 0 arguments.
      if (!memoryRef.current) return 8;
      const view = new DataView(memoryRef.current.buffer);
      view.setUint32(argcPtr, 0, true);
      view.setUint32(argvBufSizePtr, 0, true);
      return 0;
    },
    args_get(_argvPtr, _argvBufPtr) { return 0; },
  };
  return { wasi_snapshot_preview1, memoryRef };
}

// Minimal DOM bridge for the WAT env.ml_dom_* host imports used by
// the browser demo. Element references are stored in a JS-side handle
// table; WAT receives opaque numeric handles as f64 values.
export function createDomImports(memoryRef = { current: null }) {
  const textDecoder = new TextDecoder('utf-8');
  const textEncoder = new TextEncoder();
  const handles = new Map();
  let nextHandle = 1;

  function readUtf8(ptr, len) {
    const mem = memoryRef.current;
    if (!mem || len <= 0) return '';
    return textDecoder.decode(new Uint8Array(mem.buffer, ptr, len));
  }

  function writeUtf8(ptr, len, value) {
    const mem = memoryRef.current;
    if (!mem || len <= 0) return 0;
    const bytes = textEncoder.encode(value ?? '');
    const written = Math.min(bytes.length, len);
    new Uint8Array(mem.buffer, ptr, written).set(bytes.subarray(0, written));
    return written;
  }

  function registerElement(element) {
    if (!element) return 0;
    const handle = nextHandle++;
    handles.set(handle, element);
    return handle;
  }

  function getElement(handle) {
    return handles.get(Math.trunc(handle)) || null;
  }

  const env = {
    ml_dom_get(idPtr, idLen) {
      return registerElement(document.getElementById(readUtf8(idPtr, idLen)));
    },
    ml_dom_set_text(handle, ptr, len) {
      const element = getElement(handle);
      if (element) element.textContent = readUtf8(ptr, len);
    },
    ml_dom_set_html(handle, ptr, len) {
      const element = getElement(handle);
      if (element) element.innerHTML = readUtf8(ptr, len);
    },
    ml_dom_get_value(handle, bufPtr, bufLen) {
      const element = getElement(handle);
      if (!element) return 0;
      const value = 'value' in element ? element.value : (element.textContent ?? '');
      return writeUtf8(bufPtr, bufLen, value);
    },
    ml_dom_set_attr(handle, namePtr, nameLen, valuePtr, valueLen) {
      const element = getElement(handle);
      if (element) element.setAttribute(readUtf8(namePtr, nameLen), readUtf8(valuePtr, valueLen));
    },
    ml_dom_create(tagPtr, tagLen) {
      return registerElement(document.createElement(readUtf8(tagPtr, tagLen)));
    },
    ml_dom_append(parentHandle, childHandle) {
      const parent = getElement(parentHandle);
      const child = getElement(childHandle);
      if (parent && child) parent.appendChild(child);
    },
    ml_dom_style(handle, propPtr, propLen, valuePtr, valueLen) {
      const element = getElement(handle);
      if (element) element.style[readUtf8(propPtr, propLen)] = readUtf8(valuePtr, valueLen);
    },
    ml_dom_remove(handle) {
      const element = getElement(handle);
      if (element) element.remove();
    },
    ml_dom_set_class(handle, ptr, len) {
      const element = getElement(handle);
      if (element) element.className = readUtf8(ptr, len);
    },
  };

  return { env, memoryRef };
}

// Read a UTF-8 string returned by a string-valued export.
// Call immediately after the export; ptrF64 is its f64 return value.
// Example:
//   const ptrF64 = exports.greet(42);
//   const str = readStringResult(exports, ptrF64);
export function readStringResult(exports, ptrF64) {
  const ptr = Math.trunc(ptrF64);
  const len = exports.__ml_str_len ? exports.__ml_str_len() : 0;
  if (!exports.memory || len === 0) return '';
  return new TextDecoder('utf-8').decode(
    new Uint8Array(exports.memory.buffer, ptr, len)
  );
}