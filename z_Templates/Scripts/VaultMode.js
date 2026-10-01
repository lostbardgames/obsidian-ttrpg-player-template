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
// One script for both moments a vault's type is decided:
//   • not chosen yet  → pop-up: single character vs several characters/campaigns
//   • single          → one-time, one-way conversion to multi
//   • multi           → informational only (cannot be switched back)

async function goMulti(app, qa, chars) {
  const s = getSettings(app);
  const character = chars.length === 1 ? chars[0].basename : "";
  let campaign = s.campaignName || (chars.length === 1 ? app.metadataCache.getFileCache(chars[0])?.frontmatter?.campaign : "") || "";

  if (chars.length === 1) {
    campaign = ((await qa.inputPrompt("Campaign name for your existing notes (blank to skip)", "e.g. The Lost Mine", campaign)) || "").trim();
  }

  const values = { vaultMode: "multi" };
  if (character) values.characterName = character;
  if (campaign) values.campaignName = campaign;

  let stamped = 0;
  if (chars.length === 1) stamped = await stampExisting(app, character, campaign);
  await setActive(app, values);

  let msg = "✅ Multiple-character mode is on.";
  if (chars.length === 1) msg += `\n${stamped} existing note(s) were assigned to ${character}${campaign ? ` / ${campaign}` : ""}.`;
  if (chars.length > 1) msg += `\nYou have ${chars.length} characters, so existing notes are left unassigned — pick a character, then use "Assign unfiled notes".`;
  new Notice(msg, 9000);
}

module.exports = async (params) => {
  const { app, quickAddApi: qa } = params;
  const mode = await getMode(app);
  const chars = getCharacterFiles(app);

  if (mode === "multi") {
    new Notice("This vault is already in multiple-character mode. It can't be switched back to single.", 8000);
    return;
  }

  if (mode === "single") {
    const ok = await qa.yesNoPrompt(
      "Convert to multiple characters?",
      "This is a ONE-WAY change — a vault can't be converted back to single-character.\n\nYour existing notes will be assigned to your current character and campaign, and new notes will be filed per campaign/character from now on. Nothing is deleted.\n\nConvert now?"
    );
    if (!ok) return;
    await goMulti(app, qa, chars);
    return;
  }

  // Not chosen yet
  const SINGLE = "single", MULTI = "multi";
  const labels = [
    "🧙  One character, one campaign — simplest. You can convert to multiple later, but not back.",
    "👥  Several characters or campaigns — each keeps its own notes. Can't be switched back to single.",
  ];
  const choice = await qa.suggester(labels, [SINGLE, MULTI], "How will you use this vault?");
  if (!choice) return;

  if (choice === SINGLE) {
    if (chars.length > 1) {
      new Notice(`You already have ${chars.length} characters, so this vault needs the "Several characters or campaigns" option.`, 9000);
      return;
    }
    await setActive(app, { vaultMode: "single" });
    new Notice("✅ Single-character vault set up.", 6000);
    return;
  }

  const ok = await qa.yesNoPrompt(
    "Set up for multiple characters?",
    "Each character and campaign will keep its own notes. This can't be switched back to single-character later.\n\nContinue?"
  );
  if (!ok) return;
  await goMulti(app, qa, chars);
};
