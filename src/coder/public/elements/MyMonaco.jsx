import React, { useEffect, useRef } from "react";
import { useRecoilValue } from "recoil";
import { callFnState } from "@chainlit/react-client";

export default function MonacoEditorComponent() {
  const editorRef = useRef(null);
  const pyRef = useRef(null);
  const editorInstanceRef = useRef(null);
  const callFn = useRecoilValue(callFnState);

  useEffect(() => {
    // If the global Monaco object already exists, initialize the editor
    if (window.monaco && window.monaco.editor) {
      initializeEditor();
      return;
    }

    // If the script is already added, wait for its loading
    const existingScript = document.querySelector(
      `script[src^="https://unpkg.com/monaco-editor"]`
    );
    if (existingScript) {
      existingScript.addEventListener("load", initializeMonaco);
      return;
    }

    // If the script is not added yet, dynamically add it
    const script = newScript("https://unpkg.com/monaco-editor@0.52.2/min/vs/loader.js", initializeMonaco);
    document.head.appendChild(script);
    // const pyScript = newScript("https://pyscript.net/releases/2025.3.1/core.js", null);
    const pyScript = newScript("https://cdn.jsdelivr.net/pyodide/v0.27.5/full/pyodide.js", initializePyodide);
    document.head.appendChild(pyScript);

    function initializeMonaco() {
      // Configure the path to Monaco modules via CDN
      window.require.config({
        paths: { vs: "https://unpkg.com/monaco-editor@0.52.2/min/vs" },
      });
      // Load the main editor module and initialize it
      window.require(["vs/editor/editor.main"], initializeEditor);
    }
    async function initializePyodide() {
      let pyodide = await loadPyodide();
      pyRef.current = pyodide;
      // Pyodide is now ready to use...
      console.log(pyRef.current.runPython(`
        import sys
        sys.version
      `));
    }

    function newScript(src, onLoad) {
      const script = document.createElement("script");
      script.src = src;
      script.async = true;
      script.defer = true;
      if (onLoad) {
        script.onload = onLoad;
      }
      return script;
    }
  }, []);

  // Example of using callFn to update the editor content
  useEffect(() => {
    if (callFn?.name === "update-editor") {
      const { newValue } = callFn.args;
      if (editorInstanceRef.current && newValue !== undefined) {
        editorInstanceRef.current.setValue(newValue);
      }
      callFn.callback();
    }
  }, [callFn]);

  const initializeEditor = () => {
    if (editorRef.current && !editorInstanceRef.current) {
      editorInstanceRef.current = window.monaco.editor.create(
        editorRef.current,
        {
          value: "function hello() {\n\talert('Hello, world!');\n}",
          language: "python",
          theme: "vs-dark",
        }
      );
    }
  };

  return (
    <div className="h-full w-full relative">
      <py-script>
        import datetime as dt
pyscript.write('today', dt.date.today().strftime('%A %B %d, %Y'))
      </py-script>
    </div>
  );
}
