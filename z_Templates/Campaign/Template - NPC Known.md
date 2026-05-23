---
tags:
  - NPCKnown
art: "[[PlaceholderCharacter.png]]"
aliases:
firstMet: []
lastSeen: []
relationship: Neutral
status: Alive
currentLocation: []
occupation:
---

> [!infobox | no-blending black]+ <font color="#ffffff">Infobox</font>
>
> `VIEW[!{art}][text(renderMarkdown)]`
>
> # Details
> | | |
> |---|---|
> | **Occupation** | `VIEW[{occupation}][text]` |
> | **Relationship** | `VIEW[{relationship}][text]` |
> | **Status** | `VIEW[{status}][text]` |
> | **Last Seen** | `VIEW[{currentLocation}][link]` |
>
> # History
> | | |
> |---|---|
> | **First Met** | `VIEW[{firstMet}][link]` |
> | **Last Seen In** | `VIEW[{lastSeen}][link]` |

# `=this.file.name`

## First Impressions

> *<font color="#646a73">What was your character's immediate reaction to this person? What stood out — appearance, demeanor, voice?</font>*

## Known Facts

> *<font color="#646a73">Things you've confirmed are true about this person.</font>*

- 

## Suspicions

> *<font color="#646a73">Things you suspect but haven't confirmed. What doesn't add up?</font>*

- 

## History with Party

> *<font color="#646a73">Key interactions, favors given or owed, conflicts, agreements.</font>*

| Session | What Happened |
| ------- | ------------- |
| | |

## Secrets Uncovered

> *<font color="#646a73">Things you've discovered about this person over time.</font>*

- [ ] *<font color="#646a73">Secret or revelation</font>*

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

