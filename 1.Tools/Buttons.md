
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
> > style: default
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
> > Permanently deletes all campaign data (character, journal, session recaps, quests, NPCs, locations, possessions). ⚠️ Files are permanently deleted and cannot be recovered.
