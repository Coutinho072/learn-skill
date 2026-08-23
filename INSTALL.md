# INSTALL — instructions for the coding agent

You are installing the `learn` tutoring skill from this package.
The human pointed you at this folder and asked you to install it.
Follow these steps in order.
Ask before overwriting anything that already exists.

## 1. Copy the files

- Copy `skills/learn/` into `~/.claude/skills/learn/`.
- Copy every file in `agents/` into `~/.claude/agents/`.
- If a target already exists, show the diff summary and ask the user: overwrite, skip, or back up.

## 2. Interview the user

Ask, in one round of questions:

1. **Vault path.** Where should lessons live?
   Any folder works, e.g. an Obsidian vault or `~/Documents/learn-vault`.
   Create it if it does not exist.
2. **Language.** Which language should lessons be written in?
3. **Medical use.** Will they study medical topics?
   If yes, keep the strict fact-check rule as is.

## 3. Personalize the installed SKILL.md

Edit `~/.claude/skills/learn/SKILL.md` (the installed copy, never this package):

- Replace the vault path on the `Paths:` line with the user's answer.
- Rule **R6** calls a vault-specific reindex script.
  Delete rule R6 unless the user's vault has `.agents/scripts/qmd-reindex.sh`.
- Rule **R7** sets the lesson language.
  Rewrite it for the user's language, keeping the short-sentence discipline.
- The frontmatter `description` mentions Obsidian paths.
  Adjust it to the user's vault name.

## 4. Check dependencies

- `rsvg-convert` (`brew install librsvg` on macOS, `apt install librsvg2-bin` on Linux).
  On Linux, also fix the hardcoded `/opt/homebrew/bin/rsvg-convert` path in `SKILL.md`, `references/formats.md`, and `agents/viz-maker.md`.
- Anki with the AnkiConnect add-on, optional.
  Without it, cards fall back to a `.txt` file the user drags into Anki.
  Do not block the install on it.
- No API keys are required.
  Optional: an `OPENAI_API_KEY` environment variable unlocks AI-generated anatomical illustrations.
  Without it, every visual is code-drawn SVG or mermaid, and nothing else changes.
  Never write the key into any file in this package or in the vault.

## 5. Verify and hand off

- Confirm `~/.claude/skills/learn/SKILL.md` and the three agents exist and contain the personalized values.
- Tell the user: restart Claude Code, then run `/learn <topic>`.
- Report what was installed, what was personalized, and any dependency still missing.
