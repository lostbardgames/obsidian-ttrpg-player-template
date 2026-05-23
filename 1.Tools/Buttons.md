
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

> [!column|2 no-t]
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
> > Permanently deletes all campaign data (character, journal, session recaps, quests, NPCs, locations, possessions). ⚠️ Files are permanently deleted and cannot be recovered.
