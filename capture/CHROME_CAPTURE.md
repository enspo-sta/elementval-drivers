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
> 2. HiFiCompass: I am logged in in this Chrome. Start at
>    <https://hificompass.com/en/speakers/measurements>, find each driver listed in the work list and
>    download the original of every chart on its page (remove `/styles/<style>/public/` from the image
>    address) for every drive level shown, and the `.frd` and `.zma` files where offered. Wait 10
>    seconds between HiFiCompass pages, as their `robots.txt` asks.
> 3. Purifi: download the datasheet PDF of each Purifi driver in the work list from
>    <https://purifi-audio.com/>.
> 4. Capture every curve: PDFs with `capture/pdf_vectors.py` (`list`, `ticks`, `extract`), images with
>    `capture/image_curves.py` (`colors`, `extract`). Look at each image yourself to set the plot
>    frame and the axis values, then plot the extracted points over the image and check they sit on
>    the curve before using them.
> 5. Store each drive level as its own measurement set: `kind` from `schema/kinds.json` (add a kind
>    there if a chart fits none, as `EXTENDING.md` describes), `conditions.spl_db` = the sound
>    pressure the fundamental reaches at 1 m (convert from the measuring distance with
>    20 × log10(distance / 1 m)), `conditions.drive_v`, `conditions.distance_mm`, and a `source`
>    naming the source (for example "HiFiCompass HD 4 V (original image)" or "datasheet v1.00 Fig.7
>    (PDF vector)"). Add sets with `capture/add_set.py`; for section 1 of the work list use
>    `--replace <set>`.
> 6. Section 2: check each disagreement against the source. Correct the stored value, or add a note
>    to the set explaining why the two differ.
> 7. Section 4: capture the listed curves again and compare them with the stored ones point by
>    point. Report every difference above 1 dB (outside the measurement's noise floor).
> 8. After each driver run `python3 watch/validate_db.py`, `python3 watch/check_consistency.py`,
>    `node --test tests/*.test.mjs` and `python3 capture/worklist.py`, and fix what they report.
> 9. Commit to a new branch named `capture/<today's date>`, push it and open a pull request. List in
>    it every source address, and for every set whether it came from PDF vectors, a data file or an
>    image. Do not merge it.

## What the tools do

| Tool | Does |
|---|---|
| `capture/pdf_vectors.py` | Reads curves that a PDF draws as lines, exactly (Purifi datasheets). Checked on a test chart: within 0.05 dB. |
| `capture/image_curves.py` | Reads a curve of one colour from a chart image and resamples it to 1/24 octave. Checked on a test chart: within 0.3 dB (one pixel). |
| `capture/add_set.py` | Adds or replaces a measurement set in `drivers.json`; refuses anything the validation check would reject. |
| `capture/worklist.py` | Rebuilds `capture/WORKLIST.md` from the database: low resolution, disagreements, missing curves, a weekly random spot check. |
