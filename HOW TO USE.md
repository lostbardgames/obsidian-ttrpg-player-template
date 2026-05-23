---
tags:
  - Guide
cssclasses:
  - wide-page
---

# 📖 How to Use This Vault

This guide covers every note type in the player vault — what each one is for, every field explained, and how notes connect to each other.

> [!tip] New to Obsidian?
> In Obsidian, **notes** are just files. **Properties** (also called frontmatter) are the structured fields at the top of a note — they power all the automatic lists and dashboards. **Internal links** look like `[[Note Name]]` and connect notes together.

---

## Table of Contents

1. [[#The Golden Rules]]
2. [[#Key Tools]]
3. [[#My Character]]
4. [[#Journal Entries]]
5. [[#Session Recaps]]
6. [[#Quests]]
7. [[#NPCs Known]]
8. [[#Locations Visited]]
9. [[#Possessions]]
   - [[#Items]]
   - [[#Spells]]
10. [[#Lore Notes]]

---

## The Golden Rules

**1. Always use the Quick Create buttons.** Use the buttons on the [[1.Tools/Homepage|Homepage]] or [[1.Tools/Buttons|Buttons]] page. They apply the right template, place the file in the right folder, and tag it so it appears on dashboards automatically.

**2. Links power everything.** When you link an NPC to a session recap, a quest to a location, or an item to your character, those connections drive the automatic lists you see on dashboards. If something isn't appearing where you expect it, check that the relevant link field is filled in.

**3. Write from your character's perspective.** This vault is your personal record. Journal entries, NPC impressions, and location notes should reflect what *your character* knows and feels — not the GM's omniscient view.

**4. Fill in fields as you go.** You don't have to fill in every property immediately. Start with the essentials and add details as you play.

---

## Key Tools

### Homepage — `1.Tools/Homepage`

Your player dashboard. Opens automatically when you launch Obsidian. Shows your character's stats, active quests, recent session recaps, and quick-create buttons for the most common note types.

### Player Screen — `1.Tools/Player Screen`

Your live session tool. Keep it open during play for your HP and stats, spell slot tracking, dice rolls, initiative, and quick rules references. Think of it as your digital character tracker for the table.

### Buttons — `1.Tools/Buttons`

Every note type has a creation button here. When you need to create something that isn't on the Homepage Quick Create panel, come here.

---

## My Character

**What it is:** Your character sheet — the central hub of your vault.

**Create it:** Homepage → Quick Create → **New Character**, or Buttons → **New Character**.

**Where it's stored:** `My Character/`

### Key Fields

| Field | What to put here |
|-------|-----------------|
| **Species** | Link to a Lore note for your race — e.g. `[[Half-Elf]]`. |
| **Class** | Link to a Lore note — e.g. `[[Fighter]]`. |
| **Subclass** | Link to a Lore note — e.g. `[[Battle Master]]`. |
| **Background** | Link to a Lore note — e.g. `[[Soldier]]`. |
| **Campaign** | The name of the campaign you're playing in. |
| **Condition** | Current status — `Healthy`, `Poisoned`, `Unconscious`, etc. Update during play. |
| **Level** | Current character level. Update when you level up. |
| **Experience** | Current XP total. |
| **HP (Max / Current / Temp)** | Hit points. Update `hp_current` during play. |
| **AC** | Armor Class. |
| **Speed** | Movement speed in feet. |
| **STR / DEX / CON / INT / WIS / CHA** | Ability scores. |

### Sections in the Note

- **Stats** — ability scores, saving throws, HP, AC, speed
- **Skills & Saving Throws** — proficiency tracking for each skill
- **Spellcasting** — spell save DC, attack bonus, prepared spells
- **Features, Traits & Proficiencies** — class features, racial traits, feats, armor/weapon proficiencies
- **Equipment & Inventory** — items carried (link to Item notes for tracked items)
- **Personality** — traits, ideals, flaws, bonds
- **Goals** — short-term and long-term character goals
- **Backstory** — birth, childhood, and the journey to adventuring
- **Session History** — auto-populated list of session recaps

> [!tip] HP During Play
> The **HP (Current)** field feeds the HP display on the Homepage and Player Screen. Update it between combats — or live using the inline field.

---

## Journal Entries

**What it is:** An in-character diary entry written from your character's point of view.

**Create it:** Homepage → Quick Create → **New Journal Entry**, or Buttons → **New Journal Entry**.

**Where it's stored:** `Campaign Notes/Journal/`

### Key Fields

| Field | What to put here |
|-------|-----------------|
| **Session** | Link to the Session Recap this entry relates to. |
| **In-World Date** | The in-game date of the entry. |
| **Real Date** | The real-world date you wrote it. |
| **Location** | Link to a Location note for where the character is writing from. |
| **Mood** | Your character's emotional state — `Hopeful`, `Troubled`, `Resolved`, `Fearful`. |

### Sections in the Note

- **Entry** — the main in-character writing. Write as your character would think and feel.
- **What I Know** — facts, clues, and information your character has learned.
- **What I Wonder** — unanswered questions, suspicions, and mysteries.
- **What I Fear** — things your character is dreading or anxious about.

> [!tip] Character Voice
> Journal entries are your best tool for developing your character's personality. Write in first person, in your character's voice. Don't worry about being "correct" — these are private notes only you will see.

---

## Session Recaps

**What it is:** Your notes from a single game session — what happened, what was decided, and what's coming next.

**Create it:** Homepage → Quick Create → **New Session Recap**, or Buttons → **New Session Recap**.

**Where it's stored:** `Campaign Notes/Session Recaps/`

### Naming Convention

Use a consistent format: `Session 01 — The Road to Millhaven`. The session number is used for sorting.

### Key Fields

| Field | What to put here |
|-------|-----------------|
| **Session Number** | A number (01, 02, 03...) used for chronological sorting. |
| **Session Date** | The real-world date the session was played. |
| **Character** | Link to your character note. |
| **XP Gained** | XP awarded this session. |
| **Gold Gained** | Gold (or other currency) awarded. |
| **Summary** | A one-line summary for dashboards. |

### Sections in the Note

- **What Happened** — your narrative summary of the session from the party's perspective.
- **Key Decisions** — choices the party made and why. Useful for looking back later.
- **Character Moments** — anything notable your character did, said, or felt.
- **Rewards** — XP, gold, and items found. Link to Item notes for magic items.
- **Questions & Mysteries** — things that came up but weren't resolved. What are you still wondering about?
- **What's Next** — your intentions and plans for the next session.
- **Live Notes** — a scratchpad for during-the-session notes. Move the good stuff up into the other sections afterward.

---

## Quests

**What it is:** A mission or objective your character is tracking.

**Create it:** Homepage → Quick Create → **New Quest**, or Buttons → **New Quest**.

**Where it's stored:** `Campaign Notes/Quests/`

### Key Fields

| Field | What to put here |
|-------|-----------------|
| **Quest Type** | `Main`, `Side`, `Personal`, `Bounty`, `Exploration`. |
| **Quest Giver** | Link to the NPC Known note for whoever gave you this quest. |
| **Status** | `Active`, `Completed`, `Failed`, `On Hold`. |
| **Linked Session** | Link to the Session Recap where you received this quest. |

### Sections in the Note

- **Objective** — checkboxes for each goal. Tick them off as you complete them.
- **What We Know** — clues, information, and discoveries. Add rows as you investigate.
- **Leads** — specific things to follow up on.
- **Rewards** — what you expect to earn on completion.
- **Notes** — anything else relevant.

---

## NPCs Known

**What it is:** Your notes about a person your character has met.

**Create it:** Buttons → **New NPC Known**.

**Where it's stored:** `Campaign Notes/NPCs Known/`

### Key Fields

| Field | What to put here |
|-------|-----------------|
| **First Met** | Link to the Session Recap where you first encountered this person. |
| **Last Seen** | Link to the most recent Session Recap they appeared in. |
| **Relationship** | `Friend`, `Ally`, `Neutral`, `Suspicious`, `Enemy`. |
| **Status** | `Alive`, `Dead`, `Unknown`, `Missing`. |
| **Current Location** | Link to a Location note for where they were last seen. |

### Sections in the Note

- **First Impressions** — your character's initial reaction to this person.
- **Known Facts** — what you've confirmed is true about them.
- **Suspicions** — things you suspect but haven't confirmed.
- **History with Party** — key interactions, favors, conflicts.
- **Secrets Uncovered** — things you've discovered about them over time.
- **Notes** — anything else you want to track.

---

## Locations Visited

**What it is:** Your notes about a place your character has visited.

**Create it:** Buttons → **New Location Visited**.

**Where it's stored:** `Campaign Notes/Locations/`

### Key Fields

| Field | What to put here |
|-------|-----------------|
| **Location Type** | `Settlement`, `Dungeon`, `Tavern`, `Region`, `POI`, `Shop`. |
| **First Visited** | Link to the Session Recap when the party first arrived. |
| **Status** | `Unexplored`, `Explored`, `Cleared`, `Dangerous`. |
| **Threat Level** | `Safe`, `Moderate`, `Dangerous`, `Deadly`. |

### Sections in the Note

- **Description** — what this place looks, smells, and feels like.
- **People Here** — link to NPC Known notes for people associated with this location.
- **Notable Features** — things that stood out about this location.
- **Secrets & Discoveries** — things the party uncovered.
- **Notes** — anything else to remember.

---

## Possessions

### Items

**What it is:** A specific item your character owns or is tracking.

**Create it:** Buttons → Possessions → **New Item**.

**Where it's stored:** `Possessions/Items/`

### Key Fields

| Field | What to put here |
|-------|-----------------|
| **Item Type** | `Weapon`, `Armor`, `Wondrous Item`, `Consumable`, `Adventuring Gear`, `Quest Item`. |
| **Rarity** | `Common`, `Uncommon`, `Rare`, `Very Rare`, `Legendary`, `Artifact`. |
| **Is Magical** | Toggle on for magic items. |
| **Attunement** | Whether you need to attune to it and whether you currently are. |
| **Owner** | Link to your character note. |
| **Found At** | Link to the Location where you found it. |
| **Obtained In** | Link to the Session Recap where you got it. |

---

### Spells

**What it is:** A spell your character knows or has prepared.

**Create it:** Buttons → Possessions → **New Spell**.

**Where it's stored:** `Possessions/Spells/`

### Key Fields

| Field | What to put here |
|-------|-----------------|
| **Spell Level** | 0 (cantrip) through 9. |
| **School** | `Abjuration`, `Conjuration`, `Divination`, `Enchantment`, `Evocation`, `Illusion`, `Necromancy`, `Transmutation`. |
| **Casting Time** | `1 action`, `1 bonus action`, `1 reaction`, `1 minute`, etc. |
| **Range** | `Self`, `Touch`, `30 feet`, `60 feet`, etc. |
| **Duration** | `Instantaneous`, `1 round`, `Concentration, up to 1 hour`, etc. |
| **Concentration** | Toggle on for concentration spells. |
| **Ritual** | Toggle on if it can be cast as a ritual. |
| **Prepared** | Toggle on if this spell is currently prepared. |

---

## Lore Notes

The `Lore/` folder is a free-form area for world lore your character has learned — histories, religious texts, faction details, monster knowledge, anything your character would know or have researched. Create notes here manually or use the Buttons page.

Link Lore notes from your Journal entries and Session Recaps to build a living record of the world as your character understands it.

---

> [!abstract] Need Help?
> For plugin-specific questions, check **Settings → Community Plugins** and click the plugin name for its documentation. The [Obsidian community forum](https://forum.obsidian.md) is also an excellent resource.
