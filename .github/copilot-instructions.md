You are a coding assistant specialized in ComfyUI custom node development.
This repository contains agent skills for building ComfyUI custom nodes
using the V3 and V1 Python APIs.

## Repository Structure

- `plugins/comfyui-custom-nodes/skills/` — 9 `SKILL.md` files (one per topic)
- `plugins/comfyui-custom-nodes/` — AI integration plugin manifests (one subdirectory per AI agent)
- `.github/plugin/` — GitHub Copilot CLI plugin and marketplace manifests (auto-discovered)
- `skill_test_nodes/` — Example nodes used to validate skill content
- `README.md` / `README_ZH.md` — User-facing documentation

## Skills Covered

| Skill file | Topic |
|---|---|
| `comfyui-node-basics` | V3 node structure, Schema, registration |
| `comfyui-node-inputs` | INT, FLOAT, STRING, BOOLEAN, COMBO, optional/lazy inputs |
| `comfyui-node-outputs` | NodeOutput, PreviewImage/Mask/Audio/Text, SavedImages |
| `comfyui-node-datatypes` | IMAGE, LATENT, MASK, MODEL, CLIP, VAE, AUDIO, VIDEO, 3D, custom types |
| `comfyui-node-advanced` | MatchType, Autogrow, DynamicCombo, GraphBuilder, MultiType |
| `comfyui-node-lifecycle` | fingerprint_inputs, validate_inputs, check_lazy_status, execution order |
| `comfyui-node-frontend` | JS hooks, sidebar tabs, commands, settings, toasts, dialogs |
| `comfyui-node-migration` | V1 → V3 API migration |
| `comfyui-node-packaging` | Project layout, __init__.py, pyproject.toml, WEB_DIRECTORY, publishing |

## Coding Conventions

- Prefer the **V3 API** (`io.ComfyNode`, `io.Schema`, `io.NodeOutput`) for all new nodes.
- Reference V1 patterns only when documenting migration or backward compatibility.
- Keep `SKILL.md` files self-contained and free of duplication — they are shared across all supported AI agents.
- All skills must remain accurate against the ComfyUI backend (`comfy_api/latest/`) and frontend source.
- When working on one AI integration's plugin files, do not modify the others.

## When Making Changes

- **Editing a `SKILL.md`**: verify accuracy against the ComfyUI source links in `README.md` before committing.
- **Adding a new skill**: create a directory under `skills/`, add `SKILL.md`, and register it in all relevant plugin manifests and the `README.md` skill table.
- **Adding a new AI integration**: follow the same pattern as existing plugin subdirectories — a manifest pointing to `./skills`. Marketplace URLs should point to the upstream repo (`jtydhr88/comfyui-custom-node-skills`), not forks.
- Do not change unrelated AI integration files when working on a single integration task.
