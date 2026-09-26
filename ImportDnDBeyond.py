#!/usr/bin/env python3
"""
D&D Beyond character importer for the LBG TTRPG Player Template.
Called by ImportDnDBeyond.js — args: <vault_path> <char_id> <campaign_name> [cobalt_token]
Writes the character note to My Character/ (this vault has no party system).
Prints a single JSON object to stdout on completion.
"""

import sys, os, json, re, argparse, urllib.request, urllib.error
from collections import defaultdict
from datetime import datetime

# Force UTF-8 output on Windows (default console encoding is often cp1252)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Constants ──────────────────────────────────────────────────────────────────

API_URL = "https://character-service.dndbeyond.com/character/v5/character/{id}"

STAT_IDS = {1: "str", 2: "dex", 3: "con", 4: "int", 5: "wis", 6: "cha"}

XP_THRESHOLDS = [0,300,900,2700,6500,14000,23000,34000,48000,
                 64000,85000,100000,120000,140000,165000,195000,
                 225000,265000,305000,355000]

ALIGNMENTS = {
    1:"Lawful Good",2:"Neutral Good",3:"Chaotic Good",
    4:"Lawful Neutral",5:"True Neutral",6:"Chaotic Neutral",
    7:"Lawful Evil",8:"Neutral Evil",9:"Chaotic Evil",
}

SPELLCASTER_ABILITIES = {
    "Artificer":"int","Wizard":"int",
    "Cleric":"wis","Druid":"wis","Ranger":"wis",
    "Bard":"cha","Paladin":"cha","Sorcerer":"cha","Warlock":"cha",
}

CLASS_HIT_DICE = {
    "Barbarian":"d12",
    "Fighter":"d10","Paladin":"d10","Ranger":"d10",
    "Artificer":"d8","Bard":"d8","Cleric":"d8",
    "Druid":"d8","Monk":"d8","Rogue":"d8","Warlock":"d8",
    "Sorcerer":"d6","Wizard":"d6",
}

SKILL_SUBTYPES = {
    "acrobatics":"Acrobatics (DEX)","animal-handling":"Animal Handling (WIS)",
    "arcana":"Arcana (INT)","athletics":"Athletics (STR)",
    "deception":"Deception (CHA)","history":"History (INT)",
    "insight":"Insight (WIS)","intimidation":"Intimidation (CHA)",
    "investigation":"Investigation (INT)","medicine":"Medicine (WIS)",
    "nature":"Nature (INT)","perception":"Perception (WIS)",
    "performance":"Performance (CHA)","persuasion":"Persuasion (CHA)",
    "religion":"Religion (INT)","sleight-of-hand":"Sleight of Hand (DEX)",
    "stealth":"Stealth (DEX)","survival":"Survival (WIS)",
}

SKILL_ABILITY = {
    "acrobatics":"dex","animal-handling":"wis","arcana":"int",
    "athletics":"str","deception":"cha","history":"int",
    "insight":"wis","intimidation":"cha","investigation":"int",
    "medicine":"wis","nature":"int","perception":"wis",
    "performance":"cha","persuasion":"cha","religion":"int",
    "sleight-of-hand":"dex","stealth":"dex","survival":"wis",
}

LANGUAGE_NAMES = {
    "common":"Common","elvish":"Elvish","dwarvish":"Dwarvish",
    "giant":"Giant","gnomish":"Gnomish","goblin":"Goblin",
    "halfling":"Halfling","orc":"Orc","abyssal":"Abyssal",
    "celestial":"Celestial","draconic":"Draconic",
    "deep-speech":"Deep Speech","infernal":"Infernal",
    "primordial":"Primordial","sylvan":"Sylvan",
    "undercommon":"Undercommon","druidic":"Druidic",
    "thieves-cant":"Thieves' Cant",
}

ARMOR_PROFS = {
    "light-armor":"Light Armor","medium-armor":"Medium Armor",
    "heavy-armor":"Heavy Armor","shields":"Shields",
}

WEAPON_PROFS = {
    "simple-weapons":"Simple Weapons","martial-weapons":"Martial Weapons",
}

SAVE_SUBTYPES = {
    "strength-saving-throws":"STR","dexterity-saving-throws":"DEX",
    "constitution-saving-throws":"CON","intelligence-saving-throws":"INT",
    "wisdom-saving-throws":"WIS","charisma-saving-throws":"CHA",
}

SPELL_LEVEL_NAMES = {
    0:"Cantrips",1:"1st Level",2:"2nd Level",3:"3rd Level",
    4:"4th Level",5:"5th Level",6:"6th Level",7:"7th Level",
    8:"8th Level",9:"9th Level",
}

# DDB item names that differ from 5e.tools vault note names
ITEM_NAME_MAP = {
    # ── Armor (DDB omits "Armor" suffix) ──────────────────────────────────
    "Leather":       "Leather Armor",
    "Padded":        "Padded Armor",
    "Hide":          "Hide Armor",
    "Splint":        "Splint Armor",
    "Plate":         "Plate Armor",
    "Half Plate":    "Half Plate Armor",
    "Chain Shirt":   "Chain Shirt",   # same, listed for completeness
    "Scale Mail":    "Scale Mail",
    "Breastplate":   "Breastplate",
    # ── Crossbows (DDB uses "Crossbow, X" format) ─────────────────────────
    "Crossbow, Light":  "Light Crossbow",
    "Crossbow, Hand":   "Hand Crossbow",
    "Crossbow, Heavy":  "Heavy Crossbow",
    # ── Clothes (DDB uses "Clothes, X" format) ────────────────────────────
    "Clothes, Fine":          "Fine Clothes",
    "Clothes, Common":        "Common Clothes",
    "Clothes, Costume":       "Costume Clothes",
    "Clothes, Traveler’s":    "Traveler’s Clothes",
    "Common Clothes with Hood": "Common Clothes",
    "Dark Common Clothes":    "Common Clothes",
    # ── Saddles (DDB uses "Saddle, X" format) ────────────────────────────
    "Saddle, Riding":   "Riding Saddle",
    "Saddle, Pack":     "Pack Saddle",
    "Saddle, Exotic":   "Exotic Saddle",
    "Saddle, Military": "Military Saddle",
    # ── Lanterns (DDB uses "Lantern, X" format) ───────────────────────────
    "Lantern, Bullseye": "Bullseye Lantern",
    "Lantern, Hooded":   "Hooded Lantern",
    # ── Gear (name restructured) ───────────────────────────────────────────
    "Case, Map or Scroll":       "Map or Scroll Case",
    "Ink (1 ounce bottle)":      "Ink (1-ounce bottle)",
    "Ink (1-ounce bottle)":      "Ink (1-ounce bottle)",
    "Mirror, Steel":             "Steel Mirror",
    "Lock":                      "Lock",
    "Flask, Oil":                "Oil (flask)",
    "Oil Flask":                 "Oil (flask)",
    "Torch (10)":                "Torch",
    "Rations, 1 day":            "Rations (1 day)",
    "Rations (1 day)":           "Rations (1 day)",
    "Bedroll":                   "Bedroll",
    "Blanket, Winter":           "Blanket",
    "Winter Blanket":            "Blanket",
    "Ball Bearings (bag of 1,000)": "Ball Bearings (bag of 1,000)",
    "Playing Card Set":          "Playing Card Set",
    "Dice Set":                  "Dice Set",
    "Bone Dice":                 "Dice Set",
    "Prayer Book":               "Book",
    "Holy Symbol (Silver)":      "Holy Symbol",
    "Holy Symbol (Wooden)":      "Holy Symbol",
    "Holy Symbol (Amulet)":      "Holy Symbol",
    "Holy Symbol (Emblem)":      "Holy Symbol",
    "Holy Symbol (Reliquary)":   "Holy Symbol",
    "Arcane Focus (Crystal)":    "Arcane Focus",
    "Arcane Focus (Orb)":        "Arcane Focus",
    "Arcane Focus (Rod)":        "Arcane Focus",
    "Arcane Focus (Staff)":      "Arcane Focus",
    "Arcane Focus (Wand)":       "Arcane Focus",
    "Druidic Focus (Sprig of Mistletoe)": "Druidic Focus",
    "Druidic Focus (Totem)":     "Druidic Focus",
    "Druidic Focus (Wooden Staff)": "Druidic Focus",
    "Druidic Focus (Yew Wand)":  "Druidic Focus",
    # ── Potions (DDB appends parenthetical, 5e.tools inlines adjective) ───
    "Potion of Healing (Greater)":  "Potion of Greater Healing",
    "Potion of Healing (Superior)": "Potion of Superior Healing",
    "Potion of Healing (Supreme)":  "Potion of Supreme Healing",
    # ── Rope (DDB uses "Rope, Type (length)" format) ──────────────────────
    "Rope, Hempen (50 feet)": "Hempen Rope (50 feet)",
    "Rope, Silk (50 feet)":   "Silk Rope (50 feet)",
    "Rope (Hempen)":          "Hempen Rope (50 feet)",
    "Rope (Silk)":            "Silk Rope (50 feet)",
    # ── Background flavor items DDB includes verbatim ─────────────────────
    # These map to nearest real item with a vault note
    "Small Knife":                   "Dagger",
    "Little Bag of Sand":            "Pouch",
    "Map of the City":               "Parchment (one sheet)",
    "Scroll of Pedigree":            "Parchment (one sheet)",
    "Letter from Dead Colleague":    "Parchment (one sheet)",
    "Letter of Introduction":        "Parchment (one sheet)",
    "Signet Ring":                   "Signet Ring",
    "Shovel":                        "Shovel",
    "Iron Pot":                      "Iron Pot",
    "Fishing Tackle":                "Fishing Tackle",
}

# DDB race/subrace names → 5e.tools vault note names.
# Most subraces: DDB uses "Modifier Race", vault uses "Modifier (Race)".
# Dragonborn exception: DDB uses "Modifier Dragonborn", vault uses "Dragonborn (Modifier)".
RACE_NAME_MAP = {
    # ── Elf subraces ──────────────────────────────────────────────────────
    "High Elf":             "High (Elf)",
    "Wood Elf":             "Wood (Elf)",
    "Dark Elf":             "Drow (Elf)",
    "Drow":                 "Drow (Elf)",
    "Drow Elf":             "Drow (Elf)",
    "Sea Elf":              "Sea (Elf)",
    "Eladrin":              "Eladrin (Elf)",
    "Pallid Elf":           "Pallid (Elf)",
    "Shadar-kai":           "Shadar-kai (Elf)",
    "Shadar-kai Elf":       "Shadar-kai (Elf)",
    "Astral Elf":           "Astral Elf",            # standalone note in vault
    "Mark of Shadow Elf":   "Mark of Shadow (Elf)",
    # ── Dwarf subraces ────────────────────────────────────────────────────
    "Hill Dwarf":               "Hill (Dwarf)",
    "Mountain Dwarf":           "Mountain (Dwarf)",
    "Duergar":                  "Duergar (Dwarf)",
    "Duergar Dwarf":            "Duergar (Dwarf)",
    "Mark of Warding Dwarf":    "Mark of Warding (Dwarf)",
    # ── Halfling subraces ─────────────────────────────────────────────────
    "Lightfoot Halfling":         "Lightfoot (Halfling)",
    "Stout Halfling":             "Stout (Halfling)",
    "Ghostwise Halfling":         "Ghostwise (Halfling)",
    "Lotusden Halfling":          "Lotusden (Halfling)",
    "Mark of Healing Halfling":   "Mark of Healing (Halfling)",
    "Mark of Hospitality Halfling": "Mark of Hospitality (Halfling)",
    # ── Gnome subraces ────────────────────────────────────────────────────
    "Forest Gnome":             "Forest (Gnome)",
    "Rock Gnome":               "Rock (Gnome)",
    "Deep Gnome":               "Deep (Gnome)",
    "Svirfneblin":              "Deep (Gnome)",
    "Mark of Scribing Gnome":   "Mark of Scribing (Gnome)",
    # ── Tiefling subraces ─────────────────────────────────────────────────
    "Asmodeus Tiefling":       "Asmodeus (Tiefling)",
    "Baalzebul Tiefling":      "Baalzebul (Tiefling)",
    "Dispater Tiefling":       "Dispater (Tiefling)",
    "Fierna Tiefling":         "Fierna (Tiefling)",
    "Glasya Tiefling":         "Glasya (Tiefling)",
    "Levistus Tiefling":       "Levistus (Tiefling)",
    "Mammon Tiefling":         "Mammon (Tiefling)",
    "Mephistopheles Tiefling": "Mephistopheles (Tiefling)",
    "Zariel Tiefling":         "Zariel (Tiefling)",
    # ── Aasimar subraces ──────────────────────────────────────────────────
    "Fallen Aasimar":    "Fallen (Aasimar)",
    "Protector Aasimar": "Protector (Aasimar)",
    "Scourge Aasimar":   "Scourge (Aasimar)",
    # ── Genasi subraces ───────────────────────────────────────────────────
    "Air Genasi":   "Air (Genasi)",
    "Earth Genasi": "Earth (Genasi)",
    "Fire Genasi":  "Fire (Genasi)",
    "Water Genasi": "Water (Genasi)",
    # ── Shifter subraces ──────────────────────────────────────────────────
    "Beasthide Shifter":   "Beasthide (Shifter)",
    "Longtooth Shifter":   "Longtooth (Shifter)",
    "Swiftstride Shifter": "Swiftstride (Shifter)",
    "Wildhunt Shifter":    "Wildhunt (Shifter)",
    # ── Dragonborn variants (DDB: "X Dragonborn" → vault: "Dragonborn (X)") ──
    "Gem Dragonborn":         "Dragonborn (Gem)",
    "Chromatic Dragonborn":   "Dragonborn (Chromatic)",
    "Metallic Dragonborn":    "Dragonborn (Metallic)",
    "Draconblood Dragonborn": "Draconblood (Dragonborn)",
    "Ravenite Dragonborn":    "Ravenite (Dragonborn)",
    # ── Human variants ────────────────────────────────────────────────────
    "Variant Human":          "Variant (Human)",
    "Mark of Finding Human":  "Variant; Mark of Finding (Human)",
    "Mark of Handling Human": "Mark of Handling (Human)",
    "Mark of Making Human":   "Mark of Making (Human)",
    "Mark of Passage Human":  "Mark of Passage (Human)",
    "Mark of Sentinel Human": "Mark of Sentinel (Human)",
    # ── Half-Elf variants ─────────────────────────────────────────────────
    "Mark of Detection Half-Elf": "Variant; Mark of Detection (Half-Elf)",
    "Mark of Storm Half-Elf":     "Variant; Mark of Storm (Half-Elf)",
    # ── Half-Orc variants ─────────────────────────────────────────────────
    "Mark of Finding Half-Orc":   "Variant; Mark of Finding (Half-Orc)",
}

# DDB background names → vault note names (DDB sometimes uses the variant short-name)
BACKGROUND_NAME_MAP = {
    "Knight":              "Variant Noble (Knight)",
    "Spy":                 "Variant Criminal (Spy)",
    "Criminal / Spy":      "Variant Criminal (Spy)",
    "Gladiator":           "Variant Entertainer (Gladiator)",
    "Pirate":              "Variant Sailor (Pirate)",
    "Guild Merchant":      "Variant Guild Artisan (Guild Merchant)",
    "Investigator":        "Variant City Watch (Investigator)",
    "Sage (Cobalt Scholar)": "Cobalt Scholar (Sage)",
}

# DDB-generated class-feature entries that have no 5e.tools equivalents — skip linking these
DDB_SYNTHETIC = {
    "Hit Points", "Proficiencies", "Equipment", "Expanded Spell List",
    "Starting Equipment",
}

# DDB racial trait names → vault note names (plural/variant normalisation)
TRAIT_NAME_MAP = {
    "Ability Score Increases": "Ability Score Increase",
}

# Races whose subraces follow "Modifier Race" → "Modifier (Race)" pattern in the vault.
# Used as a programmatic fallback when a name isn't in RACE_NAME_MAP.
_PARENTHETICAL_PARENTS = frozenset([
    "Elf", "Dwarf", "Halfling", "Gnome", "Tiefling", "Aasimar",
    "Genasi", "Shifter", "Half-Elf", "Half-Orc", "Human",
])

# ── Filename / link helpers ───────────────────────────────────────────────────

def _sanitize_link(name: str) -> str:
    """Replace characters illegal in filenames so a wikilink target matches the vault note."""
    name = re.sub(r'[/\\:*?"<>|]', "-", name)
    name = re.sub(r'\s+', " ", name).strip()
    return name


# ── Name-resolution helpers ────────────────────────────────────────────────────

def _resolve_race_name(raw: str) -> str:
    """Map a DDB race/subrace fullName to the vault note name."""
    if raw in RACE_NAME_MAP:
        return RACE_NAME_MAP[raw]
    # Programmatic fallback: "Modifier Race" → "Modifier (Race)"
    for parent in _PARENTHETICAL_PARENTS:
        if raw.endswith(f" {parent}") and raw != parent:
            modifier = raw[: -(len(parent) + 1)]
            return f"{modifier} ({parent})"
    return raw


def _resolve_item_name(raw: str) -> str:
    """Map a DDB item name to the vault note name."""
    if raw in ITEM_NAME_MAP:
        return ITEM_NAME_MAP[raw]
    # "Item Name, +N" → "+N Item Name" (e.g. "Dagger, +2" → "+2 Dagger")
    m = re.match(r'^(.+),\s*(\+\d+)$', raw)
    if m:
        return f"{m.group(2)} {m.group(1)}"
    return raw


def _item_link(raw_name: str, vault_path: str) -> str:
    """Return a path-qualified wiki link (table-safe) if the vault has a note for this
    item; otherwise plain text."""
    resolved = _resolve_item_name(raw_name)
    safe = _sanitize_link(resolved)
    if os.path.exists(os.path.join(vault_path, "Possessions", "Items", f"{safe}.md")):
        return f"[[Possessions/Items/{safe}\\|{resolved}]]"
    return resolved


def _build_lore_index(vault_path: str) -> dict:
    """Scan Lore folders and build a case-insensitive name → actual filename lookup.

    Used by _lore_link to fuzzy-match DDB names against whatever notes exist in
    the vault, so mismatched capitalisation or word order doesn't produce broken links.
    """
    lore_dirs = {
        "classes":     os.path.join(vault_path, "Lore", "Classes"),
        "subclasses":  os.path.join(vault_path, "Lore", "Classes", "Subclasses"),
        "backgrounds": os.path.join(vault_path, "Lore", "Backgrounds"),
        "races":       os.path.join(vault_path, "Lore", "Races"),
        "species":     os.path.join(vault_path, "Lore", "Species"),
    }
    index: dict = {}
    for key, d in lore_dirs.items():
        mapping: dict = {}
        if os.path.isdir(d):
            for fname in os.listdir(d):
                if fname.endswith(".md"):
                    basename = fname[:-3]
                    mapping[basename.lower()] = basename
        index[key] = mapping
    return index


def _lore_exists(name: str, folder_key: str, lore_index: dict) -> bool:
    """Return True if _lore_link would find a real file (not just a fallback link)."""
    if not name:
        return False
    idx = lore_index.get(folder_key, {})
    key = name.lower()
    if name in idx.values():
        return True
    if key in idx:
        return True
    norm = re.sub(r"['''\-/]", " ", key)
    norm = re.sub(r"\s+", " ", norm).strip()
    for k in idx:
        k_norm = re.sub(r"['''\-/]", " ", k)
        k_norm = re.sub(r"\s+", " ", k_norm).strip()
        if norm == k_norm:
            return True
    for k in idx:
        if k.startswith(key) or key.startswith(k):
            return True
    return False


def _lore_link(name: str, folder_key: str, lore_index: dict, display: str = "") -> str:
    """Return '[[ActualFile|display]]' for a lore note, fuzzy-matching against the vault.

    Resolution order:
      1. Exact filename match
      2. Case-insensitive exact match
      3. Normalised match (collapse whitespace, strip punctuation differences)
      4. Prefix match (file starts with name or vice-versa)
      5. No match — return [[name]] so it shows as an unresolved link rather than plain text
    """
    if not name:
        return ""
    display = display or name
    idx = lore_index.get(folder_key, {})

    def _make_link(actual: str) -> str:
        return f"[[{actual}|{display}]]" if actual != display else f"[[{actual}]]"

    # 1. Exact
    if name in idx.values():
        return _make_link(name)
    # 2. Case-insensitive
    key = name.lower()
    if key in idx:
        return _make_link(idx[key])
    # 3. Normalised (collapse whitespace, remove common punctuation variations)
    norm = re.sub(r"['''\-/]", " ", key)
    norm = re.sub(r"\s+", " ", norm).strip()
    for k, v in idx.items():
        k_norm = re.sub(r"['''\-/]", " ", k)
        k_norm = re.sub(r"\s+", " ", k_norm).strip()
        if norm == k_norm:
            return _make_link(v)
    # 4. Prefix match
    for k, v in idx.items():
        if k.startswith(key) or key.startswith(k):
            return _make_link(v)
    # 5. Fallback — unresolved wikilink (visible in vault, user can fix)
    return f"[[{name}|{display}]]" if display != name else f"[[{name}]]"


# ── Helpers ────────────────────────────────────────────────────────────────────

def mod(score): return (score - 10) // 2
def prof_bonus(level): return 2 + (level - 1) // 4

def get_stat(lst, sid):
    for s in lst:
        if s.get("id") == sid: return s.get("value") or 0
    return 0

ABILITY_FULL = {"str": "strength", "dex": "dexterity", "con": "constitution",
                "int": "intelligence", "wis": "wisdom", "cha": "charisma"}

def _mod_value(m):
    return m.get("value") or m.get("fixedValue") or 0

def all_modifiers(data):
    """Modifiers that currently apply. Item modifiers only count while the item is
    equipped (and attuned, if it requires attunement)."""
    inv = {}
    for it in data.get("inventory") or []:
        inv[(it.get("definition") or {}).get("id")] = it
    result = []
    for grp, lst in (data.get("modifiers") or {}).items():
        if not isinstance(lst, list): continue
        for m in lst:
            if grp == "item":
                it = inv.get(m.get("componentId"))
                if not it or not it.get("equipped"): continue
                if (it.get("definition") or {}).get("canAttune") and not it.get("isAttuned"): continue
            result.append(m)
    return result

def calc_score(base, bonus, override, sid, mods=(), key=""):
    """Final ability score: override, else base + manual bonus + feat/race/item bonuses,
    raised to any 'set' modifier (e.g. Belt of Giant Strength)."""
    ov = get_stat(override, sid)
    if ov: return ov
    sub = f"{ABILITY_FULL.get(key, '')}-score"
    total = (get_stat(base, sid) or 0) + (get_stat(bonus, sid) or 0)
    total += sum(_mod_value(m) for m in mods if m.get("type") == "bonus" and m.get("subType") == sub)
    for m in mods:
        if m.get("type") == "set" and m.get("subType") == sub:
            total = max(total, _mod_value(m))
    return total

_SOURCE_TAG_RE = re.compile(r"\s*\([A-Z][A-Za-z0-9]{1,7}\)$")

def _clean_subclass_name(name: str) -> str:
    """'Tempest Domain (PHB)' -> 'Tempest Domain' (vault notes are '<Sub> (<Class>)')."""
    return _SOURCE_TAG_RE.sub("", name).strip()

_BOOKKEEPING_FEAT_RE = re.compile(r"^Increase (one|two|three) |.+ Ability Score Improvements$", re.I)

def _note_link(name: str, rel_dirs, vault_path: str, display: str = "", in_table: bool = False) -> str:
    """Path-qualified wikilink when a matching note exists (several vault notes share
    basenames across Spells/Items/Feats/Traits, so bare [[Name]] links can resolve wrongly).
    Falls back to a bare link so unresolved names stay visible."""
    safe = _sanitize_link(name)
    display = display or name
    bar = "\\|" if in_table else "|"
    for rel in rel_dirs:
        if os.path.exists(os.path.join(vault_path, *rel.split("/"), f"{safe}.md")):
            return f"[[{rel}/{safe}{bar}{display}]]"
    return f"[[{safe}{bar}{display}]]" if safe != display else f"[[{safe}]]"

def fetch(char_id):
    req = urllib.request.Request(API_URL.format(id=char_id))
    req.add_header("User-Agent", "Mozilla/5.0 TTRPG-Vault-Importer/1.0")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

def download_image(url, dest_path):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0 TTRPG-Vault-Importer/1.0")
    with urllib.request.urlopen(req, timeout=15) as r:
        with open(dest_path, "wb") as f:
            f.write(r.read())

# ── Update-in-place merge ──────────────────────────────────────────────────────
# `--update` re-fetches the character and merges it into the existing note:
# D&D Beyond-derived fields/sections are refreshed; everything the player wrote
# (personality, goals, backstory, notes, session history, location, conditions…)
# is left alone.

# Frontmatter keys D&D Beyond always owns
FM_MANAGED = ["species", "class", "subclass", "background", "languages", "level",
              "experience", "experience_next", "proficiencyBonus", "passivePerception",
              "passiveInsight", "passiveInvestigation", "str", "dex", "con", "int", "wis",
              "cha", "hp_max", "ac", "speed", "hitDie", "isSpellcaster",
              "spellcastingAbility", "spell_save_dc", "spell_attack_bonus", "ddbId"]
# Only overwritten when D&D Beyond actually has a value (players often fill these in by hand)
FM_IF_PRESENT = ["alignment", "gender", "age"]
# Body sections D&D Beyond owns (Equipment keeps the player's Notes column)
SECTIONS_MANAGED = {"Skills & Saving Throws", "Spellcasting",
                    "Features, Traits & Proficiencies", "Equipment & Inventory"}
# Body sections refreshed only while still an untouched placeholder
SECTIONS_IF_PLACEHOLDER = {"Personality Traits", "Ideals", "Flaws", "Bonds"}

_FM_LABELS = {"level": "Level", "experience": "XP", "experience_next": "XP to next level",
              "proficiencyBonus": "Proficiency bonus", "hp_max": "Max HP", "ac": "AC",
              "speed": "Speed", "hitDie": "Hit die", "spell_save_dc": "Spell save DC",
              "spell_attack_bonus": "Spell attack bonus", "passivePerception": "Passive Perception",
              "passiveInsight": "Passive Insight", "passiveInvestigation": "Passive Investigation",
              "str": "STR", "dex": "DEX", "con": "CON", "int": "INT", "wis": "WIS", "cha": "CHA",
              "species": "Species", "class": "Class", "subclass": "Subclass",
              "background": "Background", "languages": "Languages", "alignment": "Alignment",
              "gender": "Gender", "age": "Age", "isSpellcaster": "Spellcaster",
              "spellcastingAbility": "Spellcasting ability"}
_SECTION_LABELS = {"Skills & Saving Throws": "Skills", "Spellcasting": "Spells",
                   "Features, Traits & Proficiencies": "Features & proficiencies",
                   "Equipment & Inventory": "Inventory"}


def _split_note(text):
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    return (m.group(1), m.group(2)) if m else ("", text)


def _fm_blocks(fm):
    """Ordered [key, [lines]] blocks; list items/continuations stay with their key."""
    blocks = []
    for line in fm.split("\n"):
        m = re.match(r"^([A-Za-z_][\w-]*):", line)
        if m: blocks.append([m.group(1), [line]])
        elif blocks: blocks[-1][1].append(line)
    return blocks


def _fm_scalar(lines):
    v = re.sub(r"^[^:]*:\s*", "", lines[0]).strip()
    return v.strip("'\"")


def _fm_blank(lines):
    return len(lines) == 1 and _fm_scalar(lines) in ("", "[]")


def _split_sections(body):
    """→ (preamble text, [(heading, text)]) splitting on H2s outside code fences."""
    pre, secs, cur, fence = [], [], None, False
    for ln in body.split("\n"):
        if ln.startswith("```"): fence = not fence
        if not fence and ln.startswith("## "):
            cur = [ln]; secs.append((ln[3:].strip(), cur))
        elif cur is None: pre.append(ln)
        else: cur.append(ln)
    return "\n".join(pre), [(h, "\n".join(l)) for h, l in secs]


def _join_body(pre, secs):
    return "\n".join([pre] + [t for _, t in secs])


def _table_cells(row):
    return [c.strip() for c in re.split(r"(?<!\\)\|", row)[1:-1]]


def _item_key(cell):
    m = re.match(r"^\[\[(?:[^\]|\\]*[|\\]+)?([^\]]*)\]\]$", cell)
    return (m.group(1) if m else cell).strip().lower()


def _keep_inventory_notes(old_text, new_text):
    """Carry the player's per-item Notes column over into the refreshed table."""
    notes = {}
    for ln in old_text.split("\n"):
        if ln.startswith("|") and not re.match(r"^\|\s*(Name\b|-)", ln):
            cells = _table_cells(ln)
            if len(cells) >= 4 and cells[3]:
                notes[_item_key(cells[0])] = cells[3]
    out = []
    for ln in new_text.split("\n"):
        if ln.startswith("|") and not re.match(r"^\|\s*(Name\b|-)", ln):
            cells = _table_cells(ln)
            if len(cells) >= 4 and not cells[3] and _item_key(cells[0]) in notes:
                ln = re.sub(r"\|\s*\|\s*$", f"| {notes[_item_key(cells[0])]} |", ln)
        out.append(ln)
    return "\n".join(out)


def _merge_frontmatter(old_fm, new_fm, update_art, url_explicit):
    new = {k: l for k, l in _fm_blocks(new_fm)}
    changes, out, seen = [], [], set()
    old_blocks = _fm_blocks(old_fm)
    old = {k: l for k, l in old_blocks}

    # HP: keep live play state; only follow a change in max HP
    def as_int(lines):
        try: return int(_fm_scalar(lines))
        except (TypeError, ValueError): return None
    old_cur, old_max = as_int(old.get("hp_current", [""])), as_int(old.get("hp_max", [""]))
    new_max = as_int(new.get("hp_max", [""]))
    if None in (old_cur, old_max, new_max): hp_cur = as_int(new.get("hp_current", [""]))
    elif old_cur >= old_max: hp_cur = new_max
    else: hp_cur = min(old_cur, new_max)

    for key, lines in old_blocks:
        seen.add(key)
        repl = lines
        if key in FM_MANAGED and key in new: repl = new[key]
        elif key in FM_IF_PRESENT and key in new and not _fm_blank(new[key]): repl = new[key]
        elif key == "ddbUrl" and url_explicit and key in new: repl = new[key]
        elif key == "ddbLastSync" and key in new: repl = new[key]
        elif key == "hp_current" and hp_cur is not None: repl = [f"hp_current: {hp_cur}"]
        elif key == "art" and update_art and key in new: repl = new[key]
        if repl != lines and key in _FM_LABELS:
            a, b = _fm_scalar(lines), _fm_scalar(repl)
            changes.append(f"{_FM_LABELS[key]}: {a} → {b}" if len(lines) == len(repl) == 1
                           else f"{_FM_LABELS[key]} updated")
        elif repl != lines and key == "hp_current":
            changes.append(f"Current HP: {_fm_scalar(lines)} → {hp_cur}")
        out.extend(repl)
    for key in ("ddbId", "ddbUrl", "ddbLastSync"):            # notes imported before linking existed
        if key not in seen and key in new: out.extend(new[key])
    return "\n".join(out), changes


def _merge_body(old_body, new_body):
    opre, osecs = _split_sections(old_body)
    npre, nsecs = _split_sections(new_body)
    ndict, changes, out = dict(nsecs), [], []

    # Multiclass callout lives in the preamble
    cb = re.compile(r"\n> \[!info\] Multiclass\n> [^\n]*\n")
    o, n = cb.search(opre), cb.search(npre)
    if o and n and o.group(0) != n.group(0):
        opre = cb.sub(lambda m: n.group(0), opre, count=1); changes.append("Multiclass updated")
    elif o and not n:
        opre = cb.sub("", opre, count=1); changes.append("Multiclass updated")
    elif n and not o:
        opre = re.sub(r"(?m)^(# [^\n]*\n)", lambda m: m.group(1) + n.group(0), opre, count=1)
        changes.append("Multiclass updated")

    for h, text in osecs:
        if h in SECTIONS_MANAGED and h in ndict:
            nt = _keep_inventory_notes(text, ndict[h]) if h == "Equipment & Inventory" else ndict[h]
            if nt != text: changes.append(f"{_SECTION_LABELS[h]} updated")
            text = nt
        elif h in SECTIONS_IF_PLACEHOLDER and h in ndict:
            if re.search(r"Insert [A-Z]", text) and not re.search(r"Insert [A-Z]", ndict[h]):
                text = ndict[h]; changes.append(f"{h} filled from D&D Beyond")
        elif h == "Notes" and h in ndict:
            new_line = re.search(r"(?m)^> Character ID: .*$", ndict[h])
            old_line = re.search(r"(?m)^> Character ID: .*$", text)
            if new_line and old_line:
                line = new_line.group(0)
                d = re.search(r"Imported: (\d{4}-\d{2}-\d{2})", old_line.group(0))
                if d: line = re.sub(r"Imported: \d{4}-\d{2}-\d{2}", f"Imported: {d.group(1)}", line)
                text = text.replace(old_line.group(0), line, 1)
        out.append((h, text))
    return _join_body(opre, out), changes


def merge_note(old_text, new_text, update_art, url_explicit):
    ofm, obody = _split_note(old_text)
    nfm, nbody = _split_note(new_text)
    fm, fm_changes = _merge_frontmatter(ofm, nfm, update_art, url_explicit)
    body, body_changes = _merge_body(obody, nbody)
    return f"---\n{fm}\n---\n{body}", fm_changes + body_changes


def find_linked_note(vault_path, char_id):
    """Locate the note for this D&D Beyond character (ddbId frontmatter, or the
    'Character ID' callout written by earlier versions of the importer)."""
    d = os.path.join(vault_path, "My Character")
    if not os.path.isdir(d): return None
    for fname in sorted(os.listdir(d)):
        if not fname.endswith(".md"): continue
        path = os.path.join(d, fname)
        try: text = open(path, encoding="utf-8").read()
        except OSError: continue
        if (re.search(rf"(?m)^ddbId:\s*['\"]?{re.escape(char_id)}['\"]?\s*$", text)
                or f"Character ID: `{char_id}`" in text):
            return path
    return None


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault_path")
    ap.add_argument("char_id")
    ap.add_argument("campaign_name", nargs="?", default="")
    ap.add_argument("--update", action="store_true",
                    help="merge into the note already linked to this character instead of creating one")
    ap.add_argument("--url", default="", help="the D&D Beyond URL to remember on the note")
    args = ap.parse_args()

    vault_path    = args.vault_path
    char_id       = args.char_id.strip()
    campaign_name = args.campaign_name.strip()
    ddb_url       = args.url.strip()
    update_mode   = args.update
    existing_path = None
    if update_mode:
        existing_path = find_linked_note(vault_path, char_id)
        if not existing_path:
            print(json.dumps({"error": "no_linked_note"}))
            sys.exit(0)
        if not ddb_url:
            m = re.search(r"(?m)^ddbUrl:\s*['\"]?([^'\"\n]+)", open(existing_path, encoding="utf-8").read())
            ddb_url = m.group(1).strip() if m else ""
    url_explicit = bool(args.url.strip())
    if not ddb_url or not re.match(r"^https?://", ddb_url):
        ddb_url = f"https://www.dndbeyond.com/characters/{char_id}"
        url_explicit = False
    ddb_url = ddb_url.replace("'", "''")

    # ── Fetch ──────────────────────────────────────────────────────────────
    try:
        response = fetch(char_id)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            print(json.dumps({"error": "character_private"}))
            sys.exit(0)
        print(json.dumps({"error": f"HTTP {e.code}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    data = response.get("data") or {}
    if not data:
        print(json.dumps({"error": "No character data in response"}))
        sys.exit(1)

    # Default the campaign to the one this character belongs to on D&D Beyond
    if not campaign_name:
        campaign_name = (data.get("campaign") or {}).get("name") or ""
    campaign_display = campaign_name
    campaign_name = campaign_name.replace("'", "''")  # escape for single-quoted YAML

    # ── Basic info ─────────────────────────────────────────────────────────
    char_name     = data.get("name", "Unknown Character")
    race_obj      = data.get("race") or {}
    race_name_ddb = race_obj.get("fullName") or race_obj.get("baseRaceName") or ""
    race_name     = _resolve_race_name(race_name_ddb)
    alignment_str = ALIGNMENTS.get(data.get("alignmentId"), "")
    gender        = (data.get("gender") or "").strip()
    age           = str(data.get("age") or "").strip()

    # ── Classes ────────────────────────────────────────────────────────────
    classes      = data.get("classes") or []
    total_level  = sum(c.get("level", 0) for c in classes)
    primary_cls  = ""
    primary_sub  = ""
    class_parts  = []
    for c in classes:
        defn     = c.get("definition") or {}
        sub_def  = c.get("subclassDefinition")
        cls_name = defn.get("name", "")
        sub_name = sub_def.get("name", "") if sub_def else ""
        lvl      = c.get("level", 0)
        if not primary_cls:
            primary_cls = cls_name
            primary_sub = sub_name
        part = f"{cls_name} {lvl}" + (f" ({sub_name})" if sub_name else "")
        class_parts.append(part)

    multiclass_line = " / ".join(class_parts) if len(classes) > 1 else ""

    is_spellcaster    = any(c.get("definition",{}).get("name") in SPELLCASTER_ABILITIES for c in classes)
    spell_ability_key = next((SPELLCASTER_ABILITIES[c["definition"]["name"]] for c in classes
                              if c.get("definition",{}).get("name") in SPELLCASTER_ABILITIES), "")
    hit_die           = CLASS_HIT_DICE.get(primary_cls, "")

    bg_obj  = data.get("background") or {}
    bg_def  = bg_obj.get("definition") or {}
    bg_name = BACKGROUND_NAME_MAP.get(bg_def.get("name", ""), bg_def.get("name", ""))

    # ── Ability scores ─────────────────────────────────────────────────────
    base_stats     = data.get("stats") or []
    bonus_stats    = data.get("bonusStats") or []
    override_stats = data.get("overrideStats") or []
    all_mods = all_modifiers(data)
    scores = {name: calc_score(base_stats, bonus_stats, override_stats, sid, all_mods, name)
              for sid, name in STAT_IDS.items()}
    pb = prof_bonus(total_level)

    # ── HP & XP ────────────────────────────────────────────────────────────
    # DDB's baseHitPoints excludes CON and feat bonuses:
    #   max = base + CON mod × level + bonus + (per-level bonuses, e.g. Tough) × level
    hp_info = data.get("hitPointInfo") or {}
    if hp_info.get("totalHitPoints"):
        hp_max = hp_info["totalHitPoints"]
    elif data.get("overrideHitPoints"):
        hp_max = data["overrideHitPoints"]
    else:
        per_level = sum(_mod_value(m) for m in all_mods
                        if m.get("type") == "bonus" and m.get("subType") == "hit-points-per-level")
        hp_max = ((data.get("baseHitPoints") or 0)
                  + mod(scores["con"]) * total_level
                  + (data.get("bonusHitPoints") or 0)
                  + per_level * total_level)
    removed    = hp_info.get("removedHitPoints") or data.get("removedHitPoints") or 0
    hp_temp    = hp_info.get("temporaryHitPoints") or data.get("temporaryHitPoints") or 0
    hp_current = max(0, hp_max - removed)
    xp         = data.get("currentXp") or 0
    xp_next    = XP_THRESHOLDS[total_level] if total_level < 20 else XP_THRESHOLDS[19]

    # ── Speed ──────────────────────────────────────────────────────────────
    speeds = (race_obj.get("weightSpeeds") or {}).get("normal") or {}
    speed  = speeds.get("walk") or 30

    # ── AC ─────────────────────────────────────────────────────────────────
    inventory      = data.get("inventory") or []
    equipped_armor = None
    shield_bonus   = 0
    for item in inventory:
        if not item.get("equipped"): continue
        defn = item.get("definition") or {}
        if defn.get("filterType") != "Armor": continue
        # Shields have an empty `type` in the API — armorTypeId 4 is the reliable marker
        if defn.get("armorTypeId") == 4 or defn.get("baseArmorName") == "Shield" or defn.get("type") == "Shield":
            shield_bonus = max(shield_bonus, defn.get("armorClass") or 2)
        else:
            equipped_armor = {"base": defn.get("armorClass") or 0, "type_id": defn.get("armorTypeId")}

    ac_bonus = sum(_mod_value(m) for m in all_mods
                   if m.get("type") == "bonus" and m.get("subType") == "armor-class"
                   and (equipped_armor or "armor" not in (m.get("restriction") or "").lower()))

    dex_mod = mod(scores["dex"])
    if equipped_armor:
        t = equipped_armor["type_id"]
        if t == 3:   ac = equipped_armor["base"] + shield_bonus
        elif t == 2: ac = equipped_armor["base"] + min(dex_mod, 2) + shield_bonus
        else:        ac = equipped_armor["base"] + dex_mod + shield_bonus
    else:
        ac = 10 + dex_mod + shield_bonus
    ac += ac_bonus

    # ── Modifiers ──────────────────────────────────────────────────────────

    def has_prof(subtype):
        return any(m.get("type") == "proficiency" and m.get("subType") == subtype for m in all_mods)
    def has_expertise(subtype):
        return any(m.get("type") == "expertise" and m.get("subType") == subtype for m in all_mods)
    def passive(subtype, ability):
        bonus = (pb * (2 if has_expertise(subtype) else 1)) if has_prof(subtype) else 0
        return 10 + mod(scores[ability]) + bonus

    passive_perception    = passive("perception", "wis")
    passive_insight       = passive("insight", "wis")
    passive_investigation = passive("investigation", "int")

    # ── Skills ─────────────────────────────────────────────────────────────
    skill_rows = []
    for subtype, display in SKILL_SUBTYPES.items():
        p = "✓" if has_prof(subtype) else ""
        e = "✓" if has_expertise(subtype) else ""
        skill_rows.append(f"| {display} | {p} | {e} |")

    # ── Languages ──────────────────────────────────────────────────────────
    languages = []
    for m in all_mods:
        if m.get("type") != "language": continue
        subtype = m.get("subType", "")
        name = (m.get("friendlySubtypeName")
                or LANGUAGE_NAMES.get(subtype)
                or subtype.replace("-", " ").title())
        if name and name not in languages: languages.append(name)

    # ── Proficiencies ──────────────────────────────────────────────────────
    armor_profs  = []
    weapon_profs = []
    tool_profs   = []
    save_profs   = []
    seen_profs   = set()

    NON_TOOL = set(SKILL_SUBTYPES) | set(LANGUAGE_NAMES) | set(ARMOR_PROFS) | set(WEAPON_PROFS) | set(SAVE_SUBTYPES) | {"initiative"}

    for m in all_mods:
        if m.get("type") not in ("proficiency",): continue
        subtype = m.get("subType", "")
        if not subtype or subtype in seen_profs: continue
        seen_profs.add(subtype)

        if subtype in SAVE_SUBTYPES:
            save_profs.append(SAVE_SUBTYPES[subtype])
        elif subtype in ARMOR_PROFS:
            armor_profs.append(ARMOR_PROFS[subtype])
        elif subtype in WEAPON_PROFS:
            weapon_profs.append(WEAPON_PROFS[subtype])
        elif subtype not in NON_TOOL and "language" not in subtype:
            tool_profs.append(subtype.replace("-", " ").title())

    prof_lines = []
    if save_profs:   prof_lines.append(f"**Saving Throws:** {', '.join(save_profs)}")
    if armor_profs:  prof_lines.append(f"**Armor:** {', '.join(armor_profs)}")
    if weapon_profs: prof_lines.append(f"**Weapons:** {', '.join(weapon_profs)}")
    if tool_profs:   prof_lines.append(f"**Tools:** {', '.join(tool_profs)}")
    prof_block = "\n".join(prof_lines) if prof_lines else "> *No additional proficiencies found.*"

    # ── Feats ──────────────────────────────────────────────────────────────
    # DDB sometimes leaks ability score names as "feats" from ASI choices — skip them
    # Also skip ASI bookkeeping entries DDB stores as feats/options
    # ("Farmer Ability Score Improvements", "Increase two scores (+2 / +1)").
    FEAT_SKIP = {"Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"}
    feat_names = []
    # Primary source: data.feats
    for f in (data.get("feats") or []):
        name = (f.get("definition") or {}).get("name", "")
        if name and name not in feat_names and name not in FEAT_SKIP and not _BOOKKEEPING_FEAT_RE.search(name):
            feat_names.append(name)
    # Secondary source: data.options.feat (feats taken via ASI choices)
    for f in ((data.get("options") or {}).get("feat") or []):
        name = (f.get("definition") or {}).get("name", "")
        if name and name not in feat_names and name not in FEAT_SKIP and not _BOOKKEEPING_FEAT_RE.search(name):
            feat_names.append(name)

    def feat_link(name):
        # DDB appends class choices like "(Bard, Sorcerer, Warlock)"; strip for note resolution
        base = re.sub(r'\s*\([^)]*\)$', '', name).strip()
        return _note_link(base, ["Lore/Feats"], vault_path, display=name)

    feats_block = ("\n".join(f"- {feat_link(n)}" for n in feat_names)
                   if feat_names else "> *No feats found — add manually if this character has feats.*")

    # ── Class features & racial traits ────────────────────────────────────
    feature_sections = []

    for c in classes:
        defn      = c.get("definition") or {}
        sub_def   = c.get("subclassDefinition")
        cls_name  = defn.get("name", "")
        sub_name  = sub_def.get("name", "") if sub_def else ""
        cls_level = c.get("level", 0)

        cls_feats = defn.get("classFeatures") or []
        sub_feats = (sub_def.get("classFeatures") or []) if sub_def else []

        gained = []
        seen_feature_names = set()
        for f in cls_feats + sub_feats:
            f_name  = f.get("name") or (f.get("definition") or {}).get("name", "")
            f_name  = f_name.replace("’", "'").replace("‘", "'") if f_name else f_name
            f_level = f.get("requiredLevel") or f.get("level") or 0
            # 2024 classes carry a "Core <Class> Traits" table entry that has no note
            if (f_name and f_level <= cls_level and f_name not in seen_feature_names
                    and f_name not in DDB_SYNTHETIC and not re.match(r"^Core .+ Traits$", f_name)):
                seen_feature_names.add(f_name)
                gained.append((f_level, f_name))

        if gained:
            gained.sort()
            if sub_name:
                heading = f"**{cls_name} ({sub_name})**"
            else:
                heading = f"**{cls_name}**"
            lines = [
                f"- {_note_link(name, ['Lore/Classes/Features'], vault_path)} *(Lv {lvl})*"
                for lvl, name in gained
            ]
            feature_sections.append(heading + "\n" + "\n".join(lines))

    # Racial traits
    racial_traits = []
    for trait in (race_obj.get("racialTraits") or []):
        defn = trait.get("definition") or trait
        name = defn.get("name", "")
        # Normalize Unicode smart quotes/apostrophes to ASCII so links resolve
        name = name.replace("’", "'").replace("‘", "'")
        name = TRAIT_NAME_MAP.get(name, name)
        if name:
            racial_traits.append(name)
    if racial_traits:
        race_heading = f"**{race_name} Racial Traits**" if race_name else "**Racial Traits**"
        trait_dirs = ["Lore/Races/Traits", "Lore/Species/Traits"]
        trait_lines = [f"- {_note_link(t, trait_dirs, vault_path)}" for t in racial_traits]
        feature_sections.append(race_heading + "\n" + "\n".join(trait_lines))

    # Background feature — 2024 backgrounds grant an origin feat (e.g. Tough) that is
    # already listed under Feats, so only show it here when it isn't.
    bg_feature = (bg_def.get("featureName") or "").strip().replace("’", "'").replace("‘", "'") if bg_def else ""
    if bg_feature and bg_feature not in feat_names:
        bg_heading = f"**{bg_name} Background Feature**" if bg_name else "**Background Feature**"
        bg_feat_link = _note_link(bg_feature, ["Lore/Backgrounds/Features", "Lore/Feats"], vault_path)
        feature_sections.append(f"{bg_heading}\n- {bg_feat_link}")

    class_features_block = ("\n\n".join(feature_sections)
                            if feature_sections
                            else "> *No class features found — add manually.*")

    # ── Spells ─────────────────────────────────────────────────────────────
    spells_raw = data.get("spells") or {}
    spells_by_level = defaultdict(list)
    for source in ("class", "race", "background", "item", "feat"):
        for spell in (spells_raw.get(source) or []):
            defn  = spell.get("definition") or {}
            name  = defn.get("name", "")
            level = defn.get("level", 0)
            if name and name not in spells_by_level[level]:
                spells_by_level[level].append(name)

    spell_save_dc      = 0
    spell_attack_bonus = 0
    if is_spellcaster and spell_ability_key:
        spell_save_dc      = 8 + pb + mod(scores[spell_ability_key])
        spell_attack_bonus = pb + mod(scores[spell_ability_key])

    if spells_by_level:
        spell_lines = []
        for lvl in sorted(spells_by_level):
            heading = SPELL_LEVEL_NAMES.get(lvl, f"Level {lvl}")
            spell_lines.append(f"\n### {heading}")
            for s in sorted(spells_by_level[lvl]):
                spell_lines.append(f"- {_note_link(s, ['Possessions/Spells'], vault_path)}")
        spell_section = "\n".join(spell_lines)
    else:
        spell_section = "\n> *No spells found — fill in manually if this character is a spellcaster.*"

    # ── Personality traits ─────────────────────────────────────────────────
    traits      = data.get("traits") or {}
    personality = (traits.get("personalityTraits") or "").strip()
    ideals      = (traits.get("ideals") or "").strip()
    bonds       = (traits.get("bonds") or "").strip()
    flaws       = (traits.get("flaws") or "").strip()

    _ph = "#646a73"
    personality_text = personality or f'> *<font color="{_ph}">Insert Personality Traits.</font>*'
    ideals_text      = ideals      or f'> *<font color="{_ph}">Insert Ideals.</font>*'
    flaws_text       = flaws       or f'> *<font color="{_ph}">Insert Flaws.</font>*'
    bonds_text       = bonds       or f'> *<font color="{_ph}">Insert Bonds.</font>*'

    # ── Inventory ──────────────────────────────────────────────────────────
    # Aggregate duplicates: keyed by (name, type), summing quantity
    inv_agg = {}
    for item in inventory:
        defn  = item.get("definition") or {}
        name  = defn.get("name", "")
        qty   = item.get("quantity") or 1
        itype = defn.get("filterType") or defn.get("type") or ""
        if not name:
            continue
        key = (name, itype)
        inv_agg[key] = inv_agg.get(key, 0) + qty

    inv_rows = [f"| {_item_link(name, vault_path)} | {itype} | {count} | |"
                for (name, itype), count in inv_agg.items()]
    inv_table = ("| Name | Type | Count | Notes |\n| ---- | ---- | :---: | ----- |\n"
                 + ("\n".join(inv_rows) if inv_rows else "| | | | |"))

    # ── Character image ────────────────────────────────────────────────────
    decorations = data.get("decorations") or {}
    avatar_url  = decorations.get("avatarUrl") or data.get("avatarUrl") or ""
    art_field   = "[[PlaceholderCharacter.png]]"
    safe_name   = re.sub(r'[\\/:*?"<>|]', "", char_name)

    if avatar_url:
        try:
            ext      = ".png" if avatar_url.lower().endswith(".png") else ".jpg"
            img_name = f"{safe_name}{ext}"
            img_dir  = os.path.join(vault_path, "z_Assets", "Character")
            os.makedirs(img_dir, exist_ok=True)
            download_image(avatar_url, os.path.join(img_dir, img_name))
            art_field = f"[[{img_name}]]"
        except Exception:
            pass  # fall back to placeholder

    # ── Build note ─────────────────────────────────────────────────────────
    # Build vault-aware lore index so links resolve against files that actually exist.
    lore_index = _build_lore_index(vault_path)

    # Determine which character-type folder the active system uses.
    # Priority: (1) whichever folder actually contains the character's race note,
    # (2) whichever folder has any content at all, (3) vault-config.json.
    if _lore_exists(race_name, "races", lore_index):
        _race_folder = "races"
    elif _lore_exists(race_name, "species", lore_index):
        _race_folder = "species"
    elif lore_index.get("races"):
        _race_folder = "races"
    elif lore_index.get("species"):
        _race_folder = "species"
    else:
        try:
            _cfg = json.loads(open(os.path.join(vault_path, "vault-config.json")).read())
            _race_folder = "species" if _cfg.get("gameSystem") == "dnd5e_2024" else "races"
        except Exception:
            _race_folder = "races"

    def lore_link(val, folder):
        return f"'{_lore_link(val, folder, lore_index)}'" if val else "''"
    def subclass_link(sub, cls):
        # Vault names subclasses "SubclassName (ClassName).md"; DDB names carry a source
        # tag ("Tempest Domain (PHB)") that the vault note doesn't, so try both forms.
        if not sub: return "''"
        candidates = [f"{sub} ({cls})", f"{_clean_subclass_name(sub)} ({cls})"]
        note_name = next((n for n in candidates if _lore_exists(n, "subclasses", lore_index)), candidates[-1])
        return f"'{_lore_link(note_name, 'subclasses', lore_index, display=sub)}'"

    # Languages need path-qualified links to avoid colliding with same-named race notes
    lang_yaml   = "\n".join(f"  - '[[Lore/Languages/{l}|{l}]]'" for l in languages) if languages else "  []"
    lang_block  = f"languages:\n{lang_yaml}" if languages else "languages: []"
    skills_table = ("| Skill | Proficient | Expertise |\n| ----- | :-------: | :-------: |\n"
                    + "\n".join(skill_rows))
    multiclass_callout = f'\n> [!info] Multiclass\n> {multiclass_line}\n' if multiclass_line else ""

    folder   = "My Character"
    file_rel = f"{folder}/{safe_name}.md"
    abs_dir  = os.path.join(vault_path, *folder.split("/"))
    os.makedirs(abs_dir, exist_ok=True)

    content = f"""---
tags:
  - Character
  - Player
art: "{art_field}"
aliases:
species: {lore_link(race_name, _race_folder)}
class: {lore_link(primary_cls, "classes")}
subclass: {subclass_link(primary_sub, primary_cls)}
background: {lore_link(bg_name, "backgrounds")}
alignment: '{alignment_str}'
gender: '{gender}'
pronouns: ''
sexuality: ''
age: '{age}'
birthday: ''
{lang_block}
occupation: []
organizations: []
religions: []
condition:
  - Healthy
currentLocation: []
campaign: '{campaign_name}'
level: {total_level}
experience: {xp}
experience_next: {xp_next}
proficiencyBonus: {pb}
passivePerception: {passive_perception}
passiveInsight: {passive_insight}
passiveInvestigation: {passive_investigation}
str: {scores['str']}
dex: {scores['dex']}
con: {scores['con']}
int: {scores['int']}
wis: {scores['wis']}
cha: {scores['cha']}
hp_max: {hp_max}
hp_current: {hp_current}
hp_temp: {hp_temp}
ac: {ac}
speed: {speed}
hitDie: '{hit_die}'
isSpellcaster: {str(is_spellcaster).lower()}
spellcastingAbility: '{spell_ability_key.upper() if spell_ability_key else ""}'
spell_save_dc: {spell_save_dc}
spell_attack_bonus: {spell_attack_bonus}
ddbId: '{char_id}'
ddbUrl: '{ddb_url}'
ddbLastSync: {datetime.now().strftime('%Y-%m-%d')}
---

> [!infobox | no-blending black]+ <font color="#ffffff">Infobox</font>
>
> `VIEW[!{{art}}][text(renderMarkdown)]`
>
> # Bio
> | | |
> |---|---|
> | **Aliases** | `VIEW[{{aliases}}][text]` |
> | **Species** | `VIEW[{{species}}][link]` |
> | **Class** | `VIEW[{{class}}][link]` |
> | **Subclass** | `VIEW[{{subclass}}][link]` |
> | **Background** | `VIEW[{{background}}][link]` |
> | **Alignment** | `VIEW[{{alignment}}][text]` |
> | **Gender** | `VIEW[{{gender}}][text]` |
> | **Pronouns** | `VIEW[{{pronouns}}][text]` |
> | **Sexuality** | `VIEW[{{sexuality}}][text]` |
> | **Age** | `VIEW[{{age}}][text]` |
>
> # Details
> | | |
> |---|---|
> | **Languages** | `VIEW[{{languages}}][link]` |
> | **Occupations** | `VIEW[{{occupation}}][text]` |
> | **Organizations** | `VIEW[{{organizations}}][link]` |
> | **Religions** | `VIEW[{{religions}}][link]` |
> | **Condition** | `VIEW[{{condition}}]` |
> | **Location** | `VIEW[{{currentLocation}}][link]` |
>
> # Combat
> | | |
> |---|---|
> | **Level** | `VIEW[{{level}}]` |
> | **XP** | `VIEW[{{experience}}]` / `VIEW[{{experience_next}}]` |
> | **HP** | `VIEW[{{hp_current}}]` / `VIEW[{{hp_max}}]` (Temp: `VIEW[{{hp_temp}}]`) |
> | **AC** | `VIEW[{{ac}}]` |
> | **Speed** | `VIEW[{{speed}}]` ft |
> | **Prof. Bonus** | +`VIEW[{{proficiencyBonus}}]` |
> | **Hit Die** | `VIEW[{{hitDie}}][text]` |

# {char_name}
{multiclass_callout}
## Ability Scores

| STR | DEX | CON | INT | WIS | CHA |
|:---:|:---:|:---:|:---:|:---:|:---:|
| `INPUT[number:str]` | `INPUT[number:dex]` | `INPUT[number:con]` | `INPUT[number:int]` | `INPUT[number:wis]` | `INPUT[number:cha]` |

## Skills & Saving Throws

{skills_table}

## Spellcasting

> *Spell save DC: `VIEW[{{spell_save_dc}}]` | Spell attack bonus: +`VIEW[{{spell_attack_bonus}}]` | Ability: `VIEW[{{spellcastingAbility}}][text]`*
{spell_section}

## Features, Traits & Proficiencies

### Class Features & Traits

{class_features_block}

### Feats

{feats_block}

### Proficiencies

{prof_block}

## Equipment & Inventory

{inv_table}

## Personality Traits

{personality_text}

## Ideals

{ideals_text}

## Flaws

{flaws_text}

## Bonds

{bonds_text}

## Secrets

- [ ] *<font color="#646a73">Secret 1</font>*

## Goals

> [!column | 2 no-t]
> > [!metadata|shortterm] Short Term
> > - *<font color="#646a73">What does this character want to accomplish in the next month to six months?</font>*
>
> > [!metadata|longterm] Long Term
> > - *<font color="#646a73">What does this character want to accomplish in the next 5-10 years?</font>*

## Past

### Birth

- **Birthday:** `VIEW[{{birthday}}][text]`
- **Birth Location:**
- **Mother:** | **Father:**

### Childhood

> *<font color="#646a73">What was this character's childhood like?</font>*

### Journey

> *<font color="#646a73">What brought this character to where they are now?</font>*

### Worship

> *<font color="#646a73">Is there any deity or group this character holds loyalty to?</font>*

## Session History

```dataview
TABLE WITHOUT ID
  file.link as "Session",
  sessionNumber as "#",
  sessionDate as "Date",
  summary as "Summary"
FROM "Campaign Notes/Session Recaps"
WHERE econtains(tags,"SessionRecap") AND contains(file.outlinks, this.file.link)
SORT sessionNumber DESC
```

## Notes

> [!info] Imported from D&D Beyond
> Character ID: `{char_id}` · Imported: {datetime.now().strftime('%Y-%m-%d')} · Last synced: {datetime.now().strftime('%Y-%m-%d')} · [Open on D&D Beyond]({ddb_url})
"""

    if update_mode:
        old_text = open(existing_path, encoding="utf-8").read()
        # Only replace the portrait with a fresh D&D Beyond one, and never clobber custom art
        old_art = re.search(r'(?m)^art:\s*(.*)$', old_text)
        old_is_ours = bool(old_art and ("Placeholder" in old_art.group(1)
                                        or (avatar_url and os.path.splitext(img_name)[0] in old_art.group(1))))
        update_art = art_field != "[[PlaceholderCharacter.png]]" and old_is_ours
        merged, changes = merge_note(old_text, content, update_art, url_explicit)
        if merged != old_text:
            with open(existing_path, "w", encoding="utf-8") as fh:
                fh.write(merged)
        rel = os.path.relpath(existing_path, vault_path).replace(os.sep, "/")
        print(json.dumps({"success": True, "updated": True, "file": rel,
                          "name": char_name, "changes": changes}))
        return

    with open(os.path.join(vault_path, *file_rel.split("/")), "w", encoding="utf-8") as fh:
        fh.write(content)

    print(json.dumps({"success": True, "file": file_rel, "name": char_name, "campaign": campaign_display}))


if __name__ == "__main__":
    main()
