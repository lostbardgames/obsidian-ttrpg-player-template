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

// ── Main ───────────────────────────────────────────────────────────────────

module.exports = async (params) => {
  const { app, quickAddApi: qa } = params;

  const known = new Set();
  for (const f of getCharacterFiles(app)) {
    const c = app.metadataCache.getFileCache(f)?.frontmatter?.campaign;
    if (c) known.add(String(c));
  }
  const settings = getSettings(app);
  if (settings.campaignName) known.add(String(settings.campaignName));

  const NEW = "➕ New campaign…";
  const names = [...known].sort();
  const labels = [...names.map(n => (n === settings.campaignName ? `${n}  ✓ (active)` : n)), NEW];
  const picked = await qa.suggester(labels, [...names, NEW]);
  if (!picked) return;

  let campaign = picked;
  if (picked === NEW) {
    campaign = ((await qa.inputPrompt("Campaign name", "")) || "").trim();
    if (!campaign) return;
  }

  await setActive(app, { campaignName: campaign });

  // Keep the active character's own campaign field in step
  const active = getCharacterFiles(app).find(f => f.basename === settings.characterName);
  if (active) await app.fileManager.processFrontMatter(active, fm => { fm.campaign = campaign; });

  new Notice(`📖 Active campaign: ${campaign}`, 5000);
};
