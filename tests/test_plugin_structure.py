"""Plugin manifests and skill files are well formed."""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
# Backticked relative paths a SKILL.md tells Claude to open or run.
REL_PATH = re.compile(r"`((?:\.\./|\./|scripts/|references/|templates/)[^`\s]+)`")


def load_json(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def skill_files():
    return sorted(SKILLS.glob("*/SKILL.md"))


def frontmatter(path):
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    match = FRONTMATTER.match(text)
    assert match, f"{path} is missing YAML frontmatter"
    fields = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"')
    return fields, text


def test_plugin_manifest():
    data = load_json(".claude-plugin/plugin.json")
    assert data["name"] == "acqdemo"
    assert re.fullmatch(r"\d+\.\d+\.\d+", data["version"])
    assert data["description"]


def test_marketplace_matches_plugin():
    plugin = load_json(".claude-plugin/plugin.json")
    market = load_json(".claude-plugin/marketplace.json")
    assert market["name"] == "acqdemo"
    assert len(market["plugins"]) == 1
    entry = market["plugins"][0]
    assert entry["name"] == plugin["name"]
    assert entry["version"] == plugin["version"]
    assert entry["source"] == "./"


@pytest.mark.parametrize("skill", skill_files(), ids=lambda p: p.parent.name)
def test_skill_frontmatter(skill):
    fields, _ = frontmatter(skill)
    assert fields.get("name") == skill.parent.name
    description = fields.get("description", "")
    assert description.startswith("Use when"), "descriptions start with 'Use when'"
    assert len(description) <= 1024


@pytest.mark.parametrize("skill", skill_files(), ids=lambda p: p.parent.name)
def test_skill_relative_paths_exist(skill):
    _, text = frontmatter(skill)
    missing = [rel for rel in REL_PATH.findall(text) if not (skill.parent / rel).exists()]
    assert not missing, f"{skill} references missing paths: {missing}"
