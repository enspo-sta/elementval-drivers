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

## What the tools do

| Tool | Does |
|---|---|
| `capture/pdf_vectors.py` | Reads curves that a PDF draws as lines, exactly (Purifi datasheets). Checked on a test chart: within 0.05 dB. |
| `capture/image_curves.py` | Reads a curve of one colour from a chart image and resamples it to 1/24 octave. Checked on a test chart: within 0.3 dB (one pixel). |
| `capture/add_set.py` | Adds or replaces a measurement set in `drivers.json`; refuses anything the validation check would reject. |
| `capture/chart_read.py` | Runs on GitHub (which can reach HiFiCompass): reads the response, harmonics, current-distortion and impedance charts of the drivers in `capture/chart_read_request.txt`, calibrated from each chart's grid and labels, with self-checks against the page's table; `capture/sets_from_chart_read.py --write` turns the result into sets. |
| `capture/imd_read.py` | Runs on GitHub: reads the two-tone intermodulation spectra of the drivers in `capture/imd_read_request.txt` (the test from the file name, the peaks at both tones and every product up to the 5th order, checked against the cursor readout each chart prints); `capture/sets_from_imd_read.py --write` turns the result into sets. |
| `capture/datasheet_probe.py` | Runs on GitHub (which can reach Purifi): finds each model in `capture/datasheet_request.txt` on purifi-audio.com, and writes the datasheet's text, printed numbers and vector lines, and the measured files in the downloads beside it (off-axis responses, impedance, on-axis response), as numbers only; `capture/sets_from_datasheet_probe.py --write` turns the files into sets after checking each against the datasheet's stated sensitivity or minimum impedance. |
| `capture/worklist.py` | Rebuilds `capture/WORKLIST.md` from the database: low resolution, disagreements, missing curves, a weekly random spot check. |
