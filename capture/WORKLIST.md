# Capture work list

Written by `capture/worklist.py` on 2026-09-26. How to work through it: `capture/CHROME_CAPTURE.md`.

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
| Purifi PTT10.0X04-NAB-02 (`purifi-ptt10-0x04-nab-02`) | 19 | Voice-coil current HD vs frequency @ 2.83 V | HiFiCompass | 29 per decade | original image (remove `/styles/<style>/public/` from the image address), then `capture/image_curves.py` |
| SB Acoustics SB17CAC35-4 (proxy) (`sb17cac35-4`) | 0 | Large-signal compression vs frequency | Erin's Audio Corner | 37 per decade | original chart (Dropbox or site image, 1600 × 900), then `capture/image_curves.py` |
| SB Acoustics SB17CAC35-4 (proxy) (`sb17cac35-4`) | 1 | Large-signal distortion vs frequency | Erin's Audio Corner | 37 per decade | original chart (Dropbox or site image, 1600 × 900), then `capture/image_curves.py` |
| Purifi PTT6.5W04 (paper, proxy) (`ptt65w04-paper`) | 0 | Large-signal compression vs frequency | Erin's Audio Corner | 37 per decade | original chart (Dropbox or site image, 1600 × 900), then `capture/image_curves.py` |
| Purifi PTT6.5W04 (paper, proxy) (`ptt65w04-paper`) | 1 | Large-signal distortion vs frequency | Erin's Audio Corner | 37 per decade | original chart (Dropbox or site image, 1600 × 900), then `capture/image_curves.py` |
| Purifi PTT6.5X04-NAA-08A (`ptt65x04naa08a`) | 20 | Voice-coil current HD vs frequency @ 5.6 V | HiFiCompass | 37 per decade | original image (remove `/styles/<style>/public/` from the image address), then `capture/image_curves.py` |
| Purifi PTT6.5X04-NAA-08A (`ptt65x04naa08a`) | 21 | Voice-coil current HD vs frequency @ 8 V | HiFiCompass | 33 per decade | original image (remove `/styles/<style>/public/` from the image address), then `capture/image_curves.py` |

## 2. Values that disagree: check against the source

From `watch/check_consistency.py` (full list in `watch/consistency.md`).

| Check | Driver | Detail |
|---|---|---|
| band THD | `ptt525x04naa05` | 450–1800 Hz at 94 dB: table 0.095 %, from the curve 0.0774 % (-1.8 dB) |
| band THD | `ptt525x04naa05` | 80–5000 Hz at 94 dB: table 0.254 %, from the curve 0.157 % (-4.2 dB) |
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

Level slopes that differ from the typical rule (H2 +1.0, H3 +0.7 dB per dB). Information, not an error: each drive level is stored as the source measured it and the viewer prefers a measured level over a scaled one; a slope far off the rule says only that the rule would mislead for this driver. Look at the curve if it also looks wrong beside its chart.

| Driver | Detail |
|---|---|
| `m74t-6` | H3: 104.5 dB curve minus 95.5 dB curve = +11.0 dB on average over 156 shared frequencies (typical slope expects +6.3 dB) |
| `m74t-6` | H3: 104.5 dB curve minus 98.5 dB curve = +8.5 dB on average over 162 shared frequencies (typical slope expects +4.2 dB) |
| `ptt13t04hag01` | H2: 102.9 dB curve minus 88 dB curve = +10.1 dB on average over 176 shared frequencies (typical slope expects +14.9 dB) |
| `ptt13t04hag01` | H2: 102.9 dB curve minus 90.9 dB curve = +7.5 dB on average over 187 shared frequencies (typical slope expects +12.0 dB) |
| `ptt13t04hag01` | H2: 102.9 dB curve minus 93.9 dB curve = +4.9 dB on average over 187 shared frequencies (typical slope expects +9.0 dB) |
| `ptt13t04hag01` | H2: 102.9 dB curve minus 96.9 dB curve = +0.9 dB on average over 187 shared frequencies (typical slope expects +6.0 dB) |
| `ptt13t04hag01` | H3: 102.9 dB curve minus 88 dB curve = +6.2 dB on average over 105 shared frequencies (typical slope expects +10.4 dB) |
| `ptt65x04naa08a` | H2: 100.7 dB curve minus 85.7 dB curve = +11.0 dB on average over 216 shared frequencies (typical slope expects +15.0 dB) |
| `ptt65x04naa08a` | H3: 100.7 dB curve minus 85.7 dB curve = +4.6 dB on average over 201 shared frequencies (typical slope expects +10.5 dB) |
| `ptt65x04naa08a` | H3: 100.7 dB curve minus 85.7 dB curve = +6.0 dB on average over 175 shared frequencies (typical slope expects +10.5 dB) |
| `ptt65x04naa08a` | H3: 100.7 dB curve minus 88.7 dB curve = +4.0 dB on average over 204 shared frequencies (typical slope expects +8.4 dB) |
| `ptt65x04naa08a` | H3: 94.7 dB curve minus 85.7 dB curve = +1.6 dB on average over 153 shared frequencies (typical slope expects +6.3 dB) |
| `purifi-ptt10-0x04-nab-02` | H2: 104.5 dB curve minus 86.5 dB curve = +13.7 dB on average over 240 shared frequencies (typical slope expects +18.0 dB) |
| `sb-satori-mr16tx-8` | H3: 105.2 dB curve minus 87.2 dB curve = +17.1 dB on average over 145 shared frequencies (typical slope expects +12.6 dB) |
| `sb-satori-mr16tx-8` | H3: 105.2 dB curve minus 90.2 dB curve = +15.0 dB on average over 148 shared frequencies (typical slope expects +10.5 dB) |
| `sb-satori-mr16tx-8` | H3: 105.2 dB curve minus 93.2 dB curve = +12.5 dB on average over 150 shared frequencies (typical slope expects +8.4 dB) |
| `sb-satori-mw19tx-4` | H3: 101.9 dB curve minus 89.9 dB curve = +3.3 dB on average over 171 shared frequencies (typical slope expects +8.4 dB) |
| `sb-satori-mw19tx-4` | H3: 101.9 dB curve minus 92.9 dB curve = +2.0 dB on average over 172 shared frequencies (typical slope expects +6.3 dB) |
| `sb-satori-mw19tx-4` | H3: 98.9 dB curve minus 89.9 dB curve = +1.9 dB on average over 178 shared frequencies (typical slope expects +6.3 dB) |
| `sb-satori-tw29bnwg-4` | H2: 108.5 dB curve minus 90.5 dB curve = +13.1 dB on average over 187 shared frequencies (typical slope expects +18.0 dB) |
| `sb-satori-tw29bnwg-4` | H2: 108.5 dB curve minus 93.5 dB curve = +10.4 dB on average over 187 shared frequencies (typical slope expects +15.0 dB) |
| `sb-satori-tw29bnwg-4` | H2: 108.5 dB curve minus 96.5 dB curve = +7.8 dB on average over 187 shared frequencies (typical slope expects +12.0 dB) |
| `sb-satori-tw29bnwg-4` | H3: 102.5 dB curve minus 93.5 dB curve = +13.0 dB on average over 131 shared frequencies (typical slope expects +6.3 dB) |
| `sb-satori-tw29bnwg-4` | H3: 102.5 dB curve minus 96.5 dB curve = +9.1 dB on average over 157 shared frequencies (typical slope expects +4.2 dB) |
| `sb-satori-tw29bnwg-4` | H3: 105.5 dB curve minus 93.5 dB curve = +14.5 dB on average over 131 shared frequencies (typical slope expects +8.4 dB) |
| `sb-satori-tw29bnwg-4` | H3: 105.5 dB curve minus 96.5 dB curve = +10.9 dB on average over 157 shared frequencies (typical slope expects +6.3 dB) |
| `sb-satori-tw29txn-b` | H3: 102.6 dB curve minus 87.7 dB curve = +5.4 dB on average over 155 shared frequencies (typical slope expects +10.4 dB) |
| `sb-satori-tw29txn-b` | H3: 102.6 dB curve minus 90.6 dB curve = +3.9 dB on average over 154 shared frequencies (typical slope expects +8.4 dB) |
| `sb-satori-tw29txn-b` | H3: 102.6 dB curve minus 96.6 dB curve = -0.0 dB on average over 160 shared frequencies (typical slope expects +4.2 dB) |
| `sb-satori-tw29txn-b` | H3: 102.6 dB curve minus 99.6 dB curve = -2.2 dB on average over 164 shared frequencies (typical slope expects +2.1 dB) |
| `t25a-6` | H2: 96 dB curve minus 84 dB curve = +7.5 dB on average over 187 shared frequencies (typical slope expects +12.0 dB) |
| `t25a-6` | H2: 96 dB curve minus 87 dB curve = +4.9 dB on average over 187 shared frequencies (typical slope expects +9.0 dB) |
| `t25a-6` | H2: 98.9 dB curve minus 84 dB curve = +8.9 dB on average over 187 shared frequencies (typical slope expects +14.9 dB) |
| `t25a-6` | H2: 98.9 dB curve minus 87 dB curve = +6.4 dB on average over 187 shared frequencies (typical slope expects +11.9 dB) |
| `t25a-6` | H2: 98.9 dB curve minus 90 dB curve = +3.5 dB on average over 187 shared frequencies (typical slope expects +8.9 dB) |
| `t25a-6` | H3: 96 dB curve minus 84 dB curve = +2.7 dB on average over 122 shared frequencies (typical slope expects +8.4 dB) |
| `t25a-6` | H3: 96 dB curve minus 87 dB curve = -1.2 dB on average over 123 shared frequencies (typical slope expects +6.3 dB) |
| `t25a-6` | H3: 96 dB curve minus 90 dB curve = -2.6 dB on average over 128 shared frequencies (typical slope expects +4.2 dB) |
| `t25a-6` | H3: 96 dB curve minus 93 dB curve = -3.7 dB on average over 133 shared frequencies (typical slope expects +2.1 dB) |
| `t25a-6` | H3: 98.9 dB curve minus 87 dB curve = +3.1 dB on average over 122 shared frequencies (typical slope expects +8.3 dB) |
| `t25a-6` | H3: 98.9 dB curve minus 90 dB curve = +1.7 dB on average over 127 shared frequencies (typical slope expects +6.2 dB) |
| `t25t-6` | H2: 99.8 dB curve minus 87.8 dB curve = +7.5 dB on average over 187 shared frequencies (typical slope expects +12.0 dB) |
| `t25t-6` | H3: 93.9 dB curve minus 87.8 dB curve = -0.2 dB on average over 130 shared frequencies (typical slope expects +4.3 dB) |
| `t25t-6` | H3: 96.8 dB curve minus 87.8 dB curve = +2.2 dB on average over 136 shared frequencies (typical slope expects +6.3 dB) |
| `t25t-6` | H3: 99.8 dB curve minus 87.8 dB curve = +2.8 dB on average over 138 shared frequencies (typical slope expects +8.4 dB) |
| `t34b-4` | H3: 100.1 dB curve minus 97.1 dB curve = +6.2 dB on average over 141 shared frequencies (typical slope expects +2.1 dB) |

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
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), HiFiCompass: stored frequency-response, hd-current, hd-frequency 102.9 dB, hd-frequency 88.0 dB, hd-frequency 90.9 dB, hd-frequency 93.9 dB, hd-frequency 96.9 dB, hd-frequency 99.9 dB, impedance. Page: <https://hificompass.com/ru/speakers/measurements/purifi/purifi-ptt13t04-hag-01> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), Manufacturer datasheet: stored hd-frequency 94 dB, hd-level.
  Add: frequency response figure; impedance figure; current distortion; intermodulation spectra (both tone pairs).
- **SB Acoustics Satori WO24P-8** (`sb-satori-wo24p-8`), HiFiCompass: stored hd-frequency 91 dB, thd-bands 91 dB. Page: <https://hificompass.com/ru/speakers/measurements/satori/satori-wo24p-8> (what it offers: `capture/inventory.md`).
  Add: the harmonics above 500 Hz, up to the end of the page's harmonics charts (the stored curve stops at 500 Hz, so Simulate has no data above it where this driver still plays; `watch/sim_coverage.md`); axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); impedance (use the .zma file when offered); two-tone intermodulation, where measured.
- **SB Acoustics SB34NRXL75-8 (Norex)** (`sb-sb34nrxl75-8`), HiFiCompass: stored hd-frequency 91 dB, imd-summary 91.1 dB, thd-bands 91 dB. Page: <https://hificompass.com/ru/speakers/measurements/sbacoustics/sb-acoustics-sb34nrxl75-8> (what it offers: `capture/inventory.md`).
  Add: the harmonics above 500 Hz, up to the end of the page's harmonics charts (the stored curve stops at 500 Hz, so Simulate has no data above it where this driver still plays; `watch/sim_coverage.md`); axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); impedance (use the .zma file when offered).
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), HiFiCompass: stored frequency-response, hd-current, hd-frequency 102.2 dB, hd-frequency 105.2 dB, hd-frequency 90.2 dB, hd-frequency 93.2 dB, hd-frequency 96.2 dB, hd-frequency 99.2 dB, imd-products, impedance. Page: <https://hificompass.com/ru/speakers/measurements/purifi/purifi-ptt80x04-nab-02> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), Manufacturer datasheet: stored nothing.
  Add (if Purifi publishes a datasheet for this exact variant): frequency response figure; impedance figure; harmonic distortion vs frequency at 94 dB; harmonic distortion vs level (level sweeps); current distortion; intermodulation spectra (both tone pairs).
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), HiFiCompass: stored frequency-response, hd-current, hd-frequency 101.5 dB, hd-frequency 104.5 dB, hd-frequency 86.5 dB, hd-frequency 89.5 dB, hd-frequency 92.5 dB, hd-frequency 95.5 dB, hd-frequency 98.5 dB, hd-spectrum, imd-products, imd-summary 91.67 dB, impedance. Page: <https://hificompass.com/ru/speakers/measurements/purifi/purifi-ptt100x04-nab-02> (what it offers: `capture/inventory.md`).
  Add: check every drive level is stored, as measured.
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), Manufacturer datasheet: stored nothing.
  Add (if Purifi publishes a datasheet for this exact variant): frequency response figure; impedance figure; harmonic distortion vs frequency at 94 dB; harmonic distortion vs level (level sweeps); current distortion; intermodulation spectra (both tone pairs).
- **SB Acoustics Satori WO24P-4** (`sb-satori-wo24p-4`), HiFiCompass: stored imd-summary 91.15 dB. Page: <https://hificompass.com/ru/speakers/measurements/satori/satori-wo24p-4> (what it offers: `capture/inventory.md`).
  Add: axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); harmonics H2 to H5 at every drive level shown, as measured (not normalised to one level: the viewer interpolates); impedance (use the .zma file when offered).
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), HiFiCompass: stored frequency-response, hd-current, hd-frequency 100.7 dB, hd-frequency 85.7 dB, hd-frequency 88.7 dB, hd-frequency 91.7 dB, hd-frequency 94.7 dB, hd-frequency 97.7 dB, hd-spectrum, imd-products, impedance. Page: <https://hificompass.com/ru/speakers/measurements/purifi/purifi-ptt65x04-naa-08a> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), Manufacturer datasheet: stored nothing.
  Add (if Purifi publishes a datasheet for this exact variant): frequency response figure; impedance figure; harmonic distortion vs frequency at 94 dB; harmonic distortion vs level (level sweeps); current distortion; intermodulation spectra (both tone pairs).
- **SB Acoustics SB17NBAC35-8** (`sb17nbac35-8`), HiFiCompass: stored hd-frequency 94 dB, thd-bands 94 dB. Page: <https://hificompass.com/ru/speakers/measurements/sbacoustics/sb-acoustics-sb17nbac35-8> (what it offers: `capture/inventory.md`).
  Add: the harmonics at each drive level actually measured (the stored 94 dB curve was normalised from them; keep it until they are in); axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); impedance (use the .zma file when offered); two-tone intermodulation, where measured.
- **BlieSMa M74T-6** (`m74t-6`), HiFiCompass: stored frequency-response, hd-current, hd-frequency 101.4 dB, hd-frequency 104.5 dB, hd-frequency 89.5 dB, hd-frequency 92.5 dB, hd-frequency 95.5 dB, hd-frequency 98.5 dB, imd-products, impedance. Page: <https://hificompass.com/en/speakers/measurements/bliesma/bliesma-m74t-6> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **BlieSMa M74A-6** (`m74a-6`), HiFiCompass: stored frequency-response, hd-current, hd-frequency 102.1 dB, hd-frequency 105.0 dB, hd-frequency 90.1 dB, hd-frequency 93.0 dB, hd-frequency 96.1 dB, hd-frequency 99.0 dB, imd-products, impedance. Page: <https://hificompass.com/en/speakers/measurements/bliesma/bliesma-m74a-6> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **BlieSMa T25A-6** (`t25a-6`), HiFiCompass: stored frequency-response, hd-frequency 84.0 dB, hd-frequency 87.0 dB, hd-frequency 90.0 dB, hd-frequency 93.0 dB, hd-frequency 96.0 dB, hd-frequency 98.9 dB, impedance. Page: <https://hificompass.com/en/speakers/measurements/bliesma/bliesma-t25a-6> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **BlieSMa T25T-6** (`t25t-6`), HiFiCompass: stored frequency-response, hd-current, hd-frequency 87.8 dB, hd-frequency 90.8 dB, hd-frequency 93.9 dB, hd-frequency 96.8 dB, hd-frequency 99.8 dB, impedance. Page: <https://hificompass.com/en/speakers/measurements/bliesma/bliesma-t25t-6> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **BlieSMa T34A-4** (`t34a-4`), HiFiCompass: stored frequency-response, hd-frequency 100.6 dB, hd-frequency 85.6 dB, hd-frequency 88.7 dB, hd-frequency 91.7 dB, hd-frequency 94.7 dB, hd-frequency 97.7 dB, impedance. Page: <https://hificompass.com/en/speakers/measurements/bliesma/bliesma-t34a-4> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **BlieSMa T34B-4** (`t34b-4`), HiFiCompass: stored frequency-response, hd-frequency 100.1 dB, hd-frequency 85.1 dB, hd-frequency 88.1 dB, hd-frequency 91.1 dB, hd-frequency 94.1 dB, hd-frequency 97.1 dB, impedance. Page: <https://hificompass.com/en/speakers/measurements/bliesma/bliesma-t34b-4> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), HiFiCompass: stored frequency-response, hd-current, hd-frequency 102.2 dB, hd-frequency 105.2 dB, hd-frequency 87.2 dB, hd-frequency 90.2 dB, hd-frequency 93.2 dB, hd-frequency 96.2 dB, hd-frequency 99.2 dB, imd-products, impedance. Page: <https://hificompass.com/ru/speakers/measurements/satori/satori-mr16tx-8> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), HiFiCompass: stored frequency-response, hd-current, hd-frequency 101.9 dB, hd-frequency 104.9 dB, hd-frequency 89.9 dB, hd-frequency 92.9 dB, hd-frequency 95.9 dB, hd-frequency 98.9 dB, hd-spectrum, imd-products, impedance. Page: <https://hificompass.com/ru/speakers/measurements/satori/satori-mw19tx-4> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), HiFiCompass: stored frequency-response, hd-current, hd-frequency 102.5 dB, hd-frequency 105.5 dB, hd-frequency 108.5 dB, hd-frequency 90.5 dB, hd-frequency 93.5 dB, hd-frequency 96.5 dB, hd-frequency 99.5 dB, imd-products, impedance. Page: <https://hificompass.com/ru/speakers/measurements/satori/satori-tw29bnwg-4> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), HiFiCompass: stored frequency-response, hd-current, hd-frequency 102.6 dB, hd-frequency 87.7 dB, hd-frequency 90.6 dB, hd-frequency 93.6 dB, hd-frequency 96.6 dB, hd-frequency 99.6 dB, imd-products, impedance. Page: <https://hificompass.com/ru/speakers/measurements/satori/satori-tw29txn-b> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.

## 4. Random spot check

Chosen at random for week 39 of 2026 (the choice changes weekly). For each, capture the source's curve again and compare with the stored one; differences above 1 dB outside the noise floor need a note or a recapture.

- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`): sets 0: Axial frequency response @ 2.83 V; 1: Axial frequency response @ 4 V; 2: Axial frequency response @ 5.6 V; 3: Axial frequency response @ 8 V; 4: Axial frequency response @ 11.2 V; 5: Axial frequency response @ 16 V; 6: HD (orders) vs frequency @ 2 V; 7: HD (orders) vs frequency @ 2.83 V; 8: HD (orders) vs frequency @ 4 V; 9: HD (orders) vs frequency @ 5.6 V; 10: HD (orders) vs frequency @ 8 V; 11: HD (orders) vs frequency @ 11.2 V; 12: HD (orders) vs frequency @ 16 V; 13: Voice-coil current HD vs frequency @ 2.83 V; 14: Voice-coil current HD vs frequency @ 4 V; 15: Voice-coil current HD vs frequency @ 5.6 V; 16: Impedance (chart to 150 ohm)
- **Purifi PTT5.25X04-NAA-05** (`ptt525x04naa05`): sets 0: HD vs frequency (ratio); 3: HD vs SPL (level sweep); 5: HD (orders) vs frequency @ 94 dB
- **BlieSMa M74A-6** (`m74a-6`): sets 0: Axial frequency response @ 1.41 V; 1: Axial frequency response @ 2 V; 2: Axial frequency response @ 2.83 V; 3: Axial frequency response @ 4 V; 4: Axial frequency response @ 5.6 V; 5: Axial frequency response @ 8 V; 6: HD (orders) vs frequency @ 1.41 V; 7: HD (orders) vs frequency @ 2 V; 8: HD (orders) vs frequency @ 2.83 V; 9: HD (orders) vs frequency @ 4 V; 10: HD (orders) vs frequency @ 5.6 V; 11: HD (orders) vs frequency @ 8 V; 12: Voice-coil current HD vs frequency @ 1.41 V; 13: Voice-coil current HD vs frequency @ 2 V; 14: Voice-coil current HD vs frequency @ 2.83 V; 15: Impedance (chart to 50 ohm)

## 5. Sets read automatically from chart images (check by eye)

Read on GitHub by `capture/chart_read.py` from the source's chart images and stored with confidence *medium*. Open the chart named in the set's note beside the viewer's curve; a difference above 1 dB (0.3 ohm for impedance) outside the noise floor needs a note or a recapture. The self-checks in each note compare the reading with the page's table.

- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), set 2: Axial frequency response @ 2 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), set 3: Axial frequency response @ 2.83 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), set 4: Axial frequency response @ 4 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), set 5: Axial frequency response @ 5.6 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), set 6: Axial frequency response @ 8 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), set 7: Axial frequency response @ 11.2 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), set 8: HD (orders) vs frequency @ 2 V — check on the image: H2 100 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), set 9: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), set 10: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), set 11: HD (orders) vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), set 12: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), set 13: HD (orders) vs frequency @ 11.2 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), set 14: Voice-coil current HD vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), set 15: Voice-coil current HD vs frequency @ 2.83 V — check on the image: H2 100 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), set 16: Voice-coil current HD vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), set 17: Voice-coil current HD vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), set 18: Voice-coil current HD vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), set 19: Voice-coil current HD vs frequency @ 11.2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), set 20: Impedance (chart to 15 ohm) — check impedance minimum against Re, read 3.94, stated 4.6; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), set 21: Impedance (chart to 5 ohm) — check impedance minimum against Re, read 3.9, stated 4.6; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 5: Axial frequency response @ 2.83 V — check on the image: SPL 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 6: Axial frequency response @ 4 V — check on the image: SPL 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 7: Axial frequency response @ 5.6 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 8: Axial frequency response @ 8 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 9: Axial frequency response @ 11.2 V — check on the image: SPL 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 10: Axial frequency response @ 16 V — check on the image: SPL 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 11: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 99 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 12: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 13: HD (orders) vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 14: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 15: HD (orders) vs frequency @ 11.2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 16: HD (orders) vs frequency @ 16 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 17: HD (orders) vs frequency @ 2.83 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 18: HD (orders) vs frequency @ 4 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 19: HD (orders) vs frequency @ 5.6 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 20: HD (orders) vs frequency @ 8 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 21: HD (orders) vs frequency @ 11.2 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 22: Voice-coil current HD vs frequency @ 1.41 V — check on the image: H2 95 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 23: Voice-coil current HD vs frequency @ 2 V — check on the image: H2 99 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 24: Voice-coil current HD vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 25: Voice-coil current HD vs frequency @ 4 V — check on the image: H2 100 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 26: Voice-coil current HD vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 27: Voice-coil current HD vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 28: Impedance (chart to 70 ohm) — check impedance minimum against Re, read 3.78, stated 3.55; check impedance peak against Fs, read hz 24.06, read ohm 49.84, stated fs 28.8; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 29: Impedance (chart to 7 ohm) — check impedance minimum against Re, read 3.73, stated 3.55; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 30: Intermodulation 30 + 255 Hz, 4:1, low tone 2 mm peak excursion — no self-check possible for this kind
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 31: Intermodulation 30 + 255 Hz, 4:1, low tone 3 mm peak excursion — no self-check possible for this kind
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 32: Intermodulation 30 + 255 Hz, 4:1, low tone 4.5 mm peak excursion — no self-check possible for this kind
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 33: Intermodulation 30 + 255 Hz, 4:1, low tone 6 mm peak excursion — no self-check possible for this kind
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 34: Intermodulation 30 + 255 Hz, 4:1, low tone 9 mm peak excursion — no self-check possible for this kind
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 35: Intermodulation 30 + 255 Hz, 4:1, low tone 10 mm peak excursion — no self-check possible for this kind
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 36: Intermodulation 50 + 425 Hz, 4:1, low tone 1 mm peak excursion — no self-check possible for this kind
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 37: Intermodulation 50 + 425 Hz, 4:1, low tone 2 mm peak excursion — no self-check possible for this kind
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 38: Intermodulation 50 + 425 Hz, 4:1, low tone 3 mm peak excursion — no self-check possible for this kind
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 39: Intermodulation 50 + 425 Hz, 4:1, low tone 6 mm peak excursion — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 4: Axial frequency response @ 2.83 V — check 2.83 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 86.5, expected 88.0, stated sens 88.0, difference db -1.5; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 5: Axial frequency response @ 4 V — check 4 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 89.5, expected 91.0, stated sens 88.0, difference db -1.5; check on the image: SPL 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 6: Axial frequency response @ 5.6 V — check 5.6 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 92.5, expected 93.9, stated sens 88.0, difference db -1.4; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 7: Axial frequency response @ 8 V — check 8 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 95.5, expected 97.0, stated sens 88.0, difference db -1.5; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 8: Axial frequency response @ 11.2 V — check 11.2 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 98.5, expected 99.9, stated sens 88.0, difference db -1.5; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 9: Axial frequency response @ 16 V — check 16 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 101.5, expected 103.0, stated sens 88.0, difference db -1.6; check on the image: SPL 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 10: Axial frequency response @ 22.5 V — check 22.5 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 104.5, expected 106.0, stated sens 88.0, difference db -1.5; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 11: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 12: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 13: HD (orders) vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 14: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 15: HD (orders) vs frequency @ 11.2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 16: HD (orders) vs frequency @ 16 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 17: HD (orders) vs frequency @ 22.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 18: HD (orders) vs frequency @ 16 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 19: Voice-coil current HD vs frequency @ 2.83 V — check on the image: H2 98 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 20: Voice-coil current HD vs frequency @ 4 V — check on the image: H2 98 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 21: Voice-coil current HD vs frequency @ 5.6 V — check on the image: H2 97 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 22: Voice-coil current HD vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 23: Voice-coil current HD vs frequency @ 11.2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 24: Impedance (chart to 70 ohm) — check impedance minimum against Re, read 4.69, stated 3.9; check impedance peak against Fs, read hz 22.71, read ohm 60.64, stated fs 24; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 25: Impedance (chart to 15 ohm) — check impedance minimum against Re, read 4.63, stated 3.9; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 26: Harmonics of one tone, 20 Hz at 2.83 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 27: Harmonics of one tone, 30 Hz at 2.83 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 28: Harmonics of one tone, 40 Hz at 2.83 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 29: Harmonics of one tone, 50 Hz at 2.83 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 30: Harmonics of one tone, 75 Hz at 2.83 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 31: Harmonics of one tone, 100 Hz at 2.83 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 32: Harmonics of one tone, 150 Hz at 2.83 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 33: Harmonics of one tone, 20 Hz at 4 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 34: Harmonics of one tone, 30 Hz at 4 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 35: Harmonics of one tone, 40 Hz at 4 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 36: Harmonics of one tone, 50 Hz at 4 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 37: Harmonics of one tone, 75 Hz at 4 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 38: Harmonics of one tone, 100 Hz at 4 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 39: Harmonics of one tone, 150 Hz at 4 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 40: Harmonics of one tone, 20 Hz at 5.6 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 41: Harmonics of one tone, 30 Hz at 5.6 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 42: Harmonics of one tone, 40 Hz at 5.6 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 43: Harmonics of one tone, 50 Hz at 5.6 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 44: Harmonics of one tone, 75 Hz at 5.6 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 45: Harmonics of one tone, 100 Hz at 5.6 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 46: Harmonics of one tone, 150 Hz at 5.6 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 47: Harmonics of one tone, 20 Hz at 8 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 48: Harmonics of one tone, 30 Hz at 8 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 49: Harmonics of one tone, 40 Hz at 8 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 50: Harmonics of one tone, 50 Hz at 8 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 51: Harmonics of one tone, 75 Hz at 8 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 52: Harmonics of one tone, 100 Hz at 8 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 53: Harmonics of one tone, 150 Hz at 8 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 54: Harmonics of one tone, 20 Hz at 11.2 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 55: Harmonics of one tone, 30 Hz at 11.2 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 56: Harmonics of one tone, 40 Hz at 11.2 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 57: Harmonics of one tone, 50 Hz at 11.2 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 58: Harmonics of one tone, 75 Hz at 11.2 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 59: Harmonics of one tone, 100 Hz at 11.2 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 60: Harmonics of one tone, 150 Hz at 11.2 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 61: Intermodulation 30 + 255 Hz, 4:1, low tone 3 mm peak excursion — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 62: Intermodulation 30 + 255 Hz, 4:1, low tone 4.5 mm peak excursion — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 63: Intermodulation 30 + 255 Hz, 4:1, low tone 6 mm peak excursion — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 64: Intermodulation 30 + 255 Hz, 4:1, low tone 9 mm peak excursion — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 65: Intermodulation 30 + 255 Hz, 4:1, low tone 12 mm peak excursion — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 66: Intermodulation 50 + 425 Hz, 4:1, low tone 1 mm peak excursion — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 67: Intermodulation 50 + 425 Hz, 4:1, low tone 2 mm peak excursion — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 68: Intermodulation 50 + 425 Hz, 4:1, low tone 3 mm peak excursion — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 69: Intermodulation 50 + 425 Hz, 4:1, low tone 4.5 mm peak excursion — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 70: Intermodulation 50 + 425 Hz, 4:1, low tone 6 mm peak excursion — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 2: Axial frequency response @ 2.83 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 3: Axial frequency response @ 4 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 4: Axial frequency response @ 5.6 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 5: Axial frequency response @ 8 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 6: Axial frequency response @ 11.2 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 7: Axial frequency response @ 16 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 8: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 9: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 10: HD (orders) vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 11: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 12: HD (orders) vs frequency @ 11.2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 13: HD (orders) vs frequency @ 16 V — check on the image: H2 100 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 14: HD (orders) vs frequency @ 2.83 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 15: HD (orders) vs frequency @ 4 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 16: HD (orders) vs frequency @ 5.6 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 17: HD (orders) vs frequency @ 8 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 18: Voice-coil current HD vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 19: Voice-coil current HD vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 20: Voice-coil current HD vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 21: Voice-coil current HD vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 22: Impedance (chart to 70 ohm) — check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 23: Harmonics of one tone, 20 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 24: Harmonics of one tone, 30 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 25: Harmonics of one tone, 40 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 26: Harmonics of one tone, 50 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 27: Harmonics of one tone, 75 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 28: Harmonics of one tone, 100 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 29: Harmonics of one tone, 150 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 30: Harmonics of one tone, 220 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 31: Harmonics of one tone, 300 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 32: Harmonics of one tone, 20 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 33: Harmonics of one tone, 30 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 34: Harmonics of one tone, 40 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 35: Harmonics of one tone, 50 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 36: Harmonics of one tone, 75 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 37: Harmonics of one tone, 100 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 38: Harmonics of one tone, 150 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 39: Harmonics of one tone, 220 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 40: Harmonics of one tone, 300 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 41: Intermodulation 30 + 255 Hz, 4:1, low tone 2 mm peak excursion — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 42: Intermodulation 30 + 255 Hz, 4:1, low tone 3 mm peak excursion — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 43: Intermodulation 30 + 255 Hz, 4:1, low tone 4.5 mm peak excursion — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 44: Intermodulation 30 + 255 Hz, 4:1, low tone 6 mm peak excursion — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 45: Intermodulation 30 + 255 Hz, 4:1, low tone 9 mm peak excursion — no self-check possible for this kind
- **BlieSMa M74T-6** (`m74t-6`), set 2: Axial frequency response @ 1.41 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 3: Axial frequency response @ 2 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 4: Axial frequency response @ 2.83 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 5: Axial frequency response @ 4 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 6: Axial frequency response @ 5.6 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 7: Axial frequency response @ 8 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 8: HD (orders) vs frequency @ 1.41 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 9: HD (orders) vs frequency @ 2 V — check on the image: H2 100 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 10: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 11: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 12: HD (orders) vs frequency @ 5.6 V — check on the image: H2 99 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 13: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 99 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 14: Voice-coil current HD vs frequency @ 1 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 15: Voice-coil current HD vs frequency @ 1.41 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 16: Voice-coil current HD vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 17: Voice-coil current HD vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 18: Impedance (chart to 70 ohm) — check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 19: Impedance (chart to 15 ohm) — check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 20: Intermodulation 125 + 1063 Hz, 1:1, 1 V per tone — no self-check possible for this kind
- **BlieSMa M74T-6** (`m74t-6`), set 21: Intermodulation 125 + 1063 Hz, 1:1, 1.41 V per tone — no self-check possible for this kind
- **BlieSMa M74T-6** (`m74t-6`), set 22: Intermodulation 125 + 1063 Hz, 1:1, 2 V per tone — no self-check possible for this kind
- **BlieSMa M74T-6** (`m74t-6`), set 23: Intermodulation 125 + 1063 Hz, 1:1, 2.83 V per tone — no self-check possible for this kind
- **BlieSMa M74T-6** (`m74t-6`), set 24: Intermodulation 125 + 1063 Hz, 1:1, 4 V per tone — no self-check possible for this kind
- **BlieSMa M74T-6** (`m74t-6`), set 25: Intermodulation 500 + 4250 Hz, 1:1, 1 V per tone — no self-check possible for this kind
- **BlieSMa M74T-6** (`m74t-6`), set 26: Intermodulation 500 + 4250 Hz, 1:1, 1.41 V per tone — no self-check possible for this kind
- **BlieSMa M74T-6** (`m74t-6`), set 27: Intermodulation 500 + 4250 Hz, 1:1, 2 V per tone — no self-check possible for this kind
- **BlieSMa M74T-6** (`m74t-6`), set 28: Intermodulation 500 + 4250 Hz, 1:1, 2.83 V per tone — no self-check possible for this kind
- **BlieSMa M74A-6** (`m74a-6`), set 0: Axial frequency response @ 1.41 V — check 1.41 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 90.1, expected 88.9, stated sens 95.0, difference db 1.1; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 1: Axial frequency response @ 2 V — check 2 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 93.0, expected 92.0, stated sens 95.0, difference db 1.0; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 2: Axial frequency response @ 2.83 V — check 2.83 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 96.1, expected 95.0, stated sens 95.0, difference db 1.1; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 3: Axial frequency response @ 4 V — check 4 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 99.0, expected 98.0, stated sens 95.0, difference db 1.0; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 4: Axial frequency response @ 5.6 V — check 5.6 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 102.1, expected 100.9, stated sens 95.0, difference db 1.1; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 5: Axial frequency response @ 8 V — check 8 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 105.0, expected 104.0, stated sens 95.0, difference db 1.0; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 6: HD (orders) vs frequency @ 1.41 V — check on the image: H2 100 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 7: HD (orders) vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 8: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 9: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 10: HD (orders) vs frequency @ 5.6 V — check on the image: H2 99 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 11: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 12: Voice-coil current HD vs frequency @ 1.41 V — check on the image: H2 100 %, H3 100 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 13: Voice-coil current HD vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 14: Voice-coil current HD vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 15: Impedance (chart to 50 ohm) — check impedance minimum against Re, read 5.98, stated 5.6; check impedance peak against Fs, read hz 391.2, read ohm 45.26, stated fs 400.0; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 16: Intermodulation 500 + 4250 Hz, 1:1, 1 V per tone — no self-check possible for this kind
- **BlieSMa M74A-6** (`m74a-6`), set 17: Intermodulation 500 + 4250 Hz, 1:1, 1.41 V per tone — no self-check possible for this kind
- **BlieSMa M74A-6** (`m74a-6`), set 18: Intermodulation 500 + 4250 Hz, 1:1, 2 V per tone — no self-check possible for this kind
- **BlieSMa M74A-6** (`m74a-6`), set 19: Intermodulation 500 + 4250 Hz, 1:1, 2.83 V per tone — no self-check possible for this kind
- **BlieSMa T25A-6** (`t25a-6`), set 0: Axial frequency response @ 2 V — check 2 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 84.0, expected 90.0, stated sens 93.0, difference db -6.0; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25A-6** (`t25a-6`), set 1: Axial frequency response @ 2.83 V — check 2.83 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 87.0, expected 93.0, stated sens 93.0, difference db -6.0; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25A-6** (`t25a-6`), set 2: Axial frequency response @ 4 V — check 4 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 90.0, expected 96.0, stated sens 93.0, difference db -6.0; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25A-6** (`t25a-6`), set 3: Axial frequency response @ 5.6 V — check 5.6 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 93.0, expected 98.9, stated sens 93.0, difference db -5.9; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25A-6** (`t25a-6`), set 4: Axial frequency response @ 8 V — check 8 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 96.0, expected 102.0, stated sens 93.0, difference db -6.0; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25A-6** (`t25a-6`), set 5: Axial frequency response @ 11.2 V — check 11.2 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 98.9, expected 104.9, stated sens 93.0, difference db -6.0; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25A-6** (`t25a-6`), set 6: HD (orders) vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25A-6** (`t25a-6`), set 7: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25A-6** (`t25a-6`), set 8: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25A-6** (`t25a-6`), set 9: HD (orders) vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25A-6** (`t25a-6`), set 10: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25A-6** (`t25a-6`), set 11: HD (orders) vs frequency @ 11.2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25A-6** (`t25a-6`), set 12: Impedance (chart to 15 ohm) — check impedance minimum against Re, read 5.5, stated 5.2; check impedance peak against Fs, read hz 805.33, read ohm 12.94, stated fs 980.0; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25A-6** (`t25a-6`), set 13: Impedance (chart to 7 ohm) — check impedance minimum against Re, read 5.48, stated 5.2; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25T-6** (`t25t-6`), set 0: Axial frequency response @ 2.83 V — check 2.83 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 87.8, expected 91.0, stated sens 91.0, difference db -3.2; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25T-6** (`t25t-6`), set 1: Axial frequency response @ 4 V — check 4 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 90.8, expected 94.0, stated sens 91.0, difference db -3.2; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25T-6** (`t25t-6`), set 2: Axial frequency response @ 5.6 V — check 5.6 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 93.9, expected 96.9, stated sens 91.0, difference db -3.1; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25T-6** (`t25t-6`), set 3: Axial frequency response @ 8 V — check 8 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 96.8, expected 100.0, stated sens 91.0, difference db -3.2; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25T-6** (`t25t-6`), set 4: Axial frequency response @ 11.2 V — check 11.2 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 99.8, expected 102.9, stated sens 91.0, difference db -3.1; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25T-6** (`t25t-6`), set 5: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25T-6** (`t25t-6`), set 6: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25T-6** (`t25t-6`), set 7: HD (orders) vs frequency @ 5.6 V — check on the image: H2 100 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25T-6** (`t25t-6`), set 8: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25T-6** (`t25t-6`), set 9: HD (orders) vs frequency @ 11.2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25T-6** (`t25t-6`), set 10: Voice-coil current HD vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25T-6** (`t25t-6`), set 11: Voice-coil current HD vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25T-6** (`t25t-6`), set 12: Voice-coil current HD vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25T-6** (`t25t-6`), set 13: Impedance (chart to 20 ohm) — check impedance minimum against Re, read 5.26, stated 5.2; check impedance peak against Fs, read hz 878.21, read ohm 15.24, stated fs 940.0; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25T-6** (`t25t-6`), set 14: Impedance (chart to 7 ohm) — check impedance minimum against Re, read 5.25, stated 5.2; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 0: Axial frequency response @ 1.41 V — check 1.41 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 85.6, expected 89.9, stated sens 96.0, difference db -4.3; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 1: Axial frequency response @ 2.83 V — check 2.83 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 91.7, expected 96.0, stated sens 96.0, difference db -4.3; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 2: Axial frequency response @ 4 V — check 4 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 94.7, expected 99.0, stated sens 96.0, difference db -4.3; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 3: Axial frequency response @ 5.6 V — check 5.6 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 97.7, expected 101.9, stated sens 96.0, difference db -4.2; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 4: Axial frequency response @ 8 V — check 8 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 100.6, expected 105.0, stated sens 96.0, difference db -4.5; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 5: Axial frequency response @ 11.2 V — check 11.2 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 103.1, expected 107.9, stated sens 96.0, difference db -4.8; check on the image: SPL 99 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 6: Axial frequency response @ 1.41 V (no smoothing) — check 1.41 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 85.6, expected 89.9, stated sens 96.0, difference db -4.3; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 7: HD (orders) vs frequency @ 1.41 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 8: HD (orders) vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 9: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 10: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 11: HD (orders) vs frequency @ 5.6 V — check on the image: H2 100 %, H3 99 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 12: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 13: Impedance (chart to 7 ohm) — check impedance minimum against Re, read 3.69, stated 3.3; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 14: Impedance (chart to 20 ohm) — check impedance minimum against Re, read 3.73, stated 3.3; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34B-4** (`t34b-4`), set 0: Axial frequency response @ 1.41 V — check 1.41 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 85.1, expected 91.4, stated sens 97.5, difference db -6.3; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34B-4** (`t34b-4`), set 1: Axial frequency response @ 2 V — check 2 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 88.1, expected 94.5, stated sens 97.5, difference db -6.4; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34B-4** (`t34b-4`), set 2: Axial frequency response @ 2.83 V — check 2.83 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 91.1, expected 97.5, stated sens 97.5, difference db -6.4; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34B-4** (`t34b-4`), set 3: Axial frequency response @ 4 V — check 4 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 94.1, expected 100.5, stated sens 97.5, difference db -6.4; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34B-4** (`t34b-4`), set 4: Axial frequency response @ 5.6 V — check 5.6 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 97.1, expected 103.4, stated sens 97.5, difference db -6.3; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34B-4** (`t34b-4`), set 5: Axial frequency response @ 8 V — check 8 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 100.1, expected 106.5, stated sens 97.5, difference db -6.4; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34B-4** (`t34b-4`), set 6: HD (orders) vs frequency @ 1.41 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34B-4** (`t34b-4`), set 7: HD (orders) vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34B-4** (`t34b-4`), set 8: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34B-4** (`t34b-4`), set 9: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34B-4** (`t34b-4`), set 10: HD (orders) vs frequency @ 5.6 V — check on the image: H2 100 %, H3 99 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34B-4** (`t34b-4`), set 11: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34B-4** (`t34b-4`), set 12: Impedance (chart to 5 ohm) — check impedance minimum against Re, read 3.6, stated 3.3; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34B-4** (`t34b-4`), set 13: Impedance (chart to 20 ohm) — check impedance minimum against Re, read 3.63, stated 3.3; check impedance peak against Fs, read hz 760.13, read ohm 16.94, stated fs 790.0; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 0: Axial frequency response @ 2.83 V — check 2.83 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 90.2, expected 89.0, stated sens 89.0, difference db 1.2; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 1: Axial frequency response @ 4 V — check 4 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 93.2, expected 92.0, stated sens 89.0, difference db 1.2; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 2: Axial frequency response @ 5.6 V — check 5.6 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 96.2, expected 94.9, stated sens 89.0, difference db 1.3; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 3: Axial frequency response @ 8 V — check 8 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 99.2, expected 98.0, stated sens 89.0, difference db 1.2; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 4: Axial frequency response @ 11.2 V — check 11.2 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 102.2, expected 100.9, stated sens 89.0, difference db 1.3; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 5: Axial frequency response @ 16 V — check 16 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 105.2, expected 104.0, stated sens 89.0, difference db 1.2; check on the image: SPL 99 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 6: HD (orders) vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 7: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 8: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 9: HD (orders) vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 10: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 11: HD (orders) vs frequency @ 11.2 V — check on the image: H2 99 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 12: HD (orders) vs frequency @ 16 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 13: Voice-coil current HD vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 14: Voice-coil current HD vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 15: Voice-coil current HD vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 16: Impedance (chart to 150 ohm) — check impedance minimum against Re, read 6.66, stated 6.2; check impedance peak against Fs, read hz 35.02, read ohm 107.47, stated fs 35.0; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 17: Intermodulation 30 + 255 Hz, 4:1, low tone 1 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 18: Intermodulation 30 + 255 Hz, 4:1, low tone 1.5 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 19: Intermodulation 30 + 255 Hz, 4:1, low tone 2 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 20: Intermodulation 30 + 255 Hz, 4:1, low tone 3 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 21: Intermodulation 30 + 255 Hz, 4:1, low tone 4 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 22: Intermodulation 125 + 1063 Hz, 1:1, 2 V per tone — no self-check possible for this kind
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 23: Intermodulation 125 + 1063 Hz, 1:1, 2.83 V per tone — no self-check possible for this kind
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 24: Intermodulation 125 + 1063 Hz, 1:1, 4 V per tone — no self-check possible for this kind
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 25: Intermodulation 125 + 1063 Hz, 1:1, 5.6 V per tone — no self-check possible for this kind
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 26: Intermodulation 125 + 1063 Hz, 1:1, 8 V per tone — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 0: Axial frequency response @ 2 V — check 2 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 89.9, expected 90.0, stated sens 93.0, difference db -0.0; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 1: Axial frequency response @ 2.83 V — check 2.83 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 92.9, expected 93.0, stated sens 93.0, difference db -0.1; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 2: Axial frequency response @ 4 V — check 4 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 95.9, expected 96.0, stated sens 93.0, difference db -0.1; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 3: Axial frequency response @ 5.6 V — check 5.6 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 98.9, expected 98.9, stated sens 93.0, difference db 0.0; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 4: Axial frequency response @ 8 V — check 8 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 101.9, expected 102.0, stated sens 93.0, difference db -0.1; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 5: Axial frequency response @ 11.2 V — check 11.2 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 104.9, expected 104.9, stated sens 93.0, difference db -0.1; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 6: HD (orders) vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 7: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 8: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 9: HD (orders) vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 10: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 11: HD (orders) vs frequency @ 11.2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 12: HD (orders) vs frequency @ 2 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 13: HD (orders) vs frequency @ 2.83 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 14: HD (orders) vs frequency @ 4 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 15: HD (orders) vs frequency @ 5.6 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 16: HD (orders) vs frequency @ 8 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 17: Voice-coil current HD vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 18: Voice-coil current HD vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 19: Voice-coil current HD vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 20: Voice-coil current HD vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 21: Voice-coil current HD vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 22: Impedance (chart to 70 ohm) — check impedance minimum against Re, read 4.0, stated 3.4; check impedance peak against Fs, read hz 32.12, read ohm 59.32, stated fs 32.0; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 23: Impedance (chart to 7 ohm) — check impedance minimum against Re, read 3.93, stated 3.4; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 24: Harmonics of one tone, 20 Hz at 2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 25: Harmonics of one tone, 30 Hz at 2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 26: Harmonics of one tone, 40 Hz at 2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 27: Harmonics of one tone, 50 Hz at 2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 28: Harmonics of one tone, 75 Hz at 2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 29: Harmonics of one tone, 100 Hz at 2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 30: Harmonics of one tone, 150 Hz at 2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 31: Harmonics of one tone, 220 Hz at 2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 32: Harmonics of one tone, 300 Hz at 2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 33: Harmonics of one tone, 20 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 34: Harmonics of one tone, 30 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 35: Harmonics of one tone, 40 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 36: Harmonics of one tone, 50 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 37: Harmonics of one tone, 75 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 38: Harmonics of one tone, 100 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 39: Harmonics of one tone, 150 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 40: Harmonics of one tone, 220 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 41: Harmonics of one tone, 300 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 42: Harmonics of one tone, 20 Hz at 4 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 43: Harmonics of one tone, 30 Hz at 4 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 44: Harmonics of one tone, 40 Hz at 4 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 45: Harmonics of one tone, 50 Hz at 4 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 46: Harmonics of one tone, 75 Hz at 4 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 47: Harmonics of one tone, 100 Hz at 4 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 48: Harmonics of one tone, 150 Hz at 4 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 49: Harmonics of one tone, 220 Hz at 4 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 50: Harmonics of one tone, 300 Hz at 4 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 51: Harmonics of one tone, 20 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 52: Harmonics of one tone, 30 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 53: Harmonics of one tone, 40 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 54: Harmonics of one tone, 50 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 55: Harmonics of one tone, 75 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 56: Harmonics of one tone, 100 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 57: Harmonics of one tone, 150 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 58: Harmonics of one tone, 220 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 59: Harmonics of one tone, 300 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 60: Intermodulation 30 + 255 Hz, 4:1, low tone 3 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 61: Intermodulation 30 + 255 Hz, 4:1, low tone 6 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 62: Intermodulation 30 + 255 Hz, 4:1, low tone 9 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 0: Axial frequency response @ 1.41 V — check 1.41 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 90.5, expected 90.9, stated sens 97.0, difference db -0.4; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 1: Axial frequency response @ 2 V — check 2 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 93.5, expected 94.0, stated sens 97.0, difference db -0.5; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 2: Axial frequency response @ 2.83 V — check 2.83 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 96.5, expected 97.0, stated sens 97.0, difference db -0.5; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 3: Axial frequency response @ 4 V — check 4 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 99.5, expected 100.0, stated sens 97.0, difference db -0.5; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 4: Axial frequency response @ 5.6 V — check 5.6 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 102.5, expected 102.9, stated sens 97.0, difference db -0.5; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 5: Axial frequency response @ 8 V — check 8 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 105.5, expected 106.0, stated sens 97.0, difference db -0.5; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 6: Axial frequency response @ 11.2 V — check 11.2 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 108.5, expected 108.9, stated sens 97.0, difference db -0.4; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 7: HD (orders) vs frequency @ 1.41 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 8: HD (orders) vs frequency @ 2 V — check on the image: H2 100 %, H3 99 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 9: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 10: HD (orders) vs frequency @ 4 V — check on the image: H2 99 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 11: HD (orders) vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 12: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 13: HD (orders) vs frequency @ 11.2 V — check on the image: H2 99 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 14: Voice-coil current HD vs frequency @ 1.41 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 15: Voice-coil current HD vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 16: Voice-coil current HD vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 17: Voice-coil current HD vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 18: Voice-coil current HD vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 19: Impedance (chart to 5 ohm) — check impedance minimum against Re, read 3.03, stated 3.0; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 20: Intermodulation 1000 + 10000 Hz, 1:1, 2.83 V per tone — no self-check possible for this kind
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 21: Intermodulation 2000 + 10000 Hz, 1:1, 2.83 V per tone — no self-check possible for this kind
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 22: Intermodulation 800 + 10000 Hz, 1:1, 2.83 V per tone — no self-check possible for this kind
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 0: Axial frequency response @ 1.41 V — check 1.41 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 87.7, expected 89.9, stated sens 96.0, difference db -2.3; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 1: Axial frequency response @ 2 V — check 2 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 90.6, expected 93.0, stated sens 96.0, difference db -2.4; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 2: Axial frequency response @ 2.83 V — check 2.83 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 93.6, expected 96.0, stated sens 96.0, difference db -2.4; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 3: Axial frequency response @ 4 V — check 4 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 96.6, expected 99.0, stated sens 96.0, difference db -2.4; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 4: Axial frequency response @ 5.6 V — check 5.6 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 99.6, expected 101.9, stated sens 96.0, difference db -2.3; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 5: Axial frequency response @ 8 V — check 8 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 102.6, expected 105.0, stated sens 96.0, difference db -2.4; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 6: HD (orders) vs frequency @ 1.41 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 7: HD (orders) vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 8: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 9: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 10: HD (orders) vs frequency @ 5.6 V — check on the image: H2 99 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 11: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 12: Voice-coil current HD vs frequency @ 1.41 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 13: Voice-coil current HD vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 14: Voice-coil current HD vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 15: Voice-coil current HD vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 16: Voice-coil current HD vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 17: Impedance (chart to 15 ohm) — check impedance minimum against Re, read 3.04, stated 3.0; check impedance peak against Fs, read hz 620.99, read ohm 10.31, stated fs 600.0; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 18: Impedance (chart to 5 ohm) — check impedance minimum against Re, read 3.04, stated 3.0; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 19: Intermodulation 1000 + 10000 Hz, 1:1, 2.83 V per tone — no self-check possible for this kind
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 20: Intermodulation 19000 + 20000 Hz, 1:1, 2.83 V per tone — no self-check possible for this kind
