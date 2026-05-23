---
tags:
  - SessionRecap
aliases:
character: []
sessionNumber:
sessionDate: 2026-05-22
xpGained: 0
gpGained: 0
summary: ""
---

# `=this.file.name`

> [!column|3 no-t]
> **Character:** `VIEW[{character}][link]`
>
> **Session #:** `VIEW[{sessionNumber}]`
>
> **Date:** `VIEW[{sessionDate}][text]`

## Quick References

> [!column|3 no-t]
>> ##### People
>> ```dataview
>> LIST
>> FROM outgoing([[]])
>> WHERE econtains(tags,"NPCKnown") OR econtains(tags,"Player")
>> SORT file.name ASC
>> ```
>
>> ##### Locations
>> ```dataview
>> LIST
>> FROM outgoing([[]])
>> WHERE econtains(tags,"Location")
>> SORT file.name ASC
>> ```
>
>> ##### Quests
>> ```dataview
>> LIST
>> FROM outgoing([[]])
>> WHERE econtains(tags,"Quest")
>> SORT file.name ASC
>> ```

---

## What Happened

> *<font color="#7f7f7f">Your narrative summary of the session from the party's perspective. What did you do, where did you go, what did you learn?</font>*

- 

## Key Decisions

> *<font color="#7f7f7f">What choices did the party make? What did you agree to, refuse, or commit to?</font>*

- 

## Character Moments

> *<font color="#7f7f7f">Anything notable your character did, said, or felt — highlights, lowlights, moments that mattered.</font>*

- 

## Rewards

| Type | Amount |
| ---- | ------ |
| **XP Gained** | `INPUT[number:xpGained]` |
| **Gold Gained** | `INPUT[number:gpGained]` gp |
| **Items Found** | |
| **Other** | |

## Questions & Mysteries

> *<font color="#7f7f7f">What came up this session that still doesn't have an answer? What are you still wondering about?</font>*

- 

## What's Next

> *<font color="#7f7f7f">Your intentions and plans for the next session. What does your character want to do?</font>*

- 

## Live Notes

> *<font color="#7f7f7f">Notes taken during the session. Move the good stuff up into the sections above afterward.</font>*

- 
