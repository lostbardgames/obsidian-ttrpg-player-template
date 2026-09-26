// Updates an already-imported character from D&D Beyond in place (merge, not re-import).

// ── Helpers ────────────────────────────────────────────────────────────────

// ── Python detection (same pattern as RunImport.js / UpdateVault.js) ───────

async function detectPython() {
  const candidates = process.platform === "win32"
    ? ["python", "py", "python3"]
    : ["python3", "python"];

  for (const cmd of candidates) {
    const found = await checkPython3(cmd);
    if (found) return cmd;
  }
  return null;
}

function checkPython3(cmd) {
  return new Promise((resolve) => {
    const { exec } = require("child_process");
    exec(`"${cmd}" --version`, { timeout: 8000 }, (err, stdout, stderr) => {
      const output = (stdout + stderr).trim();
      resolve(!err && /Python 3\./.test(output) ? cmd : null);
    });
  });
}

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

async function handleMissingPython(qa) {
  const platform = process.platform;
  const options = [];

  if (platform === "darwin") {
    const hasBrew = await commandExists("brew");
    if (hasBrew) {
      options.push({ label: "Install via Homebrew (recommended)", action: async () => {
        const notice = new Notice("⏳ Installing Python 3 via Homebrew… this may take a few minutes.", 0);
        try {
          await runCommand("brew install python3", 300000);
          notice.hide();
          new Notice("✅ Python 3 installed. Retrying update…", 5000);
          return await detectPython();
        } catch (e) {
          notice.hide();
          new Notice(`❌ Homebrew install failed:\n${e.message}\n\nTry installing manually from python.org.`, 10000);
          return null;
        }
      }});
    } else {
      options.push({ label: "Install Homebrew + Python", action: async () => {
        const confirm = await qa.yesNoPrompt(
          "Install Homebrew?",
          "This will open a Terminal window to install Homebrew and Python 3. Your system password may be required. Continue?"
        );
        if (!confirm) return null;
        const { exec } = require("child_process");
        exec(`osascript -e 'tell application "Terminal" to do script "/bin/bash -c \\"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\\" && brew install python3"'`);
        new Notice("⏳ Homebrew installer opened in Terminal.\n\nFollow the prompts there, then click Update Character from D&D Beyond again.", 12000);
        return null;
      }});
    }
    options.push({ label: "Open python.org download page", action: () => {
      require("electron").shell.openExternal("https://www.python.org/downloads/");
      new Notice("🌐 Opening python.org.\n\nAfter installing Python 3, restart Obsidian and try again.", 10000);
      return null;
    }});
  } else if (platform === "win32") {
    const hasWinget = await commandExists("winget");
    if (hasWinget) {
      options.push({ label: "Install via winget (recommended)", action: async () => {
        const notice = new Notice("⏳ Installing Python 3 via winget… this may take a few minutes.", 0);
        const versions = ["3.13", "3.12", "3.11", "3.10"];
        let installed = false;
        for (const v of versions) {
          try {
            await runCommand(`winget install --id Python.Python.${v} --source winget --silent`, 300000);
            installed = true;
            break;
          } catch (_) { /* try next version */ }
        }
        notice.hide();
        if (installed) {
          new Notice("✅ Python 3 installed. You may need to restart Obsidian for the PATH to update.", 8000);
          return await detectPython();
        }
        new Notice("❌ winget install failed for all Python versions.\n\nTry installing manually from python.org.", 10000);
        return null;
      }});
    }
    options.push({ label: "Open python.org download page", action: () => {
      require("electron").shell.openExternal("https://www.python.org/downloads/");
      new Notice("🌐 Opening python.org.\n\nInstall Python 3 and check \"Add Python to PATH\", then restart Obsidian and try again.", 12000);
      return null;
    }});
  } else {
    options.push({ label: "Open python.org download page", action: () => {
      require("electron").shell.openExternal("https://www.python.org/downloads/");
      new Notice("🌐 Opening python.org.\n\nAfter installing Python 3, restart Obsidian and try again.", 10000);
      return null;
    }});
  }

  options.push({ label: "Cancel", action: null });

  const labels = options.map(o => o.label);
  const choice = await qa.suggester(labels, labels);
  if (!choice || choice === "Cancel") return null;

  const selected = options.find(o => o.label === choice);
  return selected?.action ? await selected.action(qa) : null;
}

// ── Linked characters ──────────────────────────────────────────────────────

// Notes in My Character/ that remember their D&D Beyond character ID (ddbId frontmatter,
// or the "Character ID" callout written by earlier versions of the importer).
async function findLinkedCharacters(app) {
  const found = [];
  for (const f of app.vault.getMarkdownFiles().filter(f => f.path.startsWith("My Character/"))) {
    const text = await app.vault.cachedRead(f);
    const m = text.match(/^ddbId:\s*['"]?(\d+)['"]?\s*$/m) || text.match(/Character ID: `(\d+)`/);
    if (m) found.push({ file: f, id: m[1] });
  }
  return found;
}

// ── Main ───────────────────────────────────────────────────────────────────

module.exports = async (params) => {
  const { app, quickAddApi: qa } = params;
  const vaultPath = app.vault.adapter.basePath;

  const linked = await findLinkedCharacters(app);
  if (linked.length === 0) {
    new Notice(
      "No character in My Character/ is linked to D&D Beyond yet.\n\nUse \"Import Character from D&D Beyond\" first — it remembers the link so you can update later.",
      10000
    );
    return;
  }

  // Multi mode: update the active character; otherwise ask when there are several
  const SETTINGS_PATH = "z_Databases/Vault Hub/Player Settings.md";
  let multi = false;
  try { multi = /^vaultMode:\s*['"]?multi['"]?\s*$/m.test(await app.vault.adapter.read(SETTINGS_PATH)); } catch (_) { /* no settings yet */ }
  const sf = app.vault.getAbstractFileByPath(SETTINGS_PATH);
  const activeName = (sf && app.metadataCache.getFileCache(sf)?.frontmatter?.characterName) || "";
  const activeLinked = linked.find(l => l.file.basename === activeName);

  let target = linked[0];
  if (multi && activeLinked) {
    target = activeLinked;
  } else if (linked.length > 1) {
    const names = linked.map(l => l.file.basename);
    const chosen = await qa.suggester(names, names);
    if (!chosen) return;
    target = linked.find(l => l.file.basename === chosen);
  }

  const proceed = await qa.yesNoPrompt(
    `Update ${target.file.basename} from D&D Beyond?`,
    "Refreshes what comes from D&D Beyond: level, XP, ability scores, HP max, AC, speed, skills, proficiencies, spells, features, feats, inventory (your per-item notes are kept).\n\nLeft alone: your current HP, conditions, location, personality/ideals/bonds/flaws you've written, goals, backstory, secrets, session history, and all your notes.\n\nContinue?"
  );
  if (!proceed) return;

  let python = await detectPython();
  if (!python) {
    python = await handleMissingPython(qa);
    if (!python) return;
  }

  const { exec } = require("child_process");
  const { promisify } = require("util");
  const path = require("path");
  const execAsync = promisify(exec);

  const shellQuote = a => `"${String(a).replace(/\\/g, "\\\\").replace(/"/g, '\\"')}"`;
  const scriptPath = path.join(vaultPath, "ImportDnDBeyond.py");
  const cmd = [shellQuote(python), shellQuote(scriptPath), shellQuote(vaultPath), shellQuote(target.id), shellQuote(""), "--update"].join(" ");

  const fetchingNotice = new Notice("⏳ Fetching latest from D&D Beyond…", 0);

  let result;
  try {
    const { stdout } = await execAsync(cmd, { maxBuffer: 10 * 1024 * 1024, timeout: 60000 });
    const lines = stdout.trim().split("\n").filter(Boolean);
    result = JSON.parse(lines[lines.length - 1]);
  } catch (e) {
    fetchingNotice.hide();
    new Notice(`❌ Update failed: ${e.message}`, 10000);
    console.error("[UpdateDnDBeyond] error:", e);
    return;
  }
  fetchingNotice.hide();

  if (result.error === "character_private") {
    new Notice(
      "🔒 This character is set to private on D&D Beyond.\n\nGo to your character sheet → Share → set visibility to Public, then try again.",
      15000
    );
    return;
  }

  if (result.error === "no_linked_note") {
    new Notice("❌ Couldn't find the linked character note.", 8000);
    return;
  }

  if (result.error) {
    new Notice(`❌ Update failed: ${result.error}`, 10000);
    console.error("[UpdateDnDBeyond] result:", result);
    return;
  }

  console.log("[UpdateDnDBeyond] result:", result);
  const changes = result.changes || [];
  if (changes.length === 0) {
    new Notice(`✅ ${result.name} is already up to date with D&D Beyond.`, 6000);
    return;
  }

  const shown = changes.slice(0, 12).map(c => `• ${c}`).join("\n");
  const more = changes.length > 12 ? `\n…and ${changes.length - 12} more` : "";
  new Notice(`✅ Updated ${result.name} from D&D Beyond:\n${shown}${more}\n\nReloading vault…`, 9000);
  setTimeout(() => app.commands.executeCommandById("app:reload"), 3000);
};
