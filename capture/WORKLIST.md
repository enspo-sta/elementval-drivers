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
| Purifi PTT10.0X04-NAB-02 (`purifi-ptt10-0x04-nab-02`) | 70 | Voice-coil current HD vs frequency @ 2.83 V | HiFiCompass | 29 per decade | original image (remove `/styles/<style>/public/` from the image address), then `capture/image_curves.py` |
| SB Acoustics SB17CAC35-4 (proxy) (`sb17cac35-4`) | 0 | Large-signal compression vs frequency | Erin's Audio Corner | 37 per decade | original chart (Dropbox or site image, 1600 × 900), then `capture/image_curves.py` |
| SB Acoustics SB17CAC35-4 (proxy) (`sb17cac35-4`) | 1 | Large-signal distortion vs frequency | Erin's Audio Corner | 37 per decade | original chart (Dropbox or site image, 1600 × 900), then `capture/image_curves.py` |
| Purifi PTT6.5W04 (paper, proxy) (`ptt65w04-paper`) | 0 | Large-signal compression vs frequency | Erin's Audio Corner | 37 per decade | original chart (Dropbox or site image, 1600 × 900), then `capture/image_curves.py` |
| Purifi PTT6.5W04 (paper, proxy) (`ptt65w04-paper`) | 1 | Large-signal distortion vs frequency | Erin's Audio Corner | 37 per decade | original chart (Dropbox or site image, 1600 × 900), then `capture/image_curves.py` |
| Purifi PTT6.5X04-NAA-08A (`ptt65x04naa08a`) | 44 | Voice-coil current HD vs frequency @ 5.6 V | HiFiCompass | 37 per decade | original image (remove `/styles/<style>/public/` from the image address), then `capture/image_curves.py` |
| Purifi PTT6.5X04-NAA-08A (`ptt65x04naa08a`) | 45 | Voice-coil current HD vs frequency @ 8 V | HiFiCompass | 33 per decade | original image (remove `/styles/<style>/public/` from the image address), then `capture/image_curves.py` |

## 2. Values that disagree: check against the source

From `watch/check_consistency.py` (full list in `watch/consistency.md`).

| Check | Driver | Detail |
|---|---|---|
| band THD | `ptt525x04naa05` | 450–1800 Hz at 94 dB: table 0.095 %, from the curve 0.0774 % (-1.8 dB) |
| band THD | `ptt525x04naa05` | 80–5000 Hz at 94 dB: table 0.254 %, from the curve 0.157 % (-4.2 dB) |
| curves | `ptt13t04hag01` | set 26 (Impedance (Purifi's measured file)) Z: frequencies not strictly increasing |
| curves | `ptt13t04hag10` | set 3 (Impedance (Purifi's measured file)) Z: frequencies not strictly increasing |
| notes | `purifi-ptt10-0x04-nab-02` | a note says Pe was corrected to 350, the stored Pe is 'TBD (est 400)' |
| parameters | `m74a-6` | Qes: stored 0.75, from the others 0.7 (6.7 % apart) |
| parameters | `t25a-6` | Qes: stored 0.82, from the others 0.568 (30.7 % apart) |
| parameters | `t34a-4` | Qes: stored 0.42, from the others 0.374 (10.9 % apart) |
| parameters | `t34b-4` | Qes: stored 0.42, from the others 0.348 (17.2 % apart) |
| parameters | `wavecor-tw030wa11` | Vas: stored 0.1, from the others 0.0656 (34.4 % apart) |
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
| `m74t-6` | H3: 104.5 dB curve minus 98.5 dB curve = +8.6 dB on average over 162 shared frequencies (typical slope expects +4.2 dB) |
| `ptt13t04hag01` | H2: 102.9 dB curve minus 88 dB curve = +8.8 dB on average over 184 shared frequencies (typical slope expects +14.9 dB) |
| `ptt13t04hag01` | H2: 102.9 dB curve minus 90.9 dB curve = +7.5 dB on average over 187 shared frequencies (typical slope expects +12.0 dB) |
| `ptt13t04hag01` | H2: 102.9 dB curve minus 93.9 dB curve = +4.9 dB on average over 187 shared frequencies (typical slope expects +9.0 dB) |
| `ptt13t04hag01` | H2: 102.9 dB curve minus 96.9 dB curve = +0.9 dB on average over 187 shared frequencies (typical slope expects +6.0 dB) |
| `ptt13t04hag01` | H3: 102.9 dB curve minus 88 dB curve = +6.2 dB on average over 105 shared frequencies (typical slope expects +10.4 dB) |
| `ptt65x04naa08a` | H2: 100.7 dB curve minus 85.7 dB curve = +10.8 dB on average over 218 shared frequencies (typical slope expects +15.0 dB) |
| `ptt65x04naa08a` | H3: 100.7 dB curve minus 85.7 dB curve = +4.6 dB on average over 201 shared frequencies (typical slope expects +10.5 dB) |
| `ptt65x04naa08a` | H3: 100.7 dB curve minus 85.7 dB curve = +6.0 dB on average over 175 shared frequencies (typical slope expects +10.5 dB) |
| `ptt65x04naa08a` | H3: 100.7 dB curve minus 88.7 dB curve = +4.0 dB on average over 204 shared frequencies (typical slope expects +8.4 dB) |
| `ptt65x04naa08a` | H3: 94.7 dB curve minus 85.7 dB curve = +2.1 dB on average over 157 shared frequencies (typical slope expects +6.3 dB) |
| `purifi-ptt10-0x04-nab-02` | H2: 104.5 dB curve minus 86.5 dB curve = +13.6 dB on average over 213 shared frequencies (typical slope expects +18.0 dB) |
| `purifi-ptt10-0x04-nab-02` | H2: 104.5 dB curve minus 86.5 dB curve = +13.7 dB on average over 240 shared frequencies (typical slope expects +18.0 dB) |
| `purifi-ptt10-0x04-nab-02` | H2: 104.5 dB curve minus 89.5 dB curve = +10.9 dB on average over 215 shared frequencies (typical slope expects +15.0 dB) |
| `sb-satori-mr16tx-8` | H3: 105.2 dB curve minus 87.2 dB curve = +17.8 dB on average over 193 shared frequencies (typical slope expects +12.6 dB) |
| `sb-satori-mr16tx-8` | H3: 105.2 dB curve minus 90.2 dB curve = +15.2 dB on average over 196 shared frequencies (typical slope expects +10.5 dB) |
| `sb-satori-mw19tx-4` | H3: 101.9 dB curve minus 89.9 dB curve = +3.6 dB on average over 175 shared frequencies (typical slope expects +8.4 dB) |
| `sb-satori-mw19tx-4` | H3: 101.9 dB curve minus 92.9 dB curve = +2.3 dB on average over 176 shared frequencies (typical slope expects +6.3 dB) |
| `sb-satori-mw19tx-4` | H3: 98.9 dB curve minus 89.9 dB curve = +2.2 dB on average over 182 shared frequencies (typical slope expects +6.3 dB) |
| `sb-satori-tw29bnwg-4` | H3: 102.5 dB curve minus 93.5 dB curve = +13.0 dB on average over 131 shared frequencies (typical slope expects +6.3 dB) |
| `sb-satori-tw29bnwg-4` | H3: 102.5 dB curve minus 96.5 dB curve = +9.1 dB on average over 157 shared frequencies (typical slope expects +4.2 dB) |
| `sb-satori-tw29bnwg-4` | H3: 105.5 dB curve minus 93.5 dB curve = +14.5 dB on average over 131 shared frequencies (typical slope expects +8.4 dB) |
| `sb-satori-tw29bnwg-4` | H3: 105.5 dB curve minus 96.5 dB curve = +10.9 dB on average over 157 shared frequencies (typical slope expects +6.3 dB) |
| `sb-satori-tw29txn-b` | H3: 102.6 dB curve minus 87.7 dB curve = +5.4 dB on average over 155 shared frequencies (typical slope expects +10.4 dB) |
| `sb-satori-tw29txn-b` | H3: 102.6 dB curve minus 90.6 dB curve = +3.9 dB on average over 154 shared frequencies (typical slope expects +8.4 dB) |
| `sb-satori-tw29txn-b` | H3: 102.6 dB curve minus 96.6 dB curve = -0.0 dB on average over 160 shared frequencies (typical slope expects +4.2 dB) |
| `sb-satori-tw29txn-b` | H3: 102.6 dB curve minus 99.6 dB curve = -2.2 dB on average over 164 shared frequencies (typical slope expects +2.1 dB) |
| `sb-satori-wo24tx-8` | H2: 104.6 dB curve minus 89.6 dB curve = +10.8 dB on average over 217 shared frequencies (typical slope expects +15.0 dB) |
| `sb-satori-wo24tx-8` | H2: 104.6 dB curve minus 92.6 dB curve = +7.9 dB on average over 217 shared frequencies (typical slope expects +12.0 dB) |
| `sb-satori-wo24tx-8` | H2: 104.6 dB curve minus 95.6 dB curve = +5.0 dB on average over 218 shared frequencies (typical slope expects +9.0 dB) |
| `sb-satori-wo24tx-8` | H2: 104.6 dB curve minus 98.6 dB curve = +10.0 dB on average over 218 shared frequencies (typical slope expects +6.0 dB) |
| `sb-satori-wo24tx-8` | H2: 104.6 dB curve minus 98.6 dB curve = +2.0 dB on average over 217 shared frequencies (typical slope expects +6.0 dB) |
| `sb-satori-wo24tx-8` | H2: 98.6 dB curve minus 89.6 dB curve = +4.9 dB on average over 217 shared frequencies (typical slope expects +9.0 dB) |
| `sb-satori-wo24tx-8` | H2: 98.6 dB curve minus 92.6 dB curve = +1.9 dB on average over 217 shared frequencies (typical slope expects +6.0 dB) |
| `sb-satori-wo24tx-8` | H3: 101.6 dB curve minus 89.6 dB curve = +4.2 dB on average over 175 shared frequencies (typical slope expects +8.4 dB) |
| `sb-satori-wo24tx-8` | H3: 104.6 dB curve minus 89.6 dB curve = +5.6 dB on average over 171 shared frequencies (typical slope expects +10.5 dB) |
| `t25a-6` | H2: 96 dB curve minus 84 dB curve = +7.5 dB on average over 187 shared frequencies (typical slope expects +12.0 dB) |
| `t25a-6` | H2: 96 dB curve minus 87 dB curve = +4.9 dB on average over 187 shared frequencies (typical slope expects +9.0 dB) |
| `t25a-6` | H2: 98.9 dB curve minus 84 dB curve = +9.0 dB on average over 187 shared frequencies (typical slope expects +14.9 dB) |
| `t25a-6` | H2: 98.9 dB curve minus 87 dB curve = +6.5 dB on average over 187 shared frequencies (typical slope expects +11.9 dB) |
| `t25a-6` | H2: 98.9 dB curve minus 90 dB curve = +3.6 dB on average over 187 shared frequencies (typical slope expects +8.9 dB) |
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
| `wavecor-tw030wa11` | H2: 101.3 dB curve minus 89.3 dB curve = +6.7 dB on average over 184 shared frequencies (typical slope expects +12.0 dB) |
| `wavecor-tw030wa11` | H2: 101.3 dB curve minus 92.3 dB curve = +4.8 dB on average over 167 shared frequencies (typical slope expects +9.0 dB) |
| `wavecor-tw030wa11` | H2: 95.3 dB curve minus 89.3 dB curve = +1.0 dB on average over 184 shared frequencies (typical slope expects +6.0 dB) |
| `wavecor-tw030wa11` | H2: 98.3 dB curve minus 89.3 dB curve = +3.6 dB on average over 184 shared frequencies (typical slope expects +9.0 dB) |
| `wavecor-tw030wa11` | H2: 98.3 dB curve minus 92.3 dB curve = +1.7 dB on average over 167 shared frequencies (typical slope expects +6.0 dB) |
| `wavecor-tw030wa11` | H3: 101.3 dB curve minus 89.3 dB curve = +1.0 dB on average over 159 shared frequencies (typical slope expects +8.4 dB) |
| `wavecor-tw030wa11` | H3: 101.3 dB curve minus 92.3 dB curve = -0.3 dB on average over 160 shared frequencies (typical slope expects +6.3 dB) |
| `wavecor-tw030wa11` | H3: 95.3 dB curve minus 89.3 dB curve = -3.4 dB on average over 160 shared frequencies (typical slope expects +4.2 dB) |
| `wavecor-tw030wa11` | H3: 95.3 dB curve minus 92.3 dB curve = -4.8 dB on average over 161 shared frequencies (typical slope expects +2.1 dB) |
| `wavecor-tw030wa11` | H3: 98.3 dB curve minus 89.3 dB curve = -1.7 dB on average over 158 shared frequencies (typical slope expects +6.3 dB) |
| `wavecor-tw030wa11` | H3: 98.3 dB curve minus 92.3 dB curve = -3.1 dB on average over 159 shared frequencies (typical slope expects +4.2 dB) |

## 3. Every curve HiFiCompass and Purifi publish

Stored now, and what to add. Capture each drive level as its own set with the SPL it gives at 1 m.

- **Purifi PTT6.5M08-NAA-08** (`ptt65m08naa08`), Manufacturer datasheet: stored frequency-response, hd-current, hd-frequency 94 dB, imd-spectrum 94 dB, impedance.
  Add: harmonic distortion vs level (level sweeps).
- **Purifi PTT8.0X04-NAB-01** (`ptt80x04nab01`), Manufacturer datasheet: stored frequency-response, hd-frequency 94 dB, hd-level, imd-spectrum 80 dB, impedance.
  Add: current distortion.
- **Purifi PTT6.5X04-NAA-08** (`ptt65x04naa08`), Manufacturer datasheet: stored frequency-response, hd-frequency 94 dB, hd-level, imd-spectrum 80 dB, impedance.
  Add: current distortion.
- **Purifi PTT5.25X04-NAA-05** (`ptt525x04naa05`), HiFiCompass: stored hd-frequency 94 dB, thd-bands 94 dB.
  Add: the harmonics at each drive level actually measured (the stored 94 dB curve was normalised from them; keep it until they are in); axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); impedance (use the .zma file when offered); two-tone intermodulation, where measured.
- **Purifi PTT5.25X04-NAA-05** (`ptt525x04naa05`), Manufacturer datasheet: stored hd-frequency 94 dB, hd-level, imd-spectrum 80 dB, impedance, off-axis.
  Add: frequency response figure; current distortion.
- **Purifi PTT1.3T04-HAG-10** (`ptt13t04hag10`), Manufacturer datasheet: stored hd-frequency 94 dB, hd-level, impedance, off-axis.
  Add: frequency response figure; current distortion; intermodulation spectra (both tone pairs).
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), HiFiCompass: stored frequency-response, hd-current, hd-frequency 102.9 dB, hd-frequency 88.0 dB, hd-frequency 90.9 dB, hd-frequency 93.9 dB, hd-frequency 96.9 dB, hd-frequency 99.9 dB, impedance, off-axis, off-axis-normalized. Page: <https://hificompass.com/ru/speakers/measurements/purifi/purifi-ptt13t04-hag-01> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), Manufacturer datasheet: stored hd-frequency 94 dB, hd-level, impedance, off-axis.
  Add: frequency response figure; current distortion; intermodulation spectra (both tone pairs).
- **SB Acoustics Satori WO24P-8** (`sb-satori-wo24p-8`), HiFiCompass: stored hd-frequency 91 dB, thd-bands 91 dB. Page: <https://hificompass.com/ru/speakers/measurements/satori/satori-wo24p-8> (what it offers: `capture/inventory.md`).
  Add: the harmonics above 500 Hz, up to the end of the page's harmonics charts (the stored curve stops at 500 Hz, so Simulate has no data above it where this driver still plays; `watch/sim_coverage.md`); axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); impedance (use the .zma file when offered); two-tone intermodulation, where measured.
- **SB Acoustics SB34NRXL75-8 (Norex)** (`sb-sb34nrxl75-8`), HiFiCompass: stored hd-frequency 91 dB, imd-summary 91.1 dB, thd-bands 91 dB. Page: <https://hificompass.com/ru/speakers/measurements/sbacoustics/sb-acoustics-sb34nrxl75-8> (what it offers: `capture/inventory.md`).
  Add: the harmonics above 500 Hz, up to the end of the page's harmonics charts (the stored curve stops at 500 Hz, so Simulate has no data above it where this driver still plays; `watch/sim_coverage.md`); axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); impedance (use the .zma file when offered).
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), HiFiCompass: stored frequency-response, hd-current, hd-frequency 102.2 dB, hd-frequency 105.2 dB, hd-frequency 90.2 dB, hd-frequency 93.2 dB, hd-frequency 96.2 dB, hd-frequency 99.2 dB, imd-products, impedance, off-axis, off-axis-normalized. Page: <https://hificompass.com/ru/speakers/measurements/purifi/purifi-ptt80x04-nab-02> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), Manufacturer datasheet: stored nothing.
  Add (if Purifi publishes a datasheet for this exact variant): frequency response figure; impedance figure; harmonic distortion vs frequency at 94 dB; harmonic distortion vs level (level sweeps); current distortion; intermodulation spectra (both tone pairs).
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), HiFiCompass: stored frequency-response, hd-current, hd-frequency 101.5 dB, hd-frequency 104.5 dB, hd-frequency 86.5 dB, hd-frequency 89.5 dB, hd-frequency 92.5 dB, hd-frequency 95.5 dB, hd-frequency 98.5 dB, hd-spectrum, imd-products, imd-summary 91.67 dB, impedance, off-axis, off-axis-normalized. Page: <https://hificompass.com/ru/speakers/measurements/purifi/purifi-ptt100x04-nab-02> (what it offers: `capture/inventory.md`).
  Add: check every drive level is stored, as measured.
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), Manufacturer datasheet: stored nothing.
  Add (if Purifi publishes a datasheet for this exact variant): frequency response figure; impedance figure; harmonic distortion vs frequency at 94 dB; harmonic distortion vs level (level sweeps); current distortion; intermodulation spectra (both tone pairs).
- **SB Acoustics Satori WO24P-4** (`sb-satori-wo24p-4`), HiFiCompass: stored imd-summary 91.15 dB. Page: <https://hificompass.com/ru/speakers/measurements/satori/satori-wo24p-4> (what it offers: `capture/inventory.md`).
  Add: axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); harmonics H2 to H5 at every drive level shown, as measured (not normalised to one level: the viewer interpolates); impedance (use the .zma file when offered).
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), HiFiCompass: stored frequency-response, hd-current, hd-frequency 100.7 dB, hd-frequency 85.7 dB, hd-frequency 88.7 dB, hd-frequency 91.7 dB, hd-frequency 94.7 dB, hd-frequency 97.7 dB, hd-spectrum, imd-products, impedance, off-axis, off-axis-normalized. Page: <https://hificompass.com/ru/speakers/measurements/purifi/purifi-ptt65x04-naa-08a> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), Manufacturer datasheet: stored nothing.
  Add (if Purifi publishes a datasheet for this exact variant): frequency response figure; impedance figure; harmonic distortion vs frequency at 94 dB; harmonic distortion vs level (level sweeps); current distortion; intermodulation spectra (both tone pairs).
- **SB Acoustics SB17NBAC35-8** (`sb17nbac35-8`), HiFiCompass: stored hd-frequency 94 dB, thd-bands 94 dB. Page: <https://hificompass.com/ru/speakers/measurements/sbacoustics/sb-acoustics-sb17nbac35-8> (what it offers: `capture/inventory.md`).
  Add: the harmonics at each drive level actually measured (the stored 94 dB curve was normalised from them; keep it until they are in); axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); impedance (use the .zma file when offered); two-tone intermodulation, where measured.
- **BlieSMa M74T-6** (`m74t-6`), HiFiCompass: stored frequency-response, hd-current, hd-frequency 101.4 dB, hd-frequency 104.5 dB, hd-frequency 89.5 dB, hd-frequency 92.5 dB, hd-frequency 95.5 dB, hd-frequency 98.5 dB, imd-products, impedance, off-axis, off-axis-normalized. Page: <https://hificompass.com/en/speakers/measurements/bliesma/bliesma-m74t-6> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **BlieSMa M74A-6** (`m74a-6`), HiFiCompass: stored frequency-response, hd-current, hd-frequency 102.1 dB, hd-frequency 105.0 dB, hd-frequency 90.1 dB, hd-frequency 93.0 dB, hd-frequency 96.1 dB, hd-frequency 99.0 dB, imd-products, impedance, off-axis, off-axis-normalized. Page: <https://hificompass.com/en/speakers/measurements/bliesma/bliesma-m74a-6> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **BlieSMa T25A-6** (`t25a-6`), HiFiCompass: stored frequency-response, hd-frequency 84.0 dB, hd-frequency 87.0 dB, hd-frequency 90.0 dB, hd-frequency 93.0 dB, hd-frequency 96.0 dB, hd-frequency 98.9 dB, impedance, off-axis, off-axis-normalized. Page: <https://hificompass.com/en/speakers/measurements/bliesma/bliesma-t25a-6> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **BlieSMa T25T-6** (`t25t-6`), HiFiCompass: stored frequency-response, hd-current, hd-frequency 87.8 dB, hd-frequency 90.8 dB, hd-frequency 93.9 dB, hd-frequency 96.8 dB, hd-frequency 99.8 dB, impedance, off-axis, off-axis-normalized. Page: <https://hificompass.com/en/speakers/measurements/bliesma/bliesma-t25t-6> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **BlieSMa T34A-4** (`t34a-4`), HiFiCompass: stored frequency-response, hd-frequency 100.6 dB, hd-frequency 85.6 dB, hd-frequency 88.7 dB, hd-frequency 91.7 dB, hd-frequency 94.7 dB, hd-frequency 97.7 dB, impedance, off-axis, off-axis-normalized. Page: <https://hificompass.com/en/speakers/measurements/bliesma/bliesma-t34a-4> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **BlieSMa T34B-4** (`t34b-4`), HiFiCompass: stored frequency-response, hd-frequency 100.1 dB, hd-frequency 85.1 dB, hd-frequency 88.1 dB, hd-frequency 91.1 dB, hd-frequency 94.1 dB, hd-frequency 97.1 dB, impedance, off-axis, off-axis-normalized. Page: <https://hificompass.com/en/speakers/measurements/bliesma/bliesma-t34b-4> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), HiFiCompass: stored frequency-response, hd-current, hd-frequency 102.2 dB, hd-frequency 105.2 dB, hd-frequency 87.2 dB, hd-frequency 90.2 dB, hd-frequency 93.2 dB, hd-frequency 96.2 dB, hd-frequency 99.2 dB, imd-products, impedance, off-axis, off-axis-normalized. Page: <https://hificompass.com/ru/speakers/measurements/satori/satori-mr16tx-8> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), HiFiCompass: stored frequency-response, hd-current, hd-frequency 101.9 dB, hd-frequency 104.9 dB, hd-frequency 89.9 dB, hd-frequency 92.9 dB, hd-frequency 95.9 dB, hd-frequency 98.9 dB, hd-spectrum, imd-products, impedance, off-axis, off-axis-normalized. Page: <https://hificompass.com/ru/speakers/measurements/satori/satori-mw19tx-4> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), HiFiCompass: stored frequency-response, hd-current, hd-frequency 102.5 dB, hd-frequency 105.5 dB, hd-frequency 108.5 dB, hd-frequency 90.5 dB, hd-frequency 93.5 dB, hd-frequency 96.5 dB, hd-frequency 99.5 dB, imd-products, impedance, off-axis, off-axis-normalized. Page: <https://hificompass.com/ru/speakers/measurements/satori/satori-tw29bnwg-4> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), HiFiCompass: stored frequency-response, hd-current, hd-frequency 102.6 dB, hd-frequency 87.7 dB, hd-frequency 90.6 dB, hd-frequency 93.6 dB, hd-frequency 96.6 dB, hd-frequency 99.6 dB, imd-products, impedance, off-axis, off-axis-normalized. Page: <https://hificompass.com/ru/speakers/measurements/satori/satori-tw29txn-b> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **SB Acoustics SB26ADC-C000-4** (`sb-sb26adc-c000-4`), HiFiCompass: stored nothing. Page: <https://hificompass.com/ru/speakers/measurements/sbacoustics/sb-acoustics-sb26adc-c000-4> (what it offers: `capture/inventory.md`).
  Add: axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); harmonics H2 to H5 at every drive level shown, as measured (not normalised to one level: the viewer interpolates); impedance (use the .zma file when offered); two-tone intermodulation, where measured.
- **Wavecor TW030WA11** (`wavecor-tw030wa11`), HiFiCompass: stored frequency-response, hd-frequency 101.3 dB, hd-frequency 89.3 dB, hd-frequency 92.3 dB, hd-frequency 95.3 dB, hd-frequency 98.3 dB, impedance, off-axis, off-axis-normalized. Page: <https://hificompass.com/ru/speakers/measurements/wavecor/wavecor-tw030wa11> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), HiFiCompass: stored frequency-response, hd-current, hd-frequency 101.6 dB, hd-frequency 104.6 dB, hd-frequency 107.6 dB, hd-frequency 89.6 dB, hd-frequency 92.6 dB, hd-frequency 95.6 dB, hd-frequency 98.6 dB, hd-spectrum, imd-products, impedance, off-axis, off-axis-normalized. Page: <https://hificompass.com/ru/speakers/measurements/satori/satori-wo24tx-8> (what it offers: `capture/inventory.md`).
  Add: two-tone intermodulation, where measured.
- **SB Audience Rosso 12MW300** (`sb-audience-rosso-12mw300`), HiFiCompass: stored nothing. Page: <https://hificompass.com/ru/speakers/measurements/sb-audience/sb-audience-rosso-12mw300> (what it offers: `capture/inventory.md`).
  Add: axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); harmonics H2 to H5 at every drive level shown, as measured (not normalised to one level: the viewer interpolates); impedance (use the .zma file when offered); two-tone intermodulation, where measured.
- **Lavoce MAN062.00-8** (`lavoce-man06200-8`), HiFiCompass: stored nothing. Page: <https://hificompass.com/en/speakers/measurements/lavoce/lavoce-man06200-8> (what it offers: `capture/inventory.md`).
  Add: axial sound pressure at every drive level shown (one set per drive voltage, with its SPL at 1 m); harmonics H2 to H5 at every drive level shown, as measured (not normalised to one level: the viewer interpolates); impedance (use the .zma file when offered); two-tone intermodulation, where measured.

## 4. Random spot check

Chosen at random for week 39 of 2026 (the choice changes weekly). For each, capture the source's curve again and compare with the stored one; differences above 1 dB outside the noise floor need a note or a recapture.

- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`): sets 37: Axial frequency response @ 2.83 V; 38: Axial frequency response @ 4 V; 39: Axial frequency response @ 5.6 V; 40: Axial frequency response @ 8 V; 41: Axial frequency response @ 11.2 V; 42: Axial frequency response @ 16 V; 43: Axial frequency response @ 22 V; 44: Near-field frequency response @ 1 V (near field 3 mm); 45: HD (orders) vs frequency @ 2.83 V; 46: HD (orders) vs frequency @ 4 V; 47: HD (orders) vs frequency @ 5.6 V; 48: HD (orders) vs frequency @ 8 V; 49: HD (orders) vs frequency @ 11.2 V; 50: HD (orders) vs frequency @ 16 V; 51: HD (orders) vs frequency @ 22 V; 52: HD (orders) vs frequency @ 2.83 V (near field 20 mm); 53: HD (orders) vs frequency @ 4 V (near field 20 mm); 54: HD (orders) vs frequency @ 5.6 V (near field 20 mm); 55: HD (orders) vs frequency @ 8 V (near field 20 mm); 56: HD (orders) vs frequency @ 11.2 V (near field 20 mm); 57: HD (orders) vs frequency @ 16 V (near field 20 mm); 58: Voice-coil current HD vs frequency @ 2.83 V; 59: Voice-coil current HD vs frequency @ 4 V; 60: Voice-coil current HD vs frequency @ 5.6 V; 61: Voice-coil current HD vs frequency @ 8 V; 62: Voice-coil current HD vs frequency @ 11.2 V; 63: Impedance (chart to 100 ohm); 64: Impedance (chart to 15 ohm); 65: Off-axis response; 66: Off-axis response (relative to on axis, chart range 10-50 dB); 67: Off-axis response (relative to on axis, chart range 5-30 dB)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`): sets 10: Axial frequency response @ 2.83 V; 11: Axial frequency response @ 4 V; 12: Axial frequency response @ 5.6 V; 13: Axial frequency response @ 8 V; 14: Axial frequency response @ 11.2 V; 15: Axial frequency response @ 16 V; 16: Near-field frequency response @ 1 V (near field 5 mm); 17: HD (orders) vs frequency @ 2 V; 18: HD (orders) vs frequency @ 2.83 V; 19: HD (orders) vs frequency @ 4 V; 20: HD (orders) vs frequency @ 5.6 V; 21: HD (orders) vs frequency @ 8 V; 22: HD (orders) vs frequency @ 11.2 V; 23: HD (orders) vs frequency @ 16 V; 24: Voice-coil current HD vs frequency @ 2.83 V; 25: Voice-coil current HD vs frequency @ 4 V; 26: Voice-coil current HD vs frequency @ 5.6 V; 27: Impedance (chart to 150 ohm); 28: Off-axis response; 29: Off-axis response (relative to on axis, chart range 10-50 dB); 30: Off-axis response (relative to on axis, chart range 5-30 dB)
- **Purifi PTT5.25X04-NAA-05** (`ptt525x04naa05`): sets 0: HD vs frequency (ratio); 3: HD vs SPL (level sweep); 5: HD (orders) vs frequency @ 94 dB; 7: Off-axis response (Purifi's measured files); 8: Impedance (Purifi's measured file)

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
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), set 22: Off-axis response — check on the image: 0° 99 %, 15° 100 %, 30° 100 %, 45° 100 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), set 23: Off-axis response (relative to on axis, chart range 10-50 dB) — check on the image: 0° 99 %, 15° 100 %, 30° 99 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT1.3T04-HAG-01** (`ptt13t04hag01`), set 24: Off-axis response (relative to on axis, chart range 5-30 dB) — check on the image: 0° 99 %, 15° 100 %, 30° 99 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 5: Intermodulation 30 + 255 Hz, 4:1, low tone 2 mm peak excursion — no self-check possible for this kind
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 6: Intermodulation 30 + 255 Hz, 4:1, low tone 3 mm peak excursion — no self-check possible for this kind
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 7: Intermodulation 30 + 255 Hz, 4:1, low tone 4.5 mm peak excursion — no self-check possible for this kind
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 8: Intermodulation 30 + 255 Hz, 4:1, low tone 6 mm peak excursion — no self-check possible for this kind
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 9: Intermodulation 30 + 255 Hz, 4:1, low tone 9 mm peak excursion — no self-check possible for this kind
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 10: Intermodulation 30 + 255 Hz, 4:1, low tone 10 mm peak excursion — no self-check possible for this kind
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 11: Intermodulation 50 + 425 Hz, 4:1, low tone 1 mm peak excursion — no self-check possible for this kind
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 12: Intermodulation 50 + 425 Hz, 4:1, low tone 2 mm peak excursion — no self-check possible for this kind
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 13: Intermodulation 50 + 425 Hz, 4:1, low tone 3 mm peak excursion — no self-check possible for this kind
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 14: Intermodulation 50 + 425 Hz, 4:1, low tone 6 mm peak excursion — no self-check possible for this kind
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 15: Axial frequency response @ 2.83 V — check on the image: SPL 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 16: Axial frequency response @ 4 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 17: Axial frequency response @ 5.6 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 18: Axial frequency response @ 8 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 19: Axial frequency response @ 11.2 V — check on the image: SPL 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 20: Axial frequency response @ 16 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 21: Near-field frequency response @ 2.83 V (near field 20 mm) — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 22: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 99 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 23: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 24: HD (orders) vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 25: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 26: HD (orders) vs frequency @ 11.2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 27: HD (orders) vs frequency @ 16 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 28: HD (orders) vs frequency @ 2.83 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 29: HD (orders) vs frequency @ 4 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 30: HD (orders) vs frequency @ 5.6 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 31: HD (orders) vs frequency @ 8 V (near field 20 mm) — check on the image: H2 100 %, H3 99 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 32: HD (orders) vs frequency @ 11.2 V (near field 20 mm) — check on the image: H2 100 %, H3 99 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 33: Voice-coil current HD vs frequency @ 1.41 V — check on the image: H2 96 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 34: Voice-coil current HD vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 35: Voice-coil current HD vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 36: Voice-coil current HD vs frequency @ 4 V — check on the image: H2 100 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 37: Voice-coil current HD vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 38: Voice-coil current HD vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 39: Impedance (chart to 70 ohm) — check impedance minimum against Re, read 3.78, stated 3.55; check impedance peak against Fs, read hz 24.06, read ohm 49.84, stated fs 28.8; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 40: Impedance (chart to 7 ohm) — check impedance minimum against Re, read 3.73, stated 3.55; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 41: Off-axis response — check on the image: 0° 92 %, 15° 96 %, 30° 97 %, 45° 100 %, 60° 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 42: Off-axis response (relative to on axis, chart range 10-50 dB) — check on the image: 0° 96 %, 15° 96 %, 30° 95 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT8.0X04-NAB-02** (`purifi-ptt8-0x04-nab-02`), set 43: Off-axis response (relative to on axis, chart range 5-30 dB) — check on the image: 0° 97 %, 15° 98 %, 30° 96 %, 45° 100 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 4: Harmonics of one tone, 20 Hz at 2.83 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 5: Harmonics of one tone, 30 Hz at 2.83 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 6: Harmonics of one tone, 40 Hz at 2.83 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 7: Harmonics of one tone, 50 Hz at 2.83 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 8: Harmonics of one tone, 75 Hz at 2.83 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 9: Harmonics of one tone, 100 Hz at 2.83 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 10: Harmonics of one tone, 150 Hz at 2.83 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 11: Harmonics of one tone, 20 Hz at 4 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 12: Harmonics of one tone, 30 Hz at 4 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 13: Harmonics of one tone, 40 Hz at 4 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 14: Harmonics of one tone, 50 Hz at 4 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 15: Harmonics of one tone, 75 Hz at 4 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 16: Harmonics of one tone, 100 Hz at 4 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 17: Harmonics of one tone, 150 Hz at 4 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 18: Harmonics of one tone, 20 Hz at 5.6 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 19: Harmonics of one tone, 30 Hz at 5.6 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 20: Harmonics of one tone, 40 Hz at 5.6 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 21: Harmonics of one tone, 50 Hz at 5.6 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 22: Harmonics of one tone, 75 Hz at 5.6 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 23: Harmonics of one tone, 100 Hz at 5.6 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 24: Harmonics of one tone, 150 Hz at 5.6 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 25: Harmonics of one tone, 20 Hz at 8 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 26: Harmonics of one tone, 30 Hz at 8 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 27: Harmonics of one tone, 40 Hz at 8 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 28: Harmonics of one tone, 50 Hz at 8 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 29: Harmonics of one tone, 75 Hz at 8 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 30: Harmonics of one tone, 100 Hz at 8 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 31: Harmonics of one tone, 150 Hz at 8 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 32: Harmonics of one tone, 20 Hz at 11.2 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 33: Harmonics of one tone, 30 Hz at 11.2 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 34: Harmonics of one tone, 40 Hz at 11.2 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 35: Harmonics of one tone, 50 Hz at 11.2 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 36: Harmonics of one tone, 75 Hz at 11.2 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 37: Harmonics of one tone, 100 Hz at 11.2 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 38: Harmonics of one tone, 150 Hz at 11.2 V (microphone at 50 mm) — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 39: Intermodulation 30 + 255 Hz, 4:1, low tone 3 mm peak excursion — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 40: Intermodulation 30 + 255 Hz, 4:1, low tone 4.5 mm peak excursion — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 41: Intermodulation 30 + 255 Hz, 4:1, low tone 6 mm peak excursion — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 42: Intermodulation 30 + 255 Hz, 4:1, low tone 9 mm peak excursion — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 43: Intermodulation 30 + 255 Hz, 4:1, low tone 12 mm peak excursion — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 44: Intermodulation 50 + 425 Hz, 4:1, low tone 1 mm peak excursion — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 45: Intermodulation 50 + 425 Hz, 4:1, low tone 2 mm peak excursion — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 46: Intermodulation 50 + 425 Hz, 4:1, low tone 3 mm peak excursion — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 47: Intermodulation 50 + 425 Hz, 4:1, low tone 4.5 mm peak excursion — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 48: Intermodulation 50 + 425 Hz, 4:1, low tone 6 mm peak excursion — no self-check possible for this kind
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 49: Axial frequency response @ 2.83 V — check 2.83 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 86.5, expected 88.0, stated sens 88.0, difference db -1.5; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 50: Axial frequency response @ 4 V — check 4 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 89.5, expected 91.0, stated sens 88.0, difference db -1.5; check on the image: SPL 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 51: Axial frequency response @ 5.6 V — check 5.6 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 92.5, expected 93.9, stated sens 88.0, difference db -1.4; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 52: Axial frequency response @ 8 V — check 8 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 95.5, expected 97.0, stated sens 88.0, difference db -1.5; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 53: Axial frequency response @ 11.2 V — check 11.2 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 98.5, expected 99.9, stated sens 88.0, difference db -1.5; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 54: Axial frequency response @ 16 V — check 16 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 101.5, expected 103.0, stated sens 88.0, difference db -1.6; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 55: Axial frequency response @ 22.5 V — check 22.5 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 104.5, expected 106.0, stated sens 88.0, difference db -1.5; check on the image: SPL 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 56: Near-field frequency response @ 2.83 V (near field 20 mm) — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 57: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 58: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 59: HD (orders) vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 60: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 61: HD (orders) vs frequency @ 11.2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 62: HD (orders) vs frequency @ 16 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 63: HD (orders) vs frequency @ 22.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 64: HD (orders) vs frequency @ 2.83 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 65: HD (orders) vs frequency @ 4 V (near field 20 mm) — check on the image: H2 99 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 66: HD (orders) vs frequency @ 5.6 V (near field 20 mm) — check on the image: H2 99 %, H3 100 %, H5 97 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 67: HD (orders) vs frequency @ 8 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 68: HD (orders) vs frequency @ 11.2 V (near field 20 mm) — check on the image: H2 100 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 69: HD (orders) vs frequency @ 16 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 70: Voice-coil current HD vs frequency @ 2.83 V — check on the image: H2 99 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 71: Voice-coil current HD vs frequency @ 4 V — check on the image: H2 98 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 72: Voice-coil current HD vs frequency @ 5.6 V — check on the image: H2 98 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 73: Voice-coil current HD vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 74: Voice-coil current HD vs frequency @ 11.2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 75: Impedance (chart to 70 ohm) — check impedance minimum against Re, read 4.69, stated 3.9; check impedance peak against Fs, read hz 22.71, read ohm 60.64, stated fs 24; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 76: Impedance (chart to 15 ohm) — check impedance minimum against Re, read 4.63, stated 3.9; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 77: Off-axis response — check on the image: 0° 94 %, 15° 96 %, 30° 99 %, 45° 100 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 78: Off-axis response (relative to on axis, chart range 10-50 dB) — check on the image: 0° 99 %, 15° 93 %, 30° 97 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT10.0X04-NAB-02** (`purifi-ptt10-0x04-nab-02`), set 79: Off-axis response (relative to on axis, chart range 5-30 dB) — check on the image: 0° 98 %, 15° 93 %, 30° 97 %, 45° 100 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 2: Harmonics of one tone, 20 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 3: Harmonics of one tone, 30 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 4: Harmonics of one tone, 40 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 5: Harmonics of one tone, 50 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 6: Harmonics of one tone, 75 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 7: Harmonics of one tone, 100 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 8: Harmonics of one tone, 150 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 9: Harmonics of one tone, 220 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 10: Harmonics of one tone, 300 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 11: Harmonics of one tone, 20 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 12: Harmonics of one tone, 30 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 13: Harmonics of one tone, 40 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 14: Harmonics of one tone, 50 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 15: Harmonics of one tone, 75 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 16: Harmonics of one tone, 100 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 17: Harmonics of one tone, 150 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 18: Harmonics of one tone, 220 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 19: Harmonics of one tone, 300 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 20: Intermodulation 30 + 255 Hz, 4:1, low tone 2 mm peak excursion — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 21: Intermodulation 30 + 255 Hz, 4:1, low tone 3 mm peak excursion — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 22: Intermodulation 30 + 255 Hz, 4:1, low tone 4.5 mm peak excursion — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 23: Intermodulation 30 + 255 Hz, 4:1, low tone 6 mm peak excursion — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 24: Intermodulation 30 + 255 Hz, 4:1, low tone 9 mm peak excursion — no self-check possible for this kind
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 25: Axial frequency response @ 2.83 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 26: Axial frequency response @ 4 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 27: Axial frequency response @ 5.6 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 28: Axial frequency response @ 8 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 29: Axial frequency response @ 11.2 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 30: Axial frequency response @ 16 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 31: Near-field frequency response @ 2.83 V (near field 20 mm) — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 32: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 33: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 34: HD (orders) vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 35: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 36: HD (orders) vs frequency @ 11.2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 37: HD (orders) vs frequency @ 16 V — check on the image: H2 100 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 38: HD (orders) vs frequency @ 2.83 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 39: HD (orders) vs frequency @ 4 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 40: HD (orders) vs frequency @ 5.6 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 41: HD (orders) vs frequency @ 8 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 42: Voice-coil current HD vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 43: Voice-coil current HD vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 44: Voice-coil current HD vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 45: Voice-coil current HD vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 46: Impedance (chart to 70 ohm) — check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 47: Off-axis response — check on the image: 0° 98 %, 15° 98 %, 30° 97 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 48: Off-axis response (relative to on axis, chart range 10-50 dB) — check on the image: 0° 98 %, 15° 97 %, 30° 98 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **Purifi PTT6.5X04-NAA-08A** (`ptt65x04naa08a`), set 49: Off-axis response (relative to on axis, chart range 5-30 dB) — check on the image: 0° 97 %, 15° 97 %, 30° 98 %, 45° 100 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 2: Intermodulation 125 + 1063 Hz, 1:1, 1 V per tone — no self-check possible for this kind
- **BlieSMa M74T-6** (`m74t-6`), set 3: Intermodulation 125 + 1063 Hz, 1:1, 1.41 V per tone — no self-check possible for this kind
- **BlieSMa M74T-6** (`m74t-6`), set 4: Intermodulation 125 + 1063 Hz, 1:1, 2 V per tone — no self-check possible for this kind
- **BlieSMa M74T-6** (`m74t-6`), set 5: Intermodulation 125 + 1063 Hz, 1:1, 2.83 V per tone — no self-check possible for this kind
- **BlieSMa M74T-6** (`m74t-6`), set 6: Intermodulation 125 + 1063 Hz, 1:1, 4 V per tone — no self-check possible for this kind
- **BlieSMa M74T-6** (`m74t-6`), set 7: Intermodulation 500 + 4250 Hz, 1:1, 1 V per tone — no self-check possible for this kind
- **BlieSMa M74T-6** (`m74t-6`), set 8: Intermodulation 500 + 4250 Hz, 1:1, 1.41 V per tone — no self-check possible for this kind
- **BlieSMa M74T-6** (`m74t-6`), set 9: Intermodulation 500 + 4250 Hz, 1:1, 2 V per tone — no self-check possible for this kind
- **BlieSMa M74T-6** (`m74t-6`), set 10: Intermodulation 500 + 4250 Hz, 1:1, 2.83 V per tone — no self-check possible for this kind
- **BlieSMa M74T-6** (`m74t-6`), set 11: Axial frequency response @ 1.41 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 12: Axial frequency response @ 2 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 13: Axial frequency response @ 2.83 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 14: Axial frequency response @ 4 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 15: Axial frequency response @ 5.6 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 16: Axial frequency response @ 8 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 17: HD (orders) vs frequency @ 1.41 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 18: HD (orders) vs frequency @ 2 V — check on the image: H2 100 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 19: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 20: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 21: HD (orders) vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 22: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 99 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 23: Voice-coil current HD vs frequency @ 1 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 24: Voice-coil current HD vs frequency @ 1.41 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 25: Voice-coil current HD vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 26: Voice-coil current HD vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 27: Impedance (chart to 70 ohm) — check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 28: Impedance (chart to 15 ohm) — check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 29: Off-axis response — check on the image: 0° 96 %, 15° 95 %, 30° 98 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 30: Off-axis response (relative to on axis, chart range 10-50 dB) — check on the image: 0° 96 %, 15° 98 %, 30° 98 %, 45° 99 %, 60° 99 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74T-6** (`m74t-6`), set 31: Off-axis response (relative to on axis, chart range 5-30 dB) — check on the image: 0° 96 %, 15° 97 %, 30° 98 %, 45° 100 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 0: Intermodulation 500 + 4250 Hz, 1:1, 1 V per tone — no self-check possible for this kind
- **BlieSMa M74A-6** (`m74a-6`), set 1: Intermodulation 500 + 4250 Hz, 1:1, 1.41 V per tone — no self-check possible for this kind
- **BlieSMa M74A-6** (`m74a-6`), set 2: Intermodulation 500 + 4250 Hz, 1:1, 2 V per tone — no self-check possible for this kind
- **BlieSMa M74A-6** (`m74a-6`), set 3: Intermodulation 500 + 4250 Hz, 1:1, 2.83 V per tone — no self-check possible for this kind
- **BlieSMa M74A-6** (`m74a-6`), set 4: Axial frequency response @ 1.41 V — check 1.41 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 90.1, expected 88.9, stated sens 95.0, difference db 1.1; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 5: Axial frequency response @ 2 V — check 2 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 93.0, expected 92.0, stated sens 95.0, difference db 1.0; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 6: Axial frequency response @ 2.83 V — check 2.83 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 96.1, expected 95.0, stated sens 95.0, difference db 1.1; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 7: Axial frequency response @ 4 V — check 4 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 99.0, expected 98.0, stated sens 95.0, difference db 1.0; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 8: Axial frequency response @ 5.6 V — check 5.6 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 102.1, expected 100.9, stated sens 95.0, difference db 1.1; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 9: Axial frequency response @ 8 V — check 8 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 105.0, expected 104.0, stated sens 95.0, difference db 1.0; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 10: HD (orders) vs frequency @ 1.41 V — check on the image: H2 100 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 11: HD (orders) vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 12: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 13: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 14: HD (orders) vs frequency @ 5.6 V — check on the image: H2 99 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 15: HD (orders) vs frequency @ 8 V — check on the image: H2 99 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 16: Voice-coil current HD vs frequency @ 1.41 V — check on the image: H2 100 %, H3 100 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 17: Voice-coil current HD vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 18: Voice-coil current HD vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 19: Impedance (chart to 50 ohm) — check impedance minimum against Re, read 5.98, stated 5.6; check impedance peak against Fs, read hz 391.2, read ohm 45.26, stated fs 400.0; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 20: Off-axis response — check on the image: 0° 97 %, 15° 98 %, 30° 99 %, 45° 99 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 21: Off-axis response (relative to on axis, chart range 10-50 dB) — check on the image: 0° 96 %, 15° 96 %, 30° 97 %, 45° 100 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa M74A-6** (`m74a-6`), set 22: Off-axis response (relative to on axis, chart range 5-30 dB) — check on the image: 0° 98 %, 15° 96 %, 30° 96 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
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
- **BlieSMa T25A-6** (`t25a-6`), set 14: Off-axis response — check on the image: 0° 94 %, 15° 96 %, 30° 99 %, 45° 99 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25A-6** (`t25a-6`), set 15: Off-axis response (relative to on axis, chart range 10-50 dB) — check on the image: 0° 94 %, 15° 97 %, 30° 97 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25A-6** (`t25a-6`), set 16: Off-axis response (relative to on axis, chart range 5-30 dB) — check on the image: 0° 93 %, 15° 98 %, 30° 98 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
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
- **BlieSMa T25T-6** (`t25t-6`), set 15: Off-axis response — check on the image: 0° 98 %, 15° 97 %, 30° 97 %, 45° 100 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25T-6** (`t25t-6`), set 16: Off-axis response (relative to on axis, chart range 10-50 dB) — check on the image: 0° 98 %, 15° 97 %, 30° 95 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T25T-6** (`t25t-6`), set 17: Off-axis response (relative to on axis, chart range 5-30 dB) — check on the image: 0° 96 %, 15° 98 %, 30° 97 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 0: Axial frequency response @ 1.41 V — check 1.41 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 85.6, expected 89.9, stated sens 96.0, difference db -4.3; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 1: Axial frequency response @ 2.83 V — check 2.83 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 91.7, expected 96.0, stated sens 96.0, difference db -4.3; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 2: Axial frequency response @ 4 V — check 4 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 94.7, expected 99.0, stated sens 96.0, difference db -4.3; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 3: Axial frequency response @ 5.6 V — check 5.6 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 97.7, expected 101.9, stated sens 96.0, difference db -4.2; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 4: Axial frequency response @ 8 V — check 8 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 100.6, expected 105.0, stated sens 96.0, difference db -4.5; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 5: Axial frequency response @ 11.2 V — check 11.2 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 103.1, expected 107.9, stated sens 96.0, difference db -4.8; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 6: Axial frequency response @ 1.41 V (no smoothing) — check 1.41 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 85.6, expected 89.9, stated sens 96.0, difference db -4.3; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 7: HD (orders) vs frequency @ 1.41 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 8: HD (orders) vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 9: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 10: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 11: HD (orders) vs frequency @ 5.6 V — check on the image: H2 100 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 12: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 13: Impedance (chart to 7 ohm) — check impedance minimum against Re, read 3.69, stated 3.3; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 14: Impedance (chart to 20 ohm) — check impedance minimum against Re, read 3.73, stated 3.3; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 15: Off-axis response — check on the image: 0° 94 %, 15° 95 %, 30° 98 %, 45° 99 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 16: Off-axis response (relative to on axis, chart range 10-50 dB) — check on the image: 0° 95 %, 15° 98 %, 30° 95 %, 45° 100 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34A-4** (`t34a-4`), set 17: Off-axis response (relative to on axis, chart range 10-25 dB) — check on the image: 0° 93 %, 15° 96 %, 30° 96 %, 45° 100 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
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
- **BlieSMa T34B-4** (`t34b-4`), set 10: HD (orders) vs frequency @ 5.6 V — check on the image: H2 100 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34B-4** (`t34b-4`), set 11: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34B-4** (`t34b-4`), set 12: Impedance (chart to 5 ohm) — check impedance minimum against Re, read 3.6, stated 3.3; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34B-4** (`t34b-4`), set 13: Impedance (chart to 20 ohm) — check impedance minimum against Re, read 3.63, stated 3.3; check impedance peak against Fs, read hz 760.13, read ohm 16.94, stated fs 790.0; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34B-4** (`t34b-4`), set 14: Off-axis response — check on the image: 0° 96 %, 15° 98 %, 30° 96 %, 45° 100 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34B-4** (`t34b-4`), set 15: Off-axis response (relative to on axis, chart range 10-50 dB) — check on the image: 0° 94 %, 15° 95 %, 30° 96 %, 45° 98 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **BlieSMa T34B-4** (`t34b-4`), set 16: Off-axis response (relative to on axis, chart range 10-25 dB) — check on the image: 0° 94 %, 15° 95 %, 30° 98 %, 45° 99 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 0: Intermodulation 30 + 255 Hz, 4:1, low tone 1 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 1: Intermodulation 30 + 255 Hz, 4:1, low tone 1.5 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 2: Intermodulation 30 + 255 Hz, 4:1, low tone 2 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 3: Intermodulation 30 + 255 Hz, 4:1, low tone 3 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 4: Intermodulation 30 + 255 Hz, 4:1, low tone 4 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 5: Intermodulation 125 + 1063 Hz, 1:1, 2 V per tone — no self-check possible for this kind
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 6: Intermodulation 125 + 1063 Hz, 1:1, 2.83 V per tone — no self-check possible for this kind
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 7: Intermodulation 125 + 1063 Hz, 1:1, 4 V per tone — no self-check possible for this kind
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 8: Intermodulation 125 + 1063 Hz, 1:1, 5.6 V per tone — no self-check possible for this kind
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 9: Intermodulation 125 + 1063 Hz, 1:1, 8 V per tone — no self-check possible for this kind
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 10: Axial frequency response @ 2.83 V — check 2.83 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 90.2, expected 89.0, stated sens 89.0, difference db 1.2; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 11: Axial frequency response @ 4 V — check 4 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 93.2, expected 92.0, stated sens 89.0, difference db 1.2; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 12: Axial frequency response @ 5.6 V — check 5.6 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 96.2, expected 94.9, stated sens 89.0, difference db 1.3; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 13: Axial frequency response @ 8 V — check 8 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 99.2, expected 98.0, stated sens 89.0, difference db 1.2; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 14: Axial frequency response @ 11.2 V — check 11.2 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 102.2, expected 100.9, stated sens 89.0, difference db 1.3; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 15: Axial frequency response @ 16 V — check 16 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 105.2, expected 104.0, stated sens 89.0, difference db 1.2; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 16: Near-field frequency response @ 1 V (near field 5 mm) — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 17: HD (orders) vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 18: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 19: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 20: HD (orders) vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 21: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 22: HD (orders) vs frequency @ 11.2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 23: HD (orders) vs frequency @ 16 V — check on the image: H2 99 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 24: Voice-coil current HD vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 25: Voice-coil current HD vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 26: Voice-coil current HD vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 27: Impedance (chart to 150 ohm) — check impedance minimum against Re, read 6.66, stated 6.2; check impedance peak against Fs, read hz 35.02, read ohm 107.47, stated fs 35.0; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 28: Off-axis response — check on the image: 0° 98 %, 15° 99 %, 30° 97 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 29: Off-axis response (relative to on axis, chart range 10-50 dB) — check on the image: 0° 98 %, 15° 95 %, 30° 98 %, 45° 97 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MR16TX-8** (`sb-satori-mr16tx-8`), set 30: Off-axis response (relative to on axis, chart range 5-30 dB) — check on the image: 0° 99 %, 15° 96 %, 30° 96 %, 45° 100 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 0: Harmonics of one tone, 20 Hz at 2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 1: Harmonics of one tone, 30 Hz at 2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 2: Harmonics of one tone, 40 Hz at 2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 3: Harmonics of one tone, 50 Hz at 2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 4: Harmonics of one tone, 75 Hz at 2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 5: Harmonics of one tone, 100 Hz at 2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 6: Harmonics of one tone, 150 Hz at 2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 7: Harmonics of one tone, 220 Hz at 2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 8: Harmonics of one tone, 300 Hz at 2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 9: Harmonics of one tone, 20 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 10: Harmonics of one tone, 30 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 11: Harmonics of one tone, 40 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 12: Harmonics of one tone, 50 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 13: Harmonics of one tone, 75 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 14: Harmonics of one tone, 100 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 15: Harmonics of one tone, 150 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 16: Harmonics of one tone, 220 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 17: Harmonics of one tone, 300 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 18: Harmonics of one tone, 20 Hz at 4 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 19: Harmonics of one tone, 30 Hz at 4 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 20: Harmonics of one tone, 40 Hz at 4 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 21: Harmonics of one tone, 50 Hz at 4 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 22: Harmonics of one tone, 75 Hz at 4 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 23: Harmonics of one tone, 100 Hz at 4 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 24: Harmonics of one tone, 150 Hz at 4 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 25: Harmonics of one tone, 220 Hz at 4 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 26: Harmonics of one tone, 300 Hz at 4 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 27: Harmonics of one tone, 20 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 28: Harmonics of one tone, 30 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 29: Harmonics of one tone, 40 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 30: Harmonics of one tone, 50 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 31: Harmonics of one tone, 75 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 32: Harmonics of one tone, 100 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 33: Harmonics of one tone, 150 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 34: Harmonics of one tone, 220 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 35: Harmonics of one tone, 300 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 36: Intermodulation 30 + 255 Hz, 4:1, low tone 3 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 37: Intermodulation 30 + 255 Hz, 4:1, low tone 6 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 38: Intermodulation 30 + 255 Hz, 4:1, low tone 9 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 39: Axial frequency response @ 2 V — check 2 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 89.9, expected 90.0, stated sens 93.0, difference db -0.0; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 40: Axial frequency response @ 2.83 V — check 2.83 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 92.9, expected 93.0, stated sens 93.0, difference db -0.1; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 41: Axial frequency response @ 4 V — check 4 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 95.9, expected 96.0, stated sens 93.0, difference db -0.1; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 42: Axial frequency response @ 5.6 V — check 5.6 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 98.9, expected 98.9, stated sens 93.0, difference db 0.0; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 43: Axial frequency response @ 8 V — check 8 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 101.9, expected 102.0, stated sens 93.0, difference db -0.1; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 44: Axial frequency response @ 11.2 V — check 11.2 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 104.9, expected 104.9, stated sens 93.0, difference db -0.1; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 45: Near-field frequency response @ 2.83 V (near field 20 mm) — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 46: HD (orders) vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 47: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 48: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 49: HD (orders) vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 50: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 51: HD (orders) vs frequency @ 11.2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 52: HD (orders) vs frequency @ 2 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 53: HD (orders) vs frequency @ 2.83 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 54: HD (orders) vs frequency @ 4 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 55: HD (orders) vs frequency @ 5.6 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 56: HD (orders) vs frequency @ 8 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 57: Voice-coil current HD vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 58: Voice-coil current HD vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 59: Voice-coil current HD vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 60: Voice-coil current HD vs frequency @ 5.6 V — check on the image: H2 99 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 61: Voice-coil current HD vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 62: Impedance (chart to 70 ohm) — check impedance minimum against Re, read 4.0, stated 3.4; check impedance peak against Fs, read hz 32.12, read ohm 59.32, stated fs 32.0; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 63: Impedance (chart to 7 ohm) — check impedance minimum against Re, read 3.93, stated 3.4; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 64: Off-axis response — check on the image: 0° 96 %, 15° 97 %, 30° 97 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 65: Off-axis response (relative to on axis, chart range 10-50 dB) — check on the image: 0° 99 %, 15° 98 %, 30° 97 %, 45° 97 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori MW19TX-4** (`sb-satori-mw19tx-4`), set 66: Off-axis response (relative to on axis, chart range 5-30 dB) — check on the image: 0° 98 %, 15° 97 %, 30° 98 %, 45° 94 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 0: Intermodulation 1000 + 10000 Hz, 1:1, 2.83 V per tone — no self-check possible for this kind
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 1: Intermodulation 2000 + 10000 Hz, 1:1, 2.83 V per tone — no self-check possible for this kind
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 2: Intermodulation 800 + 10000 Hz, 1:1, 2.83 V per tone — no self-check possible for this kind
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 3: Axial frequency response @ 1.41 V — check 1.41 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 90.5, expected 90.9, stated sens 97.0, difference db -0.4; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 4: Axial frequency response @ 2 V — check 2 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 93.5, expected 94.0, stated sens 97.0, difference db -0.5; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 5: Axial frequency response @ 2.83 V — check 2.83 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 96.5, expected 97.0, stated sens 97.0, difference db -0.5; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 6: Axial frequency response @ 4 V — check 4 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 99.5, expected 100.0, stated sens 97.0, difference db -0.5; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 7: Axial frequency response @ 5.6 V — check 5.6 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 102.5, expected 102.9, stated sens 97.0, difference db -0.5; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 8: Axial frequency response @ 8 V — check 8 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 105.5, expected 106.0, stated sens 97.0, difference db -0.5; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 9: Axial frequency response @ 11.2 V — check 11.2 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 108.5, expected 108.9, stated sens 97.0, difference db -0.4; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 10: HD (orders) vs frequency @ 1.41 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 11: HD (orders) vs frequency @ 2 V — check on the image: H2 100 %, H3 99 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 12: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 13: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 14: HD (orders) vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 15: HD (orders) vs frequency @ 8 V — check on the image: H2 99 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 16: HD (orders) vs frequency @ 11.2 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 17: Voice-coil current HD vs frequency @ 1.41 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 18: Voice-coil current HD vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 19: Voice-coil current HD vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 20: Voice-coil current HD vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 21: Voice-coil current HD vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 22: Impedance (chart to 5 ohm) — check impedance minimum against Re, read 3.03, stated 3.0; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 23: Off-axis response — check on the image: 0° 98 %, 15° 99 %, 30° 99 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 24: Off-axis response (relative to on axis, chart range 10-50 dB) — check on the image: 0° 100 %, 15° 99 %, 30° 97 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29BNWG-4** (`sb-satori-tw29bnwg-4`), set 25: Off-axis response (relative to on axis, chart range 5-30 dB) — check on the image: 0° 99 %, 15° 99 %, 30° 96 %, 45° 100 %, 60° 98 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 0: Intermodulation 1000 + 10000 Hz, 1:1, 2.83 V per tone — no self-check possible for this kind
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 1: Intermodulation 19000 + 20000 Hz, 1:1, 2.83 V per tone — no self-check possible for this kind
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 2: Axial frequency response @ 1.41 V — check 1.41 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 87.7, expected 89.9, stated sens 96.0, difference db -2.3; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 3: Axial frequency response @ 2 V — check 2 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 90.6, expected 93.0, stated sens 96.0, difference db -2.4; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 4: Axial frequency response @ 2.83 V — check 2.83 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 93.6, expected 96.0, stated sens 96.0, difference db -2.4; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 5: Axial frequency response @ 4 V — check 4 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 96.6, expected 99.0, stated sens 96.0, difference db -2.4; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 6: Axial frequency response @ 5.6 V — check 5.6 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 99.6, expected 101.9, stated sens 96.0, difference db -2.3; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 7: Axial frequency response @ 8 V — check 8 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 102.6, expected 105.0, stated sens 96.0, difference db -2.4; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 8: HD (orders) vs frequency @ 1.41 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 9: HD (orders) vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 10: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 11: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 99 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 12: HD (orders) vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 13: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 14: Voice-coil current HD vs frequency @ 1.41 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 15: Voice-coil current HD vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 16: Voice-coil current HD vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 17: Voice-coil current HD vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 18: Voice-coil current HD vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 98 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 19: Impedance (chart to 15 ohm) — check impedance minimum against Re, read 3.04, stated 3.0; check impedance peak against Fs, read hz 620.99, read ohm 10.31, stated fs 600.0; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 20: Impedance (chart to 5 ohm) — check impedance minimum against Re, read 3.04, stated 3.0; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 21: Off-axis response — check on the image: 0° 97 %, 15° 99 %, 30° 100 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 22: Off-axis response (relative to on axis, chart range 10-50 dB) — check on the image: 0° 98 %, 15° 99 %, 30° 99 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori TW29TXN-B** (`sb-satori-tw29txn-b`), set 23: Off-axis response (relative to on axis, chart range 5-30 dB) — check on the image: 0° 97 %, 15° 99 %, 30° 98 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **Wavecor TW030WA11** (`wavecor-tw030wa11`), set 0: Axial frequency response @ 2 V — check 2 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 89.3, expected 90.5, stated sens 93.5, difference db -1.2; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Wavecor TW030WA11** (`wavecor-tw030wa11`), set 1: Axial frequency response @ 2.83 V — check 2.83 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 92.3, expected 93.5, stated sens 93.5, difference db -1.2; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Wavecor TW030WA11** (`wavecor-tw030wa11`), set 2: Axial frequency response @ 4 V — check 4 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 95.3, expected 96.5, stated sens 93.5, difference db -1.3; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Wavecor TW030WA11** (`wavecor-tw030wa11`), set 3: Axial frequency response @ 5.6 V — check 5.6 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 98.3, expected 99.4, stated sens 93.5, difference db -1.2; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Wavecor TW030WA11** (`wavecor-tw030wa11`), set 4: Axial frequency response @ 8 V — check 8 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 101.3, expected 102.5, stated sens 93.5, difference db -1.3; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **Wavecor TW030WA11** (`wavecor-tw030wa11`), set 5: HD (orders) vs frequency @ 2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Wavecor TW030WA11** (`wavecor-tw030wa11`), set 6: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Wavecor TW030WA11** (`wavecor-tw030wa11`), set 7: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Wavecor TW030WA11** (`wavecor-tw030wa11`), set 8: HD (orders) vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **Wavecor TW030WA11** (`wavecor-tw030wa11`), set 9: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **Wavecor TW030WA11** (`wavecor-tw030wa11`), set 10: Impedance (chart to 5 ohm) — check impedance minimum against Re, read 3.51, stated 3.5; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **Wavecor TW030WA11** (`wavecor-tw030wa11`), set 11: Off-axis response — check on the image: 0° 98 %, 15° 100 %, 30° 98 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **Wavecor TW030WA11** (`wavecor-tw030wa11`), set 12: Off-axis response (relative to on axis, chart range 10-50 dB) — check on the image: 0° 98 %, 15° 98 %, 30° 97 %, 45° 100 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **Wavecor TW030WA11** (`wavecor-tw030wa11`), set 13: Off-axis response (relative to on axis, chart range 10-25 dB) — check on the image: 0° 100 %, 15° 97 %, 30° 96 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 0: Harmonics of one tone, 20 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 1: Harmonics of one tone, 30 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 2: Harmonics of one tone, 40 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 3: Harmonics of one tone, 50 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 4: Harmonics of one tone, 75 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 5: Harmonics of one tone, 100 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 6: Harmonics of one tone, 150 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 7: Harmonics of one tone, 220 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 8: Harmonics of one tone, 300 Hz at 2.83 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 9: Harmonics of one tone, 20 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 10: Harmonics of one tone, 30 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 11: Harmonics of one tone, 40 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 12: Harmonics of one tone, 50 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 13: Harmonics of one tone, 75 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 14: Harmonics of one tone, 100 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 15: Harmonics of one tone, 150 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 16: Harmonics of one tone, 220 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 17: Harmonics of one tone, 300 Hz at 5.6 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 18: Harmonics of one tone, 20 Hz at 11.2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 19: Harmonics of one tone, 30 Hz at 11.2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 20: Harmonics of one tone, 40 Hz at 11.2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 21: Harmonics of one tone, 50 Hz at 11.2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 22: Harmonics of one tone, 75 Hz at 11.2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 23: Harmonics of one tone, 100 Hz at 11.2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 24: Harmonics of one tone, 150 Hz at 11.2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 25: Harmonics of one tone, 220 Hz at 11.2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 26: Harmonics of one tone, 300 Hz at 11.2 V (microphone at 20 mm) — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 27: Intermodulation 30 + 255 Hz, 4:1, low tone 2 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 28: Intermodulation 30 + 255 Hz, 4:1, low tone 3 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 29: Intermodulation 30 + 255 Hz, 4:1, low tone 4.5 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 30: Intermodulation 30 + 255 Hz, 4:1, low tone 6 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 31: Intermodulation 30 + 255 Hz, 4:1, low tone 8 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 32: Intermodulation 30 + 255 Hz, 4:1, low tone 9 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 33: Intermodulation 50 + 425 Hz, 4:1, low tone 2 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 34: Intermodulation 50 + 425 Hz, 4:1, low tone 3 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 35: Intermodulation 50 + 425 Hz, 4:1, low tone 4.5 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 36: Intermodulation 50 + 425 Hz, 4:1, low tone 6 mm peak excursion — no self-check possible for this kind
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 37: Axial frequency response @ 2.83 V — check 2.83 V response at 1 kHz against the stated sensitivity (2.83 V, scaled by the voltage), read 89.6, expected 88.0, stated sens 88.0, difference db 1.6; check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 38: Axial frequency response @ 4 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 39: Axial frequency response @ 5.6 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 40: Axial frequency response @ 8 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 41: Axial frequency response @ 11.2 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 42: Axial frequency response @ 16 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 43: Axial frequency response @ 22 V — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 44: Near-field frequency response @ 1 V (near field 3 mm) — check on the image: SPL 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 45: HD (orders) vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 46: HD (orders) vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 47: HD (orders) vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 48: HD (orders) vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 49: HD (orders) vs frequency @ 11.2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 50: HD (orders) vs frequency @ 16 V — check on the image: H2 100 %, H3 100 %, H5 99 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 51: HD (orders) vs frequency @ 22 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 52: HD (orders) vs frequency @ 2.83 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 53: HD (orders) vs frequency @ 4 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 54: HD (orders) vs frequency @ 5.6 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 55: HD (orders) vs frequency @ 8 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 56: HD (orders) vs frequency @ 11.2 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 57: HD (orders) vs frequency @ 16 V (near field 20 mm) — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 58: Voice-coil current HD vs frequency @ 2.83 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 59: Voice-coil current HD vs frequency @ 4 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 60: Voice-coil current HD vs frequency @ 5.6 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 61: Voice-coil current HD vs frequency @ 8 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 62: Voice-coil current HD vs frequency @ 11.2 V — check on the image: H2 100 %, H3 100 %, H5 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 63: Impedance (chart to 100 ohm) — check impedance minimum against Re, read 6.33, stated 5.8; check impedance peak against Fs, read hz 26.24, read ohm 91.05, stated fs 25.0; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 64: Impedance (chart to 15 ohm) — check impedance minimum against Re, read 6.34, stated 5.8; check on the image: Z 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 65: Off-axis response — check on the image: 0° 95 %, 15° 96 %, 30° 98 %, 45° 100 %, 60° 99 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 66: Off-axis response (relative to on axis, chart range 10-50 dB) — check on the image: 0° 97 %, 15° 97 %, 30° 99 %, 45° 97 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
- **SB Acoustics Satori WO24TX-8** (`sb-satori-wo24tx-8`), set 67: Off-axis response (relative to on axis, chart range 5-30 dB) — check on the image: 0° 96 %, 15° 97 %, 30° 98 %, 45° 100 %, 60° 100 % of the read points lie on the drawn curve (within 2 px)
