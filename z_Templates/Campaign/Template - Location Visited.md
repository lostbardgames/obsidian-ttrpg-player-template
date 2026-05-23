---
tags:
  - Location
art: "[[PlaceholderSettlement.png]]"
aliases:
locationType:
firstVisited: []
status: Explored
threatLevel: Safe
---

> [!infobox | no-blending black]+ <font color="#ffffff">Infobox</font>
>
> `VIEW[!{art}][text(renderMarkdown)]`
>
> # Details
> | | |
> |---|---|
> | **Type** | `VIEW[{locationType}][text]` |
> | **Status** | `VIEW[{status}][text]` |
> | **Threat Level** | `VIEW[{threatLevel}][text]` |
> | **First Visited** | `VIEW[{firstVisited}][link]` |

# `=this.file.name`

## Description

> *<font color="#646a73">What does this place look, smell, and feel like? What's the first thing you notice when you arrive?</font>*

## People Here

> *<font color="#646a73">Link to NPC Known notes for people associated with this location.</font>*

```dataview
LIST FROM "Campaign Notes/NPCs Known"
WHERE econtains(currentLocation, this.file.link)
SORT file.name ASC
```

## Notable Features

> *<font color="#646a73">What stood out about this location? Anything unusual, memorable, or useful?</font>*

- 

## Secrets & Discoveries

> *<font color="#646a73">Things the party uncovered here — hidden passages, buried history, unexpected finds.</font>*

- [ ] *<font color="#646a73">Discovery</font>*

## Session Visits

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

