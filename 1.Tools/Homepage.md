---
tags:
  - Homepage
cssclasses:
  - wide-page
---

# ⚔️ `$= dv.page("z_Databases/Vault Hub/Player Settings")?.campaignName || "My Campaign"`

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

---

> [!column|3 no-t]
>
> > [!tip] ⚡ Quick Create
> >
> > ```meta-bind-button
> > label: "New Character"
> > style: primary
> > actions:
> >   - type: command
> >     command: quickadd:choice:p1b2c3d4-0001-4000-8000-000000000001
> > ```
> >
> > ```meta-bind-button
> > label: "New Journal Entry"
> > style: primary
> > actions:
> >   - type: command
> >     command: quickadd:choice:p1b2c3d4-0001-4000-8000-000000000002
> > ```
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
> > label: "New Quest"
> > style: primary
> > actions:
> >   - type: command
> >     command: quickadd:choice:p1b2c3d4-0001-4000-8000-000000000004
> > ```
> >
> > ```meta-bind-button
> > label: "New NPC Known"
> > style: primary
> > actions:
> >   - type: command
> >     command: quickadd:choice:p1b2c3d4-0001-4000-8000-000000000005
> > ```
> >
> > ```meta-bind-button
> > label: "New Location"
> > style: primary
> > actions:
> >   - type: command
> >     command: quickadd:choice:p1b2c3d4-0001-4000-8000-000000000006
> > ```
> >
> > → [[Buttons|All Buttons]]
>
> > [!info] ⚔️ My Character
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
> >   const c = chars.where(x => x.file.name === name)[0];
> >   if (!c) {
> >     dv.paragraph(`_No character found named "${name}" in My Character/._`);
> >   } else {
> >     dv.table(["Field", "Value"], [
> >       ["**Name**", c.file.link],
> >       ["**Class**", c.class ? String(c.class) : "—"],
> >       ["**Level**", c.level ?? "—"],
> >       ["**HP**", `${c.hp_current ?? "?"}/${c.hp_max ?? "?"}`],
> >       ["**AC**", c.ac ?? "—"],
> >       ["**Condition**", Array.isArray(c.condition) ? c.condition.join(", ") : (c.condition ?? "Healthy")]
> >     ]);
> >   }
> > }
> > ```
>
> > [!abstract] 👁️ At a Glance
> >
> > **⚡ Active Quests**
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
> > const rows = dv.pages('"Campaign Notes/Quests"').where(p => (p.status == null || p.status === "Active") && mine(p, "campaign")).sort(p => p.file.mtime, "desc").slice(0, 6);
> > if (rows.length) dv.list(rows.map(p => p.file.link)); else dv.paragraph("_No active quests._");
> > ```
> >
> > **📝 Recent Sessions**
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
> > const rows = dv.pages('"Campaign Notes/Session Recaps"').where(p => hasTag(p, "SessionRecap") && mine(p, "campaign")).sort(p => p.sessionDate, "desc").slice(0, 4);
> > dv.table(["Session", "#", "Date"], rows.map(p => [p.file.link, p.sessionNumber, p.sessionDate]));
> > ```

---

## 📓 Journal

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
const rows = dv.pages('"Campaign Notes/Journal"').where(p => hasTag(p, "Journal") && mine(p, "character")).sort(p => p.realDate, "desc").slice(0, 5);
dv.table(["Entry", "Date", "Mood", "Location"], rows.map(p => [p.file.link, p.realDate, p.mood, p.location]));
```

---

## 🗡️ Possessions

> [!column|2 no-t]
>
> > [!note] ⚔️ Items
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
> > const rows = dv.pages('"Possessions/Items"').where(p => !isLib(p) && mine(p, "character")).sort(p => p.file.name).slice(0, 10);
> > dv.table(["Item", "Type", "Rarity", "Magic"], rows.map(p => [p.file.link, p.itemType, p.rarity, p.isMagical]));
> > ```
>
> > [!note] 🔮 Spells
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
> > const rows = dv.pages('"Possessions/Spells"').where(p => !isLib(p) && mine(p, "character")).sort(p => p.spellLevel).slice(0, 10);
> > dv.table(["Spell", "Level", "School", "Prepared"], rows.map(p => [p.file.link, p.spellLevel, p.school, p.prepared]));
> > ```

---

## 🎲 Inspiration

> [!column|3 no-t]
>
> > [!dice] 🎲 Dice
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
>
> > [!question] 💡 Character Sparks
> >
> > **Character Motivation** `dice: 1d12`
> > 1. Justice / Revenge
> > 2. Loyalty to the party
> > 3. Personal redemption
> > 4. Protecting someone
> > 5. Proving myself
> > 6. Uncovering the truth
> > 7. Survival
> > 8. Finding a place to belong
> > 9. Wealth / Security
> > 10. Serving a higher calling
> > 11. Curiosity / Adventure
> > 12. Fulfilling a promise
>
> > [!question] 📖 Journal Prompts
> >
> > **In-Character Prompts** `dice: 1d8`
> > 1. What was my character thinking during the hardest moment this session?
> > 2. How has my character changed since we started?
> > 3. What does my character think of a specific party member?
> > 4. What is my character most afraid of right now?
> > 5. What does my character want more than anything?
> > 6. What would my character never do — and why?
> > 7. Describe the last battle from my character's eyes
> > 8. What would my character write in a letter home?
