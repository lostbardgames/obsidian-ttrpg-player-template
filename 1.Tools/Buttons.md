
## ⚔️ Character

> [!column|2 no-t]
>
> > [!note|no-t]
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
> > label: "Import Character from D&D Beyond"
> > style: primary
> > actions:
> >   - type: command
> >     command: quickadd:choice:p1b2c3d4-0001-4000-8000-000000000012
> > ```
> >
> > ```meta-bind-button
> > label: "Update Character from D&D Beyond"
> > style: primary
> > actions:
> >   - type: command
> >     command: quickadd:choice:p1b2c3d4-0001-4000-8000-000000000013
> > ```
>
> > [!note|no-t]
> >
> > ```meta-bind-button
> > label: "New Journal Entry"
> > style: primary
> > actions:
> >   - type: command
> >     command: quickadd:choice:p1b2c3d4-0001-4000-8000-000000000002
> > ```

---

## 📓 Campaign Notes

> [!column|2 no-t]
>
> > [!note|no-t]
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
>
> > [!note|no-t]
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
> > label: "New Location Visited"
> > style: primary
> > actions:
> >   - type: command
> >     command: quickadd:choice:p1b2c3d4-0001-4000-8000-000000000006
> > ```

---

## 💼 Possessions

> [!column|2 no-t]
>
> > [!note|no-t]
> >
> > ```meta-bind-button
> > label: "New Item"
> > style: primary
> > actions:
> >   - type: command
> >     command: quickadd:choice:p1b2c3d4-0001-4000-8000-000000000007
> > ```
>
> > [!note|no-t]
> >
> > ```meta-bind-button
> > label: "New Spell"
> > style: primary
> > actions:
> >   - type: command
> >     command: quickadd:choice:p1b2c3d4-0001-4000-8000-000000000008
> > ```

---

## 🗄️ Vault

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
  dv.paragraph("**Vault type:** not chosen yet.");
  btn("Choose vault type", 16);
} else if (mode === "single") {
  dv.paragraph("**Vault type:** one character, one campaign.");
  btn("Convert to multiple characters", 16);
  dv.paragraph("_One-way: a vault can't be converted back to single-character. Nothing is deleted._");
} else {
  dv.paragraph("**Vault type:** several characters or campaigns. _This can't be switched back to single-character._");
  const n = unassigned();
  if (n > 0) { dv.paragraph(`⚠️ ${n} note(s) aren't assigned to a character or campaign yet.`); btn("Assign unfiled notes", 17); }
}
```

> [!column|3 no-t]
>
> > [!success|no-t] **Import Data**
> >
> > ```meta-bind-button
> > label: "Import 5e.tools Data"
> > style: primary
> > actions:
> >   - type: command
> >     command: quickadd:choice:p1b2c3d4-0001-4000-8000-000000000011
> > ```
> >
> > Downloads reference notes for spells, items, classes, races, backgrounds, feats, languages, deities, conditions, and optional features from 5e.tools. Pick WotC official, specific books, or all sources.
> >
> > Non-destructive — existing notes are never overwritten, so it's safe to re-run. If Python 3 is not installed, the button will offer to install it for you. Requires an internet connection.
> >
> > > [!warning] ⚠️ License Disclaimer
> > > You are responsible for ensuring you have a valid license or legal right to access the content you import. This tool does not grant any rights to copyrighted material. Content from the SRD 5.1 is available under the Creative Commons license. All other sourcebooks require a valid purchase or license from the publisher.
>
> > [!info|no-t] **Update Vault**
> >
> > ```meta-bind-button
> > label: "Check for Updates"
> > style: primary
> > actions:
> >   - type: command
> >     command: quickadd:choice:p1b2c3d4-0001-4000-8000-000000000009
> > ```
> >
> > 📦 **Installed version:** v`$= app.vault.adapter.read("version.json").then(f => JSON.parse(f).version)`
> >
> > Checks GitHub for a newer version of the Player Template and walks you through the update. Your campaign data is never touched.
>
> > [!danger] ⚠️ Danger Zone
> >
> > ```meta-bind-button
> > label: "Reset Vault"
> > style: destructive
> > actions:
> >   - type: command
> >     command: quickadd:choice:p1b2c3d4-0001-4000-8000-000000000010
> > ```
> >
> > Permanently deletes campaign data (characters, journal, session recaps, quests, NPCs, locations, possessions). In multiple-character mode you can reset just one character or one campaign instead. Your vault type is never reset. ⚠️ Files are permanently deleted and cannot be recovered.
