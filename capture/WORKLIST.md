# Capture work list

Written by `capture/worklist.py` on 2026-09-25. How to work through it: `capture/CHROME_CAPTURE.md`.

## 1. Capture again at higher resolution

Below 40 points per decade (target 80, CAPTURE.md). Replace each set with `capture/add_set.py --replace <set>`.

| Driver | Set | What | Source | Now | How |
|---|---|---|---|---|---|
| Purifi PTT6.5M08-NAA-08 (`ptt65m08naa08`) | 2 | HD (orders) | Manufacturer datasheet | 11 per decade | PDF vector data: `capture/pdf_vectors.py` (Purifi draws its graphs as vector lines) |
| Purifi PTT6.5M08-NAA-08 (`ptt65m08naa08`) | 3 | HD (current-domain) | Manufacturer datasheet | 5 per decade | PDF vector data: `capture/pdf_vectors.py` (Purifi draws its graphs as vector lines) |
| Purifi PTT8.0X04-NAB-01 (`ptt80x04nab01`) | 0 | HD vs frequency (ratio) | Manufacturer datasheet | 20 per decade | PDF vector data: `capture/pdf_vectors.py` (Purifi draws its graphs as vector lines) |
| Purifi PTT6.5X04-NAA-08 (`ptt65x04naa08`) | 0 | HD vs frequency (ratio) | Manufacturer datasheet | 20 per decade | PDF vector data: `capture/pdf_vectors.py` (Purifi draws its graphs as vector lines) |
| Purifi PTT5.25X04-NAA-05 (`ptt525x04naa05`) | 0 | HD vs frequency (ratio) | Manufacturer datasheet | 20 per decade | PDF vector data: `capture/pdf_vectors.py` (Purifi draws its graphs as vector lines) |
| Purifi PTT1.3T04-HAG-10 (`ptt13t04hag10`) | 0 | HD vs frequency (ratio) | Manufacturer datasheet | 20 per decade | PDF vector data: `capture/pdf_vectors.py` (Purifi draws its graphs as vector lines) |
| Purifi PTT1.3T04-HAG-01 (`ptt13t04hag01`) | 0 | HD vs frequency (ratio) | Manufacturer datasheet | 20 per decade | PDF vector data: `capture/pdf_vectors.py` (Purifi draws its graphs as vector lines) |
| SB Acoustics Satori WO24P-8 (`sb-satori-wo24p-8`) | 0 | HD (orders) vs frequency | HiFiCompass | 5 per decade | original image (remove `/styles/<style>/public/` from the image address), then `capture/image_curves.py` |
| SB Acoustics SB34NRXL75-8 (Norex) (`sb-sb34nrxl75-8`) | 0 | HD (orders) vs frequency | HiFiCompass | 5 per decade | original image (remove `/styles/<style>/public/` from the image address), then `capture/image_curves.py` |
| Purifi PTT8.0X04-NAB-02 (`purifi-ptt8-0x04-nab-02`) | 0 | HD (orders) vs frequency | HiFiCompass | 5 per decade | original image (remove `/styles/<style>/public/` from the image address), then `capture/image_curves.py` |
| Purifi PTT10.0X04-NAB-02 (`purifi-ptt10-0x04-nab-02`) | 0 | HD (orders) vs frequency | HiFiCompass | 5 per decade | original image (remove `/styles/<style>/public/` from the image address), then `capture/image_curves.py` |
| SB Acoustics SB17CAC35-4 (proxy) (`sb17cac35-4`) | 0 | Large-signal compression vs frequency | Erin's Audio Corner | 37 per decade | original chart (Dropbox or site image, 1600 × 900), then `capture/image_curves.py` |
| SB Acoustics SB17CAC35-4 (proxy) (`sb17cac35-4`) | 1 | Large-signal distortion vs frequency | Erin's Audio Corner | 37 per decade | original chart (Dropbox or site image, 1600 × 900), then `capture/image_curves.py` |
| Purifi PTT6.5W04 (paper, proxy) (`ptt65w04-paper`) | 0 | Large-signal compression vs frequency | Erin's Audio Corner | 37 per decade | original chart (Dropbox or site image, 1600 × 900), then `capture/image_curves.py` |
| Purifi PTT6.5W04 (paper, proxy) (`ptt65w04-paper`) | 1 | Large-signal distortion vs frequency | Erin's Audio Corner | 37 per decade | original chart (Dropbox or site image, 1600 × 900), then `capture/image_curves.py` |

## 2. Values that disagree: check against the source

From `watch/check_consistency.py` (full list in `watch/consistency.md`).

| Check | Driver | Detail |
|---|---|---|
| band THD | `ptt525x04naa05` | 450–1800 Hz at 94 dB: table 0.095 %, from the curve 0.0774 % (-1.8 dB) |
| band THD | `ptt525x04naa05` | 80–5000 Hz at 94 dB: table 0.254 %, from the curve 0.157 % (-4.2 dB) |
| band THD | `purifi-ptt10-0x04-nab-02` | 50–300 Hz at 91 dB: table 0.156 %, from the curve 0.128 % (-1.7 dB) |
| notes | `purifi-ptt10-0x04-nab-02` | a note says Pe was corrected to 350, the stored Pe is 'TBD (est 400)' |
| parameters | `m74a-6` | Qes: stored 0.75, from the others 0.7 (6.7 % apart) |
| parameters | `t25a-6` | Qes: stored 0.82, from the others 0.568 (30.7 % apart) |
| parameters | `t34a-4` | Qes: stored 0.42, from the others 0.374 (10.9 % apart) |
| parameters | `t34b-4` | Qes: stored 0.42, from the others 0.348 (17.2 % apart) |
| sweep | `ptt13t04hag01` | H2 at 1000 Hz, 94 dB: sweep -60.9 dB, curve -69.2 dB (+8.3 dB) |
| sweep | `ptt13t04hag01` | H3 at 1000 Hz, 94 dB: sweep -50.9 dB, curve -66.4 dB (+15.5 dB) |
| sweep | `ptt13t04hag01` | H3 at 4000 Hz, 94 dB: sweep -98.2 dB, curve -91.1 dB (-7.2 dB) |
| sweep | `ptt13t04hag10` | H2 at 1000 Hz, 94 dB: sweep -48.8 dB, curve -54.6 dB (+5.8 dB) |
| sweep | `ptt13t04hag10` | H3 at 1000 Hz, 94 dB: sweep -55.4 dB, curve -66.7 dB (+11.4 dB) |
| sweep | `ptt13t04hag10` | H3 at 4000 Hz, 94 dB: sweep -97.1 dB, curve -91.0 dB (-6.1 dB) |
| sweep | `ptt65x04naa08` | H3 at 125 Hz, 94 dB: sweep -65.6 dB, curve -70.6 dB (+5.0 dB) |

## 3. Every curve HiFiCompass and Purifi publish

Stored now, and what to add. Capture each drive level as its own set with the SPL it gives at 1 m.

- **Purifi PTT6.5M08-NAA-08** (`ptt65m08naa08`), Manufacturer datasheet: stored hd-current, hd-frequency 94 dB, imd-spectrum 94 dB.
  Add: frequency response figure; impedance figure; harmonic distortion vs level (level sweeps).
- **Purifi PTT8.0X04-NAB-01** (`ptt80x04nab01`), Manufacturer datasheet: stored hd-frequency 94 dB, hd-level, imd-spectrum 80 dB.
  Add: frequency response figure; impedance figure; current distortion.
- **Purifi PTT6.5X04-NAA-08** (`ptt65x04naa08`), Manufacturer datasheet: stored hd-frequency 94 dB, hd-level, imd-spectrum 80 dB.
  Add: frequency response figure; impedance figure; current distortion.
- **Purifi PTT5.25X04-NAA-05** (`ptt525x04naa05`), HiFiCompass: stored hd-frequency 94 dB, thd-bands 94 dB.
  Add: the harmonics at each drive level actually measured (the stored 94 dB curve was normalised from them; keep it until they are in); axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); impedance (use the .zma file when offered); two-tone intermodulation, where measured.
- **Purifi PTT5.25X04-NAA-05** (`ptt525x04naa05`), Manufacturer datasheet: stored hd-frequency 94 dB, hd-level, imd-spectrum 80 dB.
  Add: frequency response figure; impedance figure; current distortion.
- **Purifi PTT1.3T04-HAG-10** (`ptt13t04hag10`), Manufacturer datasheet: stored hd-frequency 94 dB, hd-level.
  Add: frequency response figure; impedance figure; current distortion; intermodulation spectra (both tone pairs).
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), Manufacturer datasheet: stored hd-frequency 94 dB, hd-level.
  Add: frequency response figure; impedance figure; current distortion; intermodulation spectra (both tone pairs).
- **SB Acoustics Satori WO24P-8** (`sb-satori-wo24p-8`), HiFiCompass: stored hd-frequency 91 dB, thd-bands 91 dB.
  Add: axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); impedance (use the .zma file when offered); two-tone intermodulation, where measured.
- **SB Acoustics SB34NRXL75-8 (Norex)** (`sb-sb34nrxl75-8`), HiFiCompass: stored hd-frequency 91 dB, imd-summary 91.1 dB, thd-bands 91 dB.
  Add: axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); impedance (use the .zma file when offered).
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), HiFiCompass: stored hd-frequency 91 dB, hd-frequency 94 dB, thd-bands 91 dB, thd-bands 94 dB.
  Add: the harmonics at each drive level actually measured (the stored 94 dB curve was normalised from them; keep it until they are in); axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); impedance (use the .zma file when offered); two-tone intermodulation, where measured.
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), Manufacturer datasheet: stored nothing.
  Add (if Purifi publishes a datasheet for this exact variant): frequency response figure; impedance figure; harmonic distortion vs frequency at 94 dB; harmonic distortion vs level (level sweeps); current distortion; intermodulation spectra (both tone pairs).
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), HiFiCompass: stored hd-frequency 91 dB, imd-summary 91.67 dB, thd-bands 91 dB.
  Add: axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); impedance (use the .zma file when offered).
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), Manufacturer datasheet: stored nothing.
  Add (if Purifi publishes a datasheet for this exact variant): frequency response figure; impedance figure; harmonic distortion vs frequency at 94 dB; harmonic distortion vs level (level sweeps); current distortion; intermodulation spectra (both tone pairs).
- **SB Acoustics Satori WO24P-4** (`sb-satori-wo24p-4`), HiFiCompass: stored imd-summary 91.15 dB.
  Add: axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); harmonics H2 to H5 at every drive level shown, as measured (not normalised to one level: the viewer interpolates); impedance (use the .zma file when offered).
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), HiFiCompass: stored hd-frequency 94 dB, thd-bands 94 dB.
  Add: the harmonics at each drive level actually measured (the stored 94 dB curve was normalised from them; keep it until they are in); axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); impedance (use the .zma file when offered); two-tone intermodulation, where measured.
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), Manufacturer datasheet: stored nothing.
  Add (if Purifi publishes a datasheet for this exact variant): frequency response figure; impedance figure; harmonic distortion vs frequency at 94 dB; harmonic distortion vs level (level sweeps); current distortion; intermodulation spectra (both tone pairs).
- **SB Acoustics SB17NBAC35-8** (`sb17nbac35-8`), HiFiCompass: stored hd-frequency 94 dB, thd-bands 94 dB.
  Add: the harmonics at each drive level actually measured (the stored 94 dB curve was normalised from them; keep it until they are in); axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); impedance (use the .zma file when offered); two-tone intermodulation, where measured.
- **BlieSMa M74T-6** (`m74t-6`), HiFiCompass: stored hd-frequency 94 dB, thd-bands 94 dB.
  Add: the harmonics at each drive level actually measured (the stored 94 dB curve was normalised from them; keep it until they are in); axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); impedance (use the .zma file when offered); two-tone intermodulation, where measured.
- **BlieSMa M74A-6** (`m74a-6`), HiFiCompass: stored nothing. Page: <https://hificompass.com/en/speakers/measurements/bliesma/bliesma-m74a-6> (what it offers: `capture/inventory.md`).
  Add: axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); harmonics H2 to H5 at every drive level shown, as measured (not normalised to one level: the viewer interpolates); impedance (use the .zma file when offered); two-tone intermodulation, where measured.
- **BlieSMa T25A-6** (`t25a-6`), HiFiCompass: stored nothing. Page: <https://hificompass.com/en/speakers/measurements/bliesma/bliesma-t25a-6> (what it offers: `capture/inventory.md`).
  Add: axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); harmonics H2 to H5 at every drive level shown, as measured (not normalised to one level: the viewer interpolates); impedance (use the .zma file when offered); two-tone intermodulation, where measured.
- **BlieSMa T25T-6** (`t25t-6`), HiFiCompass: stored nothing. Page: <https://hificompass.com/en/speakers/measurements/bliesma/bliesma-t25t-6> (what it offers: `capture/inventory.md`).
  Add: axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); harmonics H2 to H5 at every drive level shown, as measured (not normalised to one level: the viewer interpolates); impedance (use the .zma file when offered); two-tone intermodulation, where measured.
- **BlieSMa T34A-4** (`t34a-4`), HiFiCompass: stored nothing. Page: <https://hificompass.com/en/speakers/measurements/bliesma/bliesma-t34a-4> (what it offers: `capture/inventory.md`).
  Add: axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); harmonics H2 to H5 at every drive level shown, as measured (not normalised to one level: the viewer interpolates); impedance (use the .zma file when offered); two-tone intermodulation, where measured.
- **BlieSMa T34B-4** (`t34b-4`), HiFiCompass: stored nothing. Page: <https://hificompass.com/en/speakers/measurements/bliesma/bliesma-t34b-4> (what it offers: `capture/inventory.md`).
  Add: axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); harmonics H2 to H5 at every drive level shown, as measured (not normalised to one level: the viewer interpolates); impedance (use the .zma file when offered); two-tone intermodulation, where measured.
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), HiFiCompass: stored nothing. Page: <https://hificompass.com/ru/speakers/measurements/satori/satori-mr16tx-8> (what it offers: `capture/inventory.md`).
  Add: axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); harmonics H2 to H5 at every drive level shown, as measured (not normalised to one level: the viewer interpolates); impedance (use the .zma file when offered); two-tone intermodulation, where measured.
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), HiFiCompass: stored nothing. Page: <https://hificompass.com/ru/speakers/measurements/satori/satori-mw19tx-4> (what it offers: `capture/inventory.md`).
  Add: axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); harmonics H2 to H5 at every drive level shown, as measured (not normalised to one level: the viewer interpolates); impedance (use the .zma file when offered); two-tone intermodulation, where measured.
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), HiFiCompass: stored nothing. Page: <https://hificompass.com/ru/speakers/measurements/satori/satori-tw29bnwg-4> (what it offers: `capture/inventory.md`).
  Add: axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); harmonics H2 to H5 at every drive level shown, as measured (not normalised to one level: the viewer interpolates); impedance (use the .zma file when offered); two-tone intermodulation, where measured.
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), HiFiCompass: stored nothing. Page: <https://hificompass.com/ru/speakers/measurements/satori/satori-tw29txn-b> (what it offers: `capture/inventory.md`).
  Add: axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); harmonics H2 to H5 at every drive level shown, as measured (not normalised to one level: the viewer interpolates); impedance (use the .zma file when offered); two-tone intermodulation, where measured.

## 4. Random spot check

Chosen at random for week 39 of 2026 (the choice changes weekly). For each, capture the source's curve again and compare with the stored one; differences above 1 dB outside the noise floor need a note or a recapture.

- **BlieSMa M74T-6** (`m74t-6`): sets 0: HD (orders) vs frequency @ 94 dB
- **SB Acoustics SB17NBAC35-8** (`sb17nbac35-8`): sets 0: HD (orders) vs frequency @ 94 dB
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`): sets 0: HD (orders) vs frequency
