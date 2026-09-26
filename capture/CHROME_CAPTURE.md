# Capturing from HiFiCompass and Purifi on your own computer

The cloud sessions cannot open HiFiCompass or Purifi, and cannot use your HiFiCompass login. Claude
Code on your own computer, connected to Chrome, can: it uses the Chrome you are logged in to. This
page is the whole routine. What to capture is in `capture/WORKLIST.md` (rebuilt with
`python3 capture/worklist.py`).

## Once: set up your computer

1. Install Claude Code and connect it to Chrome with the Claude in Chrome extension. Both are
   described in the Claude Code documentation: <https://code.claude.com/docs>.
2. Install Git and Python 3 if you do not have them: <https://git-scm.com/downloads>,
   <https://www.python.org/downloads/>. Node.js runs the viewer's tests: <https://nodejs.org/>.
3. In a terminal:

   ```sh
   git clone https://github.com/enspo-sta/elementval-drivers.git
   cd elementval-drivers
   python3 -m pip install pymupdf pillow numpy
   ```

4. Open Chrome and log in to HiFiCompass (<https://hificompass.com/>).

## Every time: start Claude Code with Chrome and paste the instructions

In the `elementval-drivers` folder run `git pull`, then `claude --chrome`, and paste this:

> Work through `capture/WORKLIST.md` in this repository. Follow `CAPTURE.md` for resolution and
> `EXTENDING.md` for the data format. Rules:
>
> 1. Save every page, chart image, PDF and data file you download under `incoming/` (one folder per
>    driver id). That folder is ignored by Git: never commit source files, the repository is public.
> 2. Drivers just added (section 3 lists them with their page address, and `capture/inventory.md`
>    lists every chart, data file and table their page offers): a GitHub job (`capture/chart_read.py`,
>    request file `capture/chart_read_request.txt`) reads the on-axis response, harmonics, current
>    distortion and impedance charts of HiFiCompass by itself and `python3 capture/sets_from_chart_read.py
>    --write` stores them as sets of confidence *medium* (section 5 of the work list lists them: check
>    each by eye against its chart). A second job (`capture/imd_read.py`, request file
>    `capture/imd_read_request.txt`) reads the two-tone intermodulation spectra; `python3
>    capture/sets_from_imd_read.py --write` stores them (kind imd-products). Capture by hand what the jobs
>    do not take: the off-axis charts, the 10 Ω impedance zooms, every table, and any chart whose reading
>    a job reports as failed or waiting.
> 3. HiFiCompass: I am logged in in this Chrome. Start at
>    <https://hificompass.com/en/speakers/measurements>, find each driver listed in the work list and
>    download the original of every chart on its page (remove `/styles/<style>/public/` from the image
>    address) for every drive level shown, and the `.frd` and `.zma` files where offered. Wait 10
>    seconds between HiFiCompass pages, as their `robots.txt` asks.
> 4. Purifi: download the datasheet PDF of each Purifi driver in the work list from
>    <https://purifi-audio.com/>.
> 5. Capture every curve: PDFs with `capture/pdf_vectors.py` (`list`, `ticks`, `extract`), images with
>    `capture/image_curves.py` (`colors`, `extract`). Look at each image yourself to set the plot
>    frame and the axis values, then plot the extracted points over the image and check they sit on
>    the curve before using them.
> 6. Store each drive level as its own measurement set: `kind` from `schema/kinds.json` (add a kind
>    there if a chart fits none, as `EXTENDING.md` describes), `conditions.spl_db` = the sound
>    pressure the fundamental reaches at 1 m as the source states it (HiFiCompass already states its
>    levels at 1 m: take them as shown, never add a distance correction), `conditions.drive_v`, `conditions.distance_mm`, and a `source`
>    naming the source (for example "HiFiCompass HD 4 V (original image)" or "datasheet v1.00 Fig.7
>    (PDF vector)"). Add sets with `capture/add_set.py`; for section 1 of the work list use
>    `--replace <set>`.
> 7. Section 2: check each disagreement against the source. Correct the stored value, or add a note
>    to the set explaining why the two differ.
> 8. Section 4: capture the listed curves again and compare them with the stored ones point by
>    point. Report every difference above 1 dB (outside the measurement's noise floor).
> 9. Prices: the weekly scan on GitHub (`watch/prices.py`) reads only public prices. Toutlehautparleur
>    (<https://www.toutlehautparleur.com/>) shows its good prices only when logged in: log in there in
>    this Chrome, open the page of every driver that has a Toutlehautparleur offer in `prices.json`
>    (and search the shop for the drivers that have none), and write the logged-in price into that
>    offer as `"price_logged_in": <number>` with `"checked": "<today>"` (add an offer with the page
>    address when the shop has the driver but the scan found no public price). For BlieSMa drivers
>    also check audio-hi.fi (<https://audio-hi.fi/en/>), the go-to European distributor.
> 10. Toutlehautparleur wishlist and cart: logged in there in this Chrome, open the wishlist ("Ma liste
>     d'envies" / "Mes listes") and the cart ("Panier"). For every driver in either, note the name as the
>     shop writes it, the page address, the price shown while logged in, the public price (open the page
>     in a private window, or read the crossed-out price), the list it came from and the quantity. Write
>     them to `capture/tlhp_wishlist.json` in the form the top of `capture/from_shop_list.py` shows, then
>     run `python3 capture/from_shop_list.py`: a driver already in the database gets the shop page and the
>     logged-in offer; a driver not yet in the database gets a new record, the offer, and a line in
>     `capture/inventory_request.txt`. Commit and push: GitHub then reads each new driver's HiFiCompass
>     page (`capture/inventory.py`) and `python3 capture/new_from_inventory.py --write` fills the record
>     with its parameters; capture its curves as step 2 says (from HiFiCompass directly, or from the
>     manufacturer's datasheet when HiFiCompass has not measured it).
> 11. After each driver run `python3 watch/validate_db.py`, `python3 watch/check_consistency.py`,
>    `node --test tests/*.test.mjs` and `python3 capture/worklist.py`, and fix what they report.
> 12. Commit to a new branch named `capture/<today's date>`, push it and open a pull request. List in
>    it every source address, and for every set whether it came from PDF vectors, a data file or an
>    image. Do not merge it.

## The charts HiFiCompass shows only to Premium accounts (seven drivers)

On these pages, a visitor who is not logged in with Premium sees a notice picture in place of each chart
("This data is only available to users with a Premium account"; `watch/completeness.md` lists them).

**On a Windows PC,** set it up once as the Windows section below says. Then, in the `elementval-drivers` folder,
run `git pull` and `claude --chrome`, and type:

> Read capture/CHROME_CAPTURE.md and do the section "The charts HiFiCompass shows only to Premium accounts".

What Claude does then (these are its instructions; you do not paste them):

> Capture the charts HiFiCompass shows only to Premium accounts, for the seven drivers below. David is logged in
> to HiFiCompass with Premium in this Chrome. He is not a programmer: when you need him to do something, say it
> in one plain sentence, and ask before you install anything or change anything outside this folder.
>
> **Rules for the whole task**
> - On Windows run Python as `python` (or `py` if `python` is not found), never `python3`: there `python3` is
>   usually a Microsoft Store placeholder that prints "Python was not found". Wherever this repository says
>   `python3`, run `python`.
> - Write files with the scripts or the Write tool, never with PowerShell's `>` or `Out-File` (they write UTF-16).
> - Everything downloaded goes under `incoming/<driver id>/`, which Git ignores. Never commit anything from
>   `incoming/`: the repository is public.
> - Change only the data. If a script or a test fails for another reason, tell David and do not edit the code.
>
> 0. **Check this computer** and show David the result as a short list: `git --version`, `git config user.name`,
>    `git config user.email`, `python --version` (3.10 or newer), `python -c "import PIL, numpy; print('ok')"`,
>    `python -c "import sys; sys.path.insert(0, 'capture'); import chart_probe as CP; print(CP.TESSERACT)"` (it
>    must print a path to tesseract, not None), `node --version` (21 or newer).
>    - For anything missing, say in one sentence what it is for and ask before installing it with winget, one
>      package at a time, adding `-e --accept-source-agreements --accept-package-agreements`: `Git.Git`,
>      `Python.Python.3.13`, `UB-Mannheim.TesseractOCR`, `OpenJS.NodeJS.LTS`. Python packages:
>      `python -m pip install pillow numpy`. Windows may ask David to click Yes.
>    - A program installed during this session is not on this session's path. If Git, Python or Node.js had to be
>      installed, tell David to close this window, open a new PowerShell window, type `cd $HOME\elementval-drivers`
>      and `claude --chrome --continue`, and run the checks again. (Tesseract is found without this.)
>    - If `git config user.name` or `user.email` is empty, ask David for his name and the email address of his
>      GitHub account, and set them with `git config --global`.
>    - Run `git pull` and `git status`. If there are changes you did not make, stop and tell David.
>    Do not start step 1 until every check passes.
> 1. **Open each page**, waiting 10 seconds between HiFiCompass pages:
>    - `sb-satori-wo24p-8`: <https://hificompass.com/ru/speakers/measurements/satori/satori-wo24p-8>
>    - `sb-satori-wo24p-4`: <https://hificompass.com/ru/speakers/measurements/satori/satori-wo24p-4>
>    - `sb-sb34nrxl75-8`: <https://hificompass.com/ru/speakers/measurements/sbacoustics/sb-acoustics-sb34nrxl75-8>
>    - `sb17nbac35-8`: <https://hificompass.com/ru/speakers/measurements/sbacoustics/sb-acoustics-sb17nbac35-8>
>    - `sb-sb26adc-c000-4`: <https://hificompass.com/ru/speakers/measurements/sbacoustics/sb-acoustics-sb26adc-c000-4>
>    - `sb-audience-rosso-12mw300`: <https://hificompass.com/ru/speakers/measurements/sb-audience/sb-audience-rosso-12mw300>
>    - `lavoce-man06200-8`: <https://hificompass.com/en/speakers/measurements/lavoce/lavoce-man06200-8>
> 2. If a chart still shows the notice "This data is only available to users with a Premium account", **stop and
>    tell David**: the account in this Chrome does not have Premium.
> 3. **Save the charts.** On each page, note the address of every chart image and of the `.frd` and `.zma` files
>    where offered. Take each chart's original image (remove `/styles/<style>/public/` from its address). Leave out
>    the step response, waterfall and energy-time charts: the database does not keep them. Off-axis first, then the
>    on-axis response, harmonics at 315 mm and at 20 mm, current distortion, impedance, the near-field response and
>    the two intermodulation pictures. Save each file under `incoming/<driver id>/` with its own name and extension
>    (a `.jpg` stays `.jpg`; if two would share a name, put the chart type in front). Download from the terminal
>    first, one driver per command (this waits 10 seconds between requests):
>
>    ```
>    python - <<'PY'
>    import sys, pathlib; sys.path.insert(0, "capture"); import chart_probe as CP
>    last, folder = [0.0], pathlib.Path("incoming/<driver id>")
>    folder.mkdir(parents=True, exist_ok=True)
>    for url in ["<address 1>", "<address 2>"]:
>        p = folder / url.split("?")[0].rsplit("/", 1)[-1]
>        p.write_bytes(CP.fetch(url, last)); print(p.name, p.stat().st_size, "bytes")
>    PY
>    ```
>
>    Then look at every saved picture yourself. If one is the Premium notice, or the download is refused, the file
>    is served only to the logged-in browser: in the Chrome tab, fetch the address with the login
>    (`fetch(address, {credentials: "include"})`) and save it through a download link. Chrome puts it in David's
>    Downloads folder (`~/Downloads` in Git Bash); move it into `incoming/<driver id>/`. If Chrome asks whether the
>    site may download several files, ask David to click Allow.
> 4. **List the chart images** in `incoming/<driver id>/charts.tsv` (write it with the Write tool), one line per
>    image, separated by tabs: file name, chart type (`response`, `near-response`, `off-axis`, `harmonics`,
>    `current` or `impedance`), and the image's address on hificompass.com. Leave the intermodulation pictures out
>    of this list (no reader on this computer takes them); name them in the pull request as saved but not read.
> 5. **Read the charts.**
>    - For each driver: `python capture/read_local_charts.py --id <driver id>`.
>    - Then `python capture/sets_from_chart_read.py` and look only at the lines for these seven ids (it prints
>      every driver in `capture/chart_read.json`).
>    - Look at every chart yourself beside its reading: the axes, the angle or drive level of each curve, the checks.
>    - The automatic reader stores one set per picture, at the voltage in the file name. These older pages may put
>      several drive levels in one picture: such a picture must not be stored that way, and must not be renamed to
>      one voltage; read it by hand (below). Rename a picture in the newer pattern (`<model>_315mm_2v83_0deg.png`,
>      `<model>_offaxis.png`, `<model>_offaxis_normalized_5-30db.png`, `<model>_315mm_4v_hpf2-60.png`,
>      `<model>_20mm_4v_hd.png`, `<model>_chd_4v.png`, `<model>_impedance_100_ohm.png`) only when it holds exactly
>      one drive level and one distance, and keep its real extension.
>    - When the automatic reading is right: `python capture/sets_from_chart_read.py --write`.
>    - Read by hand a chart with several levels, one where the reader says "axes could not be fitted", or one whose
>      reading does not sit on the curve: follow `CAPTURE.md` with `capture/image_curves.py` (`colors`, then
>      `extract ... --out incoming/<driver id>/<name>.json`). Set the plot frame and the axis values by looking at the
>      picture, then plot the points over the picture and check they sit on the curve. Add each drive level as its
>      own set: `python capture/add_set.py --driver <id> --set <meta.json> --series <file>.json`, with `kind` from
>      `schema/kinds.json`, `conditions.spl_db` (the level at 1 m as HiFiCompass states it; never add a distance
>      correction), `conditions.drive_v`, `conditions.distance_mm` (315, or 20 for the near-field pictures), and a
>      source such as "HiFiCompass off-axis (original image, logged in with Premium)".
> 6. **Check:** `python watch/validate_db.py`, `python capture/completeness.py`, `python capture/worklist.py` and
>    `node --test tests/*.test.mjs`; fix what they report in the data. In `git diff --stat`, if `drivers.json` shows
>    almost every line changed, the line endings changed: stop and tell David.
> 7. **Hand it over:** commit to a new branch named `capture/<today's date>` with only the repository files you
>    changed (`drivers.json`, `capture/chart_read.json`, `watch/completeness.json`, `watch/completeness.md`,
>    `capture/WORKLIST.md`), never `incoming/`. Push it; the first push opens a browser window to sign in to GitHub,
>    so tell David to sign in there. If the `gh` tool is installed and logged in, open a pull request with it;
>    otherwise give David the link Git prints after the push. In the pull request list every chart address and, for
>    every set, whether the automatic reader or `capture/image_curves.py` read it. List the saved intermodulation
>    pictures as not read. Do not merge it.

### Set up a Windows PC once

In PowerShell (Start menu, type PowerShell, press Enter):

1. Claude Code: `irm https://claude.ai/install.ps1 | iex`, then close the window and open a new one
   (<https://code.claude.com/docs/en/setup>).
2. The tools, in one line:
   `winget install -e --accept-source-agreements --accept-package-agreements --id Git.Git; winget install -e --accept-source-agreements --accept-package-agreements --id Python.Python.3.13; winget install -e --accept-source-agreements --accept-package-agreements --id UB-Mannheim.TesseractOCR; winget install -e --accept-source-agreements --accept-package-agreements --id OpenJS.NodeJS.LTS`
   Click Yes when Windows asks. Close the window and open a new one.
3. `python -m pip install pillow numpy`
4. `cd $HOME` then `git clone https://github.com/enspo-sta/elementval-drivers.git` (not in the Desktop or
   Documents folder, which OneDrive may sync).
5. In Chrome, install the Claude in Chrome extension
   (<https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn>) and sign in to it with
   the same Claude account (<https://code.claude.com/docs/en/chrome>).

The repository sets Python to UTF-8 for every Claude Code session in this folder (`.claude/settings.json`), and
the scripts read and write every file as UTF-8, so Windows' own character set does not matter.

## What the tools do

| Tool | Does |
|---|---|
| `capture/pdf_vectors.py` | Reads curves that a PDF draws as lines, exactly (Purifi datasheets). Checked on a test chart: within 0.05 dB. |
| `capture/image_curves.py` | Reads a curve of one colour from a chart image and resamples it to 1/24 octave. Checked on a test chart: within 0.3 dB (one pixel). |
| `capture/add_set.py` | Adds or replaces a measurement set in `drivers.json`; refuses anything the validation check would reject. |
| `capture/chart_read.py` | Runs on GitHub (which can reach HiFiCompass): reads the response, harmonics, current-distortion and impedance charts of the drivers in `capture/chart_read_request.txt`, calibrated from each chart's grid and labels, with self-checks against the page's table; `capture/sets_from_chart_read.py --write` turns the result into sets. |
| `capture/imd_read.py` | Runs on GitHub: reads the two-tone intermodulation spectra of the drivers in `capture/imd_read_request.txt` (the test from the file name, the peaks at both tones and every product up to the 5th order, checked against the cursor readout each chart prints); `capture/sets_from_imd_read.py --write` turns the result into sets. |
| `capture/datasheet_probe.py` | Runs on GitHub (which can reach Purifi): finds each model in `capture/datasheet_request.txt` on purifi-audio.com, and writes the datasheet's text, printed numbers and vector lines, and the measured files in the downloads beside it (off-axis responses, impedance, on-axis response), as numbers only; `capture/sets_from_datasheet_probe.py --write` turns the files into sets after checking each against the datasheet's stated sensitivity or minimum impedance. |
| `capture/sets_from_page_charts.py` | Turns off-axis charts read from a lab's page by `capture/datasheet_probe.py` (Erin's Audio Corner: request lines `erin record-id MODEL`) into sets: each curve named by the colour of its legend line, checked against the chart's printed mean level and against the normalized chart. |
| `capture/read_local_charts.py` | Reads chart images saved on your computer (listed in `incoming/<id>/charts.tsv`) with the GitHub job's reader and adds them to `capture/chart_read.json`, for `capture/sets_from_chart_read.py --write`. |
| `capture/worklist.py` | Rebuilds `capture/WORKLIST.md` from the database: low resolution, disagreements, missing curves, a weekly random spot check. |
