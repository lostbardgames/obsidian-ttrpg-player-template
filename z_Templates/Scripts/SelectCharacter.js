// ── Active campaign / character (kept in a settings note the updater never overwrites) ──

const SETTINGS_DIR = "z_Databases/Vault Hub";
const SETTINGS_PATH = `${SETTINGS_DIR}/Player Settings.md`;

async function setActive(app, values) {
  let file = app.vault.getAbstractFileByPath(SETTINGS_PATH);
  if (!file) {
    try { await app.vault.createFolder(SETTINGS_DIR); } catch (_) { /* already exists */ }
    file = await app.vault.create(
      SETTINGS_PATH,
      "---\ntags:\n  - Settings\ncampaignName: ''\ncharacterName: ''\n---\n\nActive campaign and character. Change them with the buttons on the Homepage.\n"
    );
  }
  await app.fileManager.processFrontMatter(file, fm => { Object.assign(fm, values); });
}

function getSettings(app) {
  const file = app.vault.getAbstractFileByPath(SETTINGS_PATH);
  return (file && app.metadataCache.getFileCache(file)?.frontmatter) || {};
}

function getCharacterFiles(app) {
  return app.vault.getMarkdownFiles().filter(f => f.path.startsWith("My Character/"));
}

async function getMode(app) {
  try {
    const m = (await app.vault.adapter.read(SETTINGS_PATH)).match(/^vaultMode:\s*['"]?(single|multi)['"]?\s*$/m);
    return m ? m[1] : null;
  } catch (_) { return null; }
}

// ── Main ───────────────────────────────────────────────────────────────────

module.exports = async (params) => {
  const { app, quickAddApi: qa } = params;

  if ((await getMode(app)) !== "multi") {
    new Notice("Switching characters is for multiple-character vaults. Your vault has a single character.", 7000);
    return;
  }

  const chars = getCharacterFiles(app);
  if (chars.length === 0) {
    new Notice("No characters yet — use New Character or Import Character from D&D Beyond first.", 8000);
    return;
  }

  const names = chars.map(f => f.basename).sort();
  const current = getSettings(app).characterName;
  const labels = names.map(n => (n === current ? `${n}  ✓ (active)` : n));
  const picked = await qa.suggester(labels, names, "Pick your active character");
  if (!picked) return;

  const file = chars.find(f => f.basename === picked);
  const fm = app.metadataCache.getFileCache(file)?.frontmatter || {};
  const values = { characterName: picked };
  if (fm.campaign) values.campaignName = String(fm.campaign);   // follow the character's campaign

  await setActive(app, values);
  new Notice(`⚔️ Active character: ${picked}${values.campaignName ? `\nCampaign: ${values.campaignName}` : ""}`, 5000);
};
