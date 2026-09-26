---
tags:
  - Homepage
cssclasses:
  - wide-page
---

# ⚔️ `$= dv.page("z_Databases/Vault Hub/Player Settings")?.campaignName || "My Campaign"`

> [!column|2 no-t]
>
> > **Campaign:** `$= dv.page("z_Databases/Vault Hub/Player Settings")?.campaignName || "My Campaign"`
> >
> > ```meta-bind-button
> > label: "Change Campaign"
> > style: primary
> > actions:
> >   - type: command
> >     command: quickadd:choice:p1b2c3d4-0001-4000-8000-000000000014
> > ```
>
> > **Character:** `$= dv.page("z_Databases/Vault Hub/Player Settings")?.characterName || (dv.pages('"My Character"').length == 1 ? dv.pages('"My Character"')[0].file.name : "None selected")`
> >
> > ```meta-bind-button
> > label: "Change Character"
> > style: primary
> > actions:
> >   - type: command
> >     command: quickadd:choice:p1b2c3d4-0001-4000-8000-000000000015
> > ```

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
> > const s = dv.page("z_Databases/Vault Hub/Player Settings");
> > const all = dv.pages('"My Character"');
> > const name = s?.characterName || (all.length === 1 ? all[0].file.name : "");
> > if (!name) {
> >   dv.paragraph("_No character selected — use **Change Character** above._");
> > } else {
> >   const chars = dv.pages('"My Character"').where(c => c.file.name === name);
> >   if (chars.length === 0) {
> >     dv.paragraph(`_No character found named "${name}" in My Character/._`);
> >   } else {
> >     const c = chars[0];
> >     dv.table(
> >       ["Field", "Value"],
> >       [
> >         ["**Name**", c.file.link],
> >         ["**Class**", c.class ? String(c.class) : "—"],
> >         ["**Level**", c.level ?? "—"],
> >         ["**HP**", `${c.hp_current ?? "?"}/${c.hp_max ?? "?"}`],
> >         ["**AC**", c.ac ?? "—"],
> >         ["**Condition**", Array.isArray(c.condition) ? c.condition.join(", ") : (c.condition ?? "Healthy")]
> >       ]
> >     );
> >   }
> > }
> > ```
>
> > [!abstract] 👁️ At a Glance
> >
> > **⚡ Active Quests**
> >
> > ```dataview
> > LIST FROM "Campaign Notes/Quests"
> > WHERE status = "Active" OR status = null
> > SORT file.mtime DESC
> > LIMIT 6
> > ```
> >
> > **📝 Recent Sessions**
> >
> > ```dataview
> > TABLE WITHOUT ID
> >   file.link as "Session",
> >   sessionNumber as "#",
> >   sessionDate as "Date"
> > FROM "Campaign Notes/Session Recaps"
> > WHERE econtains(tags, "SessionRecap")
> > SORT sessionDate DESC
> > LIMIT 4
> > ```

---

## 📓 Journal

```dataview
TABLE WITHOUT ID
  file.link as "Entry",
  realDate as "Date",
  mood as "Mood",
  location as "Location"
FROM "Campaign Notes/Journal"
WHERE econtains(tags, "Journal")
SORT realDate DESC
LIMIT 5
```

---

## 🗡️ Possessions

> [!column|2 no-t]
>
> > [!note] ⚔️ Items
> >
> > ```dataview
> > TABLE WITHOUT ID
> >   file.link as "Item",
> >   itemType as "Type",
> >   rarity as "Rarity",
> >   isMagical as "Magic"
> > FROM "Possessions/Items"
> > SORT file.name ASC
> > LIMIT 10
> > ```
>
> > [!note] 🔮 Spells
> >
> > ```dataview
> > TABLE WITHOUT ID
> >   file.link as "Spell",
> >   spellLevel as "Level",
> >   school as "School",
> >   prepared as "Prepared"
> > FROM "Possessions/Spells"
> > SORT spellLevel ASC
> > LIMIT 10
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
