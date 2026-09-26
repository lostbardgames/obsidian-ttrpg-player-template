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

// Read fresh from disk (not the metadata cache) so a just-changed mode is seen immediately
async function getMode(app) {
  try {
    const m = (await app.vault.adapter.read(SETTINGS_PATH)).match(/^vaultMode:\s*['"]?(single|multi)['"]?\s*$/m);
    return m ? m[1] : null;
  } catch (_) { return null; }
}

// Decide/verify the vault type before a character is created. Returns false to stop.
async function characterGate(app, qa) {
  let mode = await getMode(app);
  if (!mode) {                                   // first time: choose the vault type
    await qa.executeChoice("Vault Type");
    mode = await getMode(app);
    if (!mode) return false;
  }
  if (mode === "single" && getCharacterFiles(app).length > 0) {
    const go = await qa.yesNoPrompt(
      "This vault is set up for one character",
      "You already have a character. To add another, convert this vault to multiple-character mode.\n\nThis is a one-way change and nothing is deleted.\n\nConvert now?"
    );
    if (!go) return false;
    await qa.executeChoice("Vault Type");
    if ((await getMode(app)) !== "multi") return false;
  }
  return true;
}

module.exports = async (params) => {
  const { app, quickAddApi: qa } = params;

  if (!(await characterGate(app, qa))) return;

  const name = await qa.inputPrompt("New Character", "Enter your character's name...");
  if (!name) return;

  const destPath = `My Character/${name}.md`;
  if (app.vault.getAbstractFileByPath(destPath)) {
    new Notice(`"${name}" already exists!`);
    return;
  }

  const tpl = app.vault.getAbstractFileByPath("z_Templates/Characters/Template - My Character.md");
  if (!tpl) { new Notice("Character template not found!"); return; }

  const content = await app.vault.read(tpl);
  const file = await app.vault.create(destPath, content);
  const campaign = getSettings(app).campaignName;
  if (campaign) await app.fileManager.processFrontMatter(file, fm => { fm.campaign = campaign; });
  await setActive(app, { characterName: name });
  await getMainLeaf(app).openFile(file);
  new Notice(`"${name}" created!`);
};

function getMainLeaf(app) {
  return app.workspace.getLeavesOfType("markdown")
    .find(l => l.view?.file?.path !== "1.Tools/Buttons.md")
    ?? app.workspace.getLeaf();
}
