// ── Multi-character scoping ────────────────────────────────────────────────
// In "multi" vault mode new notes are tagged with the active campaign/character so they only
// show for them, and pickers only offer that campaign's notes. In single mode none of this applies.

const SETTINGS_PATH = "z_Databases/Vault Hub/Player Settings.md";
let SCOPE = { multi: false, campaign: "", character: "" };

async function getMode(app) {
  try {
    const m = (await app.vault.adapter.read(SETTINGS_PATH)).match(/^vaultMode:\s*['"]?(single|multi)['"]?\s*$/m);
    return m ? m[1] : null;
  } catch (_) { return null; }
}

async function loadScope(app) {
  const sf = app.vault.getAbstractFileByPath(SETTINGS_PATH);
  const s = (sf && app.metadataCache.getFileCache(sf)?.frontmatter) || {};
  return { multi: (await getMode(app)) === "multi", campaign: s.campaignName || "", character: s.characterName || "" };
}

function inActiveCampaign(app, f) {
  if (!SCOPE.multi || !SCOPE.campaign) return true;
  const c = app.metadataCache.getFileCache(f)?.frontmatter?.campaign;
  return !c || c === SCOPE.campaign;
}

async function stampScope(app, file, kind) {
  if (!SCOPE.multi) return;
  await app.fileManager.processFrontMatter(file, fm => {
    if (kind === "campaign" && SCOPE.campaign) fm.campaign = SCOPE.campaign;
    if (kind === "character" && SCOPE.character) fm.character = `[[${SCOPE.character}]]`;
  });
}

module.exports = async (params) => {
  const { app, quickAddApi: qa } = params;
  SCOPE = await loadScope(app);

  const name = await qa.inputPrompt("New Spell", "Enter spell name...");
  if (!name) return;

  const destPath = `Possessions/Spells/${name}.md`;
  if (app.vault.getAbstractFileByPath(destPath)) {
    new Notice(`"${name}" already exists!`);
    return;
  }

  const tpl = app.vault.getAbstractFileByPath("z_Templates/Possessions/Template - Spell.md");
  if (!tpl) { new Notice("Spell template not found!"); return; }

  const content = await app.vault.read(tpl);
  const file = await app.vault.create(destPath, content);
  await stampScope(app, file, "character");
  await getMainLeaf(app).openFile(file);
  new Notice(`"${name}" created!`);
};

function getMainLeaf(app) {
  return app.workspace.getLeavesOfType("markdown")
    .find(l => l.view?.file?.path !== "1.Tools/Buttons.md")
    ?? app.workspace.getLeaf();
}
