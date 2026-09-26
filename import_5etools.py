#!/usr/bin/env python3
"""
5e.tools → Obsidian Vault Importer

Non-destructive: skips notes that already exist — safe to re-run at any time.

Usage:
  python import_5etools.py              # WotC sources only (default)
  python import_5etools.py --all        # All sources (homebrew + third-party)
  python import_5etools.py --type spells  # Single content type only
"""

import argparse
import json
import os
import re
import ssl
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Optional

# Force UTF-8 output on Windows (default console encoding is often cp1252)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def _make_ssl_context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        pass
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "certifi", "-q"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        pass
    return ssl.create_default_context()


_SSL_CTX = _make_ssl_context()

# ── Configuration ─────────────────────────────────────────────────────────────

VAULT = Path(".")  # overridden by --vault argument at runtime
BASE_URL = "https://raw.githubusercontent.com/5etools-mirror-3/5etools-src/main/data"

# Active game system — overridden by --system argument at runtime.
# Controls folder routing (Races vs Species) and default source filter.
SYSTEM = "dnd5e"

# ── Edition source sets ────────────────────────────────────────────────────────

# D&D 5e 2014 — all WotC sources, explicitly excluding the 2024 revised books
SOURCES_5E_2014 = {
    "PHB", "DMG", "MM", "XGE", "TCE", "SCAG",
    "GGR", "AI", "ERLW", "EGW", "MOT", "FTD", "SCC", "LoX",
    "DSotDQ", "KftGV", "BMT", "AAG", "SAiS", "HAT-TG", "HAT-LMI",
    "SRD", "BasicRules", "PSI", "PSZ", "PSK", "PSX", "PSA",
    "HotDQ", "RoT", "PotA", "OotA", "CoS", "SKT", "ToA", "TftYP",
    "WDH", "WDMM", "GoS", "BGDIA", "IDRotF", "CM", "WBtW",
    "CRCotN", "JttRC", "DSotDQ", "PaBTSO", "ToFW", "VEoR",
    "MaBJoV", "LLK", "LR", "DC", "SLW", "IMR", "SADS", "EET",
    "MTF", "VGM", "MFF", "MPMM", "BGG", "MPP", "TDCSR",
}

# D&D 5.5e 2024 — core rulebooks and supplements published under / compatible with 2024 rules
SOURCES_5E_2024 = {
    # Core rulebooks (2024 revised editions)
    "XPHB", "XDMG", "XMM",
    # Adventures & supplements released for the 2024 edition
    "QftIS",  # Quests from the Infinite Staircase (2024)
    # Pre-2024 supplements that remain widely used alongside the 2024 rules
    "XGE",   # Xanathar's Guide to Everything
    "TCE",   # Tasha's Cauldron of Everything
    "SCAG",  # Sword Coast Adventurer's Guide (spells)
    "MPMM",  # Mordenkainen Presents: Monsters of the Multiverse (updated races)
}

# Combined set (used when source_filter is None / "all WotC")
WOTC_SOURCES = SOURCES_5E_2014 | SOURCES_5E_2024

# Content types available per edition
CONTENT_TYPES_5E_2014 = [
    "spells", "items", "backgrounds", "classes", "classfeatures",
    "races", "racialtraits", "backgroundfeatures",
    "languages", "deities", "feats", "conditions", "optionalfeatures",
]
CONTENT_TYPES_5E_2024 = [
    "spells", "items", "backgrounds", "classes", "classfeatures",
    "races", "racialtraits",
    "languages", "deities", "feats", "conditions", "optionalfeatures",
]

SCHOOL_MAP = {
    "A": "Abjuration", "C": "Conjuration", "D": "Divination",
    "E": "Enchantment", "V": "Evocation", "I": "Illusion",
    "N": "Necromancy", "T": "Transmutation", "P": "Psionic",
}

ITEM_TYPE_MAP = {
    "A": "Ammunition", "AF": "Ammunition (Firearm)", "AT": "Artisan Tool",
    "EM": "Eldritch Machine", "EXP": "Explosive", "F": "Food",
    "G": "Gear", "GS": "Gaming Set", "HA": "Heavy Armor",
    "INS": "Instrument", "LA": "Light Armor", "M": "Melee Weapon",
    "MA": "Medium Armor", "MNT": "Mount", "MR": "Master Rune",
    "OTH": "Other", "P": "Potion", "R": "Ranged Weapon",
    "RD": "Rod", "RG": "Ring", "S": "Shield", "SC": "Scroll",
    "SCF": "Spellcasting Focus", "SHP": "Ship", "SPC": "Spacecraft",
    "ST": "Staff", "T": "Tool", "TAH": "Tack & Harness",
    "TG": "Trade Good", "VEH": "Vehicle", "WD": "Wand",
}

WEAPON_PROP_MAP = {
    "A": "Ammunition", "AF": "Ammunition (Firearm)", "BF": "Burst Fire",
    "F": "Finesse", "H": "Heavy", "L": "Light", "LD": "Loading",
    "R": "Reach", "RLD": "Reload", "S": "Special", "T": "Thrown",
    "2H": "Two-Handed", "V": "Versatile",
}

OPTIONAL_FEATURE_TYPE_MAP = {
    "AI": "Artificer Infusion", "AS": "Arcane Shot", "ED": "Elemental Discipline",
    "EI": "Eldritch Invocation", "FS:F": "Fighting Style (Fighter)",
    "FS:B": "Fighting Style (Bard)", "FS:P": "Fighting Style (Paladin)",
    "FS:R": "Fighting Style (Ranger)", "FS:W": "Fighting Style (Warrior)",
    "FS": "Fighting Style", "MM": "Metamagic", "MV": "Battle Master Maneuver",
    "MV:B": "Maneuver (Cavalier)", "MV:C2-UA": "Maneuver (UA)",
    "OPT": "Optional Class Feature", "OR": "Onomancy Resonant",
    "PB": "Pact Boon", "PS:H": "Planar Summon (Hierarch)",
    "PS:R": "Planar Summon (Rebel)", "SHP:H": "Ship Upgrade (Hull)",
    "SHP:M": "Ship Upgrade (Movement)", "SHP:W": "Ship Upgrade (Weapon)",
    "SHP:F": "Ship Upgrade (Figurehead)", "SHP:O": "Ship Upgrade (Oar)",
    "SHP:OW": "Ship Upgrade (Outrigger Wing)", "SHP:T": "Ship Upgrade (Siege Weapon)",
    "TD": "Totem Feature", "TP": "Tunnel Perception",
}

# All possible content types across both editions (used for --type argparse choices)
CONTENT_TYPES = sorted(set(CONTENT_TYPES_5E_2014) | set(CONTENT_TYPES_5E_2024))

# ── Utilities ─────────────────────────────────────────────────────────────────

def fetch_json(url: str) -> Optional[dict]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "5etools-obsidian-importer/1.0"})
        with urllib.request.urlopen(req, timeout=30, context=_SSL_CTX) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        print(f"  HTTP {e.code}: {url}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  Error fetching {url}: {e}", file=sys.stderr)
        return None


def sanitize_filename(name: str) -> str:
    name = re.sub(r'[/\\:*?"<>|]', "-", name)
    name = re.sub(r'\s+', " ", name).strip()
    return name


def _link_name(raw: str) -> str:
    """Normalize a 5e.tools tag name to the vault filename it was written as.

    Uses title-case (to match how the file was created from the master data)
    but does NOT capitalize the letter immediately after an apostrophe —
    Python's .title() incorrectly produces "Bigby'S Hand" from "bigby's hand".
    Also applies sanitize_filename so slashes become dashes (e.g. Enlarge-Reduce).
    """
    titled = raw.title()
    # Fix apostrophe-capitalisation bug: "Bigby'S Hand" → "Bigby's Hand"
    titled = re.sub(r"(['‘’])([A-Z])",
                    lambda m: m.group(1) + m.group(2).lower(), titled)
    return sanitize_filename(titled)


def yaml_str(value: Any) -> str:
    if value is None:
        return ""
    s = str(value)
    if any(c in s for c in [':', '#', '[', ']', '{', '}', ',', '&', '*', '?', '|', '>', "'", '"', '\n']):
        escaped = s.replace('"', '\\"')
        return f'"{escaped}"'
    return s


def yaml_list(items: list) -> str:
    if not items:
        return " []"
    return "\n" + "\n".join(f"  - {yaml_str(i)}" for i in items)


def convert_tags(text: str) -> str:
    """Convert 5e.tools {@tag} notation to Obsidian wikilinks or plain text."""
    # Link-worthy tags → wikilinks
    # _link_name() applies proper title-case + sanitize_filename so the link
    # target matches the actual vault filename (fixes slashes, apostrophes, etc.)
    for tag in ("condition", "disease", "status"):
        text = re.sub(rf'\{{@{tag} ([^}}|]+)(?:\|[^}}]*)?\}}',
                      lambda m: f'[[{_link_name(m.group(1))}]]', text)
    for tag in ("spell",):
        text = re.sub(rf'\{{@{tag} ([^}}|]+)(?:\|[^}}]*)?\}}',
                      lambda m: f'[[{_link_name(m.group(1))}]]', text)
    for tag in ("item",):
        text = re.sub(rf'\{{@{tag} ([^}}|]+)(?:\|[^}}]*)?\}}',
                      lambda m: f'[[{_link_name(m.group(1))}]]', text)
    for tag in ("feat",):
        text = re.sub(rf'\{{@{tag} ([^}}|]+)(?:\|[^}}]*)?\}}',
                      lambda m: f'[[{_link_name(m.group(1))}]]', text)
    for tag in ("race",):
        # The regex already strips the |Source suffix; group(1) is the bare name
        text = re.sub(rf'\{{@{tag} ([^}}|]+)(?:\|[^}}]*)?\}}',
                      lambda m: f'[[{_link_name(m.group(1))}]]', text)
    for tag in ("class",):
        text = re.sub(rf'\{{@{tag} ([^}}|]+)(?:\|[^}}]*)?\}}',
                      lambda m: f'[[{_link_name(m.group(1))}]]', text)
    for tag in ("language",):
        text = re.sub(rf'\{{@{tag} ([^}}|]+)(?:\|[^}}]*)?\}}',
                      lambda m: f'[[{_link_name(m.group(1))}]]', text)
    for tag in ("background",):
        text = re.sub(rf'\{{@{tag} ([^}}|]+)(?:\|[^}}]*)?\}}',
                      lambda m: f'[[{_link_name(m.group(1))}]]', text)
    for tag in ("optfeature",):
        text = re.sub(rf'\{{@{tag} ([^}}|]+)(?:\|[^}}]*)?\}}',
                      lambda m: f'[[{_link_name(m.group(1))}]]', text)

    # Plain text substitutions
    text = re.sub(r'\{@damage ([^}]+)\}', r'\1', text)
    text = re.sub(r'\{@dice ([^}]+)\}', r'\1', text)
    text = re.sub(r'\{@hit ([^}]+)\}', r'+\1', text)
    text = re.sub(r'\{@dc ([^}]+)\}', r'DC \1', text)
    text = re.sub(r'\{@skill ([^}]+)\}', r'\1', text)
    text = re.sub(r'\{@ability ([^}]+)\}', r'\1', text)
    text = re.sub(r'\{@action ([^}|]+)(?:\|[^}]*)?\}', r'\1', text)
    text = re.sub(r'\{@sense ([^}|]+)(?:\|[^}]*)?\}', r'\1', text)
    text = re.sub(r'\{@chance ([^}]+)\}', r'\1%', text)
    text = re.sub(r'\{@recharge ([^}]+)\}', r'(Recharge \1–6)', text)
    text = re.sub(r'\{@recharge\}', '(Recharge 6)', text)
    text = text.replace('{@h}', '**Hit:** ')
    text = re.sub(r'\{@atk ([^}]+)\}', lambda m: _expand_atk(m.group(1)), text)
    text = re.sub(r'\{@creature ([^}|]+)(?:\|[^}]*)?\}', r'\1', text)
    text = re.sub(r'\{@table ([^}|]+)(?:\|[^}]*)?\}', r'\1', text)

    # Strip tags that don't add value in markdown
    text = re.sub(r'\{@filter [^}]*\}', '', text)
    text = re.sub(r'\{@book ([^|]+)\|[^}]*\}', r'\1', text)
    text = re.sub(r'\{@quickref [^}]*\}', '', text)
    text = re.sub(r'\{@variantrule ([^|]+)\|[^}]*\}', r'\1', text)
    text = re.sub(r'\{@5etools [^}]*\}', '', text)
    text = re.sub(r'\{@note ([^}]+)\}', r'*\1*', text)
    text = re.sub(r'\{@b ([^}]+)\}', r'**\1**', text)
    text = re.sub(r'\{@bold ([^}]+)\}', r'**\1**', text)
    text = re.sub(r'\{@i ([^}]+)\}', r'*\1*', text)
    text = re.sub(r'\{@italic ([^}]+)\}', r'*\1*', text)
    text = re.sub(r'\{@s ([^}]+)\}', r'~~\1~~', text)
    text = re.sub(r'\{@u ([^}]+)\}', r'<u>\1</u>', text)
    text = re.sub(r'\{@sup ([^}]+)\}', r'<sup>\1</sup>', text)
    text = re.sub(r'\{@sub ([^}]+)\}', r'<sub>\1</sub>', text)
    text = re.sub(r'\{@code ([^}]+)\}', r'`\1`', text)
    text = re.sub(r'\{@color #[0-9a-fA-F]+ ([^}]+)\}', r'\1', text)
    text = re.sub(r'\{@highlight ([^}]+)\}', r'\1', text)
    text = re.sub(r'\{@scaledice ([^}]+)\}', lambda m: m.group(1).split('|')[-1], text)
    text = re.sub(r'\{@scaledamage ([^}]+)\}', lambda m: m.group(1).split('|')[-1], text)

    # Catch-all: extract first segment before | or everything
    text = re.sub(r'\{@\w+ ([^}|]+)(?:\|[^}]*)?\}', r'\1', text)
    text = re.sub(r'\{[^}]*\}', '', text)
    return text


def _expand_atk(code: str) -> str:
    parts = [p.strip() for p in code.split(",")]
    labels = []
    for p in parts:
        if p == "mw": labels.append("Melee Weapon Attack")
        elif p == "rw": labels.append("Ranged Weapon Attack")
        elif p == "ms": labels.append("Melee Spell Attack")
        elif p == "rs": labels.append("Ranged Spell Attack")
        elif p == "mw,rw": labels.append("Melee or Ranged Weapon Attack")
        else: labels.append(p)
    return " or ".join(labels) + ":"


def render_entries(entries: list, indent: int = 0) -> str:
    """Recursively render 5e.tools entries array to markdown."""
    lines = []
    prefix = "  " * indent
    for entry in entries:
        if isinstance(entry, str):
            lines.append(prefix + convert_tags(entry))
        elif isinstance(entry, dict):
            t = entry.get("type", "")
            if t == "entries":
                name = entry.get("name", "")
                if name:
                    lines.append(f"\n{prefix}**{convert_tags(name)}**\n")
                sub = entry.get("entries", [])
                lines.append(render_entries(sub, indent))
            elif t == "list":
                items = entry.get("items", [])
                for item in items:
                    if isinstance(item, str):
                        lines.append(f"{prefix}- {convert_tags(item)}")
                    elif isinstance(item, dict):
                        item_name = item.get("name", "")
                        item_entries = item.get("entries", [])
                        if item_name:
                            rendered = render_entries(item_entries, 0).strip()
                            lines.append(f"{prefix}- **{convert_tags(item_name)}**: {rendered}")
                        else:
                            lines.append(render_entries([item], indent))
            elif t == "table":
                caption = entry.get("caption", "")
                if caption:
                    lines.append(f"\n{prefix}**{convert_tags(caption)}**\n")
                col_labels = entry.get("colLabels", [])
                col_styles = entry.get("colStyles", [])
                rows = entry.get("rows", [])
                if col_labels:
                    lines.append(prefix + "| " + " | ".join(convert_tags(str(c)) for c in col_labels) + " |")
                    aligns = []
                    for style in col_styles:
                        if "text-center" in style: aligns.append(":---:")
                        elif "text-right" in style: aligns.append("---:")
                        else: aligns.append("---")
                    if not aligns:
                        aligns = ["---"] * len(col_labels)
                    lines.append(prefix + "| " + " | ".join(aligns) + " |")
                    for row in rows:
                        cells = []
                        for cell in row:
                            if isinstance(cell, str):
                                cells.append(convert_tags(cell))
                            elif isinstance(cell, dict):
                                cells.append(convert_tags(str(cell.get("value", cell.get("exact", "")))))
                            else:
                                cells.append(str(cell))
                        lines.append(prefix + "| " + " | ".join(cells) + " |")
            elif t == "quote":
                q_entries = entry.get("entries", [])
                by = entry.get("by", "")
                for qe in q_entries:
                    if isinstance(qe, str):
                        lines.append(f"{prefix}> *{convert_tags(qe)}*")
                if by:
                    lines.append(f"{prefix}> — *{convert_tags(by)}*")
            elif t == "inset" or t == "insetReadaloud":
                inset_entries = entry.get("entries", [])
                name = entry.get("name", "")
                if name:
                    lines.append(f"\n{prefix}> **{convert_tags(name)}**")
                for ie in inset_entries:
                    if isinstance(ie, str):
                        lines.append(f"{prefix}> {convert_tags(ie)}")
            elif t == "section":
                name = entry.get("name", "")
                if name:
                    level = "#" * (indent + 3)
                    lines.append(f"\n{prefix}{level} {convert_tags(name)}\n")
                sub = entry.get("entries", [])
                lines.append(render_entries(sub, indent))
            elif t == "bonus":
                lines.append(f"{prefix}+{entry.get('value', '')}")
            elif t == "bonusSpeed":
                lines.append(f"{prefix}+{entry.get('value', '')} ft.")
            elif t == "abilityDc":
                lines.append(f"{prefix}**Spell save DC** = 8 + proficiency bonus + {entry.get('attributes', ['?'])[0].upper()} modifier")
            elif t == "abilityAttackMod":
                lines.append(f"{prefix}**Spell attack modifier** = proficiency bonus + {entry.get('attributes', ['?'])[0].upper()} modifier")
            elif t == "cell":
                roll = entry.get("roll", {})
                if "exact" in roll:
                    lines.append(f"{prefix}{roll['exact']}")
                elif "min" in roll and "max" in roll:
                    lines.append(f"{prefix}{roll['min']}–{roll['max']}")
            else:
                # Fallback: try to get name + entries
                name = entry.get("name", "")
                sub = entry.get("entries", [])
                if name:
                    lines.append(f"{prefix}**{convert_tags(name)}**")
                if sub:
                    lines.append(render_entries(sub, indent))
    return "\n".join(lines)


def format_prerequisite(prereqs: list) -> str:
    if not prereqs:
        return ""
    parts = []
    for p in prereqs:
        if isinstance(p, str):
            parts.append(p)
        elif isinstance(p, dict):
            sub = []
            if "level" in p:
                lvl = p["level"]
                if isinstance(lvl, dict):
                    sub.append(f"Level {lvl.get('level', '?')} {lvl.get('class', {}).get('name', '')}")
                else:
                    sub.append(f"Level {lvl}")
            if "ability" in p:
                for ab in p["ability"]:
                    for stat, val in ab.items():
                        sub.append(f"{stat.upper()} {val}+")
            if "feat" in p:
                for feat in p["feat"]:
                    fname = feat.split("|")[0]
                    sub.append(f"[[{_link_name(fname)}]]")
            if "race" in p:
                for race in p["race"]:
                    rname = race.get("name", "")
                    sub.append(f"[[{_link_name(rname)}]]")
            if "class" in p:
                cname = p["class"].get("name", "")
                sub.append(f"[[{_link_name(cname)}]]")
            if "other" in p:
                sub.append(p["other"])
            if "campaign" in p:
                sub.append(", ".join(p["campaign"]))
            if "spellcasting" in p and p["spellcasting"]:
                sub.append("Spellcasting")
            if "spellcasting2020" in p and p["spellcasting2020"]:
                sub.append("Spellcasting")
            if "psionics" in p and p["psionics"]:
                sub.append("Psionics")
            if "proficiency" in p:
                for prof in p["proficiency"]:
                    if isinstance(prof, dict):
                        for kind, val in prof.items():
                            if isinstance(val, list):
                                sub.append(f"Proficiency with {', '.join(str(v) for v in val)}")
                            elif isinstance(val, str):
                                sub.append(f"Proficiency with {val} {kind}")
                            else:
                                sub.append(f"Proficiency ({kind})")
            if sub:
                parts.append("; ".join(sub))
    return " or ".join(parts)


def format_ability_asi(ability_list: list) -> str:
    if not ability_list:
        return ""
    parts = []
    for ab in ability_list:
        if isinstance(ab, dict):
            for stat, val in ab.items():
                if stat == "choose":
                    count = ab.get("count", 1) if isinstance(ab, dict) else 1
                    parts.append(f"Choose {count} +{val}")
                else:
                    parts.append(f"{stat.upper()} +{val}")
    return ", ".join(parts)


def is_wotc(source: str, source_filter: set) -> bool:
    if not source_filter:
        return True
    return source in source_filter


_WRITTEN_PATHS: set = set()

def write_note(path: Path, content: str) -> bool:
    # Track in memory to avoid iCloud sync race conditions with path.exists()
    key = str(path)
    if key in _WRITTEN_PATHS or path.exists():
        return False
    _WRITTEN_PATHS.add(key)
    # Inject import tracking field so the vault can identify and clean up imported notes
    if content.startswith("---\n"):
        content = '---\nimport_source: "5etools"\n' + content[4:]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


# ── Spell source lookup ────────────────────────────────────────────────────────

_SPELL_LOOKUP: dict = {}


def load_spell_lookup() -> None:
    """Download gendata-spell-source-lookup.json and cache it globally."""
    global _SPELL_LOOKUP
    if _SPELL_LOOKUP:
        return
    url = f"{BASE_URL}/generated/gendata-spell-source-lookup.json"
    print("  Loading spell association lookup...", end=" ", flush=True)
    data = fetch_json(url)
    if not data:
        print("FAILED — classes/subclasses will be empty", file=sys.stderr)
        return
    _SPELL_LOOKUP = data
    total = sum(len(v) for v in data.values())
    print(f"{total} spell entries loaded")


def _get_spell_associations(spell_name: str, spell_source: str) -> dict:
    """Return classes, subclasses, species, backgrounds, feats for a spell."""
    entry = _SPELL_LOOKUP.get(spell_source.lower(), {}).get(spell_name.lower(), {})

    # Classes — flatten across all source keys, deduplicate
    classes_set: set = set()
    for _src, class_dict in entry.get("class", {}).items():
        for cls_name in class_dict:
            classes_set.add(cls_name)
    for _src, class_dict in entry.get("classVariant", {}).items():
        for cls_name in class_dict:
            classes_set.add(cls_name)

    # Subclasses — {spell_src: {class_name: {sub_src: {short_name: {name: display}}}}}
    subclasses: list = []
    seen_subs: set = set()
    for _spell_src, class_dict in entry.get("subclass", {}).items():
        for cls_name, sub_src_dict in class_dict.items():
            for _sub_src, short_name_dict in sub_src_dict.items():
                for _short, sub_info in short_name_dict.items():
                    display = sub_info.get("name", _short) if isinstance(sub_info, dict) else str(sub_info)
                    note_title = f"{display} ({cls_name})"
                    if note_title not in seen_subs:
                        seen_subs.add(note_title)
                        subclasses.append(f"[[{note_title}]]")

    # Species/Race — {src: {race_name: {baseName, baseSource}}}
    # Lookup format: "BaseName (SubraceName)" — notes are named "SubraceName (BaseName)"
    species: list = []
    seen_species: set = set()
    for _src, race_dict in entry.get("race", {}).items():
        for race_name, race_info in race_dict.items():
            base = race_info.get("baseName", "") if isinstance(race_info, dict) else ""
            m = re.match(r'^(.+?)\s*\((.+)\)$', race_name)
            if m and base and m.group(1) == base:
                # Swap to match note naming: SubraceName (BaseName)
                corrected = f"{m.group(2)} ({base})"
            else:
                corrected = race_name
            if corrected not in seen_species:
                seen_species.add(corrected)
                species.append(f"[[{corrected}]]")

    # Backgrounds — {src: {bg_name: true}}
    backgrounds: list = []
    seen_bg: set = set()
    for _src, bg_dict in entry.get("background", {}).items():
        for bg_name in bg_dict:
            if bg_name not in seen_bg:
                seen_bg.add(bg_name)
                backgrounds.append(f"[[{bg_name}]]")

    # Feats — {src: {feat_name: true}}
    feats: list = []
    seen_feats: set = set()
    for _src, feat_dict in entry.get("feat", {}).items():
        for feat_name in feat_dict:
            if feat_name not in seen_feats:
                seen_feats.add(feat_name)
                feats.append(f"[[{feat_name}]]")

    return {
        "classes": sorted(f"[[{c}]]" for c in classes_set),
        "subclasses": sorted(subclasses),
        "races": sorted(species),
        "backgrounds": sorted(backgrounds),
        "feats": sorted(feats),
    }


# ── Spell importer ─────────────────────────────────────────────────────────────

def import_spells(source_filter: set) -> int:
    out_dir = VAULT / "Possessions/Spells"
    count = 0

    load_spell_lookup()

    index = fetch_json(f"{BASE_URL}/spells/index.json")
    if not index:
        print("  Could not fetch spells index", file=sys.stderr)
        return 0

    all_spells = []
    for source, filename in index.items():
        if not is_wotc(source, source_filter):
            continue
        data = fetch_json(f"{BASE_URL}/spells/{filename}")
        if not data:
            continue
        for spell in data.get("spell", []):
            if not is_wotc(spell.get("source", ""), source_filter):
                continue
            all_spells.append(spell)

    for spell in _dedup(all_spells, lambda s: sanitize_filename(s.get("name", ""))):
        count += _write_spell(spell, out_dir)
    return count


def _write_spell(spell: dict, out_dir: Path) -> int:
    name = spell.get("name", "Unknown")
    source = spell.get("source", "")
    page = spell.get("page", "")
    level = spell.get("level", 0)
    school = SCHOOL_MAP.get(spell.get("school", ""), spell.get("school", ""))
    ritual = spell.get("meta", {}).get("ritual", False) if isinstance(spell.get("meta"), dict) else False
    concentration = False

    # Casting time
    time_list = spell.get("time", [{}])
    t = time_list[0] if time_list else {}
    num = t.get("number", 1)
    unit = t.get("unit", "action").title()
    casting_time = f"{num} {unit}"
    if t.get("condition"):
        casting_time += f", {convert_tags(t['condition'])}"

    # Range
    range_obj = spell.get("range", {})
    range_str = _format_range(range_obj)

    # Components
    comp = spell.get("components", {})
    comp_v = bool(comp.get("v", False))
    comp_s = bool(comp.get("s", False))
    comp_m_raw = comp.get("m", False)
    comp_m = bool(comp_m_raw)
    mat_desc = ""
    mat_cost = ""
    mat_consumed = False
    if isinstance(comp_m_raw, dict):
        mat_desc = comp_m_raw.get("text", "")
        mat_cost = str(comp_m_raw.get("cost", "")) if comp_m_raw.get("cost") else ""
        mat_consumed = bool(comp_m_raw.get("consume", False))
    elif isinstance(comp_m_raw, str):
        mat_desc = comp_m_raw

    # Duration
    dur_list = spell.get("duration", [{}])
    d = dur_list[0] if dur_list else {}
    dur_str = _format_duration(d)
    concentration = d.get("concentration", False)

    # Damage / save
    damage_types = spell.get("damageInflict", [])
    damage_type = damage_types[0].title() if damage_types else ""
    save_types = spell.get("savingThrow", [])
    save_type = save_types[0].title() if save_types else ""
    attack_type = spell.get("spellAttack", [""])[0] if spell.get("spellAttack") else ""
    if attack_type == "M": attack_type = "Melee"
    elif attack_type == "R": attack_type = "Ranged"

    # Classes / subclasses / species / backgrounds / feats from lookup
    assoc = _get_spell_associations(name, source)
    classes = assoc["classes"]
    subclasses = assoc["subclasses"]
    races = assoc["races"]
    bg_grants = assoc["backgrounds"]
    feat_grants = assoc["feats"]

    # Description
    desc = render_entries(spell.get("entries", []))
    higher = ""
    hl = spell.get("entriesHigherLevel", [])
    if hl:
        higher = render_entries(hl[0].get("entries", []) if isinstance(hl[0], dict) else hl)

    content = f"""---
tags:
  - Spell
art: "[[PlaceholderSpell.png]]"
aliases:
spellLevel: {level}
school: {yaml_str(school)}
castingTime: {yaml_str(casting_time)}
range: {yaml_str(range_str)}
componentsV: {str(comp_v).lower()}
componentsS: {str(comp_s).lower()}
componentsM: {str(comp_m).lower()}
materialDesc: {yaml_str(mat_desc)}
materialCost: {yaml_str(mat_cost)}
materialConsumed: {str(mat_consumed).lower()}
duration: {yaml_str(dur_str)}
concentration: {str(concentration).lower()}
ritual: {str(ritual).lower()}
damageType: {yaml_str(damage_type)}
damageDice:
saveType: {yaml_str(save_type)}
attackType: {yaml_str(attack_type)}
classes:{yaml_list(classes)}
subclasses:{yaml_list(subclasses)}
races:{yaml_list(races)}
grantedByBackgrounds:{yaml_list(bg_grants)}
grantedByFeats:{yaml_list(feat_grants)}
knownBy: []
source: {yaml_str(source)}
sourcePage: {page}
isHomebrew: false
---

> [!infobox | no-blending black]+ <font color="#ffffff">Infobox</font>
>
> `VIEW[!{{art}}][text(renderMarkdown)]`
>
> # Details
> | | |
> |---|---|
> | **Aliases** | `VIEW[{{aliases}}][text]` |
> | **Level** | `VIEW[{{spellLevel}}]` `VIEW[{{school}}][text]` |
> | **Ritual** | `VIEW[{{ritual}}]` |
> | **Concentration** | `VIEW[{{concentration}}]` |
> | **Casting Time** | `VIEW[{{castingTime}}][text]` |
> | **Range** | `VIEW[{{range}}][text]` |
> | **Duration** | `VIEW[{{duration}}][text]` |
> | **Attack / Save** | `VIEW[{{attackType}}][text]` / `VIEW[{{saveType}}][text]` |
> | **Damage** | `VIEW[{{damageDice}}][text]` `VIEW[{{damageType}}][text]` |
> | **Source** | `VIEW[{{source}}][text]` p.`VIEW[{{sourcePage}}]` |
>
> # Components
> | V | S | M |
> |:---:|:---:|:---:|
> | `VIEW[{{componentsV}}]` | `VIEW[{{componentsS}}]` | `VIEW[{{componentsM}}]` |
>
> *Material: `VIEW[{{materialDesc}}][text]` — Cost: `VIEW[{{materialCost}}][text]` — Consumed: `VIEW[{{materialConsumed}}]`*

# `=this.file.name`

## Description

{desc}

## At Higher Levels

{higher}

## Available To

| Field | Details |
| ----- | ------- |
| **Classes** | `VIEW[{{classes}}][link]` |
| **Subclasses** | `VIEW[{{subclasses}}][link]` |
| **Races** | `VIEW[{{races}}][link]` |
| **Backgrounds** | `VIEW[{{grantedByBackgrounds}}][link]` |
| **Feats** | `VIEW[{{grantedByFeats}}][link]` |
| **Known By** | `VIEW[{{knownBy}}][link]` |

## Notes

"""
    fname = sanitize_filename(name) + ".md"
    return 1 if write_note(out_dir / fname, content) else 0


def _format_range(r: dict) -> str:
    rtype = r.get("type", "")
    if rtype == "special": return "Special"
    if rtype == "sight": return "Sight"
    if rtype == "unlimited": return "Unlimited"
    if rtype == "touch": return "Touch"
    if rtype == "self":
        dist = r.get("distance", {})
        if dist:
            amt = dist.get("amount", "")
            dtype = dist.get("type", "")
            shape = r.get("shape", "")
            return f"Self ({amt}-{dtype} {shape})".strip().replace("  ", " ").replace("( ", "(")
        return "Self"
    dist = r.get("distance", {})
    amt = dist.get("amount", "")
    dtype = dist.get("type", "feet")
    if dtype == "feet": return f"{amt} feet"
    if dtype == "miles": return f"{amt} mile{'s' if amt != 1 else ''}"
    return f"{amt} {dtype}"


def _format_duration(d: dict) -> str:
    dtype = d.get("type", "")
    if dtype == "instant": return "Instantaneous"
    if dtype == "special": return "Special"
    if dtype == "permanent": return "Until dispelled"
    if dtype == "timed":
        dur = d.get("duration", {})
        amt = dur.get("amount", "")
        unit = dur.get("type", "")
        return f"{amt} {unit}{'s' if amt != 1 else ''}".strip()
    if dtype == "concentration":
        dur = d.get("duration", {})
        amt = dur.get("amount", "")
        unit = dur.get("type", "")
        return f"Concentration, up to {amt} {unit}{'s' if amt != 1 else ''}".strip()
    return dtype


# ── Item importer ──────────────────────────────────────────────────────────────

def import_items(source_filter: set) -> int:
    out_dir = VAULT / "Possessions/Items"
    count = 0

    all_items = []
    for filename in ("items.json", "items-base.json", "magicvariants.json"):
        data = fetch_json(f"{BASE_URL}/{filename}")
        if not data:
            continue
        key = "item" if "item" in data else "baseitem" if "baseitem" in data else "variant" if "variant" in data else None
        if not key:
            continue
        for item in data.get(key, []):
            if not is_wotc(item.get("source", ""), source_filter):
                continue
            all_items.append(item)

    for item in _dedup(all_items, lambda i: sanitize_filename(i.get("name", ""))):
        count += _write_item(item, out_dir)
    return count


def _write_item(item: dict, out_dir: Path) -> int:
    name = item.get("name", "Unknown")
    source = item.get("source", "")
    page = item.get("page", "")

    item_type_code = item.get("type", "")
    item_type = ITEM_TYPE_MAP.get(item_type_code, item_type_code or "Other")

    rarity = item.get("rarity", "none")
    if rarity in ("none", "unknown", "unknown (magic)", ""):
        rarity = "Common"
    else:
        rarity = rarity.title()

    req_attune = item.get("reqAttune", False)
    if req_attune is True:
        attunement = "Required"
    elif isinstance(req_attune, str):
        attunement = req_attune.title()
    else:
        attunement = "None"

    is_magical = bool(
        item.get("wondrous") or item.get("bonusWeapon") or item.get("bonusSpellAttack") or
        item.get("bonusSpellSaveDc") or item.get("bonusAc") or item.get("staff") or
        item.get("ring") or item.get("rod") or item.get("wand") or
        (rarity.lower() not in ("common", "none", ""))
    )

    weight = item.get("weight", "")
    value_cp = item.get("value", 0)
    cost, cost_unit = _format_value(value_cp)

    dmg1 = item.get("dmg1", "")
    dmg_type_code = item.get("dmgType", "")
    dmg_type_map = {"S": "Slashing", "P": "Piercing", "B": "Bludgeoning",
                    "F": "Fire", "C": "Cold", "L": "Lightning", "A": "Acid",
                    "N": "Necrotic", "R": "Radiant", "T": "Thunder",
                    "O": "Force", "I": "Psychic", "Y": "Psychic", "Po": "Poison"}
    dmg_type = dmg_type_map.get(dmg_type_code, dmg_type_code)

    weapon_type = item.get("weaponCategory", "")
    if weapon_type: weapon_type = weapon_type.title()

    props = item.get("property", [])
    def _norm_prop(p):
        # XPHB items use {"uid": "2H|XPHB", "note": "..."} dicts; others use plain strings
        code = p.get("uid", "") if isinstance(p, dict) else p
        code = code.split("|")[0]  # strip source suffix e.g. "AF|DMG" → "AF"
        return WEAPON_PROP_MAP.get(code, code)
    weapon_props = [_norm_prop(p) for p in props]

    armor_type = ""
    if item.get("armor"):
        ac_code = item.get("type", "")
        armor_type = {"LA": "Light Armor", "MA": "Medium Armor", "HA": "Heavy Armor", "S": "Shield"}.get(ac_code, "Armor")

    ac = item.get("ac", "")
    stealth_disadv = bool(item.get("stealth", False))
    min_str = item.get("strength", 0) or 0

    # Description
    entries = item.get("entries", [])
    desc_body = render_entries(entries) if entries else ""

    bonus_weapon = item.get("bonusWeapon", "")
    bonus_spell_atk = item.get("bonusSpellAttack", "")
    bonus_spell_dc = item.get("bonusSpellSaveDc", "")
    bonus_ac = item.get("bonusAc", "")
    if bonus_weapon: desc_body = f"You gain a **{bonus_weapon}** bonus to attack and damage rolls made with this weapon.\n\n" + desc_body
    if bonus_spell_atk: desc_body = f"You gain a **{bonus_spell_atk}** bonus to spell attack rolls.\n\n" + desc_body
    if bonus_spell_dc: desc_body = f"You gain a **{bonus_spell_dc}** bonus to the spell save DC.\n\n" + desc_body
    if bonus_ac: desc_body = f"You gain a **{bonus_ac}** bonus to AC.\n\n" + desc_body

    content = f"""---
tags:
  - Item
art: "[[PlaceholderItem.png]]"
aliases:
itemType: {yaml_str(item_type)}
rarity:
  - {yaml_str(rarity)}
isMagical: {str(is_magical).lower()}
attunement: {yaml_str(attunement)}
attuned:
weight: {weight}
cost: {cost}
costUnit: {yaml_str(cost_unit)}
damage: {yaml_str(dmg1)}
damageType: {yaml_str(dmg_type)}
weaponType: {yaml_str(weapon_type)}
weaponProperties:{yaml_list(weapon_props)}
armorType: {yaml_str(armor_type)}
armorClass: {ac}
armorClassBonus: 0
minStr: {min_str}
stealthDisadvantage: {str(stealth_disadv).lower()}
charges:
chargesMax:
recharge:
owner:
foundAt:
vendor:
source: {yaml_str(source)}
sourcePage: {page}
isHomebrew: false
---

> [!infobox | no-blending black]+ <font color="#ffffff">Infobox</font>
>
> `VIEW[!{{art}}][text(renderMarkdown)]`
>
> # Details
> | | |
> |---|---|
> | **Aliases** | `VIEW[{{aliases}}][text]` |
> | **Type** | `VIEW[{{itemType}}][text]` |
> | **Rarity** | `VIEW[{{rarity}}][text]` |
> | **Magical** | `VIEW[{{isMagical}}]` |
> | **Attunement** | `VIEW[{{attunement}}][text]` |
> | **Attuned By** | `VIEW[{{attuned}}][link]` |
> | **Weight** | `VIEW[{{weight}}][text]` lbs |
> | **Cost** | `VIEW[{{cost}}]` `VIEW[{{costUnit}}][text]` |
> | **Owner** | `VIEW[{{owner}}][link]` |
> | **Found At** | `VIEW[{{foundAt}}][link]` |
> | **Vendor** | `VIEW[{{vendor}}][link]` |
> | **Source** | `VIEW[{{source}}][text]` p.`VIEW[{{sourcePage}}]` |

# `=this.file.name`

## Properties

### Weapon Stats

| Damage | Type | Weapon Type | Range | Properties |
| :----: | :--: | :---------: | :---: | ---------- |
| `VIEW[{{damage}}][text]` | `VIEW[{{damageType}}][text]` | `VIEW[{{weaponType}}][text]` | | `VIEW[{{weaponProperties}}][text]` |

### Armour Stats

| Armour Type | AC | AC Bonus | Min STR | Stealth Disadvantage |
| :---------: | :-: | :------: | :-----: | :------------------: |
| `VIEW[{{armorType}}][text]` | `VIEW[{{armorClass}}]` | +`VIEW[{{armorClassBonus}}]` | `VIEW[{{minStr}}]` | `VIEW[{{stealthDisadvantage}}]` |

### Charges

> **Charges:** `VIEW[{{charges}}]` / `VIEW[{{chargesMax}}]` — **Recharge:** `VIEW[{{recharge}}][text]`

## Magical Properties & Abilities

{desc_body}

## Lore & History

## Notes

"""
    fname = sanitize_filename(name) + ".md"
    return 1 if write_note(out_dir / fname, content) else 0


def _format_value(value_cp: int) -> tuple:
    if not value_cp:
        return ("", "gp")
    if value_cp % 1000 == 0:
        return (value_cp // 1000, "gp")
    if value_cp % 100 == 0:
        return (value_cp // 100, "sp")
    return (value_cp, "cp")


# ── Background importer ────────────────────────────────────────────────────────

def import_backgrounds(source_filter: set) -> int:
    out_dir = VAULT / "Lore/Backgrounds"
    data = fetch_json(f"{BASE_URL}/backgrounds.json")
    if not data:
        return 0
    entries = [b for b in data.get("background", []) if is_wotc(b.get("source", ""), source_filter)]
    count = 0
    for bg in _dedup(entries, lambda b: sanitize_filename(b.get("name", ""))):
        count += _write_background(bg, out_dir)
    return count


def _write_background(bg: dict, out_dir: Path) -> int:
    name = bg.get("name", "Unknown")
    source = bg.get("source", "")
    page = bg.get("page", "")

    skills = []
    for sp in bg.get("skillProficiencies", [{}]):
        if isinstance(sp, dict):
            for k, v in sp.items():
                if k == "choose":
                    skills.append(f"Choose from: {', '.join(v.get('from', []))}")
                elif v is True:
                    skills.append(k.title())

    tools = []
    for tp in bg.get("toolProficiencies", [{}]):
        if isinstance(tp, dict):
            for k, v in tp.items():
                if k == "choose":
                    tools.append(f"Choose: {', '.join(v.get('from', []))}")
                elif v is True:
                    tools.append(k.title())

    langs = []
    for lp in bg.get("languageProficiencies", [{}]):
        if isinstance(lp, dict):
            any_std = lp.get("anyStandard", 0)
            if any_std:
                langs.append(f"Any {any_std} standard language{'s' if any_std > 1 else ''}")
            for k, v in lp.items():
                if k not in ("anyStandard", "choose") and v is True:
                    langs.append(k.title())

    feat_list = []
    for fp in bg.get("feats", []):
        if isinstance(fp, dict):
            for k in fp:
                fname_raw = k.split("|")[0]
                feat_list.append(f"[[{fname_raw.title()}]]")

    asi = format_ability_asi(bg.get("ability", []))

    equip_parts = []
    for eq_set in bg.get("startingEquipment", []):
        if isinstance(eq_set, dict):
            for option, items in eq_set.items():
                if option == "_":
                    rendered = _render_equipment(items)
                    if rendered:
                        equip_parts.append(rendered)
                elif option in ("a", "b", "c"):
                    rendered = _render_equipment(items)
                    if rendered:
                        equip_parts.append(f"Option {option.upper()}: {rendered}")
    equip_str = "; ".join(equip_parts)

    entries = bg.get("entries", [])
    desc_body = render_entries(entries)

    content = f"""---
tags:
  - Background
art: "[[PlaceholderBackground.png]]"
aliases:
skillProficiencies:{yaml_list(skills)}
toolProficiencies:{yaml_list(tools)}
languageProficiencies:{yaml_list(langs)}
startingEquipment: {yaml_str(equip_str)}
feats:{yaml_list(feat_list)}
abilityScoreIncrease: {yaml_str(asi)}
source: {yaml_str(source)}
sourcePage: {page}
isHomebrew: false
---

> [!infobox | no-blending black]+ <font color="#ffffff">Infobox</font>
>
> `VIEW[!{{art}}][text(renderMarkdown)]`
>
> # Details
> | | |
> |---|---|
> | **Aliases** | `VIEW[{{aliases}}][text]` |
> | **Ability Score** | `VIEW[{{abilityScoreIncrease}}][text]` |
> | **Feats** | `VIEW[{{feats}}][link]` |
> | **Source** | `VIEW[{{source}}][text]` p.`VIEW[{{sourcePage}}]` |
>
> # Proficiencies
> | | |
> |---|---|
> | **Skills** | `VIEW[{{skillProficiencies}}][text]` |
> | **Tools** | `VIEW[{{toolProficiencies}}][text]` |
> | **Languages** | `VIEW[{{languageProficiencies}}][text]` |

# `=this.file.name`

> *Summarize this background — what life experience it represents and what kind of character it suits.*

## Description

{desc_body}

## Starting Equipment

{equip_str}

## Notes

"""
    fname = sanitize_filename(name) + ".md"
    return 1 if write_note(out_dir / fname, content) else 0


def _render_equipment(items: list) -> str:
    parts = []
    for item in items:
        if isinstance(item, str):
            iname = item.split("|")[0]
            parts.append(f"[[{iname.title()}]]")
        elif isinstance(item, dict):
            if "item" in item:
                iname = item["item"].split("|")[0]
                qty = item.get("quantity", 1)
                display = item.get("displayName", iname)
                parts.append(f"{qty}× [[{display.title()}]]" if qty > 1 else f"[[{display.title()}]]")
            elif "special" in item:
                parts.append(convert_tags(item["special"]))
            elif "value" in item:
                parts.append(f"{item['value']} cp in coin")
    return ", ".join(parts)


# ── Class importer ─────────────────────────────────────────────────────────────

def import_classes(source_filter: set) -> tuple:
    class_dir = VAULT / "Lore/Classes"
    sub_dir = VAULT / "Lore/Classes/Subclasses"

    index = fetch_json(f"{BASE_URL}/class/index.json")
    if not index:
        print("  Could not fetch class index", file=sys.stderr)
        return 0, 0

    all_classes: list = []
    all_subs: list = []
    # Store per-class full_data for _write_class (needs classFeature entries)
    class_full_data: dict = {}

    for _class_name, filename in index.items():
        data = fetch_json(f"{BASE_URL}/class/{filename}")
        if not data:
            continue
        for cls in data.get("class", []):
            if is_wotc(cls.get("source", ""), source_filter):
                all_classes.append(cls)
                class_full_data[sanitize_filename(cls.get("name", ""))] = data
        for sub in data.get("subclass", []):
            if is_wotc(sub.get("source", ""), source_filter):
                all_subs.append(sub)

    deduped_classes = _dedup(all_classes, lambda c: sanitize_filename(c.get("name", "")))
    deduped_subs = _dedup(
        all_subs,
        lambda s: sanitize_filename(f"{s.get('name','')} ({s.get('className','')})")
    )

    class_count = sum(
        _write_class(cls, class_full_data.get(sanitize_filename(cls.get("name", "")), {}), class_dir)
        for cls in deduped_classes
    )
    sub_count = sum(_write_subclass(sub, sub_dir) for sub in deduped_subs)

    return class_count, sub_count


def _clean_col_label(label: str) -> str:
    """Strip {@filter Label|...} and other tags to a plain column name."""
    m = re.match(r'^\{@\w+\s+([^|}]+)', label)
    if m:
        return m.group(1).strip()
    return re.sub(r'\{@[^}]+\}', '', label).strip()


def _write_class(cls: dict, full_data: dict, out_dir: Path) -> int:
    name = cls.get("name", "Unknown")
    source = cls.get("source", "")
    page = cls.get("page", "")
    hd = cls.get("hd", {})
    hit_die = f"d{hd.get('faces', 8)}"
    saving_throws = [s.upper() for s in cls.get("proficiency", [])]
    is_caster = bool(cls.get("spellcastingAbility"))
    spell_ability = cls.get("spellcastingAbility", "").upper() if cls.get("spellcastingAbility") else ""

    start_profs = cls.get("startingProficiencies", {})
    armor_profs = _extract_profs(start_profs.get("armor", []))
    weapon_profs = _extract_profs(start_profs.get("weapons", []))
    tool_profs = _extract_profs(start_profs.get("tools", []))
    skill_choices_raw = start_profs.get("skills", [{}])
    skill_choices = []
    skill_count = 2
    for sc in skill_choices_raw:
        if isinstance(sc, dict):
            skill_count = sc.get("count", 2)
            skill_choices = sc.get("from", [])

    subclass_title = cls.get("subclassTitle", "Subclass")

    # Parse classFeatures: flat list of "Name|Class||Level[|Source]" strings
    # (some are dicts with gainSubclassFeature flag)
    class_features_by_level: dict = {i: [] for i in range(1, 21)}
    subclass_level = 3
    for feat_entry in cls.get("classFeatures", []):
        if isinstance(feat_entry, str):
            feat_str = feat_entry
            is_subclass_feat = False
        elif isinstance(feat_entry, dict):
            feat_str = feat_entry.get("classFeature", feat_entry.get("name", ""))
            is_subclass_feat = bool(feat_entry.get("gainSubclassFeature"))
        else:
            continue
        parts = feat_str.split("|")
        feat_name = convert_tags(parts[0])
        try:
            level = int(parts[3]) if len(parts) > 3 and parts[3] else 1
        except (ValueError, IndexError):
            level = 1
        if 1 <= level <= 20:
            class_features_by_level[level].append(feat_name)
        if is_subclass_feat:
            subclass_level = level

    # Parse classTableGroups for class-specific columns (Bardic Die, Cantrips, spell slots, etc.)
    extra_headers: list = []
    extra_rows: list = [[] for _ in range(20)]  # 20 levels

    for group in cls.get("classTableGroups", []):
        col_labels = group.get("colLabels", [])
        clean_labels = [_clean_col_label(lbl) for lbl in col_labels]
        # rowsSpellProgression: 0 → "—", positive → number
        rows = group.get("rowsSpellProgression") or group.get("rows") or []
        is_spell = "rowsSpellProgression" in group

        for col_idx, col_label in enumerate(clean_labels):
            extra_headers.append(col_label)
            for lvl_idx in range(20):
                if lvl_idx < len(rows) and col_idx < len(rows[lvl_idx]):
                    val = rows[lvl_idx][col_idx]
                    if isinstance(val, dict) and val.get("type") == "dice":
                        rolls = val.get("toRoll", [{}])
                        cell = "+".join(f"{r.get('number',1)}d{r.get('faces',6)}" for r in rolls)
                    elif is_spell and isinstance(val, int) and val == 0:
                        cell = "—"
                    else:
                        cell = str(val)
                else:
                    cell = "—"
                extra_rows[lvl_idx].append(cell)

    # Build markdown table
    prof_bonus = [2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6]
    base_headers = ["Level", "Prof. Bonus", "Features"]
    all_headers = base_headers + extra_headers
    sep = ["-----", ":---------:", "--------"] + ["-" * max(3, len(h)) for h in extra_headers]

    table_lines = [
        "| " + " | ".join(all_headers) + " |",
        "| " + " | ".join(sep) + " |",
    ]
    for lvl in range(1, 21):
        pb = prof_bonus[lvl - 1]
        feats_str = ", ".join(class_features_by_level.get(lvl, []))
        extra_cells = extra_rows[lvl - 1] if extra_rows[lvl - 1] else [""] * len(extra_headers)
        table_lines.append("| " + " | ".join([str(lvl), f"+{pb}", feats_str] + extra_cells) + " |")

    table_str = "\n".join(table_lines)

    content = f"""---
tags:
  - Class
art: "[[PlaceholderHeritage.png]]"
aliases:
hitDie: {yaml_str(hit_die)}
primaryAbility: []
savingThrows:{yaml_list(saving_throws)}
isSpellcaster: {str(is_caster).lower()}
spellcastingAbility: {yaml_str(spell_ability)}
armorProficiencies:{yaml_list(armor_profs)}
weaponProficiencies:{yaml_list(weapon_profs)}
toolProficiencies:{yaml_list(tool_profs)}
skillChoices:{yaml_list(skill_choices)}
skillCount: {skill_count}
subclassLevel: {subclass_level}
subclassName: {yaml_str(subclass_title)}
rarity:
source: {yaml_str(source)}
sourcePage: {page}
summary: ""
---

> [!infobox | no-blending black]+ <font color="#ffffff">Infobox</font>
>
> `VIEW[!{{art}}][text(renderMarkdown)]`
>
> # Details
> | | |
> |---|---|
> | **Aliases** | `VIEW[{{aliases}}][text]` |
> | **Hit Die** | `VIEW[{{hitDie}}][text]` |
> | **Primary Ability** | `VIEW[{{primaryAbility}}][text]` |
> | **Saving Throws** | `VIEW[{{savingThrows}}][text]` |
> | **Spellcasting** | `VIEW[{{spellcastingAbility}}][text]` (`VIEW[{{isSpellcaster}}][text]`) |
> | **Subclass At** | Level `VIEW[{{subclassLevel}}]` (`VIEW[{{subclassName}}][text]`) |
> | **Rarity** | `VIEW[{{rarity}}][text]` |
> | **Source** | `VIEW[{{source}}][text]` p.`VIEW[{{sourcePage}}]` |

# `=this.file.name`

> *Summarize what makes this class unique. Mention its core fantasy, playstyle, and what type of adventurer it represents.*

## Proficiencies

| Category | Proficiencies |
| -------- | ------------- |
| **Armour** | `VIEW[{{armorProficiencies}}][text]` |
| **Weapons** | `VIEW[{{weaponProficiencies}}][text]` |
| **Tools** | `VIEW[{{toolProficiencies}}][text]` |
| **Skills** | Choose `VIEW[{{skillCount}}]` from `VIEW[{{skillChoices}}][text]` |

## Class Table

{table_str}

## Overview

### Physical Traits

> *What noticeable physical features or trappings define members of this class?*

### Core Abilities

> *Describe the core features all members of this class share regardless of subclass.*

### Culture & Society

> *How are members of this class perceived in the world?*

### Beliefs

> *What philosophies, codes, or spiritual traditions are commonly associated with this class?*

### History

> *How did this class come to exist in the world?*

## Subclasses

```dataview
LIST
FROM "Lore/Classes/Subclasses"
WHERE econtains(tags,"Subclass") AND parentclass = this.file.link
SORT file.name ASC
```

## My Characters With This Class

```dataview
TABLE WITHOUT ID
  file.link as "Character",
  subclass as "Subclass",
  species as "Species",
  level as "Level"
FROM "My Character"
WHERE econtains(tags,"Player") AND class = this.file.link
SORT level DESC
```

## Notes

"""
    fname = sanitize_filename(name) + ".md"
    return 1 if write_note(out_dir / fname, content) else 0


def _extract_profs(items: list) -> list:
    result = []
    for item in items:
        if isinstance(item, str):
            result.append(item.title())
        elif isinstance(item, dict):
            if "proficiency" in item:
                result.extend(_extract_profs(item["proficiency"]))
            else:
                for k in item:
                    result.append(k.title())
    return result


def _write_subclass(sub: dict, out_dir: Path) -> int:
    name = sub.get("name", "Unknown")
    class_name = sub.get("className", "")
    short_name = sub.get("shortName", "")
    source = sub.get("source", "")
    page = sub.get("page", "")
    subclass_type = sub.get("subclassTitle", "")
    subclass_level = 3
    try:
        first_feature = sub.get("subclassFeatures", [[]])[0]
        if first_feature:
            parts = (first_feature[0] if isinstance(first_feature[0], str) else "").split("|")
            if len(parts) >= 4:
                subclass_level = int(parts[3])
    except (ValueError, TypeError, IndexError):
        subclass_level = 3

    has_extra_spells = bool(sub.get("additionalSpells"))
    extra_spells_rows = _render_extra_spells(sub.get("additionalSpells", []))

    features_body = _render_subclass_features(sub.get("subclassFeatures", []))

    content = f"""---
tags:
  - Subclass
art: "[[PlaceholderHeritage.png]]"
aliases: {yaml_str(short_name)}
parentclass: "[[{class_name}]]"
subclassType: {yaml_str(subclass_type)}
subclassLevel: {subclass_level}
additionalSpellcasting: {str(has_extra_spells).lower()}
rarity:
source: {yaml_str(source)}
sourcePage: {page}
summary: ""
---

> [!infobox | no-blending black]+ <font color="#ffffff">Infobox</font>
>
> `VIEW[!{{art}}][text(renderMarkdown)]`
>
> # Details
> | | |
> |---|---|
> | **Aliases** | `VIEW[{{aliases}}][text]` |
> | **Parent Class** | `VIEW[{{parentclass}}][link]` |
> | **Subclass Type** | `VIEW[{{subclassType}}][text]` |
> | **Available At** | Level `VIEW[{{subclassLevel}}]` |
> | **Extra Spells** | `VIEW[{{additionalSpellcasting}}]` |
> | **Rarity** | `VIEW[{{rarity}}][text]` |
> | **Source** | `VIEW[{{source}}][text]` p.`VIEW[{{sourcePage}}]` |

# `=this.file.name`

> *Summarize what makes this subclass unique within its parent class.*

## Expanded Spells (if applicable)

| Spell Level | Spells |
| :---------: | ------ |
{extra_spells_rows}

## Overview

### Innate Abilities

{features_body}

## Notes

"""
    fname = sanitize_filename(f"{name} ({class_name})") + ".md"
    return 1 if write_note(out_dir / fname, content) else 0


def _render_extra_spells(additional_spells: list) -> str:
    if not additional_spells:
        return "| 1st | |\n| 2nd | |\n| 3rd | |\n| 4th | |\n| 5th | |"
    rows = []
    levels = {1: [], 2: [], 3: [], 4: [], 5: []}
    for spell_set in additional_spells:
        if not isinstance(spell_set, dict):
            continue
        prepared = spell_set.get("prepared", {})
        known = spell_set.get("known", {})
        for source_dict in (prepared, known):
            for level_key, spells in source_dict.items():
                try:
                    lvl = int(level_key)
                    if 1 <= lvl <= 5:
                        for s in spells:
                            if isinstance(s, str):
                                sname = s.split("|")[0]
                                levels[lvl].append(f"[[{sname.title()}]]")
                except (ValueError, TypeError):
                    pass
    for lvl in range(1, 6):
        suffix = {1:"st",2:"nd",3:"rd",4:"th",5:"th"}[lvl]
        spells_str = ", ".join(levels[lvl]) if levels[lvl] else ""
        rows.append(f"| {lvl}{suffix} | {spells_str} |")
    return "\n".join(rows)


def _render_subclass_features(subclass_features: list) -> str:
    parts = []
    for level_features in subclass_features:
        if not isinstance(level_features, list):
            continue
        for feat_ref in level_features:
            if isinstance(feat_ref, str):
                parts.append(f"**{feat_ref.split('|')[0]}**")
    return "\n\n".join(parts) if parts else ""


# ── Class feature importer ─────────────────────────────────────────────────────

def import_class_features(source_filter: set) -> int:
    out_dir = VAULT / "Lore/Classes/Features"
    # Clear existing notes so multi-class notes replace single-class ones
    if out_dir.exists():
        for f in out_dir.iterdir():
            if f.suffix == ".md":
                f.unlink()
    out_dir.mkdir(parents=True, exist_ok=True)

    index = fetch_json(f"{BASE_URL}/class/index.json")
    if not index:
        print("  Could not fetch class index", file=sys.stderr)
        return 0

    # Pass 1: collect all sources per feature name
    feature_map: dict = {}
    for filename in index.values():
        data = fetch_json(f"{BASE_URL}/class/{filename}")
        if not data:
            continue
        for cf in (data.get("classFeature") or []):
            if is_wotc(cf.get("source", ""), source_filter):
                _collect_feature(cf, feature_map, subclass_short="")
        for scf in (data.get("subclassFeature") or []):
            if is_wotc(scf.get("source", ""), source_filter):
                short = scf.get("subclassShortName", "")
                _collect_feature(scf, feature_map, subclass_short=short)

    # Pass 2: write one note per feature with all classes listed
    count = 0
    for feat_name, sources in feature_map.items():
        class_names = list(dict.fromkeys(s["class_name"] for s in sources))
        class_yaml  = "\n".join(f"  - '{c}'" for c in class_names)
        class_links = " | ".join(f"[[{c}]]" for c in class_names)
        min_level   = min(s["level"] for s in sources)
        src0        = sources[0]

        if len(sources) == 1:
            s = src0
            sub_line = f"\n**Subclass:** {s['subclass_short']}" if s["subclass_short"] else ""
            body = render_entries(s["entries"]) if s["entries"] else ""
            class_header = f"**Class:** {class_links} | **Level:** {s['level']}{sub_line}"
        else:
            sections = []
            for s in sources:
                sub = f" ({s['subclass_short']})" if s["subclass_short"] else ""
                hdr = f"### {s['class_name']}{sub} *(Level {s['level']})*"
                desc = render_entries(s["entries"]) if s["entries"] else ""
                sections.append(f"{hdr}\n\n{desc}")
            body = "\n\n".join(sections)
            class_header = f"**Classes:** {class_links}"

        content = f"""---
tags:
  - ClassFeature
className:
{class_yaml}
featureLevel: {min_level}
source: '{src0["source"]}'
sourcePage: {src0["page"]}
---

# {feat_name}

{class_header}

{body}

## Notes

"""
        fname = sanitize_filename(feat_name) + ".md"
        if write_note(out_dir / fname, content):
            count += 1
        # Alias for die-suffixed names so [[Song of Rest]] resolves
        base = re.sub(r'\s*\([dD]\d+\)$', '', feat_name).strip()
        if base != feat_name:
            write_note(out_dir / (sanitize_filename(base) + ".md"), content)

    return count


def _collect_feature(feature: dict, feature_map: dict, subclass_short: str) -> None:
    name = feature.get("name", "Unknown")
    feature_map.setdefault(name, []).append({
        "class_name":    feature.get("className", ""),
        "level":         feature.get("level", 0),
        "subclass_short": subclass_short,
        "source":        feature.get("source", ""),
        "page":          feature.get("page", ""),
        "entries":       feature.get("entries", []),
    })


# ── Racial trait importer ───────────────────────────────────────────────────────

def import_racial_traits(source_filter: set) -> int:
    folder = "Species" if SYSTEM == "dnd5e_2024" else "Races"
    out_dir = VAULT / f"Lore/{folder}/Traits"
    # Clear existing notes so multi-race notes replace single-race ones
    if out_dir.exists():
        for f in out_dir.iterdir():
            if f.suffix == ".md":
                f.unlink()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = fetch_json(f"{BASE_URL}/races.json")
    if not data:
        return 0

    # Pass 1: collect all (race_display_name, desc) per trait name
    trait_map: dict = {}

    for race in (data.get("race") or []):
        if not is_wotc(race.get("source", ""), source_filter):
            continue
        race_name = race.get("name", "")
        for entry in (race.get("entries") or []):
            if not isinstance(entry, dict):
                continue
            name = entry.get("name", "").strip()
            if not name:
                continue
            desc = render_entries(entry.get("entries") or [])
            trait_map.setdefault(name, []).append((race_name, desc))

    for sub in (data.get("subrace") or []):
        src = sub.get("source", "")
        if not is_wotc(src, source_filter):
            continue
        race_name   = sub.get("raceName") or sub.get("name", "")
        sub_label   = sub.get("name", "")
        display     = f"{sub_label} ({race_name})" if sub_label else race_name
        for entry in (sub.get("entries") or []):
            if not isinstance(entry, dict):
                continue
            name = entry.get("name", "").strip()
            if not name:
                continue
            desc = render_entries(entry.get("entries") or [])
            trait_map.setdefault(name, []).append((display, desc))

    # Pass 2: write one note per trait with all races listed
    count = 0

    # Generic stub for Ability Score Increase — in every race but not a named entry
    stub = """---
tags:
  - RacialTrait
---

# Ability Score Increase

Each race provides an ability score increase as described in its racial traits. See your race entry for the specific increases granted.

## Notes

"""
    if write_note(out_dir / "Ability Score Increase.md", stub):
        count += 1

    for trait_name, sources in trait_map.items():
        race_names = list(dict.fromkeys(r for r, _ in sources))
        race_yaml  = "\n".join(f"  - '{r}'" for r in race_names)
        race_links = " | ".join(f"[[{r}]]" for r in race_names)

        if len(sources) == 1:
            body = sources[0][1]
        else:
            sections = [f"### {r}\n\n{d}" for r, d in sources]
            body = "\n\n".join(sections)

        content = f"""---
tags:
  - RacialTrait
race:
{race_yaml}
---

# {trait_name}

**Race:** {race_links}

{body}

## Notes

"""
        fname = sanitize_filename(trait_name) + ".md"
        if write_note(out_dir / fname, content):
            count += 1

    return count


# ── Background feature importer ─────────────────────────────────────────────────

def import_background_features(source_filter: set) -> int:
    out_dir = VAULT / "Lore/Backgrounds/Features"
    # Clear existing notes so multi-background notes replace single-background ones
    if out_dir.exists():
        for f in out_dir.iterdir():
            if f.suffix == ".md":
                f.unlink()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = fetch_json(f"{BASE_URL}/backgrounds.json")
    if not data:
        return 0

    # Pass 1: collect all (bg_name, desc) per feature name
    feat_map: dict = {}
    for bg in (data.get("background") or []):
        if not is_wotc(bg.get("source", ""), source_filter):
            continue
        bg_name = bg.get("name", "")
        for entry in (bg.get("entries") or []):
            if not isinstance(entry, dict):
                continue
            raw_name = entry.get("name", "")
            if not raw_name.startswith("Feature"):
                continue
            feat_name = raw_name.replace("Feature:", "").strip()
            if not feat_name:
                continue
            desc = render_entries(entry.get("entries") or [])
            feat_map.setdefault(feat_name, []).append((bg_name, desc))

    # Pass 2: write one note per feature with all backgrounds listed
    count = 0
    for feat_name, sources in feat_map.items():
        bg_names = list(dict.fromkeys(b for b, _ in sources))
        bg_yaml  = "\n".join(f"  - '{b}'" for b in bg_names)
        bg_links = " | ".join(f"[[{b}]]" for b in bg_names)

        if len(sources) == 1:
            body = sources[0][1]
        else:
            sections = [f"### {b}\n\n{d}" for b, d in sources]
            body = "\n\n".join(sections)

        content = f"""---
tags:
  - BackgroundFeature
background:
{bg_yaml}
---

# {feat_name}

**Background:** {bg_links}

{body}

## Notes

"""
        fname = sanitize_filename(feat_name) + ".md"
        if write_note(out_dir / fname, content):
            count += 1

    return count


# ── Race importer ──────────────────────────────────────────────────────────────

SOURCE_PRIORITY = [
    "XPHB", "XDMG", "MPMM", "TCE", "XGE", "SCAG", "GGR", "AI",
    "EGW", "MOT", "FTD", "SCC", "ERLW", "AAG", "SAiS", "BMT",
    "LoX", "DSotDQ", "KftGV", "VGM", "MTF", "PHB", "DMG", "MM",
]

def _source_rank(source: str) -> int:
    try:
        return SOURCE_PRIORITY.index(source)
    except ValueError:
        return len(SOURCE_PRIORITY)


def _dedup(entries: list, key_fn) -> list:
    """Keep one entry per key, preferring higher-priority sources."""
    best: dict = {}
    for entry in entries:
        k = key_fn(entry)
        rank = _source_rank(entry.get("source", ""))
        if k not in best or rank < best[k][0]:
            best[k] = (rank, entry)
    return [v for _, v in best.values()]


def import_races(source_filter: set) -> int:
    folder = "Species" if SYSTEM == "dnd5e_2024" else "Races"
    out_dir = VAULT / f"Lore/{folder}"

    data = fetch_json(f"{BASE_URL}/races.json")
    if not data:
        print("  Could not fetch races.json", file=sys.stderr)
        return 0

    # Collect all entries keyed by effective filename, keeping best source
    best: dict = {}  # filename_stem -> (rank, entry, parent)

    for race in data.get("race", []):
        if not race.get("name") or not is_wotc(race.get("source", ""), source_filter):
            continue
        key = sanitize_filename(race["name"])
        rank = _source_rank(race.get("source", ""))
        if key not in best or rank < best[key][0]:
            best[key] = (rank, race, None)

    for subrace in data.get("subrace", []):
        if not subrace.get("name") or not is_wotc(subrace.get("source", ""), source_filter):
            continue
        parent = subrace.get("raceName", "")
        key = sanitize_filename(f"{subrace['name']} ({parent})") if parent else sanitize_filename(subrace["name"])
        rank = _source_rank(subrace.get("source", ""))
        if key not in best or rank < best[key][0]:
            best[key] = (rank, subrace, parent if parent else None)

    count = 0
    for _key, (rank, entry, parent) in best.items():
        count += _write_race(entry, out_dir, parent=parent)
    return count


def _write_race(race: dict, out_dir: Path, parent: Optional[str]) -> int:
    name = race.get("name", "Unknown")
    source = race.get("source", "")
    page = race.get("page", "")

    size_raw = race.get("size", ["M"])
    size_map = {"F": "Fine", "D": "Diminutive", "T": "Tiny", "S": "Small",
                "M": "Medium", "L": "Large", "H": "Huge", "G": "Gargantuan", "C": "Colossal"}
    sizes = [size_map.get(s, s) for s in (size_raw if isinstance(size_raw, list) else [size_raw])]

    speed_raw = race.get("speed", 30)
    speed = 30
    speed_fly = 0
    speed_swim = 0
    speed_climb = 0
    if isinstance(speed_raw, int):
        speed = speed_raw
    elif isinstance(speed_raw, dict):
        speed = speed_raw.get("walk", 30)
        speed_fly = speed_raw.get("fly", 0) or 0
        speed_swim = speed_raw.get("swim", 0) or 0
        speed_climb = speed_raw.get("climb", 0) or 0
    darkvision = race.get("darkvision", 0) or 0

    asi = {"str":0,"dex":0,"con":0,"int":0,"wis":0,"cha":0}
    asi_free = 0
    for ab in race.get("ability", []):
        if isinstance(ab, dict):
            for stat, val in ab.items():
                if stat in asi:
                    asi[stat] += val
                elif stat == "choose":
                    asi_free += val if isinstance(val, int) else 1

    langs = []
    for lp in race.get("languageProficiencies", [{}]):
        if isinstance(lp, dict):
            any_std = lp.get("anyStandard", 0)
            if any_std:
                langs.append(f"Any {any_std} Standard")
            for k, v in lp.items():
                if k not in ("anyStandard", "choose") and v is True:
                    langs.append(f"[[{k.title()}]]")

    resistances = race.get("resist", [])
    if isinstance(resistances, str): resistances = [resistances]
    immunities = race.get("immune", [])
    if isinstance(immunities, str): immunities = [immunities]

    has_subraces = bool(race.get("subraces"))
    race_type = race.get("type", "Humanoid")
    lifespan = race.get("age", {})
    avg_lifespan = ""
    if isinstance(lifespan, dict):
        mature = lifespan.get("mature", "")
        max_age = lifespan.get("max", "")
        if mature or max_age:
            avg_lifespan = f"Mature at {mature}, live to ~{max_age}" if mature and max_age else str(max_age or mature)

    entries = race.get("entries", [])
    desc_body = render_entries(entries)
    parent_link = f'"[[{parent}]]"' if parent else ""

    is_2024 = SYSTEM == "dnd5e_2024"
    lore_folder = "Lore/Species" if is_2024 else "Lore/Races"
    primary_tag = "Species" if is_2024 else "Race"
    subrace_label = "Variants" if is_2024 else "Subraces"
    flavour_prompt = "Summarize what makes this species unique." if is_2024 else "Summarize what makes this race or species unique."

    content = f"""---
tags:
  - Race
  - Species
art: "[[PlaceholderRace.png]]"
aliases:
parentRace: {parent_link}
raceType: {yaml_str(race_type)}
size:{yaml_list(sizes)}
speed: {speed}
speedFly: {speed_fly}
speedSwim: {speed_swim}
speedClimb: {speed_climb}
darkvision: {darkvision}
asi_str: {asi['str']}
asi_dex: {asi['dex']}
asi_con: {asi['con']}
asi_int: {asi['int']}
asi_wis: {asi['wis']}
asi_cha: {asi['cha']}
asiFree: {asi_free}
languages:{yaml_list(langs)}
proficiencies: []
resistances:{yaml_list(resistances)}
immunities:{yaml_list(immunities)}
lifespan: {yaml_str(avg_lifespan)}
avgHeight:
avgWeight:
hasSubraces: {str(has_subraces).lower()}
rarity:
source: {yaml_str(source)}
sourcePage: {page}
---

> [!infobox | no-blending black]+ <font color="#ffffff">Infobox</font>
>
> `VIEW[!{{art}}][text(renderMarkdown)]`
>
> # Details
> | | |
> |---|---|
> | **Aliases** | `VIEW[{{aliases}}][text]` |
> | **Type** | `VIEW[{{raceType}}][text]` |
> | **Size** | `VIEW[{{size}}][text]` |
> | **Speed** | `VIEW[{{speed}}]` ft |
> | **Darkvision** | `VIEW[{{darkvision}}]` ft |
> | **Lifespan** | `VIEW[{{lifespan}}][text]` |
> | **Avg. Height** | `VIEW[{{avgHeight}}][text]` |
> | **Avg. Weight** | `VIEW[{{avgWeight}}][text]` |
> | **Rarity** | `VIEW[{{rarity}}][text]` |
> | **Source** | `VIEW[{{source}}][text]` p.`VIEW[{{sourcePage}}]` |
>
> # Ability Scores
> | STR | DEX | CON | INT | WIS | CHA | Free |
> |:---:|:---:|:---:|:---:|:---:|:---:|:---:|
> | +`VIEW[{{asi_str}}]` | +`VIEW[{{asi_dex}}]` | +`VIEW[{{asi_con}}]` | +`VIEW[{{asi_int}}]` | +`VIEW[{{asi_wis}}]` | +`VIEW[{{asi_cha}}]` | +`VIEW[{{asiFree}}]` |

# `=this.file.name`

> *{flavour_prompt}*

## Overview

### Physical Traits

> *What noticeable physical features define this {primary_tag.lower()}?*

### Innate Abilities

| Category | Details |
| -------- | ------- |
| **Proficiencies** | `VIEW[{{proficiencies}}][text]` |
| **Languages** | `VIEW[{{languages}}][link]` |
| **Resistances** | `VIEW[{{resistances}}][text]` |
| **Immunities** | `VIEW[{{immunities}}][text]` |

{desc_body}

### Culture & Society

> *How does this {primary_tag.lower()} typically live or interact with the world?*

### Beliefs

> *What are their common spiritual or cultural beliefs?*

### History

> *Briefly outline this {primary_tag.lower()}'s origin or major historical events.*

## {subrace_label}

```dataview
LIST
FROM "{lore_folder}"
WHERE econtains(tags,"{primary_tag}") AND parentRace = this.file.link
SORT file.name ASC
```

## Notes

"""
    # Disambiguate subraces with parent name
    if parent:
        fname = sanitize_filename(f"{name} ({parent})") + ".md"
    else:
        fname = sanitize_filename(name) + ".md"
    return 1 if write_note(out_dir / fname, content) else 0


# ── Language importer ──────────────────────────────────────────────────────────

def import_languages(source_filter: set) -> int:
    out_dir = VAULT / "Lore/Languages"
    data = fetch_json(f"{BASE_URL}/languages.json")
    if not data:
        return 0
    entries = [l for l in data.get("language", []) if is_wotc(l.get("source", ""), source_filter)]
    count = 0
    for lang in _dedup(entries, lambda l: sanitize_filename(l.get("name", ""))):
        count += _write_language(lang, out_dir)
    return count


def _write_language(lang: dict, out_dir: Path) -> int:
    name = lang.get("name", "Unknown")
    source = lang.get("source", "")
    page = lang.get("page", "")
    lang_type = lang.get("type", "Standard").title()
    script = lang.get("script", "")
    speakers = lang.get("typicalSpeakers", [])
    dialects = lang.get("dialects", [])

    entries = lang.get("entries", [])
    desc_body = render_entries(entries)

    content = f"""---
tags:
  - Language
art: "[[PlaceholderLanguage.png]]"
aliases:
languageType: {yaml_str(lang_type)}
script: {yaml_str(script)}
typicalSpeakers:{yaml_list(speakers)}
rarity:
isPlayable: true
relatedLanguages: []
dialects:{yaml_list(dialects)}
source: {yaml_str(source)}
sourcePage: {page}
---

> [!infobox | no-blending black]+ <font color="#ffffff">Infobox</font>
>
> `VIEW[!{{art}}][text(renderMarkdown)]`
>
> # Details
> | | |
> |---|---|
> | **Aliases** | `VIEW[{{aliases}}][text]` |
> | **Type** | `VIEW[{{languageType}}][text]` |
> | **Script** | `VIEW[{{script}}][text]` |
> | **Rarity** | `VIEW[{{rarity}}][text]` |
> | **Playable** | `VIEW[{{isPlayable}}]` |
> | **Typical Speakers** | `VIEW[{{typicalSpeakers}}][link]` |
> | **Related Languages** | `VIEW[{{relatedLanguages}}][link]` |
> | **Dialects** | `VIEW[{{dialects}}][text]` |

# `=this.file.name`

> *Summarize this language — what kind of beings speak it, where it is found, and what role it plays in the world.*

## Overview

### Sound & Phonology

> *What does this language sound like?*

### Grammar & Structure

> *How does this language work grammatically?*

### Script & Writing

> *How is this language written, if at all?*

{desc_body}

## Sample Phrases

| Common | `=this.file.name` | Pronunciation |
| ------ | ----------------- | ------------- |
| Hello | | |
| Goodbye | | |
| Friend | | |
| Enemy | | |
| Yes | | |
| No | | |
| Help | | |
| Danger | | |

## Distribution & History

### Where It's Spoken

> *In which regions, settlements, or factions is this language commonly spoken?*

### History & Origins

> *Where did this language come from?*

## Notes

"""
    fname = sanitize_filename(name) + ".md"
    return 1 if write_note(out_dir / fname, content) else 0


# ── Deity importer ─────────────────────────────────────────────────────────────

def import_deities(source_filter: set) -> int:
    out_dir = VAULT / "Lore/Deities"
    data = fetch_json(f"{BASE_URL}/deities.json")
    if not data:
        return 0
    entries = [d for d in data.get("deity", []) if is_wotc(d.get("source", ""), source_filter)]
    count = 0
    for deity in _dedup(entries, lambda d: sanitize_filename(d.get("name", ""))):
        count += _write_deity(deity, out_dir)
    return count


def _write_deity(deity: dict, out_dir: Path) -> int:
    name = deity.get("name", "Unknown")
    source = deity.get("source", "")
    page = deity.get("page", "")
    alignment = " ".join(deity.get("alignment", [])) if deity.get("alignment") else ""
    pantheon = deity.get("pantheon", "")
    domains = deity.get("domains", [])
    symbol = deity.get("symbol", "")
    title = deity.get("title", "")
    plane = deity.get("plane", "")
    aliases = [title] if title else []

    desc_parts = []
    for entry in deity.get("entries", []):
        if isinstance(entry, str):
            desc_parts.append(convert_tags(entry))
        elif isinstance(entry, dict):
            desc_parts.append(render_entries([entry]))

    content = f"""---
tags:
  - Character
  - NPC
  - Deity
art: "[[PlaceholderDeity.png]]"
sketch:
aliases:{yaml_list(aliases)}
pronouns:
deityPower:
alignment: {yaml_str(alignment)}
domain:{yaml_list(domains)}
clericDomains:{yaml_list(domains)}
favoredWeapon:
holySymbol: {yaml_str(symbol)}
holyDay:
homeplane: {yaml_str(plane)}
languages:
  - "[[Common]]"
organizations:
  - {yaml_str(pantheon)}
worshippers: []
alliedDeities: []
enemyDeities: []
condition:
  - Active
currentLocation: []
whichParty: []
party1Relation:
source: {yaml_str(source)}
sourcePage: {page}
---

> [!infobox | no-blending black]+ <font color="#ffffff">Infobox</font>
>
> `VIEW[!{{art}}][text(renderMarkdown)]`
>
> # Bio
> | |
> |---|---|
> | **Aliases** | `VIEW[{{aliases}}][text]` |
> | **Pronouns** | `VIEW[{{pronouns}}][text]` |
> | **Power** | `VIEW[{{deityPower}}][text]` |
> | **Alignment** | `VIEW[{{alignment}}][text]` |
> | **Holy Symbol** | `VIEW[{{holySymbol}}][text]` |
> | **Holy Day** | `VIEW[{{holyDay}}][text]` |
> | **Favored Weapon** | `VIEW[{{favoredWeapon}}][link]` |
> | **Home Plane** | `VIEW[{{homeplane}}][link]` |
>
> # Divine Info
> | |
> |---|---|
> | **Domain** | `VIEW[{{domain}}][text]` |
> | **Cleric Domains** | `VIEW[{{clericDomains}}][text]` |
> | **Organizations** | `VIEW[{{organizations}}][link]` |
> | **Worshippers** | `VIEW[{{worshippers}}][link]` |
> | **Allied Deities** | `VIEW[{{alliedDeities}}][link]` |
> | **Enemy Deities** | `VIEW[{{enemyDeities}}][link]` |
> | **Condition** | `VIEW[{{condition}}]` |
> | **Location** | `VIEW[{{currentLocation}}][link]` |

# `=this.file.name`

> *Summarize who this Deity is, highlighting their divine portfolio, personality, and significance in the cosmology.*

## Overview

### Description

{chr(10).join(desc_parts)}

### Personality & Mannerisms

> *Describe the Deity's personality and how they interact with mortals.*

### Motivations

> *Describe what drives this Deity.*

## Worship

### Clergy & Hierarchy

> *How is the church or following structured?*

### Rites & Ceremonies

> *What rituals, holy days, and ceremonies do worshippers observe?*

### Temples & Sacred Sites

> *Where are the major temples or holy sites dedicated to this deity?*

## Past

### History

> *Describe an important event from this Deity's past.*

## Notes

"""
    fname = sanitize_filename(name) + ".md"
    return 1 if write_note(out_dir / fname, content) else 0


# ── Feat importer ──────────────────────────────────────────────────────────────

def import_feats(source_filter: set) -> int:
    out_dir = VAULT / "Lore/Feats"
    data = fetch_json(f"{BASE_URL}/feats.json")
    if not data:
        return 0
    entries = [f for f in data.get("feat", []) if is_wotc(f.get("source", ""), source_filter)]
    count = 0
    for feat in _dedup(entries, lambda f: sanitize_filename(f.get("name", ""))):
        count += _write_feat(feat, out_dir)
    return count


def _write_feat(feat: dict, out_dir: Path) -> int:
    name = feat.get("name", "Unknown")
    source = feat.get("source", "")
    page = feat.get("page", "")

    category_map = {
        "G": "General", "O": "Origin", "D": "Dragonmark",
        "FS:F": "Fighting Style", "FS:P": "Fighting Style",
        "FS:R": "Fighting Style", "FS:B": "Fighting Style", "FS:W": "Fighting Style",
    }
    category = category_map.get(feat.get("category", "G"), feat.get("category", "General"))

    prereq_str = format_prerequisite(feat.get("prerequisite", []))
    asi = format_ability_asi(feat.get("ability", []))
    repeatable = bool(feat.get("repeatable", False))

    entries = feat.get("entries", [])
    desc_body = render_entries(entries)

    content = f"""---
tags:
  - Feat
art: "[[PlaceholderFeat.png]]"
aliases:
category: {yaml_str(category)}
prerequisite: {yaml_str(prereq_str)}
abilityScoreIncrease: {yaml_str(asi)}
repeatable: {str(repeatable).lower()}
source: {yaml_str(source)}
sourcePage: {page}
isHomebrew: false
---

> [!infobox | no-blending black]+ <font color="#ffffff">Infobox</font>
>
> `VIEW[!{{art}}][text(renderMarkdown)]`
>
> # Details
> | | |
> |---|---|
> | **Aliases** | `VIEW[{{aliases}}][text]` |
> | **Category** | `VIEW[{{category}}][text]` |
> | **Prerequisite** | `VIEW[{{prerequisite}}][text]` |
> | **Ability Score** | `VIEW[{{abilityScoreIncrease}}][text]` |
> | **Repeatable** | `VIEW[{{repeatable}}]` |
> | **Source** | `VIEW[{{source}}][text]` p.`VIEW[{{sourcePage}}]` |

# `=this.file.name`

> *Summarize what this feat does and what type of character it suits.*

## Description

{desc_body}

## Notes

"""
    fname = sanitize_filename(name) + ".md"
    return 1 if write_note(out_dir / fname, content) else 0


# ── Condition importer ─────────────────────────────────────────────────────────

def import_conditions(source_filter: set) -> int:
    out_dir = VAULT / "Lore/Conditions"
    data = fetch_json(f"{BASE_URL}/conditionsdiseases.json")
    if not data:
        return 0
    all_conds = data.get("condition", []) + data.get("disease", []) + data.get("status", [])
    entries = [c for c in all_conds if is_wotc(c.get("source", ""), source_filter)]
    count = 0
    for cond in _dedup(entries, lambda c: sanitize_filename(c.get("name", ""))):
        count += _write_condition(cond, out_dir)
    return count


def _write_condition(cond: dict, out_dir: Path) -> int:
    name = cond.get("name", "Unknown")
    source = cond.get("source", "")
    page = cond.get("page", "")

    entries = cond.get("entries", [])
    effects_body = render_entries(entries)

    content = f"""---
tags:
  - Condition
aliases:
source: {yaml_str(source)}
sourcePage: {page}
---

> [!infobox | no-blending black]+ <font color="#ffffff">Infobox</font>
>
> # Details
> | | |
> |---|---|
> | **Aliases** | `VIEW[{{aliases}}][text]` |
> | **Source** | `VIEW[{{source}}][text]` p.`VIEW[{{sourcePage}}]` |

# `=this.file.name`

> *Summarize what this condition represents and when it is typically applied.*

## Effects

{effects_body}

## Notes

"""
    fname = sanitize_filename(name) + ".md"
    return 1 if write_note(out_dir / fname, content) else 0


# ── Optional Feature importer ──────────────────────────────────────────────────

def import_optional_features(source_filter: set) -> int:
    out_dir = VAULT / "Lore/Optional Features"
    data = fetch_json(f"{BASE_URL}/optionalfeatures.json")
    if not data:
        return 0
    entries = [f for f in data.get("optionalfeature", []) if is_wotc(f.get("source", ""), source_filter)]
    count = 0
    for feat in _dedup(entries, lambda f: sanitize_filename(f.get("name", ""))):
        count += _write_optional_feature(feat, out_dir)
    return count


def _write_optional_feature(feat: dict, out_dir: Path) -> int:
    name = feat.get("name", "Unknown")
    source = feat.get("source", "")
    page = feat.get("page", "")

    feat_types = feat.get("featureType", [])
    feat_type_str = ", ".join(OPTIONAL_FEATURE_TYPE_MAP.get(ft, ft) for ft in feat_types)

    # Infer parent class from feature type
    class_map = {
        "EI": "[[Warlock]]", "PB": "[[Warlock]]",
        "MM": "[[Sorcerer]]",
        "MV": "[[Fighter]]", "MV:B": "[[Fighter]]", "MV:C2-UA": "[[Fighter]]",
        "AI": "[[Artificer]]",
        "AS": "[[Fighter]]",
        "ED": "[[Monk]]",
        "FS:F": "[[Fighter]]", "FS:B": "[[Bard]]", "FS:P": "[[Paladin]]",
        "FS:R": "[[Ranger]]", "FS:W": "[[Fighter]]", "FS": "[[Fighter]]",
        "TD": "[[Barbarian]]",
        "OR": "[[Wizard]]",
    }
    parent_classes = list({class_map[ft] for ft in feat_types if ft in class_map})

    prereq_str = format_prerequisite(feat.get("prerequisite", []))
    entries = feat.get("entries", [])
    desc_body = render_entries(entries)

    content = f"""---
tags:
  - OptionalFeature
aliases:
featureType: {yaml_str(feat_type_str)}
parentClass:{yaml_list(parent_classes)}
prerequisite: {yaml_str(prereq_str)}
source: {yaml_str(source)}
sourcePage: {page}
isHomebrew: false
---

> [!infobox | no-blending black]+ <font color="#ffffff">Infobox</font>
>
> # Details
> | | |
> |---|---|
> | **Aliases** | `VIEW[{{aliases}}][text]` |
> | **Type** | `VIEW[{{featureType}}][text]` |
> | **Class** | `VIEW[{{parentClass}}][link]` |
> | **Prerequisite** | `VIEW[{{prerequisite}}][text]` |
> | **Source** | `VIEW[{{source}}][text]` p.`VIEW[{{sourcePage}}]` |

# `=this.file.name`

> *Summarize what this optional feature does and which class it belongs to.*

## Description

{desc_body}

## Notes

"""
    fname = sanitize_filename(name) + ".md"
    return 1 if write_note(out_dir / fname, content) else 0


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Import 5e.tools data into Obsidian vault")
    parser.add_argument("--system", dest="system", default="dnd5e",
                        choices=["dnd5e", "dnd5e_2024"],
                        help="D&D edition: dnd5e (2014 PHB) or dnd5e_2024 (2024 XPHB)")
    parser.add_argument("--all", dest="all_sources", action="store_true",
                        help="Include all sources (not just WotC)")
    parser.add_argument("--book", dest="book_filter", default=None, nargs="+",
                        help="Import only from these specific source codes (e.g. --book PHB XGE TCE)")
    parser.add_argument("--type", dest="content_types", default=None,
                        nargs="+", choices=CONTENT_TYPES,
                        help="Import only these content types (space-separated, e.g. --type spells feats)")
    parser.add_argument("--vault", dest="vault_path", default=None,
                        help="Absolute path to the Obsidian vault (overrides the hardcoded VAULT path)")
    args = parser.parse_args()

    global VAULT, SYSTEM
    if args.vault_path:
        VAULT = Path(args.vault_path)

    SYSTEM = args.system
    edition_types = CONTENT_TYPES_5E_2024 if SYSTEM == "dnd5e_2024" else CONTENT_TYPES_5E_2014
    edition_label = "D&D 5.5e (2024)" if SYSTEM == "dnd5e_2024" else "D&D 5e (2014)"
    print(f"Edition: {edition_label}")

    if args.book_filter:
        source_filter = set(args.book_filter)
        print(f"Source filter: specific books — {', '.join(sorted(source_filter))}")
    elif args.all_sources:
        source_filter = None
        print(f"Source filter: ALL sources")
    elif SYSTEM == "dnd5e_2024":
        source_filter = SOURCES_5E_2024
        print(f"Source filter: 2024 core books ({', '.join(sorted(SOURCES_5E_2024))})")
    else:
        source_filter = SOURCES_5E_2014
        print(f"Source filter: 2014 WotC books ({len(SOURCES_5E_2014)} source codes)")
    print()

    totals = {}

    def run(label, fn):
        # Skip types not applicable to this edition
        if label not in edition_types:
            return
        if args.content_types and label not in args.content_types:
            return
        print(f"Importing {label}...", end=" ", flush=True)
        result = fn(source_filter)
        if isinstance(result, tuple):
            class_count, sub_count = result
            totals[label] = class_count
            totals["subclasses"] = sub_count
            print(f"{class_count} classes, {sub_count} subclasses")
        else:
            totals[label] = result
            print(f"{result} notes")

    run("spells", import_spells)
    run("items", import_items)
    run("backgrounds", import_backgrounds)
    run("classes", import_classes)
    run("classfeatures", import_class_features)
    run("races", import_races)
    run("racialtraits", import_racial_traits)
    run("backgroundfeatures", import_background_features)
    run("languages", import_languages)
    run("deities", import_deities)
    run("feats", import_feats)
    run("conditions", import_conditions)
    run("optionalfeatures", import_optional_features)

    total = sum(totals.values())
    print(f"\nWrote {total} notes total:")
    for k, v in totals.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
