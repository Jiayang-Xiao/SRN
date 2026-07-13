# LLM Chat MCP 配置记录

日期：2026-07-12  
最后验证：2026-07-12 12:38 CST

## 摘要

- Reviewer backend：通过 `llm-chat MCP` 调用 DeepSeek API
- 模型：`deepseek-v4-pro`
- MCP 名称：`llm-chat`
- DeepSeek base URL：`https://api.deepseek.com/v1`
- key 存储位置：`~/.config/aris/deepseek_env`，位于项目仓库之外
- 项目状态：`llm-chat MCP` 已在 Codex 中注册，并通过最小 `READY` prompt 验证
- experiment bridge 状态：不会自动进入 `/experiment-bridge`

## 检查结果

- Codex MCP 命令存在：是
- `codex mcp list` 配置后结果：`llm-chat` 作为 enabled global MCP server 出现
- ARIS server 路径：`/home/xjy/aris_repo/mcp-servers/llm-chat/server.py`
- ARIS requirements 路径：`/home/xjy/aris_repo/mcp-servers/llm-chat/requirements.txt`
- 用户级 server 路径：`~/.codex/mcp-servers/llm-chat/server.py`
- wrapper 路径：`~/.codex/mcp-servers/llm-chat/run_llm_chat.sh`
- venv Python 路径：`~/.codex/mcp-servers/llm-chat/venv/bin/python`
- 环境变量文件：已找到，`~/.config/aris/deepseek_env` 存在
- 私密配置目录权限：`~/.config/aris` 为 mode 700
- 私密 env 文件权限：`~/.config/aris/deepseek_env` 为 mode 600
- 必需运行时变量：`LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL` 均已设置

## 已安装组件

- 已从 ARIS repo 复制 `server.py` 到用户级 MCP 目录。
- 已从 ARIS repo 复制 `requirements.txt` 到用户级 MCP 目录。
- 已创建独立 venv：`~/.codex/mcp-servers/llm-chat/venv`。
- 已根据 `requirements.txt` 安装 `httpx` 依赖。
- 已创建可执行 wrapper：`run_llm_chat.sh`。
- 已用以下命令注册 Codex MCP：

```bash
codex mcp add llm-chat -- /home/xjy/.codex/mcp-servers/llm-chat/run_llm_chat.sh
```

## 验证结果

- 通过 wrapper 进行 JSON-RPC initialize：通过。
- 通过 wrapper 进行 MCP `tools/list`：通过，暴露 `chat` tool。
- `READY` prompt 测试：通过，返回文本精确为 `READY`。
- `codex mcp list`：`llm-chat` 显示为 enabled global MCP server。

## 私密环境变量文件

`~/.config/aris/deepseek_env` 已存在。其内容没有被打印，也没有复制进项目仓库。预期结构如下：

```bash
export DEEPSEEK_API_KEY="你的 DeepSeek API key"
export LLM_API_KEY="$DEEPSEEK_API_KEY"
export LLM_BASE_URL="https://api.deepseek.com/v1"
export LLM_MODEL="deepseek-v4-pro"
```

```bash
chmod 700 ~/.config/aris
chmod 600 ~/.config/aris/deepseek_env
```

不要将该文件提交或复制到 `/home/xjy/ARIS`。

## 错误摘要

- 没有打印 API key，没有把 API key 复制进项目文件，也没有写入 git-tracked 文件。
- 私密 env 文件创建后，当前没有 runtime blocker。

## 下一步

1. 当需要 `auto-review-loop-llm` 或独立评审时，使用 `llm-chat`。
2. `/experiment-bridge` 仍由当前研究计划 gate 控制；该 MCP 配置不会自动启动实验执行。
