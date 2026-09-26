// ── Edition-specific content types ────────────────────────────────────────────
// Must mirror CONTENT_TYPES_5E_2014 / CONTENT_TYPES_5E_2024 in import_5etools.py

const CONTENT_TYPES_5E_2014 = [
  "spells", "items", "backgrounds", "classes", "classfeatures",
  "races", "racialtraits", "backgroundfeatures",
  "languages", "deities", "feats", "conditions", "optionalfeatures",
];

const CONTENT_TYPES_5E_2024 = [
  "spells", "items", "backgrounds", "classes", "classfeatures",
  "races", "racialtraits",
  "languages", "deities", "feats", "conditions", "optionalfeatures",
];

// Human-readable labels shown in the checkbox picker
const TYPE_LABELS = {
  spells:             "Spells",
  items:              "Items",
  backgrounds:        "Backgrounds",
  classes:            "Classes",
  classfeatures:      "Class Features",
  races:              "Races / Species",
  racialtraits:       "Racial Traits",
  backgroundfeatures: "Background Features",
  languages:          "Languages",
  deities:            "Deities",
  feats:              "Feats",
  conditions:         "Conditions",
  optionalfeatures:   "Optional Features",
};

// ── Edition-specific book lists ────────────────────────────────────────────────

const BOOKS_5E_2014 = [
  // Core rules
  { code: "PHB",        name: "Player's Handbook (2014)" },
  { code: "DMG",        name: "Dungeon Master's Guide (2014)" },
  { code: "MM",         name: "Monster Manual" },
  { code: "SRD",        name: "SRD 5.1 (Creative Commons)" },
  { code: "BasicRules", name: "Basic Rules" },
  // Major supplements
  { code: "XGE",        name: "Xanathar's Guide to Everything" },
  { code: "TCE",        name: "Tasha's Cauldron of Everything" },
  { code: "SCAG",       name: "Sword Coast Adventurer's Guide" },
  { code: "MTF",        name: "Mordenkainen's Tome of Foes" },
  { code: "VGM",        name: "Volo's Guide to Monsters" },
  { code: "MPMM",       name: "Mordenkainen Presents: Monsters of the Multiverse" },
  { code: "FTD",        name: "Fizban's Treasury of Dragons" },
  { code: "BGG",        name: "Bigby Presents: Glory of the Giants" },
  { code: "MPP",        name: "Planescape: Adventures in the Multiverse" },
  { code: "SCC",        name: "Strixhaven: A Curriculum of Chaos" },
  // Setting guides
  { code: "GGR",        name: "Guildmasters' Guide to Ravnica" },
  { code: "ERLW",       name: "Eberron: Rising from the Last War" },
  { code: "EGW",        name: "Explorer's Guide to Wildemount" },
  { code: "MOT",        name: "Mythic Odysseys of Theros" },
  { code: "AI",         name: "Acquisitions Incorporated" },
  // Adventures
  { code: "CoS",        name: "Curse of Strahd" },
  { code: "ToA",        name: "Tomb of Annihilation" },
  { code: "SKT",        name: "Storm King's Thunder" },
  { code: "WDH",        name: "Waterdeep: Dragon Heist" },
  { code: "WDMM",       name: "Waterdeep: Dungeon of the Mad Mage" },
  { code: "BGDIA",      name: "Baldur's Gate: Descent into Avernus" },
  { code: "IDRotF",     name: "Icewind Dale: Rime of the Frostmaiden" },
  { code: "WBtW",       name: "The Wild Beyond the Witchlight" },
  { code: "CRCotN",     name: "Critical Role: Call of the Netherdeep" },
  { code: "PaBTSO",     name: "Phandelver and Below: The Shattered Obelisk" },
  { code: "DSotDQ",     name: "Dragonlance: Shadow of the Dragon Queen" },
  { code: "KftGV",      name: "Keys from the Golden Vault" },
  { code: "BMT",        name: "The Book of Many Things" },
];

const BOOKS_5E_2024 = [
  // Core rulebooks (2024 revised editions)
  { code: "XPHB",  name: "Player's Handbook (2024)" },
  { code: "XDMG",  name: "Dungeon Master's Guide (2024)" },
  { code: "XMM",   name: "Monster Manual (2024)" },
  // Adventures & supplements (2024 edition)
  { code: "QftIS", name: "Quests from the Infinite Staircase" },
  // Pre-2024 supplements widely used alongside 2024 rules
  { code: "XGE",   name: "Xanathar's Guide to Everything" },
  { code: "TCE",   name: "Tasha's Cauldron of Everything" },
  { code: "SCAG",  name: "Sword Coast Adventurer's Guide" },
  { code: "MPMM",  name: "Mordenkainen Presents: Monsters of the Multiverse" },
];

// ── Source options (per edition) ───────────────────────────────────────────────

const SOURCE_OPTIONS_5E_2014 = [
  { label: "WotC Official — all official sourcebooks & adventures", value: "wotc"  },
  { label: "Specific Books — choose exactly which books to import",  value: "books" },
  { label: "All Sources — includes third-party and homebrew",        value: "all"   },
];

const SOURCE_OPTIONS_5E_2024 = [
  { label: "WotC 2024 — core books + compatible supplements",       value: "wotc"  },
  { label: "Specific Books — choose exactly which books to import",  value: "books" },
  { label: "All Sources — includes third-party and homebrew",        value: "all"   },
];

const PYTHON_FALLBACK_PATHS = {
  darwin: ["/opt/homebrew/bin/python3", "/usr/local/bin/python3", "/usr/bin/python3"],
  linux:  ["/usr/bin/python3", "/usr/local/bin/python3"],
  win32:  [],
};

module.exports = async (params) => {
  const { app, quickAddApi: qa } = params;

  // ── Detect Python ──────────────────────────────────────────────────────────
  let python = await detectPython();
  if (!python) {
    python = await handleMissingPython(qa);
    if (!python) return;
  }

  // ── Detect active game system ──────────────────────────────────────────────
  const vaultPath = app.vault.adapter.basePath;
  const path      = require("path");
  const fs        = require("fs");

  let gameSystem = "dnd5e";
  try {
    const cfgPath = path.join(vaultPath, "vault-config.json");
    gameSystem    = JSON.parse(fs.readFileSync(cfgPath, "utf8")).gameSystem || "dnd5e";
  } catch (e) {
    console.warn("[RunImport] Could not read vault-config.json, defaulting to dnd5e:", e.message);
  }

  const is2024       = gameSystem === "dnd5e_2024";
  const editionLabel = is2024 ? "D&D 5.5e (2024)" : "D&D 5e (2014)";
  const systemArg    = `--system ${gameSystem}`;
  const activeTypes  = is2024 ? CONTENT_TYPES_5E_2024 : CONTENT_TYPES_5E_2014;
  const activeBooks  = is2024 ? BOOKS_5E_2024 : BOOKS_5E_2014;
  const srcOptions   = is2024 ? SOURCE_OPTIONS_5E_2024 : SOURCE_OPTIONS_5E_2014;

  // ── Step 1: Source mode ────────────────────────────────────────────────────
  const srcValue = await qa.suggester(
    srcOptions.map(o => o.label),
    srcOptions.map(o => o.value)
  );
  if (!srcValue) return;

  let sourceArg     = "";
  let srcLabel      = "";
  let selectedBooks = null;

  if (srcValue === "all") {
    sourceArg = "--all";
    srcLabel  = "All Sources";
  } else if (srcValue === "books") {
    selectedBooks = await pickBooks(qa, activeBooks);
    if (!selectedBooks) return;
    if (selectedBooks.length === 0) {
      new Notice("No books selected. Import cancelled.");
      return;
    }
    sourceArg = `--book ${selectedBooks.join(" ")}`;
    srcLabel  = selectedBooks.join(", ");
  } else {
    sourceArg = "";
    srcLabel  = is2024 ? "WotC 2024" : "WotC Official";
  }

  // ── Step 2: Content types ──────────────────────────────────────────────────
  const SELECT_ALL     = "☑  Select All";
  const typeLabels     = [SELECT_ALL, ...activeTypes.map(t => TYPE_LABELS[t] || t)];
  const selectedLabels = await qa.checkboxPrompt(typeLabels, typeLabels);
  if (!selectedLabels || selectedLabels.length === 0) {
    new Notice("No content types selected. Import cancelled.");
    return;
  }
  const selectedTypes = selectedLabels.includes(SELECT_ALL)
    ? [...activeTypes]
    : activeTypes.filter(t => selectedLabels.includes(TYPE_LABELS[t] || t));

  // ── Step 3: Confirm ────────────────────────────────────────────────────────
  const typesLabel = selectedTypes.length === activeTypes.length
    ? "all content types"
    : selectedLabels.join(", ");

  const confirm = await qa.yesNoPrompt(
    `Run 5e.tools Import? (${editionLabel})`,
    `Edition: ${editionLabel}\nSource: ${srcLabel}\nTypes: ${typesLabel}\n\nThis downloads data from 5e.tools and creates notes in your vault. Existing notes are never overwritten.\n\n⚠️ DISCLAIMER: You are responsible for ensuring you have a valid license or legal access to the content you import.\n\nContinue?`
  );
  if (!confirm) return;

  // ── Step 4: Build and run command ─────────────────────────────────────────
  const scriptPath = path.join(vaultPath, "import_5etools.py");
  const shellQuote = a => `"${String(a).replace(/\\/g, "\\\\").replace(/"/g, '\\"')}"`;

  const typeArg = selectedTypes.length < activeTypes.length
    ? `--type ${selectedTypes.join(" ")}`
    : "";
  const command = [
    shellQuote(python),
    shellQuote(scriptPath),
    "--vault", shellQuote(vaultPath),
    systemArg,
    sourceArg,
    typeArg,
  ].filter(Boolean).join(" ");

  const startNotice = new Notice(
    `⏳ Importing ${typesLabel} (${srcLabel})… this may take a few minutes.`, 0
  );

  const { exec } = require("child_process");
  exec(command, { cwd: vaultPath, timeout: 900000 }, (error, stdout, stderr) => {
    startNotice.hide();
    if (error) {
      const detail = stderr?.trim() || error.message;
      new Notice(`❌ Import failed:\n${detail}`, 12000);
      console.error("[RunImport] error:", error);
      console.error("[RunImport] stderr:", stderr);
      return;
    }
    const totalMatch = stdout.match(/Wrote (\d+) notes total/);
    const total = totalMatch ? totalMatch[1] : "?";
    new Notice(`✅ Import complete — ${total} notes written. Reloading vault…`, 5000);
    console.log("[RunImport] output:\n", stdout);
    if (stderr?.trim()) console.warn("[RunImport] stderr:\n", stderr);
    setTimeout(() => app.commands.executeCommandById("app:reload"), 2000);
  });
};

// ── Book picker ────────────────────────────────────────────────────────────────
// Shows a checkbox list of available books and returns selected source codes.

async function pickBooks(qa, books) {
  const SELECT_ALL = "☑  Select All";
  const labels     = [SELECT_ALL, ...books.map(b => `${b.code} — ${b.name}`)];
  const selected   = await qa.checkboxPrompt(labels, []);
  if (!selected) return null;
  if (selected.includes(SELECT_ALL)) return books.map(b => b.code);
  return selected.filter(l => l !== SELECT_ALL).map(l => l.split(" — ")[0]);
}

// ── Python detection ───────────────────────────────────────────────────────────

async function detectPython() {
  const candidates = process.platform === "win32"
    ? ["python", "py", "python3"]
    : ["python3", "python", ...(PYTHON_FALLBACK_PATHS[process.platform] || [])];

  for (const cmd of candidates) {
    const found = await getPythonVersion(cmd);
    if (found) return cmd;
  }
  return null;
}

function getPythonVersion(cmd) {
  return new Promise((resolve) => {
    const { exec } = require("child_process");
    exec(`"${cmd}" --version`, { timeout: 8000 }, (err, stdout, stderr) => {
      const output = (stdout + stderr).trim();
      resolve(!err && /Python 3\./.test(output) ? cmd : null);
    });
  });
}

// ── Missing Python handler ─────────────────────────────────────────────────────

async function handleMissingPython(qa) {
  const platform = process.platform;
  const options  = [];

  if (platform === "darwin") {
    const hasBrew = await commandExists("brew");
    if (hasBrew) {
      options.push({ label: "Install via Homebrew (recommended)", action: installViaBrew });
    } else {
      options.push({ label: "Install Homebrew + Python", action: installHomebrewAndPython });
    }
    options.push({ label: "Open python.org download page", action: openPythonOrg });
    options.push({ label: "Show manual install instructions", action: () => showInstructions(platform) });
  } else if (platform === "win32") {
    const hasWinget = await commandExists("winget");
    if (hasWinget) {
      options.push({ label: "Install via winget (recommended)", action: installViaWinget });
    }
    options.push({ label: "Open python.org download page", action: openPythonOrg });
    options.push({ label: "Show manual install instructions", action: () => showInstructions(platform) });
  } else {
    options.push({ label: "Open python.org download page", action: openPythonOrg });
    options.push({ label: "Show manual install instructions", action: () => showInstructions(platform) });
  }

  options.push({ label: "Cancel", action: null });

  const choice = await qa.suggester(
    options.map(o => o.label),
    options.map(o => o.label)
  );
  if (!choice || choice === "Cancel") return null;

  const selected = options.find(o => o.label === choice);
  return selected?.action ? await selected.action(qa) : null;
}

// ── Install actions ────────────────────────────────────────────────────────────

async function installViaBrew(qa) {
  const notice = new Notice("⏳ Installing Python 3 via Homebrew… this may take a few minutes.", 0);
  try {
    await runCommand("brew install python3", 300000);
    notice.hide();
    new Notice("✅ Python 3 installed via Homebrew.", 5000);
    return await detectPython();
  } catch (e) {
    notice.hide();
    new Notice(`❌ Homebrew install failed:\n${e.message}\n\nTry installing manually from python.org.`, 10000);
    return null;
  }
}

async function installHomebrewAndPython(qa) {
  const confirm = await qa.yesNoPrompt(
    "Install Homebrew?",
    "This will run the official Homebrew installer in a Terminal window, then install Python 3. Your system password may be required. Continue?"
  );
  if (!confirm) return null;
  const { exec } = require("child_process");
  exec(`osascript -e 'tell application "Terminal" to do script "/bin/bash -c \\"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\\" && brew install python3"'`);
  new Notice("⏳ Homebrew installer opened in Terminal.\n\nFollow the prompts there, then come back and click Import again.", 12000);
  return null;
}

async function installViaWinget(qa) {
  const notice = new Notice("⏳ Installing Python 3 via winget… this may take a few minutes.", 0);
  try {
    await runCommand("winget install --id Python.Python.3 --source winget --silent", 300000);
    notice.hide();
    new Notice("✅ Python 3 installed. You may need to restart Obsidian for the PATH to update.", 8000);
    return await detectPython();
  } catch (e) {
    notice.hide();
    new Notice(`❌ winget install failed:\n${e.message}\n\nTry installing manually from python.org.`, 10000);
    return null;
  }
}

function openPythonOrg() {
  const { shell } = require("electron");
  shell.openExternal("https://www.python.org/downloads/");
  new Notice("🌐 Opening python.org in your browser.\n\nAfter installing Python 3, restart Obsidian and click Import again.", 10000);
  return null;
}

function showInstructions(platform) {
  const instructions = {
    darwin: "Python 3 not found.\n\nmacOS:\n• brew install python3\n• python.org/downloads\n• xcode-select --install\n\nRestart Obsidian after installing.",
    linux:  "Python 3 not found.\n\nLinux:\n• sudo apt install python3\n• sudo dnf install python3\n• sudo pacman -S python\n\nRestart Obsidian after installing.",
    win32:  "Python 3 not found.\n\nWindows:\n• winget install Python.Python.3\n• Microsoft Store → search Python 3\n• python.org/downloads\n\nRestart Obsidian after installing.",
  };
  new Notice(instructions[platform] || instructions.linux, 20000);
  return null;
}

// ── Utilities ──────────────────────────────────────────────────────────────────

function commandExists(cmd) {
  return new Promise((resolve) => {
    const { exec } = require("child_process");
    const check = process.platform === "win32" ? `where ${cmd}` : `which ${cmd}`;
    exec(check, { timeout: 5000 }, (err) => resolve(!err));
  });
}

function runCommand(command, timeout = 120000) {
  return new Promise((resolve, reject) => {
    const { exec } = require("child_process");
    exec(command, { timeout }, (err, stdout, stderr) => {
      if (err) reject(new Error(stderr?.trim() || err.message));
      else resolve({ stdout, stderr });
    });
  });
}
