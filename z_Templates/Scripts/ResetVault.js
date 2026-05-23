module.exports = async (params) => {
  const { app, quickAddApi: qa } = params;

  const confirm1 = await qa.yesNoPrompt(
    "⚠️ Reset Vault",
    "This will permanently delete all campaign data (character, journal, session recaps, quests, NPCs, locations, and possessions). This CANNOT be undone. Continue?"
  );
  if (!confirm1) { new Notice("Reset cancelled."); return; }

  const confirm2 = await qa.yesNoPrompt(
    "⚠️ Final Warning",
    "Are you absolutely sure? All your notes will be permanently deleted."
  );
  if (!confirm2) { new Notice("Reset cancelled."); return; }

  const foldersToReset = [
    "My Character",
    "Campaign Notes/Journal",
    "Campaign Notes/Session Recaps",
    "Campaign Notes/Quests",
    "Campaign Notes/NPCs Known",
    "Campaign Notes/Locations",
    "Possessions/Items",
    "Possessions/Spells",
    "Lore",
    "z_Assets/Character",
    "z_Assets/Unsorted",
  ];

  let deleted = 0;
  for (const folderPath of foldersToReset) {
    const folder = app.vault.getAbstractFileByPath(folderPath);
    if (!folder?.children) continue;
    for (const child of [...folder.children]) {
      if ("children" in child) continue;
      if (child.name === ".gitkeep") continue;
      try {
        await app.vault.delete(child, true);
        deleted++;
      } catch (e) {
        console.warn(`Could not delete ${child.path}:`, e);
      }
    }
  }

  new Notice(`Reset complete. ${deleted} file(s) deleted.`);
};
