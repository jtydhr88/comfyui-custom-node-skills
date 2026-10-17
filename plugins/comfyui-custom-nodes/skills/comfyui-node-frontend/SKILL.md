---
name: comfyui-node-frontend
description: ComfyUI frontend JavaScript extensions - hooks, widgets, sidebar tabs, commands, settings, toasts, dialogs. Use when adding UI features to custom nodes, creating custom widgets, or extending the ComfyUI frontend.
---

# ComfyUI Frontend Extensions

Custom nodes can extend the ComfyUI frontend with JavaScript. Extensions register hooks, widgets, commands, settings, and UI components.

## Quick Start

### 1. Export WEB_DIRECTORY in Python

```python
# __init__.py
WEB_DIRECTORY = "./js"
__all__ = ["WEB_DIRECTORY"]
```

### 2. Create JavaScript Extension

```javascript
// js/my_extension.js
import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "my_nodes.my_extension",

    async setup() {
        console.log("Extension loaded!");
    },
});
```

All `.js` files in `WEB_DIRECTORY` are loaded automatically when ComfyUI starts.

## Extension Hooks (Lifecycle Order)

### init — After canvas created, before nodes

```javascript
app.registerExtension({
    name: "my.ext",
    async init(app) {
        // Modify core behavior, add global listeners
    },
});
```

### addCustomNodeDefs — Modify node definitions

```javascript
async addCustomNodeDefs(defs, app) {
    // defs is a dict of all node definitions
    // Can add or modify definitions before registration
    defs["MyFrontendNode"] = {
        input: { required: { text: ["STRING", {}] } },
        output: ["STRING"],
        output_name: ["text"],
        name: "MyFrontendNode",
        display_name: "My Frontend Node",
        category: "custom",
    };
},
```

### getCustomWidgets — Register custom widget types

```javascript
getCustomWidgets(app) {
    return {
        MY_WIDGET(node, inputName, inputData, app) {
            const widget = node.addWidget("text", inputName, "", () => {});
            widget.serializeValue = () => widget.value;
            return { widget };  // or { widget, minWidth, minHeight }; v1.54+ also accepts `return widget`
        },
    };
},
```

### beforeRegisterNodeDef — Modify node prototype

```javascript
async beforeRegisterNodeDef(nodeType, nodeData, app) {
    if (nodeData.name === "MyNode") {
        // Chain onto prototype methods
        const origOnCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            origOnCreated?.apply(this, arguments);
            // Add custom widget, modify behavior, etc.
            this.addWidget("button", "Run", null, () => {
                console.log("Button clicked!");
            });
        };
    }
},
```

### nodeCreated — After node instance created

```javascript
nodeCreated(node, app) {
    if (node.comfyClass === "MyNode") {
        // Modify this specific node instance
        node.color = "#335";
    }
},
```

### setup — After app fully loaded

```javascript
async setup(app) {
    // Add event listeners, register UI components
    app.api.addEventListener("executed", (event) => {
        console.log("Node executed:", event.detail);
    });
},
```

### loadedGraphNode — When loading saved graph

```javascript
loadedGraphNode(node, app) {
    if (node.comfyClass === "MyNode") {
        // Restore state from saved graph
    }
},
```

### registerCustomNodes — Register additional node types

```javascript
registerCustomNodes(app) {
    // Register custom LiteGraph node types
},
```

### beforeRegisterVueAppNodeDefs — Modify node defs before Vue registration

```javascript
beforeRegisterVueAppNodeDefs(defs, app) {
    // Modify definitions before they reach the Vue app
},
```

### beforeConfigureGraph / afterConfigureGraph

```javascript
async beforeConfigureGraph(graphData, missingNodeTypes, app) {
    // Before graph data is applied
},
async afterConfigureGraph(missingNodeTypes, app) {
    // After graph is fully configured
},
```

### beforeLoadGraph / afterLoadGraph (v1.53.5+) / onGraphLoadError (v1.54.2+)

Bracket a whole workflow load (including API-JSON and A1111 imports, which skip `beforeConfigureGraph`). Order: `beforeLoadGraph` → `beforeConfigureGraph` → `afterConfigureGraph` → `afterLoadGraph`; `onGraphLoadError` runs instead of the `after*` hooks when the load fails.

```javascript
beforeLoadGraph(app) { /* e.g. suspend your own listeners */ },
afterLoadGraph(app) { /* graph fully loaded */ },
onGraphLoadError(error, app) { /* undo whatever beforeLoadGraph started */ },
```

Upcoming (unreleased): graph loads are queued, and calling `app.loadGraphData()` / `loadApiJson()` / `handleFile()` from inside any graph-load hook rejects ("cannot start a nested graph load"). Defer it (`setTimeout`) if you must load another graph.

### getSelectionToolboxCommands — Add commands to selection toolbox

```javascript
getSelectionToolboxCommands(selectedItem) {
    // Return array of command IDs to show when item is selected
    return ["my.ext.doSomething"];
},
```

### onNodeOutputsUpdated — Execution outputs changed

```javascript
onNodeOutputsUpdated(nodeOutputs) {
    // nodeOutputs: Record<NodeLocatorId, output data>, fired when node outputs update
},
```

### Authentication Hooks

```javascript
onAuthUserResolved(user, app) {
    // Fires when user authentication resolves
},
onAuthTokenRefreshed() {
    // Fires when auth token is refreshed
},
onAuthUserLogout() {
    // Fires when user logs out
},
```

## Custom Widgets

### Adding DOM Widgets

```javascript
beforeRegisterNodeDef(nodeType, nodeData, app) {
    if (nodeData.name === "MyNode") {
        const origOnCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            origOnCreated?.apply(this, arguments);

            const container = document.createElement("div");
            container.innerHTML = `<input type="color" value="#ff0000">`;
            container.querySelector("input").addEventListener("change", (e) => {
                this.widgets.find(w => w.name === "color").value = e.target.value;
            });

            this.addDOMWidget("colorPicker", "custom", container, {
                serialize: true,
                getValue() { return container.querySelector("input").value; },
                setValue(v) { container.querySelector("input").value = v; },
            });
        };
    }
},
```

### Widget Hooks

```javascript
// Called before prompt is queued
// isPartialExecution is true when only selected nodes are queued
widget.beforeQueued = function ({ isPartialExecution } = {}) {
    // Prepare widget value
};

// Called after prompt is queued
widget.afterQueued = function ({ isPartialExecution } = {}) {
    // Reset or update widget. Core control_after_generate now also applies
    // on partial runs (v1.53.5+); the flag is still passed for your own logic.
};

// Custom serialization (may be async; it is awaited)
widget.serializeValue = function (node, index) {
    return JSON.stringify(this.value);
};
```

### Widget Rules (store-backed widgets, v1.53+)

Widget values live in a store keyed by `graphId:nodeId:widgetName`:

- **Names must be unique per node.** A repeat is renamed to `name#1`, `name#2`… or refused if it cannot be renamed (v1.58+); before that it silently overwrote the first widget's value.
- **Don't rename a widget after adding it** — the stored value stays under the old name. Remove it and add a new one.
- **Remove with `node.removeWidget(widget)`**, not by splicing `node.widgets`.
- **`node.widgets` may be `undefined`** until first assigned: `node.widgets ??= []`, `node.widgets?.length ?? 0`.
- **Create widgets via `addWidget` / `addCustomWidget` / `addDOMWidget`** (or a `BaseWidget` subclass). A plain object pushed onto `node.widgets` is never registered.

### Hiding Widgets

```javascript
widget.hidden = true;            // hide everywhere at runtime (still serialized; works in Nodes 2.0)
widget.advanced = true;          // show only when "show advanced" is on

// Per-surface policy at creation (v1.55.6+); all three keys are required
node.addWidget("text", "debug", "", null, {
    surfaces: { canvas: "shown", vueNode: "never", panel: "never" },  // "shown" | "advanced" | "never"
});
```

`options.canvasOnly` (= `vueNode`/`panel: "never"`) is deprecated but still honored; `options.hideInPanel` hides only from the right side panel.

## Declarative Extension Properties

### Commands

```javascript
app.registerExtension({
    name: "my.ext",
    commands: [
        {
            id: "my.ext.doSomething",
            label: "Do Something",
            icon: "pi pi-bolt",
            function: () => { console.log("Executed!"); },
            // v1.55.14+: refuse to run while the canvas is select-only
            mutatesGraph: true,  // or () => boolean
        },
    ],
});
```

### Keybindings

```javascript
keybindings: [
    {
        commandId: "my.ext.doSomething",
        combo: { key: "d", ctrl: true, shift: true },
    },
],
```

### Settings

```javascript
settings: [
    {
        id: "my.ext.mySetting",
        name: "My Setting",
        type: "boolean",
        defaultValue: true,
        onChange: (value) => { console.log("Setting changed:", value); },
    },
    {
        id: "my.ext.mode",
        name: "Processing Mode",
        type: "combo",
        options: ["fast", "quality", "balanced"],  // or (currentValue) => [...] for dynamic options
        defaultValue: "balanced",
    },
],
```

`onChange(newValue, oldValue)` may be async.

**Setting types**: `boolean`, `number`, `slider`, `knob`, `combo`, `radio`, `text`, `image`, `color`, `url`, `hidden`, `backgroundImage`

### Sidebar Tabs

```javascript
async setup(app) {
    app.extensionManager.registerSidebarTab({
        id: "my-sidebar",
        title: "My Panel",
        icon: "pi pi-cog",
        type: "custom",
        render: (container) => {
            container.innerHTML = "<h3>My Custom Panel</h3>";
        },
        destroy: () => {
            // Cleanup
        },
        // v1.58+: return true to handle the click yourself (skips default open/close)
        onToggle: async () => false,
    });
},
```

`type: "vue"` tabs (`component: MyVueComponent`) must bundle their own Vue UI libraries — the host no longer provides PrimeVue (upcoming; see Breaking Changes).

### Bottom Panel Tabs

```javascript
bottomPanelTabs: [
    {
        id: "my-panel",
        title: "My Panel",
        type: "custom",
        render: (container) => {
            container.innerHTML = "<div>Panel content</div>";
        },
    },
],
```

### Menu Commands

```javascript
menuCommands: [
    {
        path: ["My Extension"],
        commands: ["my.ext.doSomething"],
    },
],
```

### About Page Badges

```javascript
aboutPageBadges: [
    { label: "v1.0.0", url: "https://github.com/...", icon: "pi pi-github", severity: "warn" },
    // severity is optional: "danger" | "warn"
],
```

### Top Bar Badges

```javascript
topbarBadges: [
    {
        text: "My Extension",        // required
        label: "BETA",               // optional badge label
        variant: "info",             // "info" | "warning" | "error"
        icon: "pi pi-star",          // optional icon
        tooltip: "Extension info",   // optional tooltip
    },
],
```

### Action Bar Buttons

```javascript
actionBarButtons: [
    {
        icon: "pi pi-bolt",           // required
        label: "My Action",           // optional label
        tooltip: "Run my action",     // optional tooltip
        onClick: () => { /* ... */ },  // required click handler
    },
],
```

## API Events

Listen to execution events:

```javascript
// Node execution completed
app.api.addEventListener("executed", ({ detail }) => {
    const { node, output } = detail;
    // output contains images, text, etc.
});

// Execution progress
app.api.addEventListener("progress", ({ detail }) => {
    const { value, max, node } = detail;
});

// Execution started/completed
app.api.addEventListener("execution_start", ({ detail }) => {});
app.api.addEventListener("execution_success", ({ detail }) => {});
app.api.addEventListener("execution_error", ({ detail }) => {});

// Status updates
app.api.addEventListener("status", ({ detail }) => {
    const { exec_info } = detail;
});
```

## Server-to-Client Communication

### Python (server side):

```python
from server import PromptServer

PromptServer.instance.send_sync(
    "my_extension.update",
    {"status": "complete", "data": result}
)
```

### JavaScript (client side):

```javascript
app.api.addEventListener("my_extension.update", ({ detail }) => {
    console.log("Received:", detail);
});
```

### Calling Your Own Routes

```javascript
// fetchApi prefixes /api and adds auth headers
const res = await app.api.fetchApi("/my_extension/process", {
    method: "POST",
    body: JSON.stringify(payload),
    timeoutMs: null,  // v1.55.2+: default aborts after 60 s without response headers (TimeoutError)
});
```

Pass `timeoutMs: null` (or a larger number) for slow synchronous routes; your own `signal` is still honored.

## Toast Notifications

v1.58+ API — `success` / `info` / `warning` / `error` / `loading(title, options?)` return a `ToastId`:

```javascript
const toast = app.extensionManager.toast;
const id = toast.loading("Processing…");
// Reusing `id` replaces that toast in place
toast.success("Done", {
    id,
    description: "3 images saved",
    duration: 3000,              // ms; default is no auto-dismiss
    closable: true,
    action: { label: "Open", onClick: () => { /* ... */ } },  // does not auto-dismiss
});
toast.dismiss(id);               // returns true if a toast was removed
toast.dismissAll();
```

Older frontends only have `add()`. It still works on v1.58+ but is deprecated; feature-detect:

```javascript
if (toast.success) toast.success("Saved", { description: "Done", duration: 3000 });
else toast.add({ severity: "success", summary: "Saved", detail: "Done", life: 3000 });
// add() severities: "success" | "info" | "warn" | "error" ("secondary"/"contrast" → info).
// group/styleClass are ignored and remove()/removeAll() are gone on v1.58+.
```

## Dialogs

```javascript
// Confirmation dialog — resolves true / false, or null if dismissed
const result = await app.extensionManager.dialog.confirm({
    title: "Confirm Action",
    message: "Are you sure?",
    type: "delete",            // optional: "default" | "overwrite" | "delete" | "info" | ...
    itemList: ["a.png"],       // optional bullet list under the message
    hint: "Cannot be undone",  // optional
    key: "my-ext-confirm",     // v1.53+: own dialog key so an already-open shared prompt can't swallow it
});

// Prompt dialog
const value = await app.extensionManager.dialog.prompt({
    title: "Enter Value",
    message: "Provide a name:",
    defaultValue: "default",
});
```

## ExtensionManager Utilities

### Setting Access

```javascript
// Read a setting value
const val = app.extensionManager.setting.get("my.ext.mySetting");

// Write a setting value
app.extensionManager.setting.set("my.ext.mySetting", newValue);
```

### Execution Errors (read-only)

```javascript
// Last node-level errors (keyed by node ID)
const nodeErrors = app.extensionManager.lastNodeErrors;

// Last execution-level error
const execError = app.extensionManager.lastExecutionError;
```

### Markdown Rendering

```javascript
// Render markdown to sanitized HTML (marked + DOMPurify, safe for innerHTML)
const html = app.extensionManager.renderMarkdownToHtml(markdownStr, baseUrl);
```

## Context Menu Items

```javascript
app.registerExtension({
    name: "my.ext",

    // Canvas right-click menu
    getCanvasMenuItems(canvas) {
        return [{
            content: "My Action",
            callback: () => { console.log("Canvas menu clicked"); },
        }];
    },

    // Node right-click menu
    getNodeMenuItems(node) {
        if (node.comfyClass === "MyNode") {
            return [{
                content: "Custom Action",
                callback: () => { console.log("Node:", node.id); },
            }];
        }
        return [];
    },
});
```

## Node Instance Properties (LGraphNode Augmentations)

```javascript
// Available on node instances:
node.comfyClass       // ComfyUI node type name
node.isVirtualNode    // true for frontend-only nodes
node.imgs             // preview images array
node.imageIndex       // current preview image index

// Callbacks:
node.onExecuted = function(output) { /* execution result */ };
node.onExecutionStart = function() { /* about to execute */ };
node.onDragOver = function(event) { /* file drag over */ };
node.onDragDrop = function(event) { /* file dropped */ };
```

## Recent Breaking Changes (frontend 1.4x – 1.58, plus upcoming)

Changes extension authors should be aware of. Upstream migration notes with details: https://github.com/Comfy-Org/ComfyUI_frontend/tree/main/docs/extensions (`widgets-migration.md`, `connection-callbacks-migration.md`, `serialization-callbacks-migration.md`, `node-geometry-migration.md`, `link-registration-migration.md`, `primevue-removal-migration.md`, `tooltip-migration.md`).

- **PrimeVue removed (upcoming, after v1.58)** — no `$primevue`, no PrimeVue theme, no global `--p-*` CSS variables. Use design tokens instead: `--primary-background`, `--base-foreground`, `--muted-foreground`, `--base-background`, `--secondary-background`, `--border-default`. To keep using PrimeVue components, mount your own Vue app with PrimeVue installed. `pi pi-*` icon classes still work.
- **PrimeVue tooltip gone (v1.58+)** — no `v-tooltip` / `.p-tooltip`. An open tooltip is `[data-slot="tooltip-content"]` on `document.body`.
- **Toast API replaced (v1.58+)** — see Toast Notifications. `add()` / `addAlert()` are deprecated; `remove()` / `removeAll()` are removed.
- **Widget values are store-backed (v1.53+)** — see Widget Rules (unique names, `removeWidget`, `node.widgets ??= []`).
- **`input.link` / `output.links` deprecated (v1.53+)** — reads still work but warn and may lag the graph. Writes no longer change links, except that `input.link = null` disconnects. Use `node.isInputConnected(i)`, `node.getInputLink(i)`, `node.isOutputConnected(i)`, `node.getOutputNodes(i)`, `node.connect()`, `node.disconnectInput(i)`. The `node:slot-links:changed` and `node:slot-errors:changed` graph events are removed. For add/remove notifications with several subscribers, use `graph.events.addEventListener("node:added" | "node:before-removed" | "node:removed", ...)`.
- **`onConfigure(data)` receives a shallow copy (v1.55.2+)** — changing top-level keys of `data` has no effect. Persist custom state in `node.properties` / `graph.extra`.
- **Core node fields are accessors (v1.53+)** — `id`, `type`, `title`, `mode`, `flags`, `color`, `bgcolor`, `shape` no longer appear in `Object.keys(node)` / `{...node}`; use `node.serialize()`. Changing `node.type` after construction warns.
- **`node.size` is the requested size** — `getBounding()` / `boundingRect` give the rendered footprint (can be larger). `canvas.repositionNodesVueMode()` → `canvas.applyNodePositions()` (old name kept as deprecated alias).
- **`canvas.selected_nodes` deprecated (upcoming)** — warns and returns a snapshot. Read `canvas.selectedItems` (a snapshot Set; re-read it after `add`/`delete`) and change the selection with `canvas.selectItems(items, addToCurrent?)`.
- **Minor deprecations** — `node.badgePosition` (badges always render top-right; assignment is ignored), `node.widgets_up` (use `widgets_start_y`), `options.canvasOnly` (use `options.surfaces`).
- **Group nodes removed** — group nodes can no longer be created; workflows containing them auto-convert to **subgraphs** on load. `GroupNodeHandler` / `GroupNodeConfig` remain re-exported for backward compatibility only. Use subgraphs for new work.
- **`LiteGraph.use_uuids` removed** — node IDs are always numeric. Don't read or set this flag (UUIDs are still used internally for subgraph/slot IDs).
- **`LGraph.onGetNodeMenuOptions` removed**; **`LGraph.onBeforeChange` deprecated** — assigning it still works but warns; use `LGraphCanvas.onBeforeChange` instead.
- **`IBaseWidget.entityId` removed** — widget identity is the `widgetId` branded key (`graphId:nodeId:name`); promoted subgraph widgets are store-backed.
- **`node.size` is Proxy-backed** — both `node.size[1] = h` and `node.size = [w, h]` now correctly reflow Vue-rendered nodes; no polling workarounds needed.

## Frontend Scripts API

Custom node JavaScript can import from the frontend's `src/scripts/` modules. Imports use the Vite shim pattern:

```javascript
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
```

Symbols are also accessible via `window.comfyAPI.<module>.<export>`. Only directly declared exports (`export const|let|var|function|class`) are shimmed; re-exports such as `export { x } from "..."` are not reachable this way.

### Stability Levels

| Level | Modules | Notes |
|---|---|---|
| **Stable** | `scripts/app`, `scripts/api` | Guaranteed public API |
| **Internal** (console warning) | `scripts/widgets`, `scripts/domWidget`, `scripts/utils`, `scripts/pnginfo`, `scripts/changeTracker`, `scripts/defaultGraph`, `scripts/metadata/*` | Usable but may change |
| **Deprecated** | `scripts/ui` | Will be removed; use Vue alternatives |

### Key Modules

- **`scripts/api`** — `ComfyApi` class: `fetchApi()`, `queuePrompt()`, `getNodeDefs()`, WebSocket events, settings, user data, system stats
- **`scripts/app`** — `ComfyApp` singleton (`app`): graph operations, `registerExtension()`, `extensionManager`, clipboard, coordinate conversion
- **`scripts/widgets`** — `ComfyWidgets` registry (INT, FLOAT, STRING, BOOLEAN, COMBO, IMAGEUPLOAD, etc.), `addValueControlWidget(s)()`, `updateControlWidgetLabel()` (`IS_CONTROL_WIDGET` no longer exported since v1.58)
- **`scripts/domWidget`** — `addDOMWidget()`, `DOMWidgetImpl`, `ComponentWidgetImpl` (Vue component wrapper)
- **`scripts/utils`** — `clone()`, `addStylesheet()`, `uploadFile()`, storage helpers
- **`scripts/pnginfo`** — `getPngMetadata()`, `getWebpMetadata()`, `importA1111()`, format-specific extractors

For full API details, see the [API Reference](api-reference.md).

## See Also

- `comfyui-node-basics` - Backend node structure
- `comfyui-node-packaging` - Project structure with JS extensions
- `comfyui-node-inputs` - Backend input types
