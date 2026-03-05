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
            return { widget };
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

### getSelectionToolboxCommands — Add commands to selection toolbox

```javascript
getSelectionToolboxCommands(selectedItem) {
    // Return array of command IDs to show when item is selected
    return ["my.ext.doSomething"];
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
widget.beforeQueued = function () {
    // Prepare widget value
};

// Called after prompt is queued
widget.afterQueued = function () {
    // Reset or update widget
};

// Custom serialization
widget.serializeValue = function (node, index) {
    return JSON.stringify(this.value);
};
```

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
        options: ["fast", "quality", "balanced"],
        defaultValue: "balanced",
    },
],
```

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
    });
},
```

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

## Toast Notifications

```javascript
app.extensionManager.toast.add({
    severity: "info",  // "success", "info", "warn", "error"
    summary: "Title",
    detail: "Message content",
    life: 3000,  // auto-dismiss after ms
});
```

## Dialogs

```javascript
// Confirmation dialog
const result = await app.extensionManager.dialog.confirm({
    title: "Confirm Action",
    message: "Are you sure?",
});

// Prompt dialog
const value = await app.extensionManager.dialog.prompt({
    title: "Enter Value",
    message: "Provide a name:",
    defaultValue: "default",
});
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

## Frontend Scripts API

Custom node JavaScript can import from the frontend's `src/scripts/` modules. Imports use the Vite shim pattern:

```javascript
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
```

Symbols are also accessible via `window.comfyAPI.<module>.<export>`.

### Stability Levels

| Level | Modules | Notes |
|---|---|---|
| **Stable** | `scripts/app`, `scripts/api` | Guaranteed public API |
| **Internal** (console warning) | `scripts/widgets`, `scripts/domWidget`, `scripts/utils`, `scripts/pnginfo`, `scripts/changeTracker`, `scripts/defaultGraph`, `scripts/metadata/*` | Usable but may change |
| **Deprecated** | `scripts/ui` | Will be removed; use Vue alternatives |

### Key Modules

- **`scripts/api`** — `ComfyApi` class: `fetchApi()`, `queuePrompt()`, `getNodeDefs()`, WebSocket events, settings, user data, system stats
- **`scripts/app`** — `ComfyApp` singleton (`app`): graph operations, `registerExtension()`, `extensionManager`, clipboard, coordinate conversion
- **`scripts/widgets`** — `ComfyWidgets` registry (INT, FLOAT, STRING, BOOLEAN, COMBO, IMAGEUPLOAD, etc.), `addValueControlWidgets()`
- **`scripts/domWidget`** — `addDOMWidget()`, `DOMWidgetImpl`, `ComponentWidgetImpl` (Vue component wrapper)
- **`scripts/utils`** — `clone()`, `addStylesheet()`, `uploadFile()`, `downloadBlob()`, storage helpers
- **`scripts/pnginfo`** — `getPngMetadata()`, `getWebpMetadata()`, `importA1111()`, format-specific extractors

For full API details, see the [API Reference](api-reference.md).

## See Also

- `comfyui-node-basics` - Backend node structure
- `comfyui-node-packaging` - Project structure with JS extensions
- `comfyui-node-inputs` - Backend input types
