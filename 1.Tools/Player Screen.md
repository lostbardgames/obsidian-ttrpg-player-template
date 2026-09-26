---
tags:
  - PlayerScreen
currentSession:
cssclasses:
  - wide-page
---

# ⚔️ Player Screen — `$= dv.page("z_Databases/Vault Hub/Player Settings")?.campaignName || "My Campaign"`

```dataviewjs
const S = dv.page("z_Databases/Vault Hub/Player Settings") ?? {};
const mode = S.vaultMode ?? null;
const arr = v => v == null ? [] : (typeof v === "object" && !v.path && Array.isArray(v.values)) ? v.values : Array.isArray(v) ? v : [v];
const nm = x => String(x?.path ? x.path.split("/").pop().replace(/\.md$/, "") : x ?? "").replace(/^\[\[|\]\]$/g, "").split("|")[0].split("/").pop().trim();
const chars = dv.pages('"My Character"');
const activeChar = S.characterName || (chars.length === 1 ? chars[0].file.name : "");
const activeCamp = S.campaignName || "";
const isLib = p => !!p.import_source;
const hasTag = (p, t) => arr(p.tags).includes(t);
const mine = (p, kind) => {
  if (mode !== "multi") return true;
  const have = kind === "campaign" ? arr(p.campaign).map(x => String(x).trim()).filter(Boolean) : arr(p.character ?? p.owner).map(nm).filter(Boolean);
  const want = kind === "campaign" ? activeCamp : activeChar;
  return have.length === 0 || !want || have.includes(want);
};
const run = n => app.commands.executeCommandById(`quickadd:choice:p1b2c3d4-0001-4000-8000-0000000000${n}`);
const btn = (label, n) => { const b = dv.container.createEl("button", { text: label, cls: "mb-button-inner mod-cta" }); b.style.marginRight = "8px"; b.onclick = () => run(n); };
const unassigned = () => {
  let n = 0;
  for (const d of ["Session Recaps", "Quests", "NPCs Known", "Locations"]) n += dv.pages(`"Campaign Notes/${d}"`).where(p => !arr(p.campaign).some(x => String(x).trim())).length;
  n += dv.pages('"Campaign Notes/Journal"').where(p => !arr(p.character).map(nm).some(Boolean)).length;
  n += dv.pages('"Possessions/Items"').where(p => !isLib(p) && !arr(p.owner).map(nm).some(Boolean)).length;
  n += dv.pages('"Possessions/Spells"').where(p => !isLib(p) && !arr(p.character).map(nm).some(Boolean)).length;
  return n;
};
if (!mode) {
  dv.paragraph("**👋 Welcome!** Before you start, choose how you'll use this vault — one character in one campaign, or several characters and campaigns that each keep their own notes. It takes a few seconds.");
  btn("Choose vault type", 16);
} else if (mode === "single") {
  dv.paragraph(`**Campaign:** ${activeCamp || "My Campaign"}`);
  btn("Rename campaign", 14);
} else {
  dv.paragraph(`**Campaign:** ${activeCamp || "—"} &nbsp;·&nbsp; **Character:** ${activeChar || "—"}`);
  if (!activeChar) dv.paragraph("⚠️ _Pick a character to see only their notes._");
  btn("Change Campaign", 14); btn("Change Character", 15);
  const n = unassigned();
  if (n > 0) { dv.paragraph(`⚠️ ${n} note(s) aren't assigned to a character or campaign yet, so they show for everyone.`); btn("Assign unfiled notes", 17); }
}
```

Session: `INPUT[text(placeholder(Session Recap)):currentSession]`

---

> [!column|2 no-t]
>
> > [!info|no-t] **⚔️ My Stats**
> >
> > ```dataviewjs
> > const S = dv.page("z_Databases/Vault Hub/Player Settings") ?? {};
> > const mode = S.vaultMode ?? null;
> > const arr = v => v == null ? [] : (typeof v === "object" && !v.path && Array.isArray(v.values)) ? v.values : Array.isArray(v) ? v : [v];
> > const nm = x => String(x?.path ? x.path.split("/").pop().replace(/\.md$/, "") : x ?? "").replace(/^\[\[|\]\]$/g, "").split("|")[0].split("/").pop().trim();
> > const chars = dv.pages('"My Character"');
> > const activeChar = S.characterName || (chars.length === 1 ? chars[0].file.name : "");
> > const activeCamp = S.campaignName || "";
> > const isLib = p => !!p.import_source;
> > const hasTag = (p, t) => arr(p.tags).includes(t);
> > const mine = (p, kind) => {
> >   if (mode !== "multi") return true;
> >   const have = kind === "campaign" ? arr(p.campaign).map(x => String(x).trim()).filter(Boolean) : arr(p.character ?? p.owner).map(nm).filter(Boolean);
> >   const want = kind === "campaign" ? activeCamp : activeChar;
> >   return have.length === 0 || !want || have.includes(want);
> > };
> > const name = activeChar;
> > if (!name) {
> >   dv.paragraph(mode === "multi" ? "_No character selected — use **Change Character** above._" : "_No character yet — use **New Character** or **Import Character from D&D Beyond**._");
> > } else {
> >   const chars2 = chars.where(c => c.file.name === name);
> >   if (chars2.length === 0) {
> >     dv.paragraph(`_No character found: "${name}"_`);
> >   } else {
> >     const c = chars2[0];
> >     dv.table(
> >       ["Stat", "Value"],
> >       [
> >         ["**HP**", `**${c.hp_current ?? "?"}** / ${c.hp_max ?? "?"}  *(Temp: ${c.hp_temp ?? 0})*`],
> >         ["**AC**", c.ac ?? "—"],
> >         ["**Speed**", `${c.speed ?? 30} ft`],
> >         ["**Initiative**", c.dex ? `+${Math.floor((c.dex - 10) / 2)}` : "—"],
> >         ["**Passive Perc.**", c.passivePerception ?? "—"],
> >         ["**Spell Save DC**", c.spell_save_dc ?? "—"],
> >         ["**Spell Atk**", c.spell_attack_bonus ? `+${c.spell_attack_bonus}` : "—"],
> >         ["**Prof. Bonus**", c.proficiencyBonus ? `+${c.proficiencyBonus}` : "—"],
> >         ["**Condition**", Array.isArray(c.condition) ? c.condition.join(", ") : (c.condition ?? "Healthy")]
> >       ]
> >     );
> >   }
> > }
> > ```
> >
> > *Click character name to update HP, AC, and conditions live.*
>
> > [!warning|no-t] **🎲 Initiative & Dice**
> >
> > `dice: 1d20` ← Roll d20
> >
> > | Die | Roll |
> > |-----|------|
> > | d4 | `dice: 1d4` |
> > | d6 | `dice: 1d6` |
> > | d8 | `dice: 1d8` |
> > | d10 | `dice: 1d10` |
> > | d12 | `dice: 1d12` |
> > | d20 | `dice: 1d20` |
> > | d100 | `dice: 1d100` |
> > | 2d6 | `dice: 2d6` |
> > | 4d6kh3 | `dice: 4d6kh3` |
> >
> > **Death Saves**
> > Successes: ☐ ☐ ☐ &nbsp;&nbsp; Failures: ☐ ☐ ☐

---

## 🔮 Spell Slots

> [!column|3 no-t]
>
> > [!note|no-t] **Slots**
> >
> > | Level | Total | Used |
> > |:-----:|:-----:|:----:|
> > | 1st | | |
> > | 2nd | | |
> > | 3rd | | |
> > | 4th | | |
> > | 5th | | |
>
> > [!note|no-t] **Prepared Spells**
> >
> > ```dataviewjs
> > const S = dv.page("z_Databases/Vault Hub/Player Settings") ?? {};
> > const mode = S.vaultMode ?? null;
> > const arr = v => v == null ? [] : (typeof v === "object" && !v.path && Array.isArray(v.values)) ? v.values : Array.isArray(v) ? v : [v];
> > const nm = x => String(x?.path ? x.path.split("/").pop().replace(/\.md$/, "") : x ?? "").replace(/^\[\[|\]\]$/g, "").split("|")[0].split("/").pop().trim();
> > const chars = dv.pages('"My Character"');
> > const activeChar = S.characterName || (chars.length === 1 ? chars[0].file.name : "");
> > const activeCamp = S.campaignName || "";
> > const isLib = p => !!p.import_source;
> > const hasTag = (p, t) => arr(p.tags).includes(t);
> > const mine = (p, kind) => {
> >   if (mode !== "multi") return true;
> >   const have = kind === "campaign" ? arr(p.campaign).map(x => String(x).trim()).filter(Boolean) : arr(p.character ?? p.owner).map(nm).filter(Boolean);
> >   const want = kind === "campaign" ? activeCamp : activeChar;
> >   return have.length === 0 || !want || have.includes(want);
> > };
> > const rows = dv.pages('"Possessions/Spells"').where(p => !isLib(p) && p.prepared === true && mine(p, "character")).sort(p => p.spellLevel);
> > if (rows.length) dv.list(rows.map(p => p.file.link)); else dv.paragraph("_None prepared._");
> > ```
>
> > [!note|no-t] **Cantrips**
> >
> > ```dataviewjs
> > const S = dv.page("z_Databases/Vault Hub/Player Settings") ?? {};
> > const mode = S.vaultMode ?? null;
> > const arr = v => v == null ? [] : (typeof v === "object" && !v.path && Array.isArray(v.values)) ? v.values : Array.isArray(v) ? v : [v];
> > const nm = x => String(x?.path ? x.path.split("/").pop().replace(/\.md$/, "") : x ?? "").replace(/^\[\[|\]\]$/g, "").split("|")[0].split("/").pop().trim();
> > const chars = dv.pages('"My Character"');
> > const activeChar = S.characterName || (chars.length === 1 ? chars[0].file.name : "");
> > const activeCamp = S.campaignName || "";
> > const isLib = p => !!p.import_source;
> > const hasTag = (p, t) => arr(p.tags).includes(t);
> > const mine = (p, kind) => {
> >   if (mode !== "multi") return true;
> >   const have = kind === "campaign" ? arr(p.campaign).map(x => String(x).trim()).filter(Boolean) : arr(p.character ?? p.owner).map(nm).filter(Boolean);
> >   const want = kind === "campaign" ? activeCamp : activeChar;
> >   return have.length === 0 || !want || have.includes(want);
> > };
> > const rows = dv.pages('"Possessions/Spells"').where(p => !isLib(p) && p.spellLevel === 0 && mine(p, "character")).sort(p => p.file.name);
> > if (rows.length) dv.list(rows.map(p => p.file.link)); else dv.paragraph("_No cantrips yet._");
> > ```

---

## 📝 Session Notes

> [!column|2 no-t]
>
> > [!note|no-t] **📋 Current Session**
> >
> > `VIEW[{currentSession}][link]`
> >
> > ```meta-bind-button
> > label: "New Session Recap"
> > style: primary
> > actions:
> >   - type: command
> >     command: quickadd:choice:p1b2c3d4-0001-4000-8000-000000000003
> > ```
> >
> > ```meta-bind-button
> > label: "New NPC Known"
> > style: default
> > actions:
> >   - type: command
> >     command: quickadd:choice:p1b2c3d4-0001-4000-8000-000000000005
> > ```
> >
> > ```meta-bind-button
> > label: "New Journal Entry"
> > style: default
> > actions:
> >   - type: command
> >     command: quickadd:choice:p1b2c3d4-0001-4000-8000-000000000002
> > ```
>
> > [!note|no-t] **✏️ Live Notes**
> >
> > *(Quick notes during the session — move important stuff to your Session Recap afterwards)*
> >
> > ---
> >

---

## 📖 Quick Rules Reference

> [!column|3 no-t]
>
> > [!danger|no-t] **💀 Conditions**
> >
> > **Blinded** — Can't see; attacks against you have advantage; your attacks have disadvantage.
> >
> > **Charmed** — Can't attack the charmer; charmer has advantage on social checks against you.
> >
> > **Deafened** — Can't hear; automatically fails sound-based checks.
> >
> > **Exhaustion** — Cumulative effects at each level (1–6). Level 6 = death.
> >
> > **Frightened** — Disadvantage on checks/attacks while source is in sight; can't move closer.
> >
> > **Grappled** — Speed = 0. Ends if grappler is incapacitated or creature is moved away.
> >
> > **Incapacitated** — Can't take actions or reactions.
> >
> > **Invisible** — Can't be seen; attacks against you have disadvantage; your attacks have advantage.
> >
> > **Paralyzed** — Incapacitated, can't move or speak. Attacks against you have advantage. Melee hits within 5 ft are critical.
> >
> > **Poisoned** — Disadvantage on attack rolls and ability checks.
> >
> > **Prone** — Movement costs double; melee attacks against you have advantage; ranged have disadvantage. Standing costs half movement.
> >
> > **Restrained** — Speed = 0; attacks against you have advantage; your attacks have disadvantage; disadvantage on DEX saves.
> >
> > **Stunned** — Incapacitated, can't move. Attacks against you have advantage. Fails STR and DEX saves.
> >
> > **Unconscious** — Incapacitated, can't move or speak, drops held items, prone. Attacks have advantage; melee hits within 5 ft are critical.
>
> > [!tip|no-t] **⚡ Action Economy**
> >
> > **Action**
> > Attack, Cast a Spell, Dash, Disengage, Dodge, Help, Hide, Ready, Search, Use Object
> >
> > **Bonus Action**
> > Class features, spells with BA casting time, two-weapon fighting (light weapons)
> >
> > **Reaction**
> > Opportunity Attack, Ready trigger, Shield, Counterspell, Hellish Rebuke
> >
> > **Free (same turn)**
> > Draw/sheathe a weapon, drop an item, speak a few words, interact with one object
> >
> > **Movement**
> > Split freely before/during/after actions. Difficult terrain costs double.
> >
> > ---
> >
> > **Opportunity Attacks**
> > Triggered when a creature you can see leaves your reach without Disengaging. Uses your reaction.
> >
> > **Grappling & Shoving**
> > Contested STR (Athletics) vs STR (Athletics) or DEX (Acrobatics). Shove: knock prone or push 5 ft.
> >
> > **Two-Weapon Fighting**
> > Bonus action attack with second light weapon when you attack with a light weapon. No ability modifier to damage (unless negative).
>
> > [!abstract|no-t] **🎯 Key DCs & Rules**
> >
> > **Common DCs**
> > | Task Difficulty | DC |
> > |---|:---:|
> > | Very Easy | 5 |
> > | Easy | 10 |
> > | Medium | 15 |
> > | Hard | 20 |
> > | Very Hard | 25 |
> > | Nearly Impossible | 30 |
> >
> > ---
> >
> > **Death Saves**
> > Roll d20 on your turn. **10+** = success; **1–9** = failure. 3 successes = stable; 3 failures = dead. Natural **1** = 2 failures. Natural **20** = 1 HP, conscious.
> >
> > Damage at 0 HP = 1 failure (melee within 5 ft = 2 failures). Being healed cancels all death saves.
> >
> > ---
> >
> > **Concentration**
> > Damaged while concentrating → CON save DC = max(10, half damage). Fail = spell ends. Incapacitated or killed also ends concentration.
> >
> > ---
> >
> > **Cover**
> > **Half (+2 AC/DEX saves)** — Low wall, furniture, creature. **Three-Quarters (+5)** — Arrow slit, thick tree. **Total** — Complete cover, can't be targeted directly.
> >
> > ---
> >
> > **Short Rest** — 1+ hours, spend Hit Dice to heal.
> > **Long Rest** — 8+ hours, regain all HP and half Hit Dice (min 1).
