# Skill Scope

MIAO-80 scope:

- Package the project as an AI Agent Skill plus a runnable Python engine.
- Expose the deterministic foundation: birth data, true solar time, four pillars, five elements, ten gods, configurable rulesets, and structured rule tags.
- Use `computeFromBirth` as the only public entrypoint. Do not expose a separate `computeFromPillars` API in v0.

Rationale:

- Date input is the natural workflow for GitHub users and AI agents.
- Configurable rulesets let users tune weights without requiring Miaosuan to publish its commercial calibration.
- A working Skill is more useful than a prompt-only repo and avoids empty-repo lead generation.
