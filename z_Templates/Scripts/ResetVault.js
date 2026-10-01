const SETTINGS_PATH = "z_Databases/Vault Hub/Player Settings.md";

async function getMode(app) {
  try {
    const m = (await app.vault.adapter.read(SETTINGS_PATH)).match(/^vaultMode:\s*['"]?(single|multi)['"]?\s*$/m);
    return m ? m[1] : null;
  } catch (_) { return null; }
}

const nameOf = v => String(v?.path ? v.path.split("/").pop().replace(/\.md$/, "") : v ?? "")
  .replace(/^\[\[|\]\]$/g, "").split("|")[0].split("/").pop().trim();
const namesOf = v => (Array.isArray(v) ? v : v == null ? [] : [v]).map(nameOf).filter(Boolean);

async function confirmTwice(qa, first, second) {
  if (!(await qa.yesNoPrompt("⚠️ Reset Vault", first))) return false;
  return await qa.yesNoPrompt("⚠️ Final Warning", second);
}

async function deleteFiles(app, files) {
  let n = 0;
  for (const f of files) {
    try { await app.vault.delete(f, true); n++; } catch (e) { console.warn(`Could not delete ${f.path}:`, e); }
  }
  return n;
}

// Everything: all characters, campaigns and imported reference notes (vault type is kept)
async function resetEverything(app, qa) {
  const ok = await confirmTwice(
    qa,
    "This will permanently delete all campaign data (characters, journal, session recaps, quests, NPCs, locations, and possessions) and imported reference notes. This CANNOT be undone. Continue?",
    "Are you absolutely sure? All your notes will be permanently deleted."
  );
  if (!ok) return null;

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
    const files = folder.children.filter(c => !("children" in c) && c.name !== ".gitkeep");
    deleted += await deleteFiles(app, files);
  }

  // Forget the active selection but KEEP the vault type — it can't be switched back to single
  const settings = app.vault.getAbstractFileByPath(SETTINGS_PATH);
  if (settings) await app.fileManager.processFrontMatter(settings, fm => { fm.campaignName = ""; fm.characterName = ""; });
  return deleted;
}

// One character's sheet, portrait and personal notes (multi mode)
async function resetCharacter(app, qa, character) {
  const ok = await confirmTwice(
    qa,
    `This will permanently delete ${character}'s character sheet, portrait, journal entries, items and spells. Shared campaign notes (quests, NPCs, locations, session recaps) and other characters are not touched. This CANNOT be undone. Continue?`,
    `Are you absolutely sure you want to delete ${character}?`
  );
  if (!ok) return null;

  const files = [];
  for (const f of app.vault.getMarkdownFiles()) {
    const fm = app.metadataCache.getFileCache(f)?.frontmatter || {};
    if (fm.import_source) continue;
    if (f.path === `My Character/${character}.md`) files.push(f);
    else if (f.path.startsWith("Campaign Notes/Journal/") || f.path.startsWith("Possessions/Spells/")) {
      if (namesOf(fm.character).includes(character)) files.push(f);
    } else if (f.path.startsWith("Possessions/Items/")) {
      if (namesOf(fm.owner).includes(character)) files.push(f);
    }
  }
  const art = app.vault.getAbstractFileByPath("z_Assets/Character")?.children?.filter(c => !("children" in c) && c.basename === character) || [];

  const deleted = await deleteFiles(app, [...files, ...art]);
  const settings = app.vault.getAbstractFileByPath(SETTINGS_PATH);
  if (settings) await app.fileManager.processFrontMatter(settings, fm => { fm.characterName = ""; });
  return deleted;
}

// One campaign's shared notes (multi mode)
async function resetCampaign(app, qa, campaign) {
  const ok = await confirmTwice(
    qa,
    `This will permanently delete the quests, NPCs, locations and session recaps of the campaign "${campaign}". Characters and their personal notes are not touched. This CANNOT be undone. Continue?`,
    `Are you absolutely sure you want to delete campaign "${campaign}"?`
  );
  if (!ok) return null;

  const dirs = ["Campaign Notes/Session Recaps/", "Campaign Notes/Quests/", "Campaign Notes/NPCs Known/", "Campaign Notes/Locations/"];
  const files = app.vault.getMarkdownFiles().filter(f => {
    if (!dirs.some(d => f.path.startsWith(d))) return false;
    return String(app.metadataCache.getFileCache(f)?.frontmatter?.campaign ?? "").trim() === campaign;
  });
  const deleted = await deleteFiles(app, files);
  const settings = app.vault.getAbstractFileByPath(SETTINGS_PATH);
  if (settings) await app.fileManager.processFrontMatter(settings, fm => { fm.campaignName = ""; });
  return deleted;
}

module.exports = async (params) => {
  const { app, quickAddApi: qa } = params;

  let deleted = null;
  if ((await getMode(app)) === "multi") {
    const sf = app.vault.getAbstractFileByPath(SETTINGS_PATH);
    const s = (sf && app.metadataCache.getFileCache(sf)?.frontmatter) || {};
    const opts = [];
    if (s.characterName) opts.push({ label: `Only ${s.characterName} — sheet, journal, items, spells`, run: () => resetCharacter(app, qa, s.characterName) });
    if (s.campaignName) opts.push({ label: `Only the campaign "${s.campaignName}" — quests, NPCs, locations, sessions`, run: () => resetCampaign(app, qa, s.campaignName) });
    opts.push({ label: "Everything — all characters and campaigns", run: () => resetEverything(app, qa) });

    const labels = opts.map(o => o.label);
    const choice = await qa.suggester(labels, labels, "What do you want to reset?");
    const opt = opts.find(o => o.label === choice);
    if (!opt) { new Notice("Reset cancelled."); return; }
    deleted = await opt.run();
  } else {
    deleted = await resetEverything(app, qa);
  }

  if (deleted === null) { new Notice("Reset cancelled."); return; }
  new Notice(`Reset complete. ${deleted} file(s) deleted.`);
};
