---
tags:
  - Character
  - Player
art: "[[PlaceholderCharacter.png]]"
sketch:
aliases:
species:
class:
subclass:
background:
alignment:
gender:
pronouns:
sexuality:
age:
birthday:
languages: []
occupation: []
organizations: []
religions: []
condition:
  - Healthy
currentLocation: []
campaign:
level: 1
experience: 0
experience_next: 300
proficiencyBonus: 2
passivePerception: 10
passiveInsight: 10
passiveInvestigation: 10
str: 10
dex: 10
con: 10
int: 10
wis: 10
cha: 10
hp_max: 0
hp_current: 0
hp_temp: 0
ac: 10
speed: 30
hitDie:
isSpellcaster: false
spellcastingAbility:
spell_save_dc: 0
spell_attack_bonus: 0
---

> [!infobox | no-blending black]+ <font color="#ffffff">Infobox</font>
>
> `VIEW[!{art}][text(renderMarkdown)]`
>
> # Bio
> | | |
> |---|---|
> | **Aliases** | `VIEW[{aliases}][text]` |
> | **Species** | `VIEW[{species}][link]` |
> | **Class** | `VIEW[{class}][link]` |
> | **Subclass** | `VIEW[{subclass}][link]` |
> | **Background** | `VIEW[{background}][link]` |
> | **Alignment** | `VIEW[{alignment}][text]` |
> | **Gender** | `VIEW[{gender}][text]` |
> | **Pronouns** | `VIEW[{pronouns}][text]` |
> | **Age** | `VIEW[{age}][text]` |
>
> # Details
> | | |
> |---|---|
> | **Languages** | `VIEW[{languages}][link]` |
> | **Organizations** | `VIEW[{organizations}][link]` |
> | **Religions** | `VIEW[{religions}][link]` |
> | **Condition** | `VIEW[{condition}]` |
> | **Location** | `VIEW[{currentLocation}][link]` |
> | **Campaign** | `VIEW[{campaign}][text]` |
>
> # Combat
> | | |
> |---|---|
> | **Level** | `VIEW[{level}]` |
> | **XP** | `VIEW[{experience}]` / `VIEW[{experience_next}]` |
> | **HP** | `VIEW[{hp_current}]` / `VIEW[{hp_max}]` (Temp: `VIEW[{hp_temp}]`) |
> | **AC** | `VIEW[{ac}]` |
> | **Speed** | `VIEW[{speed}]` ft |
> | **Prof. Bonus** | +`VIEW[{proficiencyBonus}]` |
> | **Hit Die** | `VIEW[{hitDie}][text]` |

# `=this.file.name`

## Sketch

`VIEW[!{sketch}][text(renderMarkdown)]`

## Ability Scores

| STR | DEX | CON | INT | WIS | CHA |
|:---:|:---:|:---:|:---:|:---:|:---:|
| `INPUT[number:str]` | `INPUT[number:dex]` | `INPUT[number:con]` | `INPUT[number:int]` | `INPUT[number:wis]` | `INPUT[number:cha]` |

## Skills & Saving Throws

| Skill | Proficient | Expertise |
| ----- | :-------: | :-------: |
| Acrobatics (DEX) | | |
| Animal Handling (WIS) | | |
| Arcana (INT) | | |
| Athletics (STR) | | |
| Deception (CHA) | | |
| History (INT) | | |
| Insight (WIS) | | |
| Intimidation (CHA) | | |
| Investigation (INT) | | |
| Medicine (WIS) | | |
| Nature (INT) | | |
| Perception (WIS) | | |
| Performance (CHA) | | |
| Persuasion (CHA) | | |
| Religion (INT) | | |
| Sleight of Hand (DEX) | | |
| Stealth (DEX) | | |
| Survival (WIS) | | |

**Saving Throws:** STR ☐ DEX ☐ CON ☐ INT ☐ WIS ☐ CHA ☐

## Spellcasting

> *<font color="#646a73">Fill if your character casts spells. Spell save DC: `VIEW[{spell_save_dc}]` | Spell attack bonus: +`VIEW[{spell_attack_bonus}]` | Ability: `VIEW[{spellcastingAbility}][text]`</font>*

| Spell Level | Slots Total | Slots Used | Notes |
| :---: | :---: | :---: | --- |
| Cantrips | ∞ | — | |
| 1st | | | |
| 2nd | | | |
| 3rd | | | |
| 4th | | | |
| 5th | | | |
| 6th | | | |
| 7th | | | |
| 8th | | | |
| 9th | | | |

## Features, Traits & Proficiencies

### Class Features & Traits

> *<font color="#646a73">List key class features, subclass features, racial traits, and background features by level.</font>*

### Feats

> *<font color="#646a73">List any feats your character has taken.</font>*

### Proficiencies

> *<font color="#646a73">Armour, weapons, tools, and any special skill proficiencies or expertise.</font>*

## Equipment & Inventory

| Name | Type | Notes |
| ---- | ---- | ----- |
| | | |

## Personality Traits

> *<font color="#646a73">What makes your character distinct? Their mannerisms, speech patterns, and habits.</font>*

## Ideals

> *<font color="#646a73">What does your character believe in most deeply?</font>*

## Flaws

> *<font color="#646a73">What weakness, fear, or failing does your character struggle with?</font>*

## Bonds

> *<font color="#646a73">Who or what does your character care about more than anything?</font>*

## Goals

> [!column | 2 no-t]
> > [!metadata|shortterm] Short Term
> > - *<font color="#646a73">What does your character want to accomplish in the near future?</font>*
>
> > [!metadata|longterm] Long Term
> > - *<font color="#646a73">What does your character want their legacy to be?</font>*

## Backstory

### Birth

- **Birthday:** `VIEW[{birthday}][text]`
- **Birth Location:**
- **Mother:** &nbsp;&nbsp;&nbsp;&nbsp; **Father:**

### Childhood

> *<font color="#646a73">What was your character's childhood like? What events shaped who they are today?</font>*

### Journey to Adventure

> *<font color="#646a73">What brought your character to where they are now? What set them on the path of adventure?</font>*

### Worship & Faith

> *<font color="#646a73">Does your character follow any deity or hold any spiritual beliefs?</font>*

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

