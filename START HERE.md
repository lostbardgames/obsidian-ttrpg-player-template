---
tags:
  - Setup
cssclasses:
  - wide-page
---

# ⚔️ TTRPG Player Vault — Setup Guide

Welcome to your personal TTRPG player vault. This guide walks you through getting fully set up. Follow each step in order.

---

> [!warning] ⏱️ Estimated Setup Time
> **5–10 minutes** for full setup

---

## Step 1 — Open the Vault in Obsidian

> [!info] Prerequisites
> You must have **Obsidian** installed. Download it free from [obsidian.md](https://obsidian.md) if you haven't already.

1. Open **Obsidian**
2. On the vault picker screen, click **"Open folder as vault"**
3. Navigate to and select the **LBG TTRPG Player Template** folder you downloaded
4. Click **Open**

---

## Step 2 — Enable Community Plugins

All plugins are pre-installed inside the vault. You just need to turn them on.

> [!warning] You will see a Safe Mode warning
> Obsidian shows this for any vault containing community plugins. All plugins in this vault are open-source and widely used by the TTRPG community.

1. When prompted, click **"Turn on community plugins"**
   - If you don't see the prompt: go to **Settings → Community Plugins → Turn off Restricted Mode**
2. All plugins will activate automatically — no manual enabling needed

**Plugins included:**

| Plugin | Purpose |
|--------|---------|
| Dataview | Powers all dynamic tables and lists |
| Meta Bind | Inline editable fields on notes |
| QuickAdd | One-click note creation with templates |
| Templater | Advanced template scripting |
| Supercharged Links | Colored icons on links in notes |
| File Color | Colored folder names in the explorer |
| Dice Roller | Inline dice rolls throughout the vault |
| Calendarium | In-world campaign calendar |
| Excalidraw | Freehand drawing and maps |
| Hover Editor | Pop-up note preview and editing |
| Editing Toolbar | Formatting toolbar in the editor |
| Homepage | Auto-opens Homepage on launch |
| Style Settings | Theme customization controls |
| Pretty Properties | Cleaner property display |
| Various Complements | Autocomplete for note links |

---

## Step 3 — Verify the Theme

The vault uses the **ITS Theme** which must be active for the layout and callouts to display correctly.

1. Go to **Settings → Appearance**
2. Under **Themes**, confirm **ITS Theme** is selected
3. If not: click **Manage**, search for `ITS Theme`, install it, then set it as active

---

## Step 4 — Enable CSS Snippets

The vault's icons and colors in the file explorer require two CSS snippets to be active.

1. Go to **Settings → Appearance → CSS Snippets** (scroll to the bottom)
2. Make sure both of these are toggled **ON**:
   - ✅ `TTRPG-Icons` — adds icons and colors to internal note links
   - ✅ `TTRPG-Folders` — adds icons and colors to folders and key files in the explorer

> [!tip] If you don't see them
> Click the **refresh icon** (⟳) next to "CSS Snippets" to reload the list.

---

## Step 5 — (Optional) Import 5e Content

The vault includes a one-click importer that downloads reference notes from 5e.tools for spells, items, classes, races, backgrounds, feats, languages, deities, conditions, and optional features — handy for looking up rules for your character without leaving Obsidian.

> [!warning] License Disclaimer
> You are responsible for ensuring you have a valid license or legal right to the content you import. Content from the **SRD 5.1** is freely available under the Creative Commons license. All other sourcebooks require a valid purchase from the publisher.

**Requirements:** Python 3 must be installed. The importer will detect it automatically and offer to install it if missing.

**To import:**
1. Open **1.Tools/Buttons.md**
2. Scroll to the **🗄️ Vault** section
3. Click **"Import 5e.tools Data"**
4. Follow the prompts:
   - Choose your **source** (WotC official / specific books / all sources)
   - Select **which books** (if using specific books mode)
   - Select **content types** to import
   - Confirm and wait — a notification appears when complete

> [!tip] Safe to re-run
> The importer never overwrites existing notes. You can run it multiple times to add new content types or books without affecting notes you've already edited.

---

## Step 6 — Choose Your Vault Type

The first time you open the Homepage, a welcome card asks how you'll use this vault (you'll also be asked the first time you create a character):

- **One character, one campaign** — the simplest setup. Everything in the vault is yours; there are no pickers to manage.
- **Several characters or campaigns** — each character and campaign keeps its own notes. The Homepage shows only the active ones, and you switch with the **Change Character** / **Change Campaign** buttons.

> [!info] You can grow, but not shrink
> A single-character vault can be converted to multiple characters at any time from **1.Tools/Buttons.md → Vault → Convert to multiple characters** (nothing is deleted, and your existing notes are assigned to your current character and campaign). It can't be converted back.

---

## Step 7 — Create Your Character

Choose one:

**Option A — Import from D&D Beyond**
1. Make sure your D&D Beyond character sheet is set to **Public** (Share → Visibility)
2. Open **1.Tools/Buttons.md**
3. Click **"Import Character from D&D Beyond"**
4. Paste your character's URL or ID, optionally enter a campaign name, and confirm
5. Your full character sheet is generated automatically — stats, skills, spells, inventory, and features all filled in
6. The link to your D&D Beyond sheet is remembered on the note — after you level up or change gear, click **"Update Character from D&D Beyond"** to pull in the changes without losing anything you've written

**Option B — Create manually**
1. Open **1.Tools/Homepage.md**
2. Click **New Character** in the Quick Create panel — your character sheet will open automatically and becomes your active character
3. Set the campaign name with the button under the Homepage title (**Rename campaign** in a single-character vault, **Change Campaign** in a multi-character one)
4. Fill in your character details and start using the vault!

> [!tip] Requires Python 3
> The D&D Beyond importer needs Python 3, same as the 5e.tools importer above. The button will offer to install it automatically if it's missing.

---

## Feature Reference

### 🧰 Key Files

| File | Purpose |
|------|---------|
| **1.Tools/Homepage.md** | Your player dashboard — character overview, active quests, recent sessions |
| **1.Tools/Player Screen.md** | Session tool — your stats at a glance, dice rolls, rules quick reference |
| **1.Tools/Buttons.md** | All quick-create buttons organized by category |

### 📁 Folder Structure

```
My Character/         Your character sheet
Campaign Notes/
├── Journal/          In-character diary entries
├── Session Recaps/   Your notes from each session
├── Quests/           Quests you're tracking
├── NPCs Known/       People your character has met
└── Locations/        Places you've visited
Possessions/
├── Items/            Your items and equipment
└── Spells/           Your spells (if applicable)
Lore/                 World lore and reference notes (5e.tools imports land here)
z_Uncategorized/       Catch-all for new/unfiled notes (Obsidian's default for new files)
```

> [!tip] Unsorted Notes
> Any note you create without picking a folder — a quick scratch note, or a file dropped into Obsidian — lands in `z_Uncategorized/` automatically. Move it into a proper folder once you know what it is. This folder is personal scratch space: it's never touched by the updater and isn't included when you download the template.

### 🎨 Icon & Color System

Every note type has a matching color and emoji icon that appears on internal links and in the file explorer automatically based on the note's tags.

| Tag | Icon | Color |
|-----|------|-------|
| Player | ⚔️ | Gold |
| SessionRecap | 📝 | Mint |
| Quest | ⚡ | Yellow |
| NPCKnown | 👤 | Gray |
| Location | 🏰 | Orange |
| Spell | 🔮 | Lavender |
| Item | 🎒 | Teal |
| Journal | 📖 | Purple |

---

> [!abstract] 💬 Support & Feedback
> If you have questions or run into issues, refer to the documentation for each plugin linked in **Settings → Community Plugins**. The Obsidian community forum at [forum.obsidian.md](https://forum.obsidian.md) is also an excellent resource.
