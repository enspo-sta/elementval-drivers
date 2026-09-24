/**
 * elementval-drivers: backup receiver for Google Drive.
 *
 * Paste this whole file into a new Google Apps Script project (https://script.google.com),
 * then Deploy > New deployment > Web app, "Execute as: Me", "Who has access: Anyone".
 * Put the web app address in GitHub as the repository secret GOOGLE_DRIVE_BACKUP_URL.
 * Every Sunday the GitHub "Backup" job then sends its backup files here, and this script
 * saves them in the Drive folder below. Full instructions: BACKUP.md in the repository.
 *
 * Open the web app address in a browser to see how many backups the folder holds.
 */
const FOLDER_NAME = 'elementval-drivers backups';
const NAME_PATTERN = /^elementval-drivers(-files)?-\d{4}-\d{2}-\d{2}\.(bundle|zip)$/;
const MAX_BYTES = 50 * 1024 * 1024;

// The GitHub job sends each backup file as base64 text, with its file name as ?name=...
function doPost(e) {
  const name = String((e && e.parameter && e.parameter.name) || '');
  if (!NAME_PATTERN.test(name)) {
    return reply({ ok: false, error: 'unexpected file name: ' + name });
  }
  const text = (e.postData && e.postData.contents) || '';
  if (!text || text.length > MAX_BYTES * 1.4) {
    return reply({ ok: false, error: 'empty or too large' });
  }
  const bytes = Utilities.base64Decode(text);
  const folder = backupFolder();
  const earlier = folder.getFilesByName(name);          // a re-run on the same day replaces that day's file
  while (earlier.hasNext()) earlier.next().setTrashed(true);
  const type = name.endsWith('.zip') ? 'application/zip' : 'application/octet-stream';
  const file = folder.createFile(Utilities.newBlob(bytes, type, name));
  return reply({ ok: true, name: name, bytes: bytes.length, id: file.getId() });
}

// Opening the web app address in a browser shows that the receiver works.
function doGet() {
  const folder = backupFolder();
  const files = folder.getFiles();
  let count = 0, latest = '';
  while (files.hasNext()) {
    const date = (files.next().getName().match(/\d{4}-\d{2}-\d{2}/) || [''])[0];
    count++;
    if (date > latest) latest = date;
  }
  return reply({ ok: true, folder: FOLDER_NAME, files: count, latest_backup_date: latest });
}

function backupFolder() {
  const found = DriveApp.getFoldersByName(FOLDER_NAME);
  return found.hasNext() ? found.next() : DriveApp.createFolder(FOLDER_NAME);
}

function reply(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
