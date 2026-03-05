/**
 * Covers: comfyui-node-frontend
 * - Extension hooks (all lifecycle hooks)
 * - Custom widgets (addDOMWidget)
 * - Widget hooks (beforeQueued, afterQueued, serializeValue)
 * - Commands, Keybindings
 * - Settings (boolean, combo, number, slider, color, text, radio)
 * - Sidebar tabs
 * - Bottom panel tabs
 * - Menu commands
 * - About page badges
 * - Top bar badges
 * - Action bar buttons
 * - API events
 * - Server-to-client communication
 * - Toast notifications
 * - Dialogs
 * - Context menu items
 * - Node instance properties (onExecuted, etc.)
 * - Frontend Scripts API (import patterns)
 */

import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "skill_test.frontend_extension",

    // ===== Extension Hooks (Lifecycle Order) =====

    // init: After canvas created, before nodes
    async init(app) {
        console.log("[SkillTest] init hook fired");
    },

    // addCustomNodeDefs: Modify node definitions
    async addCustomNodeDefs(defs, app) {
        console.log("[SkillTest] addCustomNodeDefs hook fired, node count:", Object.keys(defs).length);
    },

    // getCustomWidgets: Register custom widget types
    getCustomWidgets(app) {
        return {
            SKILL_TEST_WIDGET(node, inputName, inputData, app) {
                const widget = node.addWidget("text", inputName, "default", () => {});
                widget.serializeValue = () => widget.value;
                return { widget };
            },
        };
    },

    // beforeRegisterNodeDef: Modify node prototype
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "SkillTest_BasicNode") {
            const origOnCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                origOnCreated?.apply(this, arguments);

                // Add a DOM widget (covers Custom Widgets / addDOMWidget)
                const container = document.createElement("div");
                container.style.padding = "4px";
                container.innerHTML = `<small style="color:#888">SkillTest DOM Widget</small>`;

                this.addDOMWidget("skillTestWidget", "custom", container, {
                    serialize: false,
                    getValue() { return ""; },
                    setValue(v) {},
                });
            };
        }
    },

    // nodeCreated: After node instance created
    nodeCreated(node, app) {
        if (node.comfyClass === "SkillTest_PreviewText") {
            // Node instance properties
            node.onExecuted = function(output) {
                console.log("[SkillTest] onExecuted for PreviewText:", output);
            };
            node.onExecutionStart = function() {
                console.log("[SkillTest] onExecutionStart for PreviewText");
            };
        }
    },

    // setup: After app fully loaded
    async setup(app) {
        console.log("[SkillTest] setup hook fired");

        // --- API Events ---
        api.addEventListener("executed", ({ detail }) => {
            // console.log("[SkillTest] Node executed:", detail);
        });

        api.addEventListener("progress", ({ detail }) => {
            // console.log("[SkillTest] Progress:", detail.value, "/", detail.max);
        });

        api.addEventListener("execution_start", ({ detail }) => {
            console.log("[SkillTest] Execution started");
        });

        api.addEventListener("execution_success", ({ detail }) => {
            console.log("[SkillTest] Execution success");
        });

        api.addEventListener("execution_error", ({ detail }) => {
            console.log("[SkillTest] Execution error:", detail);
        });

        api.addEventListener("status", ({ detail }) => {
            // console.log("[SkillTest] Status:", detail);
        });

        // --- Server-to-Client Communication ---
        api.addEventListener("skill_test.status", ({ detail }) => {
            console.log("[SkillTest] Server message received:", detail);
        });

        // --- Sidebar Tabs ---
        app.extensionManager.registerSidebarTab({
            id: "skill-test-sidebar",
            title: "Skill Test",
            icon: "pi pi-check-circle",
            type: "custom",
            render: (container) => {
                container.innerHTML = `
                    <div style="padding: 12px;">
                        <h3 style="margin: 0 0 8px 0;">Skill Test Panel</h3>
                        <p style="margin: 0; color: #888;">This sidebar tab was registered by the skill test extension.</p>
                        <button id="skill-test-toast-btn" style="margin-top: 8px; padding: 4px 8px;">Show Toast</button>
                        <button id="skill-test-dialog-btn" style="margin-top: 4px; padding: 4px 8px;">Show Dialog</button>
                    </div>
                `;

                // --- Toast Notifications ---
                container.querySelector("#skill-test-toast-btn")?.addEventListener("click", () => {
                    app.extensionManager.toast.add({
                        severity: "info",
                        summary: "Skill Test Toast",
                        detail: "This is a test toast notification",
                        life: 3000,
                    });
                });

                // --- Dialogs ---
                container.querySelector("#skill-test-dialog-btn")?.addEventListener("click", async () => {
                    const result = await app.extensionManager.dialog.confirm({
                        title: "Skill Test Confirm",
                        message: "This is a test confirmation dialog. Continue?",
                    });
                    console.log("[SkillTest] Dialog result:", result);
                });
            },
            destroy: () => {
                console.log("[SkillTest] Sidebar tab destroyed");
            },
        });
    },

    // loadedGraphNode: When loading saved graph
    loadedGraphNode(node, app) {
        if (node.comfyClass?.startsWith("SkillTest_")) {
            // console.log("[SkillTest] loadedGraphNode:", node.comfyClass);
        }
    },

    // registerCustomNodes: Register additional node types
    registerCustomNodes(app) {
        console.log("[SkillTest] registerCustomNodes hook fired");
    },

    // beforeRegisterVueAppNodeDefs: Modify node defs before Vue registration
    beforeRegisterVueAppNodeDefs(defs, app) {
        console.log("[SkillTest] beforeRegisterVueAppNodeDefs hook fired");
    },

    // beforeConfigureGraph / afterConfigureGraph
    async beforeConfigureGraph(graphData, missingNodeTypes, app) {
        // console.log("[SkillTest] beforeConfigureGraph");
    },
    async afterConfigureGraph(missingNodeTypes, app) {
        // console.log("[SkillTest] afterConfigureGraph");
    },

    // getSelectionToolboxCommands: Add commands to selection toolbox
    getSelectionToolboxCommands(selectedItem) {
        return ["skill_test.log_selection"];
    },

    // Authentication Hooks
    onAuthUserResolved(user, app) {
        console.log("[SkillTest] onAuthUserResolved:", user);
    },
    onAuthTokenRefreshed() {
        console.log("[SkillTest] onAuthTokenRefreshed");
    },
    onAuthUserLogout() {
        console.log("[SkillTest] onAuthUserLogout");
    },

    // ===== Declarative Extension Properties =====

    // --- Commands ---
    commands: [
        {
            id: "skill_test.log_selection",
            label: "Log Selection (SkillTest)",
            icon: "pi pi-info-circle",
            function: () => {
                console.log("[SkillTest] Command executed: log_selection");
            },
        },
        {
            id: "skill_test.show_toast",
            label: "Show Toast (SkillTest)",
            icon: "pi pi-bell",
            function: () => {
                app.extensionManager.toast.add({
                    severity: "success",
                    summary: "Command Toast",
                    detail: "Triggered via command",
                    life: 2000,
                });
            },
        },
        {
            id: "skill_test.prompt_dialog",
            label: "Prompt Dialog (SkillTest)",
            icon: "pi pi-pencil",
            function: async () => {
                const value = await app.extensionManager.dialog.prompt({
                    title: "Skill Test Prompt",
                    message: "Enter a test value:",
                    defaultValue: "default",
                });
                console.log("[SkillTest] Prompt result:", value);
            },
        },
    ],

    // --- Keybindings ---
    keybindings: [
        {
            commandId: "skill_test.log_selection",
            combo: { key: "l", ctrl: true, shift: true },
        },
    ],

    // --- Settings ---
    settings: [
        {
            id: "skill_test.enabled",
            name: "Enable Skill Test Features",
            type: "boolean",
            defaultValue: true,
            onChange: (value) => {
                console.log("[SkillTest] Setting 'enabled' changed:", value);
            },
        },
        {
            id: "skill_test.mode",
            name: "Processing Mode",
            type: "combo",
            options: ["fast", "quality", "balanced"],
            defaultValue: "balanced",
        },
        {
            id: "skill_test.threshold",
            name: "Detection Threshold",
            type: "slider",
            defaultValue: 0.5,
            attrs: { min: 0, max: 1, step: 0.01 },
        },
        {
            id: "skill_test.label",
            name: "Custom Label",
            type: "text",
            defaultValue: "SkillTest",
        },
    ],

    // --- Bottom Panel Tabs ---
    bottomPanelTabs: [
        {
            id: "skill-test-panel",
            title: "Skill Test",
            type: "custom",
            render: (container) => {
                container.innerHTML = `
                    <div style="padding: 8px;">
                        <p>Bottom panel tab registered by skill test extension.</p>
                    </div>
                `;
            },
        },
    ],

    // --- Menu Commands ---
    menuCommands: [
        {
            path: ["Skill Test"],
            commands: ["skill_test.log_selection", "skill_test.show_toast", "skill_test.prompt_dialog"],
        },
    ],

    // --- About Page Badges ---
    aboutPageBadges: [
        {
            label: "SkillTest v1.0",
            url: "https://github.com/example/skill-test-nodes",
            icon: "pi pi-check-circle",
        },
    ],

    // --- Top Bar Badges ---
    topbarBadges: [
        {
            text: "Skill Test",
            label: "TEST",
            variant: "info",
            icon: "pi pi-check-circle",
            tooltip: "Skill test nodes are loaded",
        },
    ],

    // --- Action Bar Buttons ---
    actionBarButtons: [
        {
            icon: "pi pi-bolt",
            label: "SkillTest",
            tooltip: "Run skill test action",
            onClick: () => {
                app.extensionManager.toast.add({
                    severity: "warn",
                    summary: "Action Bar",
                    detail: "Skill test action button clicked",
                    life: 2000,
                });
            },
        },
    ],

    // ===== Context Menu Items =====

    // Canvas right-click menu
    getCanvasMenuItems(canvas) {
        return [{
            content: "Skill Test: Canvas Action",
            callback: () => {
                console.log("[SkillTest] Canvas context menu clicked");
            },
        }];
    },

    // Node right-click menu
    getNodeMenuItems(node) {
        if (node.comfyClass?.startsWith("SkillTest_")) {
            return [{
                content: "Skill Test: Node Info",
                callback: () => {
                    console.log("[SkillTest] Node context menu for:", node.comfyClass, "id:", node.id);
                    // Node instance properties
                    console.log("  comfyClass:", node.comfyClass);
                    console.log("  isVirtualNode:", node.isVirtualNode);
                    console.log("  imgs:", node.imgs);
                    console.log("  imageIndex:", node.imageIndex);
                },
            }];
        }
        return [];
    },
});
