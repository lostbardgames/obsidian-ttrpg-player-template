---
tags:
  - Quest
aliases:
questType:
questGiver: []
status: Active
linkedSession: []
reward_gp: 0
reward_other:
completed: false
---

# `=this.file.name`

> [!column|3 no-t]
> **Type:** `VIEW[{questType}][text]`
>
> **Quest Giver:** `VIEW[{questGiver}][link]`
>
> **Status:** `VIEW[{status}][text]`

---

## Objective

- [ ] *<font color="#646a73">Primary objective</font>*
- [ ] *<font color="#646a73">Secondary objective</font>*

## What We Know

| Clue / Info | Source | Session |
| ----------- | ------ | ------- |
| | | |

## Leads

> *<font color="#646a73">Specific things to follow up on — people to talk to, places to go, items to find.</font>*

- 

## Rewards

> *<font color="#646a73">What do you expect to earn on completion?</font>*

- **Gold:** `VIEW[{reward_gp}]` gp
- **Other:** `VIEW[{reward_other}][text]`

## Session Appearances

```dataview
TABLE WITHOUT ID
  file.link as "Session",
  sessionNumber as "#",
  sessionDate as "Date"
FROM "Campaign Notes/Session Recaps"
WHERE econtains(tags,"SessionRecap") AND contains(file.outlinks, this.file.link)
SORT sessionNumber ASC
```

## Notes

