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
> > ```dataviewjs
> > const S = dv.page("z_Databases/Vault Hub/Player Settings") ?? {};
> > const arr = v => v == null ? [] : (typeof v === "object" && !v.path && Array.isArray(v.values)) ? v.values : Array.isArray(v) ? v : [v];
> > const nm = x => String(x?.path ? x.path.split("/").pop().replace(/\.md$/, "") : x ?? "").replace(/^\[\[|\]\]$/g, "").split("|")[0].split("/").pop().trim();
> > const chars = dv.pages('"My Character"');
> > const name = S.characterName || (chars.length === 1 ? chars[0].file.name : "");
> > const edition = S.rulesEdition === "2014" ? "2014" : "2024";
> > const c = name ? chars.where(x => x.file.name === name)[0] : null;
> > if (!c) {
> >   dv.paragraph("_Pick a character to track spell slots._");
> > } else {
> >   // Slots per spell level for a full caster of level 1-20
> >   const FULL = [null, [2], [3], [4, 2], [4, 3], [4, 3, 2], [4, 3, 3], [4, 3, 3, 1], [4, 3, 3, 2], [4, 3, 3, 3, 1], [4, 3, 3, 3, 2], [4, 3, 3, 3, 2, 1], [4, 3, 3, 3, 2, 1], [4, 3, 3, 3, 2, 1, 1], [4, 3, 3, 3, 2, 1, 1], [4, 3, 3, 3, 2, 1, 1, 1], [4, 3, 3, 3, 2, 1, 1, 1], [4, 3, 3, 3, 2, 1, 1, 1, 1], [4, 3, 3, 3, 3, 1, 1, 1, 1], [4, 3, 3, 3, 3, 2, 1, 1, 1], [4, 3, 3, 3, 3, 2, 2, 1, 1]];
> >   // Warlock Pact Magic: [slots, slot level]
> >   const PACT = [null, [1, 1], [2, 1], [2, 2], [2, 2], [2, 3], [2, 3], [2, 4], [2, 4], [2, 5], [2, 5], [3, 5], [3, 5], [3, 5], [3, 5], [3, 5], [3, 5], [4, 5], [4, 5], [4, 5], [4, 5]];
> >   const clamp = l => Math.max(0, Math.min(20, l));
> >   const up = (n, d) => Math.ceil(n / d), down = (n, d) => Math.floor(n / d);
> >
> >   // Class levels: "Cleric 5 (Tempest Domain)" per class (imported characters), else class + level
> >   const entries = arr(c.classLevels).map(s => { const m = String(s).match(/^(.+?)\s+(\d+)(?:\s*\((.*)\))?$/); return m ? { cls: m[1].trim(), lvl: +m[2], sub: m[3] || "" } : null; }).filter(Boolean);
> >   if (!entries.length && c.class) entries.push({ cls: nm(c.class), lvl: Number(c.level) || 1, sub: nm(c.subclass) });
> >   const kind = e => {
> >     const n = e.cls.toLowerCase();
> >     if (/^(bard|cleric|druid|sorcerer|wizard)/.test(n)) return "full";
> >     if (/^(paladin|ranger)/.test(n)) return "half";
> >     if (/^artificer/.test(n)) return "artificer";
> >     if (/^fighter/.test(n) && /eldritch knight/i.test(e.sub)) return "third";
> >     if (/^rogue/.test(n) && /arcane trickster/i.test(e.sub)) return "third";
> >     if (/^warlock/.test(n)) return "pact";
> >     return null;
> >   };
> >   const casters = entries.filter(e => ["full", "half", "artificer", "third"].includes(kind(e)));
> >   const lock = entries.find(e => kind(e) === "pact");
> >
> >   // Single-class casters use their own class table; multiclass uses the combined caster level.
> >   // 2024 rounds half-caster levels up; 2014 rounds them down (Artificer always up). Thirds round down.
> >   let total = [];
> >   if (casters.length === 1) {
> >     const e = casters[0], k = kind(e);
> >     if (k === "full") total = FULL[clamp(e.lvl)] || [];
> >     else if (k === "half") total = (edition === "2014" && e.lvl < 2) ? [] : (FULL[clamp(up(e.lvl, 2))] || []);
> >     else if (k === "artificer") total = FULL[clamp(up(e.lvl, 2))] || [];
> >     else total = e.lvl < 3 ? [] : (FULL[clamp(up(e.lvl, 3))] || []);
> >   } else if (casters.length > 1) {
> >     let cl = 0;
> >     for (const e of casters) {
> >       const k = kind(e);
> >       cl += k === "full" ? e.lvl : k === "artificer" ? up(e.lvl, 2) : k === "half" ? (edition === "2014" ? down(e.lvl, 2) : up(e.lvl, 2)) : down(e.lvl, 3);
> >     }
> >     total = FULL[clamp(cl)] || [];
> >   }
> >   const pact = lock ? PACT[clamp(lock.lvl)] : null;
> >
> >   const ord = n => ["1st", "2nd", "3rd"][n - 1] ?? `${n}th`;
> >   const file = app.vault.getAbstractFileByPath(c.file.path);
> >   const stored = arr(c.spellSlotsUsed).map(Number);
> >   const state = { used: Array.from({ length: 9 }, (_, i) => Math.min(stored[i] || 0, total[i] || 0)), pact: Math.min(Number(c.pactSlotsUsed) || 0, pact ? pact[0] : 0) };
> >   const save = () => app.fileManager.processFrontMatter(file, fm => { fm.spellSlotsUsed = [...state.used]; if (pact) fm.pactSlotsUsed = state.pact; });
> >
> >   const box = dv.container.createDiv();
> >   const draw = () => {
> >     box.empty();
> >     if (!total.length && !pact) { box.createEl("p", { text: "No spell slots for this class." }); return; }
> >     const tbl = box.createEl("table");
> >     const hr = tbl.createEl("thead").createEl("tr");
> >     for (const h of ["Level", "Total", "Used", "Slots"]) hr.createEl("th", { text: h });
> >     const body = tbl.createEl("tbody");
> >     const row = (label, n, used, set) => {
> >       const tr = body.createEl("tr");
> >       tr.createEl("td", { text: label });
> >       tr.createEl("td", { text: String(n) });
> >       tr.createEl("td", { text: String(used) });
> >       const td = tr.createEl("td");
> >       for (let i = 0; i < n; i++) {
> >         const avail = i < n - used;
> >         const pip = td.createEl("span", { text: avail ? "●" : "○" });
> >         pip.style.cursor = "pointer"; pip.style.marginRight = "4px";
> >         pip.onclick = () => { set(avail ? used + 1 : used - 1); draw(); save(); };
> >       }
> >     };
> >     total.forEach((n, i) => row(ord(i + 1), n, state.used[i], v => { state.used[i] = v; }));
> >     if (pact) row(`Pact (${ord(pact[1])})`, pact[0], state.pact, v => { state.pact = v; });
> >
> >     const bar = box.createDiv();
> >     const rest = (label, fn) => {
> >       const b = bar.createEl("button", { text: label, cls: "mb-button-inner mod-cta" });
> >       b.style.marginRight = "8px";
> >       b.onclick = () => { fn(); draw(); save(); };
> >     };
> >     rest("Long Rest", () => { state.used = state.used.map(() => 0); state.pact = 0; });
> >     if (pact) rest("Short Rest", () => { state.pact = 0; });
> >     const cap = box.createEl("p");
> >     cap.createEl("small", { text: `${entries.map(e => `${e.cls} ${e.lvl}`).join(" / ")} · ${edition === "2014" ? "5e (2014)" : "5.5e (2024)"} slot rules · click a slot to spend or restore it` });
> >   };
> >   draw();
> > }
> > ```
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
> > style: primary
> > actions:
> >   - type: command
> >     command: quickadd:choice:p1b2c3d4-0001-4000-8000-000000000005
> > ```
> >
> > ```meta-bind-button
> > label: "New Journal Entry"
> > style: primary
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

```dataviewjs
const SETTINGS = "z_Databases/Vault Hub/Player Settings.md";
const S = dv.page("z_Databases/Vault Hub/Player Settings") ?? {};
let edition = S.rulesEdition === "2014" ? "2014" : "2024";
const REF = {
  "2014": ["z_Templates/Reference/Quick Rules - 5e (2014).md"],
  "2024": ["z_Templates/Reference/Quick Rules - 5.5e (2024).md", "z_Templates/Reference/Weapon Mastery (2024).md"],
};
const save = async ed => {
  let f = app.vault.getAbstractFileByPath(SETTINGS);
  if (!f) {
    try { await app.vault.createFolder("z_Databases/Vault Hub"); } catch (e) { /* already exists */ }
    f = await app.vault.create(SETTINGS, "---\ntags:\n  - Settings\ncampaignName: ''\ncharacterName: ''\n---\n\nActive campaign and character, and the vault type. Change them with the buttons on the Homepage.\n");
  }
  await app.fileManager.processFrontMatter(f, fm => { fm.rulesEdition = ed; });
};
const strip = t => String(t ?? "").replace(/^---\n[\s\S]*?\n---\n?/, "");
const bar = dv.container.createDiv();
const body = dv.container.createDiv();
const show = async () => {
  bar.empty(); body.empty();
  for (const [ed, label] of [["2014", "5e (2014)"], ["2024", "5.5e (2024)"]]) {
    const b = bar.createEl("button", { text: label, cls: "mb-button-inner" + (ed === edition ? " mod-cta" : "") });
    b.style.marginRight = "8px";
    b.onclick = async () => { edition = ed; await show(); await save(ed); };
  }
  for (const path of REF[edition]) {
    const text = await dv.io.load(path);
    if (text == null) body.createEl("p", { text: `Reference note missing: ${path} — run Check for Updates.` });
    else dv.el("div", strip(text), { container: body });
  }
};
await show();
```
