"""Structural checks every skill must pass before it ships."""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = sorted((ROOT / "skills").glob("*/SKILL.md"))
BANNED = re.compile(r"—|–")  # em and en dashes: house style


def frontmatter(text: str) -> dict:
    assert text.startswith("---\n"), "frontmatter must open on the first line"
    end = text.index("\n---\n", 4)
    fields = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip()
    return fields


def test_there_are_seven_skills():
    assert len(SKILLS) == 7


@pytest.mark.parametrize("path", SKILLS, ids=lambda p: p.parent.name)
def test_skill_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    fm = frontmatter(text)
    assert fm.get("name") == path.parent.name
    desc = fm.get("description", "")
    assert 40 <= len(desc) <= 1024, "description should say what it does and when to use it"
    assert len(text.splitlines()) < 500, "keep SKILL.md under 500 lines"


@pytest.mark.parametrize("path", SKILLS, ids=lambda p: p.parent.name)
def test_skill_links_resolve(path):
    text = path.read_text(encoding="utf-8")
    for target in re.findall(r"\]\((?!https?://)([^)#]+)\)", text):
        assert (path.parent / target).exists(), f"broken link {target}"


def test_no_dashes_in_prose():
    for f in [*SKILLS, ROOT / "README.md", ROOT / "AGENTS.md", *ROOT.glob("skills/*/templates/*.md")]:
        assert not BANNED.search(f.read_text(encoding="utf-8")), f"em/en dash in {f.relative_to(ROOT)}"


def test_plugin_manifests_agree():
    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    assert market["plugins"][0]["name"] == plugin["name"]
    assert market["owner"]["name"]
