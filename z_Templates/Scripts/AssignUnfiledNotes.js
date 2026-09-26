// ── Vault settings note (holds the active campaign/character AND the vault mode) ──

const SETTINGS_DIR = "z_Databases/Vault Hub";
const SETTINGS_PATH = `${SETTINGS_DIR}/Player Settings.md`;

async function setActive(app, values) {
  let file = app.vault.getAbstractFileByPath(SETTINGS_PATH);
  if (!file) {
    try { await app.vault.createFolder(SETTINGS_DIR); } catch (_) { /* already exists */ }
    file = await app.vault.create(
      SETTINGS_PATH,
      "---\ntags:\n  - Settings\ncampaignName: ''\ncharacterName: ''\n---\n\nActive campaign and character, and the vault type. Change them with the buttons on the Homepage.\n"
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

// ── Assigning existing notes to a campaign / character ─────────────────────

const CAMPAIGN_FOLDERS = ["Campaign Notes/Session Recaps", "Campaign Notes/Quests", "Campaign Notes/NPCs Known", "Campaign Notes/Locations"];
const CHARACTER_FOLDERS = [
  { dir: "Campaign Notes/Journal", field: "character", list: false },
  { dir: "Possessions/Items", field: "owner", list: true },
  { dir: "Possessions/Spells", field: "character", list: false },
];
const isBlank = v => v == null || v === "" || (Array.isArray(v) && v.every(x => !x));

// Notes that would be stamped, without changing anything (imported reference-library notes are never touched)
function findUnassigned(app, character, campaign) {
  const out = [];
  for (const f of app.vault.getMarkdownFiles()) {
    const fm = app.metadataCache.getFileCache(f)?.frontmatter || {};
    if (fm.import_source) continue;
    if (campaign && CAMPAIGN_FOLDERS.some(d => f.path.startsWith(d + "/")) && isBlank(fm.campaign)) out.push({ f, field: "campaign" });
    const cf = CHARACTER_FOLDERS.find(c => f.path.startsWith(c.dir + "/"));
    if (character && cf && isBlank(fm[cf.field])) out.push({ f, field: cf.field, list: cf.list });
  }
  return out;
}

async function stampExisting(app, character, campaign) {
  const todo = findUnassigned(app, character, campaign);
  for (const { f, field, list } of todo) {
    await app.fileManager.processFrontMatter(f, fm => {
      if (field === "campaign") fm.campaign = campaign;
      else fm[field] = list ? [`[[${character}]]`] : `[[${character}]]`;
    });
  }
  return todo.length;
}

// ── Main ───────────────────────────────────────────────────────────────────
// Multi mode only: give notes that belong to no character/campaign to the ACTIVE ones.

module.exports = async (params) => {
  const { app, quickAddApi: qa } = params;

  if ((await getMode(app)) !== "multi") {
    new Notice("This is only needed in multiple-character mode.", 6000);
    return;
  }

  const s = getSettings(app);
  const character = s.characterName || "";
  const campaign = s.campaignName || "";
  if (!character && !campaign) {
    new Notice("Pick a character and campaign first (Change Character / Change Campaign), then try again.", 8000);
    return;
  }

  const todo = findUnassigned(app, character, campaign);
  if (todo.length === 0) {
    new Notice("✅ Every note is already assigned.", 5000);
    return;
  }

  const byField = f => todo.filter(t => t.field === f).length;
  const ok = await qa.yesNoPrompt(
    `Assign ${todo.length} unfiled note(s)?`,
    `They will be given to:\n• Character: ${character || "(none)"}\n• Campaign: ${campaign || "(none)"}\n\n${byField("campaign")} campaign note(s), ${todo.length - byField("campaign")} personal note(s) (journal, items, spells). Notes that already belong to someone are not touched.\n\nContinue?`
  );
  if (!ok) return;

  const n = await stampExisting(app, character, campaign);
  new Notice(`✅ Assigned ${n} note(s) to ${character || campaign}.`, 6000);
};
