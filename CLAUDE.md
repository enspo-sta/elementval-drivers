# Standing rules for this repository

Read by every Claude Code session that works here. Keep it short; details live in the files named.

## Data

- The database holds measurements exactly as the source published them: never normalise, scale,
  distance-correct or average stored data. Every level a source measured is its own set
  (`CAPTURE.md`, "Levels"). Level matching happens only in the viewer, only when comparing.
- HiFiCompass states its levels at 1 m already (its 315 mm microphone distance is corrected on the
  site): never add a distance correction to HiFiCompass data.
- Level rule when a comparison has to scale: measured sweeps first, else H2 +1.0 and H3 to H5
  +0.7 dB per dB (David's measurements). The textbook (n−1) rule over-predicts; do not use it.
- Sources are kept apart and ranked (`watch/config.json`): Purifi datasheets best, HiFiCompass
  second, Erin's Audio Corner and audioXpress less reliable, diyAudio and Parts Express vary.
- Driver identities are never merged; a variant is its own record. Every set names its `kind`
  (`schema/kinds.json`) and passes `python3 watch/validate_db.py`. Format: `EXTENDING.md`.

## Shops and prices (David's knowledge, 25 September 2026)

- **audio-hi.fi** (<https://audio-hi.fi/en/>, Finland) is the go-to distributor in Europe for BlieSMa.
- **SoundImports** (<https://www.soundimports.eu/>) is often the most expensive and no longer
  carries BlieSMa.
- **Toutlehautparleur** (<https://www.toutlehautparleur.com/>) is often the cheapest, but its good
  prices show only when logged in. Reading them needs Claude Code with the Chrome plugin on
  David's own computer (`capture/CHROME_CAPTURE.md`); the weekly scan sees only the public price.
- Prices are shown in kronor and in the shop's currency; prefer European shops.
- What the scans found (September 2026): **Purifi's own shop** lists prices six to eight times
  retail (2 400 to 3 000 EUR): treated as box prices (`"pack"` in `watch/prices_config.json`), never
  the headline price; the box size is not known. **audio-hi.fi** and **loudspeakerfreaks.com** send
  an incomplete certificate chain; the scanner completes it the way a browser does (verification
  stays on, never turned off). **Toutlehautparleur** refuses automatic reading (HTTP 403).
  **Lautsprechershop, Intertechnik, Speakerbuddies, Europe Audio, Hificollective, BlieSMa** have no
  usable sitemap; their product pages can be listed by hand (`"pages"`).

## Where things run

- Cloud sessions cannot reach HiFiCompass, Purifi or the shops: capture and logged-in prices run
  on David's computer with the Chrome plugin (`capture/CHROME_CAPTURE.md`); the weekly scans run
  on GitHub (`.github/workflows/`).
- The repository is public: never commit downloaded source files (`incoming/` is ignored).
- Answers that need a document are HTML in David's dark style; prices in SEK or EUR; no invented
  acronyms; every claim with a link.
