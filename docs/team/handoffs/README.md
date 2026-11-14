# Handoffs: how we pass work to each other

Work goes back and forth through **two inboxes**. Each file has only one writer, so the two of us never conflict.

| File | Written by | Read by |
|---|---|---|
| [to-brandon.md](to-brandon.md) | Asher | Brandon |
| [to-asher.md](to-asher.md) | Brandon | Asher |

**Rules**
- Write an entry when you hand something over, or when you change something the other person depends on.
- **Only edit the other person's inbox.** The reader may change an entry's **Status** line (🆕 new → 👀 reviewing → ✅ done), and nothing else.
- Newest entry at the top. Keep it short, and link the PR or branch.

## Template
```
### <date, time> · <what>
**Status:** 🆕 new · PR #<n>
- What's ready / what changed:
- Where (files, branch, command):
- What you need to do:
- Known issues:
```
