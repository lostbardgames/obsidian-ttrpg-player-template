module.exports = async (params) => {
  const { app, quickAddApi: qa } = params;

  const sessionName = await selectFromFolder(app, qa, "Campaign Notes/Session Recaps", "Session Recap", true);
  if (sessionName === null) return;

  const questGiver = await selectFromFolder(app, qa, "Campaign Notes/NPCs Known", "Quest Giver", true);
  if (questGiver === null) return;

  const name = await qa.inputPrompt("New Quest", "Enter quest name...");
  if (!name) return;

  const destPath = `Campaign Notes/Quests/${name}.md`;
  if (app.vault.getAbstractFileByPath(destPath)) {
    new Notice(`"${name}" already exists!`);
    return;
  }

  const tpl = app.vault.getAbstractFileByPath("z_Templates/Campaign/Template - Quest.md");
  if (!tpl) { new Notice("Quest template not found!"); return; }

  let content = await app.vault.read(tpl);
  if (sessionName) content = setListField(content, "linkedSession", sessionName);
  if (questGiver) content = setListField(content, "questGiver", questGiver);

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
  const NEW = "＋ Enter New Name";
  const opts = [...existing];
  if (allowSkip) opts.push(SKIP);
  opts.push(NEW);
  const choice = await qa.suggester(opts, opts);
  if (!choice) return null;
  if (choice === SKIP) return "";
  if (choice === NEW) {
    const n = await qa.inputPrompt(`${label} Name`, "Enter name...");
    return n || null;
  }
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
