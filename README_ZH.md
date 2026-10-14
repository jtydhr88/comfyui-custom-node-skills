# ComfyUI 自定义节点 Skills

一套面向多种 AI Agent（包括 [Claude Code](https://docs.anthropic.com/en/docs/claude-code/skills)、[OpenAI Codex](https://developers.openai.com/codex/build-skills) 与 [GitHub Copilot](https://docs.github.com/en/copilot)）的 ComfyUI 自定义节点开发知识库，涵盖 V3（推荐）和 V1（旧版）两套 API。

所有 `SKILL.md` 文件遵循开放的 [agentskills.io](https://agentskills.io) 标准，各 Agent 通用——装一次，处处可用。

> **[English](README.md)**

## Skills 一览

| Skill | 触发场景 | 内容 |
|---|---|---|
| **comfyui-node-basics** | 创建节点、定义类、项目初始化 | V3 节点结构、`io.Schema`、输入/输出、`ComfyExtension` 注册 |
| **comfyui-node-inputs** | 配置控件、添加输入 | INT、FLOAT、STRING、BOOLEAN、COMBO、隐藏/可选/惰性输入、`force_input` |
| **comfyui-node-outputs** | 返回结果、预览、保存文件 | `NodeOutput`、`PreviewImage/Mask/Audio/Text`、`SavedImages`、UI 辅助 |
| **comfyui-node-datatypes** | 处理张量、模型类型 | IMAGE、LATENT、MASK、CONDITIONING、MODEL、CLIP、VAE、AUDIO、VIDEO、3D、自定义类型 |
| **comfyui-node-advanced** | 动态输入、类型匹配、节点展开 | MatchType、Autogrow、DynamicCombo、`GraphBuilder`、MultiType、异步 |
| **comfyui-node-lifecycle** | 执行调试、缓存、校验 | `fingerprint_inputs`、`validate_inputs`、`check_lazy_status`、执行顺序 |
| **comfyui-node-frontend** | UI 功能、自定义控件、扩展 | JS 生命周期钩子、侧边栏、命令、设置、Toast、对话框、右键菜单 |
| **comfyui-node-migration** | 将 V1 节点迁移到 V3 | 属性映射、方法转换、注册方式变更 |
| **comfyui-node-packaging** | 项目搭建、发布 | 目录结构、`__init__.py`、`pyproject.toml`、`WEB_DIRECTORY`、Registry 发布 |

## 安装

### Claude Code

#### 插件市场（推荐）

在 Claude Code 中打开市场，添加本仓库 URL，即可安装 `comfyui-custom-nodes` 插件，全部 9 个 Skills 将自动可用，无需手动复制。

#### 个人级别（所有项目生效）

```bash
# 克隆仓库，然后将 Skills 复制到个人 skills 目录
git clone https://github.com/jtydhr88/comfyui-custom-node-skills.git
cp -r comfyui-custom-node-skills/plugins/comfyui-custom-nodes/skills/comfyui-node-* ~/.claude/skills/
```

#### 项目级别

```bash
# 复制到你的 ComfyUI 自定义节点项目中
cp -r comfyui-custom-node-skills/plugins/comfyui-custom-nodes/skills/comfyui-node-* /path/to/your-project/.claude/skills/
```

#### 验证

Skills 会在 Claude 检测到相关上下文时自动加载，也可以手动检查：

```
> /skills
```

### Codex（CLI / ChatGPT 桌面应用 / IDE 扩展）

#### 插件市场（推荐）

```bash
# 将本仓库添加为 Codex marketplace 来源
codex plugin marketplace add jtydhr88/comfyui-custom-node-skills

# 然后在 ChatGPT 桌面应用或 Codex CLI 中：
# Plugins → 选择 "ComfyUI Custom Node Skills" → 安装
```

插件直接复用同一份 `SKILL.md` 文件，无需任何改写或重复。

#### 个人级别（所有项目生效）

```bash
# 克隆仓库，然后将 Skills 复制到个人 skills 目录
git clone https://github.com/jtydhr88/comfyui-custom-node-skills.git
cp -r comfyui-custom-node-skills/plugins/comfyui-custom-nodes/skills/comfyui-node-* ~/.agents/skills/
```

#### 项目级别

```bash
# 复制到你的 ComfyUI 自定义节点项目中
mkdir -p .agents/skills
cp -r comfyui-custom-node-skills/plugins/comfyui-custom-nodes/skills/comfyui-node-* .agents/skills/
```

#### 验证

在 Codex 中执行 `/skills` 列出可用 Skills，或使用 `$comfyui-node-basics` 显式调用。

### GitHub Copilot

#### 自动加载（云端及本地 VSCode）

`.github/copilot-instructions.md` 文件会被云端和本地 VSCode 的 Copilot 作为仓库级指令自动读取，无需任何配置。若要使用 Skills 本身，请按照下方的插件市场或直接安装步骤，通过 Copilot CLI 安装插件。

#### 插件市场（Copilot CLI — 推荐）

```bash
# 注册插件市场（只需一次）
copilot plugin marketplace add jtydhr88/comfyui-custom-node-skills

# 浏览并安装
copilot plugin marketplace browse comfyui-custom-node-skills
copilot plugin install comfyui-custom-nodes@comfyui-custom-node-skills
```

#### 直接安装（Copilot CLI）

```bash
copilot plugin install jtydhr88/comfyui-custom-node-skills:plugins/comfyui-custom-nodes
```

#### 验证

```text
/skills list
```

## 使用示例

```
# "创建一个带图像输入和浮点滑块的 V3 节点"
# → Agent 使用 comfyui-node-basics + comfyui-node-inputs

# "给我的节点加上图片预览输出"
# → Agent 使用 comfyui-node-outputs

# "把我的 V1 节点迁移到 V3"
# → Agent 使用 comfyui-node-migration

# "添加一个带自定义设置的侧边栏"
# → Agent 使用 comfyui-node-frontend
```

## 特点

- **V3 优先** — 所有示例使用现代 V3 API（`io.ComfyNode`、`io.Schema`、`io.NodeOutput`）
- **V1 参考** — 保留旧版 V1 模式文档，方便迁移和向后兼容
- **源码验证** — 与 ComfyUI 前后端源码交叉比对，确保准确
- **覆盖全面** — 从基础节点创建到 DynamicCombo、节点展开等高级模式
- **前端扩展** — 完整的 JavaScript 扩展系统，包含 15+ 生命周期钩子
- **多 Agent 通用** — 同一份 `SKILL.md` 兼容所有支持 agentskills.io 标准的 Agent（包括 GitHub Copilot）

## 数据来源

基于以下源码构建并验证：

- [ComfyUI 后端](https://github.com/comfyanonymous/ComfyUI) — V3 API 位于 `comfy_api/latest/`，V1 位于 `comfy/comfy_types/`
  - 最后验证: `a2840e75` — Make ImageUpscaleWithModel node work with intermediate device and dtype. (#13357)
- [ComfyUI 前端](https://github.com/Comfy-Org/ComfyUI_frontend) — 扩展系统、控件类型、设置
  - 最后验证: `6f579c59` — fix: enable playwright/no-force-option lint rule (#11164)
- [ComfyUI 文档](https://docs.comfy.org/custom-nodes/overview) — 官方指南和参考
- 内置节点实现位于 `comfy_extras/`

## 许可

MIT
