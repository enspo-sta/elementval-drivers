# Backups

Everything lives in this one repository, so one backup covers it all: the viewer (`index.html`),
the scripts and automatic jobs (`watch/`, `backup/`, `.github/`), the driver database
(`drivers.json`, `drivers_survey_midbass.json`) and the full history of every change.

## The layers

| Layer | Protects against | Where | Kept |
|---|---|---|---|
| Git history | a bad edit, a mistaken deletion of data | every saved version on GitHub | forever |
| GitHub's deleted-repository restore | deleting the whole repository by mistake | Settings → Repositories → Deleted repositories | 90 days |
| Weekly backup job (Sundays 03:40 UTC) | history being overwritten, a bad automatic change | Actions → Backup → the run → Artifacts | 90 days |
| Weekly copy in Google Drive | losing access to GitHub or the GitHub account | Drive folder `elementval-drivers backups` | until you delete it |

The weekly job makes two files and proves the first one restores before keeping them:

- `elementval-drivers-<date>.bundle`: everything, with full history (about 155 KB today).
- `elementval-drivers-files-<date>.zip`: the current files, openable without Git (about 65 KB today).

## Set up the Google Drive copy (once, about 5 minutes)

Do this after pull request #1 is merged.

1. Open <https://script.google.com> and click **New project**.
2. Delete the few lines already in the editor. Paste the whole of `backup/google-drive-receiver.gs`
   from this repository. Click the save icon and name the project `elementval-drivers backup`.
3. Click **Deploy → New deployment**. Next to "Select type", click the gear and choose **Web app**.
   Set **Execute as: Me** and **Who has access: Anyone**, then click **Deploy**.
4. Click **Authorize access** and choose your Google account. Because this is your own script and
   not a published app, Google may say "Google hasn't verified this app": click **Advanced**, then
   **Go to elementval-drivers backup (unsafe)**, then **Allow**. The script only writes files into
   the folder `elementval-drivers backups`, and only files named like the backups.
5. Copy the **Web app URL** (it ends in `/exec`). Keep it private: anyone who has it could add
   files to that folder.
6. On GitHub, open the repository → **Settings** → **Secrets and variables** → **Actions** →
   **New repository secret**. Name: `GOOGLE_DRIVE_BACKUP_URL`. Secret: paste the URL.
   Click **Add secret**.
7. Test it: **Actions** → **Backup** → **Run workflow**. After about a minute, the Drive folder
   `elementval-drivers backups` holds two files with today's date. Opening the web app URL in a
   browser also shows how many backups the folder holds and the latest date.

From then on it runs every Sunday by itself. The job checks that Google stored exactly as many
bytes as it sent. If any part of the backup fails, the job opens an issue titled "Backup failed"
(label `backup-failed`) in this repository, with a link to what went wrong.

## Restoring

| Situation | What to do |
|---|---|
| One file went wrong (for example `drivers.json`) | Open the file on GitHub, click **History**, open the version you want and copy it back. Or ask Claude: "restore drivers.json to the version from <date>". |
| The whole repository was deleted | Within 90 days: your GitHub profile picture → **Settings** → **Repositories** → **Deleted repositories** → **Restore**. |
| An automatic job or a force-push damaged the history | Download the newest backup from **Actions → Backup → Artifacts**, or from Google Drive, and restore from the bundle (below). |
| GitHub, or the GitHub account, is gone | Take the newest `.bundle` from Google Drive and restore from it (below). |

Restoring from a bundle, on any computer with Git:

```sh
git clone elementval-drivers-<date>.bundle elementval-drivers
```

That gives the complete repository with its history. To put it on a new GitHub repository, create an
empty repository there, then run `git remote set-url origin <new address>` and
`git push -u origin main` inside the restored folder (main holds the software and the database).
Or give the bundle to Claude and ask it to do this. For the data alone, open
`elementval-drivers-files-<date>.zip` with any unzip tool.

## Your accounts are part of the backup

- **GitHub:** keep two-factor sign-in on and store the recovery codes somewhere safe
  (profile picture → **Settings** → **Password and authentication** → **Recovery codes**).
  GitHub Support cannot restore access to an account with two-factor sign-in if both the sign-in
  method and the recovery codes are lost.
- **Google:** the Drive copy is only as safe as your Google account.

Each weekly pair of files is about 220 KB, so a year of backups takes about 11 MB of Drive space.
Delete old ones whenever you like.
