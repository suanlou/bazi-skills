# Miaosuan 八字 Skill

面向 AI Agent 和开发者的确定性八字排盘 Skill。

它的目标很简单：让 AI 在解读八字前，先拿到可靠、结构化、可复核的排盘上下文，而不是直接凭语言模型猜四柱和十神。

这个仓库包含：

- 出生时间 -> 真太阳时 -> 四柱八字
- 五行力量、十神权重、日主强弱、命格基础判断
- 可配置的 ruleset 权重
- 适合 AI Agent 消费的结构化 `rule.tags`
- `SKILL.md`：给 Agent 使用的 Skill 入口说明
- Python 包和 CLI：给开发者直接调用

需要完整 AI 解读和交互式分析，可以使用 [妙算](https://miaosuan.xyz/?utm_source=github&utm_medium=repo&utm_campaign=bazi_skill)。

## 为什么做成 Skill

普通 prompt 很容易把“排盘”和“解读”混在一起，导致 AI 在日期、节气、十神或五行关系上产生幻觉。Skill 的定位不同：先用确定性计算生成结构化事实，再让 AI 基于这些事实做解释。

适合的使用场景：

- AI Agent 需要先计算八字，再生成解释
- 开发者想把八字排盘接入自己的 Agent / MCP / Workflow
- 命理内容创作者需要一个可复核的结构化排盘结果
- 研究者想调整 ruleset 权重，比较不同流派的输出差异

## 安装到 Agent

### Claude Code / Claude Desktop / Codex（Skill 方式）

发布到 GitHub 后，可以把整个仓库放进 Agent 的 skills 目录：

```bash
# Claude Code / Claude Desktop
git clone https://github.com/miaosuan/miaosuan-bazi-skill.git ~/.claude/skills/miaosuan-bazi
cd ~/.claude/skills/miaosuan-bazi
python3 -m pip install -e .
```

```bash
# Codex
git clone https://github.com/miaosuan/miaosuan-bazi-skill.git ~/.codex/skills/miaosuan-bazi
cd ~/.codex/skills/miaosuan-bazi
python3 -m pip install -e .
```

装好后，直接对 Agent 说：

```text
我是 1990-05-15 14:30 在广州出生的男生，先排八字，再基于排盘结果解释。
```

Agent 会读取 `SKILL.md`，先调用确定性计算，再基于结构化结果解释。

### Claude Desktop / MCP 方式

如果你的客户端支持 MCP，可以安装 optional MCP wrapper：

```bash
git clone https://github.com/miaosuan/miaosuan-bazi-skill.git ~/miaosuan-bazi-skill
cd ~/miaosuan-bazi-skill
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[mcp]"
```

然后在 Claude Desktop 的 MCP 配置中加入：

```json
{
  "mcpServers": {
    "miaosuan-bazi": {
      "command": "/ABS/PATH/TO/miaosuan-bazi-skill/.venv/bin/python",
      "args": ["-m", "miaosuan_bazi_engine.mcp_server"]
    }
  }
}
```

可用工具：

- `compute_bazi(datetime, gender, city, name?, ruleset_path?)`

### 通用 Agent

不支持固定 skills 目录的 Agent，可以直接读取这个文件：

```text
https://github.com/miaosuan/miaosuan-bazi-skill/blob/main/SKILL.md
```

或克隆仓库后让 Agent 使用本地 `SKILL.md`。

## 开发者快速开始

本地安装：

```bash
pip install -e .
```

Python 调用：

```python
from miaosuan_bazi_engine import computeFromBirth

result = computeFromBirth({
    "name": "Example",
    "gender": "male",
    "datetime": "1990-05-15T14:30:00+08:00",
    "city": "广州",
})

print(result["pillars"])
print(result["rule"]["tags"])
```

命令行调用：

```bash
miaosuan-bazi --input examples/basic.json --pretty
```

使用自定义权重：

```bash
miaosuan-bazi --input examples/basic.json --ruleset examples/custom-ruleset.json --pretty
```

## Skill 入口

仓库根目录提供 `SKILL.md`。Agent 可以按其中的流程调用本地 Python 包、CLI 或 MCP 工具：

1. 收集出生时间、性别、城市。
2. 调用 `computeFromBirth`、`miaosuan-bazi` 或 MCP 工具 `compute_bazi`。
3. 使用返回的 `pillars`、`wuxing`、`ten_gods`、`body_strength`、`mingge` 和 `rule.tags` 作为解释依据。

## 开发者接口

当前唯一公开计算入口是 `computeFromBirth`。

输入示例：

```json
{
  "name": "Example",
  "gender": "male",
  "datetime": "1990-05-15T14:30:00+08:00",
  "city": "广州"
}
```

输出包含：

- `time`：输入时间、北京时间、真太阳时、经度修正、均时差
- `lunar`：农历日期和节气信息
- `pillars`：年柱、月柱、日柱、时柱
- `day_master`：日主和日柱
- `wuxing`：五行力量分布和基础判断
- `ten_gods`：十神标签和权重
- `body_strength`：日主强弱计算
- `mingge`：命格基础判断、喜用神、忌神
- `paipan`：藏干、纳音、空亡、神煞等排盘明细
- `rule.tags`：给 AI Agent 使用的紧凑规则标签

## 可配置权重

权重从 JSON ruleset 读取。你可以复制 `examples/custom-ruleset.json`，修改里面的系数，再通过 `--ruleset` 或 `ruleset_path` 传入。

基础 ruleset 是透明的。不同流派可以 fork 或调整权重，不需要改动核心排盘代码。

## 项目范围

本项目聚焦确定性排盘和规则计算，适用于文化研究、开发者实验和 AI Agent 的结构化依据生成。

当前覆盖：

- 出生日期输入
- 真太阳时换算
- 四柱八字
- 五行、十神、身强身弱
- 命格基础判断
- 排盘明细
- `rule.tags`
- 可配置 ruleset
- MCP 工具 `compute_bazi`

## GitHub 传播目标

首批站外目标：

- GitHub Topics：`bazi`、`八字`、`lunar`、`ai-agent`、`mcp`
- 增加 MCP wrapper 后提交到 MCP / AI Agent 工具集合
- 提交到农历、命理、Chinese astrology 相关 awesome list
- CLI 输出或 demo 页完善后发布 Hacker News Show HN
- 妙算落地页和 UTM 统计闭环后提交 Product Hunt / AI 工具目录

## 免责声明

八字是传统文化体系。本项目只提供确定性计算和结构化规则标签，不提供医疗、法律、金融或任何关键人生决策建议。
