# ComfyUI Custom Node Skills

A curated collection of agent skills (for [Claude Code](https://docs.anthropic.com/en/docs/claude-code/skills) and [OpenAI Codex](https://developers.openai.com/codex/build-skills)) for developing ComfyUI custom nodes. These skills give the agent comprehensive knowledge of the ComfyUI node system, covering both the V3 (recommended) and V1 (legacy) APIs.

The `SKILL.md` files follow the open [agentskills.io](https://agentskills.io) standard and are shared by both agents — install once, works everywhere.

> **[中文说明](README_ZH.md)**

## Skills Overview

| Skill | Trigger | Description |
|---|---|---|
| **comfyui-node-basics** | Creating nodes, defining classes, project setup | V3 node structure, `io.Schema`, inputs/outputs, `ComfyExtension` registration |
| **comfyui-node-inputs** | Configuring widgets, adding inputs | INT, FLOAT, STRING, BOOLEAN, COMBO, hidden/optional/lazy inputs, `force_input` |
| **comfyui-node-outputs** | Returning results, previews, saving files | `NodeOutput`, `PreviewImage/Mask/Audio/Text`, `SavedImages`, UI helpers |
| **comfyui-node-datatypes** | Working with tensors, model types | IMAGE, LATENT, MASK, CONDITIONING, MODEL, CLIP, VAE, AUDIO, VIDEO, 3D, custom types |
| **comfyui-node-advanced** | Dynamic inputs, type matching, expansion | MatchType, Autogrow, DynamicCombo, `GraphBuilder`, MultiType, async |
| **comfyui-node-lifecycle** | Execution debugging, caching, validation | `fingerprint_inputs`, `validate_inputs`, `check_lazy_status`, execution order |
| **comfyui-node-frontend** | UI features, custom widgets, extensions | JS hooks, sidebar tabs, commands, settings, toasts, dialogs, context menus |
| **comfyui-node-migration** | Converting V1 nodes to V3 | Property mapping, method conversion, registration changes |
| **comfyui-node-packaging** | Project setup, publishing | Directory layout, `__init__.py`, `pyproject.toml`, `WEB_DIRECTORY`, registry publishing |

## Installation

### Claude Code

#### Plugin Marketplace (recommended)

In Claude Code, open the marketplace and add this repository URL. This installs the `comfyui-custom-nodes` plugin, which exposes all 9 skills automatically — no manual copying required.

#### Personal (all projects)

```bash
# Clone the repository, then copy the skills to your personal skills directory
git clone https://github.com/jtydhr88/comfyui-custom-node-skills.git
cp -r comfyui-custom-node-skills/plugins/comfyui-custom-nodes/skills/comfyui-node-* ~/.claude/skills/
```

#### Project-specific

```bash
# Copy skills into your ComfyUI custom node project
cp -r comfyui-custom-node-skills/plugins/comfyui-custom-nodes/skills/comfyui-node-* /path/to/your-project/.claude/skills/
```

#### Verify

Skills are loaded automatically when Claude detects relevant context. You can also check they're available:

```
> /skills
```

### Codex (CLI / ChatGPT desktop app / IDE extension)

#### Plugin marketplace (recommended)

```bash
# Add this repository as a Codex marketplace source
codex plugin marketplace add jtydhr88/comfyui-custom-node-skills

# Then, in the ChatGPT desktop app or Codex CLI:
# Plugins → select "ComfyUI Custom Node Skills" → Install
```

The same 9 `SKILL.md` files are shipped through the plugin's `skills/` directory — no duplication, no rewriting.

#### Personal skills (all projects)

```bash
# Clone the repository, then copy the skills to your personal skills directory
git clone https://github.com/jtydhr88/comfyui-custom-node-skills.git
cp -r comfyui-custom-node-skills/plugins/comfyui-custom-nodes/skills/comfyui-node-* ~/.agents/skills/
```

#### Project-specific

```bash
# Copy skills into your ComfyUI custom node project
mkdir -p .agents/skills
cp -r comfyui-custom-node-skills/plugins/comfyui-custom-nodes/skills/comfyui-node-* .agents/skills/
```

#### Verify

In Codex, run `/skills` to list available skills, or invoke one explicitly with `$comfyui-node-basics`.

### GitHub Copilot

#### Automatic (cloud and local VSCode)

The `.github/copilot-instructions.md` file is read automatically by GitHub Copilot as repository-wide instructions in both cloud and local VSCode contexts — no setup needed. To make the Skills themselves available, install the plugin via the Copilot CLI using the marketplace or direct install steps below.

#### Plugin marketplace (Copilot CLI — recommended)

```bash
# Register the marketplace (once)
copilot plugin marketplace add jtydhr88/comfyui-custom-node-skills

# Browse and install
copilot plugin marketplace browse comfyui-custom-node-skills
copilot plugin install comfyui-custom-nodes@comfyui-custom-node-skills
```

#### Direct install (Copilot CLI)

```bash
copilot plugin install jtydhr88/comfyui-custom-node-skills:plugins/comfyui-custom-nodes
```

#### Verify

```text
/skills list
```

## Usage Examples

```
# "Create a basic V3 node with an image input and a float slider"
# → agent uses comfyui-node-basics + comfyui-node-inputs

# "Add a preview image output to my node"
# → agent uses comfyui-node-outputs

# "Migrate my V1 node to V3"
# → agent uses comfyui-node-migration

# "Add a sidebar tab with custom settings"
# → agent uses comfyui-node-frontend
```

## Key Features

- **V3 API First** — All examples use the modern V3 API (`io.ComfyNode`, `io.Schema`, `io.NodeOutput`)
- **V1 Reference** — Legacy V1 patterns documented for migration and backward compatibility
- **Source-Verified** — Cross-referenced against actual ComfyUI backend and frontend source code
- **Complete Coverage** — From basic node creation to advanced patterns like DynamicCombo and node expansion
- **Frontend Extensions** — Full JavaScript extension system with 15+ lifecycle hooks
- **Multi-agent** — Same `SKILL.md` files work in Claude Code and Codex (open agentskills.io standard)

## Sources

Built from and verified against:

- [ComfyUI backend](https://github.com/comfyanonymous/ComfyUI) — V3 API at `comfy_api/latest/`, V1 at `comfy/comfy_types/`
  - Last verified: `a2840e75` — Make ImageUpscaleWithModel node work with intermediate device and dtype. (#13357)
- [ComfyUI frontend](https://github.com/Comfy-Org/ComfyUI_frontend) — Extension system, widget types, settings
  - Last verified: `6f579c59` — fix: enable playwright/no-force-option lint rule (#11164)
- [ComfyUI docs](https://docs.comfy.org/custom-nodes/overview) — Official guides and references
- Built-in node implementations in `comfy_extras/`

## License

MIT
