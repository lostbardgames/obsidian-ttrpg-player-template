module.exports = async (params) => {
  const { app, quickAddApi: qa } = params;

  const today = new Date();
  const dateStr = today.toISOString().split("T")[0];

  const sessionName = await selectFromFolder(app, qa, "Campaign Notes/Session Recaps", "Session Recap", true);
  if (sessionName === null) return;

  const defaultName = `Journal — ${dateStr}`;
  const name = await qa.inputPrompt("Journal Entry Title", "Enter a title...", defaultName);
  if (!name) return;

  const destPath = `Campaign Notes/Journal/${name}.md`;
  if (app.vault.getAbstractFileByPath(destPath)) {
    new Notice(`"${name}" already exists!`);
    return;
  }

  const tpl = app.vault.getAbstractFileByPath("z_Templates/Journal/Template - Journal Entry.md");
  if (!tpl) { new Notice("Journal template not found!"); return; }

  let content = await app.vault.read(tpl);
  content = content.replace(/^realDate:.*$/m, `realDate: ${dateStr}`);
  if (sessionName) content = setListField(content, "session", sessionName);

  const file = await app.vault.create(destPath, content);
  await getMainLeaf(app).openFile(file);
  new Notice(`Journal entry "${name}" created!`);
};

async function selectFromFolder(app, qa, folderPath, label, allowSkip = false) {
  const folder = app.vault.getAbstractFileByPath(folderPath);
  const existing = (folder?.children || [])
    .filter(f => !("children" in f) && f.extension === "md")
    .map(f => f.basename)
    .sort();
  const SKIP = "[ None / Skip ]";
  const opts = allowSkip ? [...existing, SKIP] : [...existing];
  if (opts.length === 0 && !allowSkip) return null;
  if (opts.length === 0) return "";
  const choice = await qa.suggester(opts, opts);
  if (!choice) return null;
  if (choice === SKIP) return "";
  return choice;
}

function setListField(content, field, value) {
  return content.replace(new RegExp(`^${field}:.*$`, "m"), `${field}:\n  - "[[${value}]]"`);
}

function getMainLeaf(app) {
  return app.workspace.getLeavesOfType("markdown")
    .find(l => l.view?.file?.path !== "1.Tools/Buttons.md")
    ?? app.workspace.getLeaf();
}
