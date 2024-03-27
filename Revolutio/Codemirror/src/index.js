/*
This is the main file which will append the code editor for the specified id.
To generate the bundle.js which you will include in the computation_studio.html
file and run following command in cmd  under Revolutio folder

node_modules/.bin/rollup ./src/index.js -f iife -o ../kore_investment/static/New_CodeMirror/js/editor.bundle.js \
  -p @rollup/plugin-node-resolve

*/

import {basicSetup, EditorView} from "codemirror"
import {EditorState} from "@codemirror/state"
import {python} from "@codemirror/lang-python"

let state = EditorState.create({
  extensions: [
    basicSetup,
    python()
  ]
})

let foo_codemirror = new EditorView({
  state,
  parent: document.getElementById('code_editor')
})

window.foo_codemirror = foo_codemirror
window.state = state