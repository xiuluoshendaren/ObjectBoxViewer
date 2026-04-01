---
name: git commit requirement
description: Automatically commit all changes to git-managed files
type: feedback
---

**规则:只要修改了 git 管理的文件，都要 commit**

**Why:** User wants to maintain a clean git history and track all changes made during development sessions

**How to apply:**
- After completing any task that modifies files tracked by git, create a commit
- Use meaningful commit messages that describe the changes
- Run `git status` first to see what will be committed
- Include the files that were modified in the commit
