# ComfyUI Frontend Scripts API Reference

Detailed reference for all importable modules from `src/scripts/`.

## Import Stability Levels

| Level | Modules | Behavior |
|---|---|---|
| **Stable** (no warning) | `scripts/app`, `scripts/api` | Guaranteed public API |
| **Internal** (console warning) | `scripts/widgets`, `scripts/domWidget`, `scripts/utils`, `scripts/pnginfo`, `scripts/changeTracker`, `scripts/defaultGraph`, `scripts/metadata/*` | Usable but may change without notice |
| **Deprecated** (removal planned) | `scripts/ui` | Will be removed; use Vue alternatives |

All imports use the Vite shim: `import { X } from "../../scripts/module.js"`.
Symbols are also accessible via `window.comfyAPI.<module>.<export>`.

---

## scripts/api — ComfyApi

```javascript
import { api, ComfyApi } from "../../scripts/api.js";
```

### ComfyApi Class (extends EventTarget)

**Properties:**
- `api_host` / `api_base` — server host and base path
- `initialClientId` / `clientId` — session identifiers
- `user` — current user ID
- `socket` — WebSocket instance
- `authToken` / `apiKey` — authentication credentials

**URL builders:**
- `internalURL(route)` — internal API URL
- `apiURL(route)` — public API URL
- `fileURL(route)` — file access URL

**Fetch:**
- `fetchApi(route, options?)` — authenticated `fetch` wrapper (adds auth headers)

**Node definitions:**
- `getNodeDefs()` — fetch all node definitions from `/object_info`
- `getExtensions()` — list extension JS URLs

**Prompt execution:**
- `queuePrompt(number, data, options?)` — queue a prompt
- `interrupt(runningJobId)` — interrupt execution

**Queue / History:**
- `getQueue()` / `getHistory()` / `getJobDetail(jobId)`
- `getItems(type)` / `deleteItem(type, id)` / `clearItems(type)`

**Models:**
- `getModelFolders()` / `getModels(folder)`
- `viewMetadata(folder, model)`
- `getEmbeddings()`

**Settings (per-user, persisted on server):**
- `getSettings()` / `getSetting(id)` / `storeSettings(settings)` / `storeSetting(id, value)`

**User data (arbitrary file storage on server):**
- `getUserData(file)` / `storeUserData(file, data)` / `deleteUserData(file)`
- `moveUserData(source, dest)` / `listUserDataFullInfo(dir)`

**System:**
- `getSystemStats()` — GPU/CPU stats
- `freeMemory(options)` — free execution cache
- `getLogs()` / `getRawLogs()` / `subscribeLogs(enabled)`
- `getFolderPaths()` — server folder paths

**Feature flags:**
- `serverSupportsFeature(name)` — boolean check
- `getServerFeature(name, defaultValue?)` — get feature value
- `getServerFeatures()` / `getClientFeatureFlags()`

**Workflow templates:**
- `getWorkflowTemplates()` / `getCoreWorkflowTemplates(locale?)`

**Subgraphs:**
- `getGlobalSubgraphData(id)` / `getGlobalSubgraphs()`

**i18n:**
- `getCustomNodesI18n()` — custom node translations

### Events

**Backend events (from WebSocket):**

| Event | Detail Fields |
|---|---|
| `status` | `exec_info` |
| `progress` | `value`, `max`, `node` |
| `executing` | `node`, `display_node`, `prompt_id` |
| `executed` | `node`, `display_node`, `output`, `prompt_id` |
| `execution_start` | `prompt_id`, `timestamp` |
| `execution_success` | `prompt_id`, `timestamp` |
| `execution_error` | `prompt_id`, `node_id`, `exception_message`, `exception_type`, `traceback` |
| `execution_interrupted` | `prompt_id` |
| `execution_cached` | `nodes`, `prompt_id` |
| `b_preview` | binary preview blob |
| `b_preview_with_metadata` | binary preview with JSON metadata |
| `progress_text` | progress text messages |
| `progress_state` | progress state updates |
| `logs` | server log messages |
| `notification` | server notifications |
| `feature_flags` | feature flag updates |
| `asset_download` / `asset_export` | asset operations |

**Frontend events:**

| Event | When |
|---|---|
| `graphChanged` | Workflow graph modified |
| `promptQueueing` | Before prompt is queued |
| `promptQueued` | After prompt is queued |
| `graphCleared` | Graph cleared |
| `reconnecting` | WebSocket reconnecting |
| `reconnected` | WebSocket reconnected |

**Custom events:**
```javascript
api.addCustomEventListener("my_extension.event", callback);
api.removeCustomEventListener("my_extension.event", callback);
api.dispatchCustomEvent("my_extension.event", detailData);
```

---

## scripts/app — ComfyApp

```javascript
import { app, ComfyApp } from "../../scripts/app.js";
```

### `app` Singleton Properties

| Property | Type | Description |
|---|---|---|
| `api` | `ComfyApi` | API client singleton |
| `ui` | `ComfyUI` | Legacy UI instance |
| `extensionManager` | `ExtensionManager` | Extension lifecycle manager (sidebar, toast, dialog, commands, settings) |
| `graph` | `LGraph` | Root LiteGraph graph (deprecated, use `rootGraph`) |
| `rootGraph` | `LGraph` | Root LiteGraph graph |
| `canvas` | `LGraphCanvas` | LiteGraph canvas instance |
| `canvasEl` | `HTMLCanvasElement` | Canvas DOM element |
| `nodeOutputs` | object | Execution output data per node ID |
| `nodePreviewImages` | object | Preview images per node |
| `configuringGraph` | boolean | Whether graph is being configured |
| `vueAppReady` | boolean | Whether Vue app is mounted |
| `bodyTop/Left/Right/Bottom` | HTMLElement | Layout DOM elements |
| `canvasContainer` | HTMLElement | Canvas container element |
| `menu` | `ComfyAppMenu` | App menu instance |

### `app` Methods

**Registration:**
- `registerExtension(extension)` — register a `ComfyExtension`
- `registerNodes()` / `registerNodeDef(nodeId, nodeDef)` / `registerNodesFromDefs(defs)`

**Graph operations:**
- `loadGraphData(graphData?, clean?, restore_view?, workflow?, options?)` — load workflow
- `graphToPrompt(graph?)` — serialize graph to API prompt format
- `queuePrompt(number, batchCount?, queueNodeIds?)` — queue execution
- `refreshComboInNodes()` — refresh all combo widget options
- `clean()` — reset state
- `getNodeDefs()` — fetch node definitions

**File handling:**
- `handleFile(file, source)` / `handleFileList(fileList)`
- `handleAudioFileList(fileList)` / `handleVideoFileList(fileList)`

**Coordinate conversion:**
- `clientPosToCanvasPos(pos)` — screen → canvas coordinates
- `canvasPosToClientPos(pos)` — canvas → screen coordinates

**Context menus:**
- `collectCanvasMenuItems(canvas)` — gather canvas context menu items
- `collectNodeMenuItems(node)` — gather node context menu items

**Node layout:**
- `positionNodes(nodes)` / `positionBatchNodes(nodes, batchNode)`

**Clipboard (static):**
- `ComfyApp.clipspace` / `ComfyApp.clipspace_invalidate_handler`
- `ComfyApp.copyToClipspace(node)` / `ComfyApp.pasteFromClipspace(node)`
- `ComfyApp.open_maskeditor` / `ComfyApp.onClipspaceEditorSave()`

---

## scripts/widgets — Widget Constructors

```javascript
import { ComfyWidgets, addValueControlWidgets } from "../../scripts/widgets.js";
```

> **Warning**: Internal API, may change.

### ComfyWidgets Registry

Built-in widget constructors keyed by type string:

`INT`, `FLOAT`, `BOOLEAN`, `STRING`, `MARKDOWN`, `COMBO`, `IMAGEUPLOAD`, `COLOR`, `IMAGECOMPARE`, `BOUNDING_BOX`, `CHART`, `GALLERIA`, `PAINTER`, `TEXTAREA`, `CURVE`

**Widget constructor signature:**
```typescript
type ComfyWidgetConstructor = (
  node: LGraphNode,
  inputName: string,
  inputData: InputSpec,
  app: ComfyApp,
  widgetName?: string
) => { widget: IBaseWidget; minWidth?: number; minHeight?: number }
```

### Control Widget Helpers

```javascript
import { addValueControlWidgets, IS_CONTROL_WIDGET } from "../../scripts/widgets.js";

// Add increment/decrement/randomize control to a seed widget
addValueControlWidgets(node, targetWidget, "fixed", undefined, opts);

// Check if a widget is a control widget
if (widget[IS_CONTROL_WIDGET]) { /* ... */ }
```

---

## scripts/domWidget — DOM-Based Widgets

```javascript
import { addWidget, DOMWidgetImpl } from "../../scripts/domWidget.js";
```

> **Warning**: Internal API, may change.

### node.addDOMWidget()

```javascript
node.addDOMWidget(name, type, element, options);
```

**DOMWidgetOptions:**
- `serialize` — boolean, include in API workflow
- `getValue()` / `setValue(v)` — custom get/set
- `onHide()` — called when widget hidden
- `hideOnZoom` — hide when zoomed out
- `selectOn` — event array for selection (e.g., `["focus", "click"]`)
- `beforeResize()` / `afterResize()` — resize hooks

### ComponentWidgetImpl

For wrapping Vue components as widgets:

```javascript
import { ComponentWidgetImpl, addWidget } from "../../scripts/domWidget.js";

const widget = new ComponentWidgetImpl(node, name, {
  component: MyVueComponent,
  modelValue: initialValue,
  "onUpdate:modelValue": (val) => { /* handle change */ },
});
addWidget(node, widget);
```

---

## scripts/utils — Utility Functions

```javascript
import { addStylesheet, uploadFile, clone } from "../../scripts/utils.js";
```

> **Warning**: Internal API, may change.

| Function | Description |
|---|---|
| `clone(obj)` | Deep clone via `structuredClone` with JSON fallback |
| `addStylesheet(url)` | Dynamically add a CSS stylesheet to the page |
| `uploadFile(type?, multiple?)` | Open file picker dialog, return selected `File` |
| `prop(obj, name, defaultVal, setter?)` | Define reactive getter/setter property |
| `getStorageValue(id)` | Read from sessionStorage or localStorage |
| `setStorageValue(id, value)` | Write to both sessionStorage and localStorage |
| `downloadBlob(filename, blob)` | Download a blob as file |

---

## scripts/pnginfo — Metadata Extraction

```javascript
import { getPngMetadata, getWebpMetadata, importA1111 } from "../../scripts/pnginfo.js";
```

> **Warning**: Internal API, may change.

| Function | Description |
|---|---|
| `getPngMetadata(file)` | Extract workflow/prompt metadata from PNG |
| `getWebpMetadata(file)` | Extract metadata from WebP (EXIF parsing) |
| `getFlacMetadata(file)` | Extract metadata from FLAC audio |
| `getAvifMetadata(file)` | Extract metadata from AVIF image |
| `getLatentMetadata(file)` | Extract metadata from safetensors |
| `importA1111(graph, parameters)` | Import A1111-format prompt into graph |

---

## scripts/ui — Legacy UI (Deprecated)

```javascript
import { $el, ComfyDialog } from "../../scripts/ui.js";
```

> **Deprecated**: Will be removed in v1.34. Use Vue alternatives.

| Export | Description |
|---|---|
| `$el(tag, props?, children?)` | DOM element creation helper |
| `ComfyDialog` | Modal dialog class with `show(html)` / `close()` |
| `ComfyUI` | Legacy menu class |

---

## scripts/changeTracker — Undo/Redo

```javascript
import { ChangeTracker } from "../../scripts/changeTracker.js";
```

> **Warning**: Internal API, may change.

| Member | Description |
|---|---|
| `activeState` | Current graph state |
| `undoQueue` / `redoQueue` | State queues |
| `undo()` / `redo()` | Undo/redo operations |
| `beforeChange()` / `afterChange()` | Bracket a change |
| `static init(app)` | Initialize tracking |

---

## scripts/metadata/ — File Format Parsers

Low-level metadata extraction for various file formats:

| Module | Exports |
|---|---|
| `metadata/png` | `getFromPngBuffer`, `getFromPngFile` |
| `metadata/flac` | `getFromFlacBuffer`, `getFromFlacFile` |
| `metadata/avif` | `getFromAvifFile` |
| `metadata/svg` | `getSvgMetadata` |
| `metadata/ebml` | `getFromWebmFile` |
| `metadata/isobmff` | `getFromIsobmffFile` |
| `metadata/json` | `getDataFromJSON` |
| `metadata/parser` | `getWorkflowDataFromFile` |
| `metadata/ply` | `parseASCIIPLY`, `isPLYAsciiFormat` |
| `metadata/gltf` | `getGltfBinaryMetadata` |
| `metadata/ogg` | `getOggMetadata` |
| `metadata/mp3` | `getMp3Metadata` |

---

## scripts/ui/ — Legacy UI Components

| Module | Exports |
|---|---|
| `ui/dialog` | `ComfyDialog` |
| `ui/settings` | `ComfySettingsDialog` (deprecated, use settingStore) |
| `ui/imagePreview` | `calculateImageGrid`, `createImageHost` |
| `ui/draggableList` | `DraggableList` |
| `ui/toggleSwitch` | `toggleSwitch` |
| `ui/utils` | `applyClasses`, `toggleElement` |
| `ui/components/button` | `ComfyButton` |
| `ui/components/buttonGroup` | `ComfyButtonGroup` |
| `ui/components/splitButton` | `ComfySplitButton` |
| `ui/components/popup` | `ComfyPopup` |
| `ui/components/asyncDialog` | `ComfyAsyncDialog` |
| `ui/menu/index` | `ComfyAppMenu` (re-exports above components) |

---

## scripts/defaultGraph

```javascript
import { defaultGraph, blankGraph } from "../../scripts/defaultGraph.js";
```

| Export | Description |
|---|---|
| `defaultGraph` | Default workflow JSON object |
| `defaultGraphJSON` | Stringified default workflow |
| `blankGraph` | Empty workflow JSON |
