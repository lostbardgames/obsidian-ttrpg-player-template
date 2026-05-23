module.exports = async (params) => {
  const { app, quickAddApi: qa } = params;

  const today = new Date();
  const dateStr = today.toISOString().split("T")[0];

  const sessionNum = await qa.inputPrompt("Session Number", "Enter session number (e.g. 01)...");
  if (!sessionNum) return;

  const sessionTitle = await qa.inputPrompt("Session Title", "Enter a short title for this session...");
  if (!sessionTitle) return;

  const paddedNum = sessionNum.toString().padStart(2, "0");
  const name = `Session ${paddedNum} — ${sessionTitle}`;
  const destPath = `Campaign Notes/Session Recaps/${name}.md`;

  if (app.vault.getAbstractFileByPath(destPath)) {
    new Notice(`"${name}" already exists!`);
    return;
  }

  const charName = await selectFromFolder(app, qa, "My Character", "Character", true);
  if (charName === null) return;

  const tpl = app.vault.getAbstractFileByPath("z_Templates/Campaign/Template - Session Recap.md");
  if (!tpl) { new Notice("Session Recap template not found!"); return; }

  let content = await app.vault.read(tpl);
  content = content.replace(/^sessionDate:.*$/m, `sessionDate: ${dateStr}`);
  content = content.replace(/^sessionNumber:.*$/m, `sessionNumber: ${parseInt(sessionNum)}`);
  if (charName) content = setListField(content, "character", charName);

  const file = await app.vault.create(destPath, content);
  await getMainLeaf(app).openFile(file);
  new Notice(`"${name}" created!`);
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
