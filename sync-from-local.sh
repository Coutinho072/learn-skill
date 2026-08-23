#!/usr/bin/env bash
# Sync the live personal skill (~/.claude) into this public repo, re-applying
# the de-personalization the public copy carries. Review the diff and commit
# yourself; this script NEVER commits and NEVER pushes.
#
# Usage: ./sync-from-local.sh
set -euo pipefail
cd "$(dirname "$0")"

cp ~/.claude/skills/learn/SKILL.md skills/learn/SKILL.md
cp ~/.claude/skills/learn/references/formats.md skills/learn/references/formats.md
cp ~/.claude/skills/learn/scripts/anki_add.py skills/learn/scripts/anki_add.py
cp ~/.claude/skills/learn/scripts/gen_image.py skills/learn/scripts/gen_image.py
cp ~/.claude/agents/fact-checker.md agents/fact-checker.md
cp ~/.claude/agents/viz-maker.md agents/viz-maker.md
cp ~/.claude/agents/deep-research-agent.md agents/deep-research-agent.md

python3 - <<'EOF'
from pathlib import Path
misses = []

def sub(path, pairs):
    p = Path(path)
    t = p.read_text()
    for old, new in pairs:
        if old not in t:
            misses.append(f"{path}: pattern not found: {old[:70]!r}")
            continue
        t = t.replace(old, new)
    p.write_text(t)

sub("skills/learn/SKILL.md", [
    ("Personal AI tutor for Marcos:", "Personal AI tutor:"),
    ("Sessions stream to Obsidian (Coutinho-Vault/learn/).",
     "Sessions stream to your notes vault (learn/)."),
    ("Paths: vault = `~/Desktop/my_brain/Coutinho-Vault`, learn root = `<vault>/learn/`.",
     "Paths: vault = `~/Documents/learn-vault` (set your own at install), learn root = `<vault>/learn/`."),
    ("- **R6 — vault hygiene.** After each vault `.md` write, run `cd ~/Desktop/my_brain/Coutinho-Vault && .agents/scripts/qmd-reindex.sh` in background. Never write files at the vault root.",
     "- **R6 — vault hygiene.** If your vault has its own reindex or hygiene script, run it in background after each vault `.md` write. Never write files at the vault root."),
    ("`viz-maker` (self-verified SVG / GPT image)",
     "`viz-maker` (self-verified SVG / mermaid; optional AI image when `OPENAI_API_KEY` is set)"),
    ("anatomical or beyond code-drawn art → viz-maker with gen_image.py; skip only when a figure would add nothing over the text)",
     "anatomical or beyond code-drawn art → viz-maker, which may use AI image generation when `OPENAI_API_KEY` is set; skip only when a figure would add nothing over the text)"),
    ("(render the SVG with `rsvg-convert` first; GPT images are already PNG)",
     "(render the SVG with `rsvg-convert` first; AI-generated images are already PNG)"),
    ("5. `gen_image.py` fails → viz-maker falls back to conceptual SVG or inline mermaid.",
     "5. `gen_image.py` fails or `OPENAI_API_KEY` is absent → viz-maker falls back to a schematic SVG or inline mermaid."),
])

sub("agents/viz-maker.md", [
    ("or organic/anatomical illustrations via GPT Image.",
     "with optional AI illustrations for organic/anatomical subjects when OPENAI_API_KEY is set."),
    ("An organic or anatomical subject (organs, tissues, physical objects), or a scene code-drawn art cannot express well, gets GPT Image via",
     "An organic or anatomical subject (organs, tissues, physical objects), or a scene code-drawn art cannot express well: if the `OPENAI_API_KEY` env var is set, generate via"),
    ("(keep GPT-generated PNGs, they ARE the asset)",
     "(keep AI-generated PNGs, they ARE the asset)"),
    ("- If `gen_image.py` exits non-zero, fall back to a conceptual SVG when the idea allows it; otherwise return VISUAL_FAILED.",
     "- If `gen_image.py` exits non-zero (or no key is set), fall back to a schematic SVG when the idea allows it; otherwise return VISUAL_FAILED."),
    ("keep GPT Image prompts schematic", "keep AI image prompts schematic"),
])

sub("skills/learn/scripts/gen_image.py", [
    ('ENV_FALLBACK = Path.home() / ".config" / "watch" / ".env"\nAPI_URL', 'API_URL'),
    ('''    if ENV_FALLBACK.exists():
        for line in ENV_FALLBACK.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("OPENAI_API_KEY=") and len(line) > len("OPENAI_API_KEY="):
                return line.split("=", 1)[1].strip()
    sys.exit("gen_image: no OPENAI_API_KEY in env or %s" % ENV_FALLBACK)''',
     '    sys.exit("gen_image: OPENAI_API_KEY is not set")'),
])

sub("skills/learn/references/formats.md", [
    ("GPT images are already PNG", "AI-generated images are already PNG"),
    ("Vault root: `~/Desktop/my_brain/Coutinho-Vault`. Learn root: `<vault>/learn/`.",
     "Vault root: the vault configured in SKILL.md. Learn root: `<vault>/learn/`."),
])

if misses:
    print("WARNING - these de-personalization patterns no longer match; fix them by hand before committing:")
    for m in misses:
        print("  " + m)
else:
    print("de-personalization applied cleanly")
EOF

# Secret scan: refuse to leave obviously sensitive strings in the tree.
if grep -rInE "sk-[A-Za-z0-9]{10,}|AKIA[0-9A-Z]{16}|-----BEGIN|(api[_-]?key|token|secret)[\"']?\s*[:=]\s*[\"'][^\"']{8,}" \
    --exclude-dir=.git --exclude="sync-from-local.sh" .; then
  echo "SECRET SCAN FAILED: inspect the lines above before committing." >&2
  exit 1
fi
echo "secret scan clean"

git status --short
echo "Review with: git diff   (then commit; pushing stays a manual, explicitly confirmed act)"
