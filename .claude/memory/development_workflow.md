---
name: development_workflow
description: 开发工作流程规范
type: feedback
---

**规则：每次修改都要先做计划，计划文件保存到当前项目，每次修改完都要提交 git**

**Why:** 保持开发过程有序和可追溯，确保每次修改都有明确的计划和记录，方便回溯和协作。

**How to apply:**
1. 在开始任何代码修改前，先制定详细计划并保存到 `.claude/plans/` 目录
2. 计划应包含：修改目标、具体步骤、影响范围
3. 完成修改后，必须创建 git commit 提交更改
4. Commit message 应清晰描述本次修改的内容