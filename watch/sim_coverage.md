# Simulate: where the harmonic data runs out

Written by `tools/sim_coverage.mjs` on 2026-09-26. For each way of a speaker with the default crossovers (2-way 2 kHz; 3-way 350 Hz and 3 kHz; 4-way 120 Hz, 700 Hz and 4 kHz; Linkwitz-Riley 24 dB per octave, summing flat), the band where that way still plays within 40 dB of the others is compared with the frequencies the driver has data for. Where they differ, Simulate draws the speaker's curve dashed there (the other ways alone, the least the speaker can have). A driver is listed only for the ways its role fits (within 0.35 of the way's position; tweeters at the top, woofers at the bottom). Simulate runs from the lowest way's first point to the highest way's last, so nothing is missing below the one or above the other. A HiFiCompass tweeter's H5 ends near 8.6 kHz and its H3 near 14.5 kHz because those harmonics would lie above about 43 kHz, beyond what the measurement records.

## Manufacturer datasheet

| Driver | Data (every order) | Speaker and way | Band it plays in | Covered | Missing |
|---|---|---|---|---|---|
| Purifi PTT1.3T04-HAG-01 | 362 Hz–18.4 kHz · H2 H3 | 2-way, way 2 (high) | 640 Hz–18.4 kHz | 100 % | — |
| Purifi PTT1.3T04-HAG-01 | 362 Hz–18.4 kHz · H2 H3 | 3-way, way 3 (high) | 959 Hz–18.4 kHz | 100 % | — |
| Purifi PTT1.3T04-HAG-01 | 362 Hz–18.4 kHz · H2 H3 | 4-way, way 3 (high mid) | 226 Hz–12.2 kHz | 87 % | H2 H3 226 Hz–359 Hz |
| Purifi PTT1.3T04-HAG-01 | 362 Hz–18.4 kHz · H2 H3 | 4-way, way 4 (high) | 1.36 kHz–18.4 kHz | 100 % | — |
| Purifi PTT1.3T04-HAG-10 | 362 Hz–18.4 kHz · H2 H3 | 2-way, way 2 (high) | 640 Hz–18.4 kHz | 100 % | — |
| Purifi PTT1.3T04-HAG-10 | 362 Hz–18.4 kHz · H2 H3 | 3-way, way 3 (high) | 959 Hz–18.4 kHz | 100 % | — |
| Purifi PTT1.3T04-HAG-10 | 362 Hz–18.4 kHz · H2 H3 | 4-way, way 3 (high mid) | 226 Hz–12.2 kHz | 87 % | H2 H3 226 Hz–359 Hz |
| Purifi PTT1.3T04-HAG-10 | 362 Hz–18.4 kHz · H2 H3 | 4-way, way 4 (high) | 1.36 kHz–18.4 kHz | 100 % | — |
| Purifi PTT5.25X04-NAA-05 | 23 Hz–16.4 kHz · H2 H3 | 3-way, way 2 (mid) | 113 Hz–9.12 kHz | 97 % | H3 8.61 kHz–9.12 kHz |
| Purifi PTT5.25X04-NAA-05 | 23 Hz–16.4 kHz · H2 H3 | 4-way, way 2 (low mid) | 40 Hz–2.15 kHz | 100 % | — |
| Purifi PTT5.25X04-NAA-05 | 23 Hz–16.4 kHz · H2 H3 | 4-way, way 3 (high mid) | 226 Hz–12.2 kHz | 90 % | H3 8.61 kHz–12.2 kHz |
| Purifi PTT6.5M08-NAA-08 | 600 Hz–3 kHz · H2 H3 | 3-way, way 2 (mid) | 113 Hz–9.12 kHz | 36 % | H2 H3 113 Hz–570 Hz; H2 H3 3.04 kHz–9.12 kHz |
| Purifi PTT6.5M08-NAA-08 | 600 Hz–3 kHz · H2 H3 | 4-way, way 2 (low mid) | 40 Hz–2.15 kHz | 33 % | H2 H3 40 Hz–570 Hz |
| Purifi PTT6.5M08-NAA-08 | 600 Hz–3 kHz · H2 H3 | 4-way, way 3 (high mid) | 226 Hz–12.2 kHz | 40 % | H2 H3 226 Hz–570 Hz; H2 H3 3.04 kHz–12.2 kHz |
| Purifi PTT6.5X04-NAA-08 | 23 Hz–16.4 kHz · H2 H3 | 3-way, way 2 (mid) | 113 Hz–9.12 kHz | 95 % | H3 7.67 kHz–9.12 kHz |
| Purifi PTT6.5X04-NAA-08 | 23 Hz–16.4 kHz · H2 H3 | 4-way, way 2 (low mid) | 40 Hz–2.15 kHz | 100 % | — |
| Purifi PTT6.5X04-NAA-08 | 23 Hz–16.4 kHz · H2 H3 | 4-way, way 3 (high mid) | 226 Hz–12.2 kHz | 87 % | H3 7.67 kHz–12.2 kHz |
| Purifi PTT8.0X04-NAB-01 | 23 Hz–16.4 kHz · H2 H3 | 2-way, way 1 (low) | 23 Hz–6.09 kHz | 100 % | — |
| Purifi PTT8.0X04-NAB-01 | 23 Hz–16.4 kHz · H2 H3 | 3-way, way 1 (low) | 23 Hz–1.08 kHz | 100 % | — |
| Purifi PTT8.0X04-NAB-01 | 23 Hz–16.4 kHz · H2 H3 | 3-way, way 2 (mid) | 113 Hz–9.12 kHz | 100 % | — |
| Purifi PTT8.0X04-NAB-01 | 23 Hz–16.4 kHz · H2 H3 | 4-way, way 1 (low) | 23 Hz–359 Hz | 100 % | — |
| Purifi PTT8.0X04-NAB-01 | 23 Hz–16.4 kHz · H2 H3 | 4-way, way 2 (low mid) | 40 Hz–2.15 kHz | 100 % | — |

Default choice per speaker (what Simulate picks when it opens):

- 2-way: way 1 Purifi PTT8.0X04-NAB-01; way 2 Purifi PTT1.3T04-HAG-01
- 3-way: way 1 Purifi PTT8.0X04-NAB-01; way 2 Purifi PTT5.25X04-NAA-05 (no data: H3 8.61 kHz–9.12 kHz); way 3 Purifi PTT1.3T04-HAG-01
- 4-way: way 1 Purifi PTT8.0X04-NAB-01; way 2 Purifi PTT6.5X04-NAA-08; way 3 Purifi PTT5.25X04-NAA-05 (no data: H3 8.61 kHz–12.2 kHz); way 4 Purifi PTT1.3T04-HAG-01

## HiFiCompass

| Driver | Data (every order) | Speaker and way | Band it plays in | Covered | Missing |
|---|---|---|---|---|---|
| BlieSMa M74A-6 | 100 Hz–20.2 kHz · H2 H3 H5 | 3-way, way 2 (mid) | 113 Hz–9.12 kHz | 97 % | H5 8.61 kHz–9.12 kHz |
| BlieSMa M74A-6 | 100 Hz–20.2 kHz · H2 H3 H5 | 4-way, way 2 (low mid) | 40 Hz–2.15 kHz | 77 % | H2 H3 H5 40 Hz–95 Hz |
| BlieSMa M74A-6 | 100 Hz–20.2 kHz · H2 H3 H5 | 4-way, way 3 (high mid) | 226 Hz–12.2 kHz | 90 % | H5 8.61 kHz–12.2 kHz |
| BlieSMa M74T-6 | 308 Hz–5.54 kHz · H2 H3 H4 H5 | 3-way, way 2 (mid) | 113 Hz–9.12 kHz | 65 % | H2 H3 H4 H5 113 Hz–302 Hz; H2 H3 H4 H5 5.75 kHz–9.12 kHz |
| BlieSMa M74T-6 | 308 Hz–5.54 kHz · H2 H3 H4 H5 | 4-way, way 2 (low mid) | 40 Hz–2.15 kHz | 49 % | H2 H3 H4 H5 40 Hz–302 Hz |
| BlieSMa M74T-6 | 308 Hz–5.54 kHz · H2 H3 H4 H5 | 4-way, way 3 (high mid) | 226 Hz–12.2 kHz | 71 % | H2 H3 H4 H5 226 Hz–302 Hz; H2 H3 H4 H5 5.75 kHz–12.2 kHz |
| BlieSMa T25A-6 | 100 Hz–21.6 kHz · H2 H3 H5 | 2-way, way 2 (high) | 640 Hz–19.3 kHz | 75 % | H3 14.5 kHz–19.3 kHz; H5 8.61 kHz–19.3 kHz |
| BlieSMa T25A-6 | 100 Hz–21.6 kHz · H2 H3 H5 | 3-way, way 3 (high) | 959 Hz–19.3 kHz | 72 % | H3 14.5 kHz–19.3 kHz; H5 8.61 kHz–19.3 kHz |
| BlieSMa T25A-6 | 100 Hz–21.6 kHz · H2 H3 H5 | 4-way, way 3 (high mid) | 226 Hz–12.2 kHz | 90 % | H5 8.61 kHz–12.2 kHz |
| BlieSMa T25A-6 | 100 Hz–21.6 kHz · H2 H3 H5 | 4-way, way 4 (high) | 1.36 kHz–19.3 kHz | 68 % | H3 14.5 kHz–19.3 kHz; H5 8.61 kHz–19.3 kHz |
| BlieSMa T25T-6 | 100 Hz–21.6 kHz · H2 H3 H5 | 2-way, way 2 (high) | 640 Hz–19.3 kHz | 75 % | H3 14.5 kHz–19.3 kHz; H5 8.61 kHz–19.3 kHz |
| BlieSMa T25T-6 | 100 Hz–21.6 kHz · H2 H3 H5 | 3-way, way 3 (high) | 959 Hz–19.3 kHz | 72 % | H3 14.5 kHz–19.3 kHz; H5 8.61 kHz–19.3 kHz |
| BlieSMa T25T-6 | 100 Hz–21.6 kHz · H2 H3 H5 | 4-way, way 3 (high mid) | 226 Hz–12.2 kHz | 90 % | H5 8.61 kHz–12.2 kHz |
| BlieSMa T25T-6 | 100 Hz–21.6 kHz · H2 H3 H5 | 4-way, way 4 (high) | 1.36 kHz–19.3 kHz | 68 % | H3 14.5 kHz–19.3 kHz; H5 8.61 kHz–19.3 kHz |
| BlieSMa T34A-4 | 100 Hz–21.6 kHz · H2 H3 H5 | 2-way, way 2 (high) | 640 Hz–19.3 kHz | 77 % | H3 14.5 kHz–19.3 kHz; H5 9.12 kHz–19.3 kHz |
| BlieSMa T34A-4 | 100 Hz–21.6 kHz · H2 H3 H5 | 3-way, way 3 (high) | 959 Hz–19.3 kHz | 74 % | H3 14.5 kHz–19.3 kHz; H5 9.12 kHz–19.3 kHz |
| BlieSMa T34A-4 | 100 Hz–21.6 kHz · H2 H3 H5 | 4-way, way 3 (high mid) | 226 Hz–12.2 kHz | 91 % | H5 9.12 kHz–12.2 kHz |
| BlieSMa T34A-4 | 100 Hz–21.6 kHz · H2 H3 H5 | 4-way, way 4 (high) | 1.36 kHz–19.3 kHz | 70 % | H3 14.5 kHz–19.3 kHz; H5 9.12 kHz–19.3 kHz |
| BlieSMa T34B-4 | 100 Hz–21.6 kHz · H2 H3 H5 | 2-way, way 2 (high) | 640 Hz–19.3 kHz | 77 % | H3 14.5 kHz–19.3 kHz; H5 9.12 kHz–19.3 kHz |
| BlieSMa T34B-4 | 100 Hz–21.6 kHz · H2 H3 H5 | 3-way, way 3 (high) | 959 Hz–19.3 kHz | 74 % | H3 14.5 kHz–19.3 kHz; H5 9.12 kHz–19.3 kHz |
| BlieSMa T34B-4 | 100 Hz–21.6 kHz · H2 H3 H5 | 4-way, way 3 (high mid) | 226 Hz–12.2 kHz | 91 % | H5 9.12 kHz–12.2 kHz |
| BlieSMa T34B-4 | 100 Hz–21.6 kHz · H2 H3 H5 | 4-way, way 4 (high) | 1.36 kHz–19.3 kHz | 70 % | H3 14.5 kHz–19.3 kHz; H5 9.12 kHz–19.3 kHz |
| Purifi PTT10.0X04-NAB-02 | 20 Hz–500 Hz · H2 H3 H4 H5 | 2-way, way 1 (low) | 20 Hz–6.09 kHz | 56 % | H2 H3 H4 H5 508 Hz–6.09 kHz |
| Purifi PTT10.0X04-NAB-02 | 20 Hz–500 Hz · H2 H3 H4 H5 | 3-way, way 1 (low) | 20 Hz–1.08 kHz | 80 % | H2 H3 H4 H5 508 Hz–1.08 kHz |
| Purifi PTT10.0X04-NAB-02 | 20 Hz–500 Hz · H2 H3 H4 H5 | 4-way, way 1 (low) | 20 Hz–359 Hz | 100 % | — |
| Purifi PTT10.0X04-NAB-02 | 20 Hz–500 Hz · H2 H3 H4 H5 | 4-way, way 2 (low mid) | 40 Hz–2.15 kHz | 63 % | H2 H3 H4 H5 508 Hz–2.15 kHz |
| Purifi PTT5.25X04-NAA-05 | 81 Hz–5.48 kHz · H2 H3 H4 H5 | 3-way, way 2 (mid) | 113 Hz–9.12 kHz | 88 % | H2 H3 H4 H5 5.75 kHz–9.12 kHz |
| Purifi PTT5.25X04-NAA-05 | 81 Hz–5.48 kHz · H2 H3 H4 H5 | 4-way, way 2 (low mid) | 40 Hz–2.15 kHz | 81 % | H2 H3 H4 H5 40 Hz–80 Hz |
| Purifi PTT5.25X04-NAA-05 | 81 Hz–5.48 kHz · H2 H3 H4 H5 | 4-way, way 3 (high mid) | 226 Hz–12.2 kHz | 80 % | H2 H3 H4 H5 5.75 kHz–12.2 kHz |
| Purifi PTT6.5X04-NAA-08A | 81 Hz–5.48 kHz · H2 H3 H4 H5 | 3-way, way 2 (mid) | 113 Hz–9.12 kHz | 88 % | H2 H3 H4 H5 5.75 kHz–9.12 kHz |
| Purifi PTT6.5X04-NAA-08A | 81 Hz–5.48 kHz · H2 H3 H4 H5 | 4-way, way 2 (low mid) | 40 Hz–2.15 kHz | 81 % | H2 H3 H4 H5 40 Hz–80 Hz |
| Purifi PTT6.5X04-NAA-08A | 81 Hz–5.48 kHz · H2 H3 H4 H5 | 4-way, way 3 (high mid) | 226 Hz–12.2 kHz | 80 % | H2 H3 H4 H5 5.75 kHz–12.2 kHz |
| Purifi PTT8.0X04-NAB-02 | 20 Hz–5.48 kHz · H2 H3 H4 H5 | 2-way, way 1 (low) | 20 Hz–6.09 kHz | 98 % | H2 H3 H4 H5 5.75 kHz–6.09 kHz |
| Purifi PTT8.0X04-NAB-02 | 20 Hz–5.48 kHz · H2 H3 H4 H5 | 3-way, way 1 (low) | 20 Hz–1.08 kHz | 100 % | — |
| Purifi PTT8.0X04-NAB-02 | 20 Hz–5.48 kHz · H2 H3 H4 H5 | 3-way, way 2 (mid) | 113 Hz–9.12 kHz | 88 % | H2 H3 H4 H5 5.75 kHz–9.12 kHz |
| Purifi PTT8.0X04-NAB-02 | 20 Hz–5.48 kHz · H2 H3 H4 H5 | 4-way, way 1 (low) | 20 Hz–359 Hz | 100 % | — |
| Purifi PTT8.0X04-NAB-02 | 20 Hz–5.48 kHz · H2 H3 H4 H5 | 4-way, way 2 (low mid) | 40 Hz–2.15 kHz | 100 % | — |
| SB Acoustics Satori MR16TX-8 | 20 Hz–21.5 kHz · H2 H3 H5 | 3-way, way 2 (mid) | 113 Hz–9.12 kHz | 97 % | H5 8.61 kHz–9.12 kHz |
| SB Acoustics Satori MR16TX-8 | 20 Hz–21.5 kHz · H2 H3 H5 | 4-way, way 2 (low mid) | 40 Hz–2.15 kHz | 100 % | — |
| SB Acoustics Satori MR16TX-8 | 20 Hz–21.5 kHz · H2 H3 H5 | 4-way, way 3 (high mid) | 226 Hz–12.2 kHz | 90 % | H5 8.61 kHz–12.2 kHz |
| SB Acoustics Satori MW19TX-4 | 20 Hz–21.5 kHz · H2 H3 H5 | 2-way, way 1 (low) | 20 Hz–6.09 kHz | 100 % | — |
| SB Acoustics Satori MW19TX-4 | 20 Hz–21.5 kHz · H2 H3 H5 | 3-way, way 1 (low) | 20 Hz–1.08 kHz | 100 % | — |
| SB Acoustics Satori MW19TX-4 | 20 Hz–21.5 kHz · H2 H3 H5 | 3-way, way 2 (mid) | 113 Hz–9.12 kHz | 97 % | H5 8.61 kHz–9.12 kHz |
| SB Acoustics Satori MW19TX-4 | 20 Hz–21.5 kHz · H2 H3 H5 | 4-way, way 1 (low) | 20 Hz–359 Hz | 100 % | — |
| SB Acoustics Satori MW19TX-4 | 20 Hz–21.5 kHz · H2 H3 H5 | 4-way, way 2 (low mid) | 40 Hz–2.15 kHz | 100 % | — |
| SB Acoustics Satori TW29BNWG-4 | 100 Hz–21.6 kHz · H2 H3 H5 | 2-way, way 2 (high) | 640 Hz–19.3 kHz | 75 % | H3 14.5 kHz–19.3 kHz; H5 8.61 kHz–19.3 kHz |
| SB Acoustics Satori TW29BNWG-4 | 100 Hz–21.6 kHz · H2 H3 H5 | 3-way, way 3 (high) | 959 Hz–19.3 kHz | 72 % | H3 14.5 kHz–19.3 kHz; H5 8.61 kHz–19.3 kHz |
| SB Acoustics Satori TW29BNWG-4 | 100 Hz–21.6 kHz · H2 H3 H5 | 4-way, way 3 (high mid) | 226 Hz–12.2 kHz | 90 % | H5 8.61 kHz–12.2 kHz |
| SB Acoustics Satori TW29BNWG-4 | 100 Hz–21.6 kHz · H2 H3 H5 | 4-way, way 4 (high) | 1.36 kHz–19.3 kHz | 68 % | H3 14.5 kHz–19.3 kHz; H5 8.61 kHz–19.3 kHz |
| SB Acoustics Satori TW29TXN-B | 100 Hz–21.6 kHz · H2 H3 H5 | 2-way, way 2 (high) | 640 Hz–19.3 kHz | 75 % | H3 14.5 kHz–19.3 kHz; H5 8.61 kHz–19.3 kHz |
| SB Acoustics Satori TW29TXN-B | 100 Hz–21.6 kHz · H2 H3 H5 | 3-way, way 3 (high) | 959 Hz–19.3 kHz | 72 % | H3 14.5 kHz–19.3 kHz; H5 8.61 kHz–19.3 kHz |
| SB Acoustics Satori TW29TXN-B | 100 Hz–21.6 kHz · H2 H3 H5 | 4-way, way 3 (high mid) | 226 Hz–12.2 kHz | 90 % | H5 8.61 kHz–12.2 kHz |
| SB Acoustics Satori TW29TXN-B | 100 Hz–21.6 kHz · H2 H3 H5 | 4-way, way 4 (high) | 1.36 kHz–19.3 kHz | 68 % | H3 14.5 kHz–19.3 kHz; H5 8.61 kHz–19.3 kHz |
| SB Acoustics Satori WO24P-8 | 20 Hz–500 Hz · H2 H3 H4 H5 | 2-way, way 1 (low) | 20 Hz–6.09 kHz | 56 % | H2 H3 H4 H5 508 Hz–6.09 kHz |
| SB Acoustics Satori WO24P-8 | 20 Hz–500 Hz · H2 H3 H4 H5 | 3-way, way 1 (low) | 20 Hz–1.08 kHz | 80 % | H2 H3 H4 H5 508 Hz–1.08 kHz |
| SB Acoustics Satori WO24P-8 | 20 Hz–500 Hz · H2 H3 H4 H5 | 4-way, way 1 (low) | 20 Hz–359 Hz | 100 % | — |
| SB Acoustics Satori WO24P-8 | 20 Hz–500 Hz · H2 H3 H4 H5 | 4-way, way 2 (low mid) | 40 Hz–2.15 kHz | 63 % | H2 H3 H4 H5 508 Hz–2.15 kHz |
| SB Acoustics SB17NBAC35-8 | 81 Hz–5.48 kHz · H2 H3 H4 H5 | 3-way, way 2 (mid) | 113 Hz–9.12 kHz | 88 % | H2 H3 H4 H5 5.75 kHz–9.12 kHz |
| SB Acoustics SB17NBAC35-8 | 81 Hz–5.48 kHz · H2 H3 H4 H5 | 4-way, way 2 (low mid) | 40 Hz–2.15 kHz | 81 % | H2 H3 H4 H5 40 Hz–80 Hz |
| SB Acoustics SB17NBAC35-8 | 81 Hz–5.48 kHz · H2 H3 H4 H5 | 4-way, way 3 (high mid) | 226 Hz–12.2 kHz | 80 % | H2 H3 H4 H5 5.75 kHz–12.2 kHz |
| SB Acoustics SB34NRXL75-8 (Norex) | 20 Hz–500 Hz · H2 H3 H4 H5 | 2-way, way 1 (low) | 20 Hz–6.09 kHz | 56 % | H2 H3 H4 H5 508 Hz–6.09 kHz |
| SB Acoustics SB34NRXL75-8 (Norex) | 20 Hz–500 Hz · H2 H3 H4 H5 | 3-way, way 1 (low) | 20 Hz–1.08 kHz | 80 % | H2 H3 H4 H5 508 Hz–1.08 kHz |
| SB Acoustics SB34NRXL75-8 (Norex) | 20 Hz–500 Hz · H2 H3 H4 H5 | 4-way, way 1 (low) | 20 Hz–359 Hz | 100 % | — |
| SB Acoustics SB34NRXL75-8 (Norex) | 20 Hz–500 Hz · H2 H3 H4 H5 | 4-way, way 2 (low mid) | 40 Hz–2.15 kHz | 63 % | H2 H3 H4 H5 508 Hz–2.15 kHz |

Default choice per speaker (what Simulate picks when it opens):

- 2-way: way 1 SB Acoustics Satori MW19TX-4; way 2 BlieSMa T34A-4 (no data: H3 14.5 kHz–19.3 kHz, H5 9.12 kHz–19.3 kHz)
- 3-way: way 1 SB Acoustics Satori MW19TX-4; way 2 SB Acoustics Satori MR16TX-8 (no data: H5 8.61 kHz–9.12 kHz); way 3 BlieSMa T34A-4 (no data: H3 14.5 kHz–19.3 kHz, H5 9.12 kHz–19.3 kHz)
- 4-way: way 1 Purifi PTT10.0X04-NAB-02; way 2 SB Acoustics Satori MW19TX-4; way 3 SB Acoustics Satori MR16TX-8 (no data: H5 8.61 kHz–12.2 kHz); way 4 BlieSMa T34A-4 (no data: H3 14.5 kHz–19.3 kHz, H5 9.12 kHz–19.3 kHz)

## Derived (model or calculation)

| Driver | Data (every order) | Speaker and way | Band it plays in | Covered | Missing |
|---|---|---|---|---|---|
| SB Acoustics SB34NRXL75-8 ×2 (coherent pair) | 20 Hz–500 Hz · H2 H3 H4 H5 | 2-way, way 1 (low) | 20 Hz–6.09 kHz | 56 % | H2 H3 H4 H5 508 Hz–6.09 kHz |
| SB Acoustics SB34NRXL75-8 ×2 (coherent pair) | 20 Hz–500 Hz · H2 H3 H4 H5 | 3-way, way 1 (low) | 20 Hz–1.08 kHz | 80 % | H2 H3 H4 H5 508 Hz–1.08 kHz |
| SB Acoustics SB34NRXL75-8 ×2 (coherent pair) | 20 Hz–500 Hz · H2 H3 H4 H5 | 4-way, way 1 (low) | 20 Hz–359 Hz | 100 % | — |
| SB Acoustics SB34NRXL75-8 ×2 (coherent pair) | 20 Hz–500 Hz · H2 H3 H4 H5 | 4-way, way 2 (low mid) | 40 Hz–2.15 kHz | 63 % | H2 H3 H4 H5 508 Hz–2.15 kHz |

Default choice per speaker (what Simulate picks when it opens):

- 2-way: way 1 SB Acoustics SB34NRXL75-8 ×2 (coherent pair) (no data: H2 508 Hz–6.09 kHz, H3 508 Hz–6.09 kHz, H4 508 Hz–6.09 kHz, H5 508 Hz–6.09 kHz); way 2 SB Acoustics SB34NRXL75-8 ×2 (coherent pair)
- 3-way: way 1 SB Acoustics SB34NRXL75-8 ×2 (coherent pair) (no data: H2 508 Hz–1.08 kHz, H3 508 Hz–1.08 kHz, H4 508 Hz–1.08 kHz, H5 508 Hz–1.08 kHz); way 2 SB Acoustics SB34NRXL75-8 ×2 (coherent pair) (no data: H2 508 Hz–9.12 kHz, H3 508 Hz–9.12 kHz, H4 508 Hz–9.12 kHz, H5 508 Hz–9.12 kHz); way 3 SB Acoustics SB34NRXL75-8 ×2 (coherent pair)
- 4-way: way 1 SB Acoustics SB34NRXL75-8 ×2 (coherent pair); way 2 SB Acoustics SB34NRXL75-8 ×2 (coherent pair) (no data: H2 508 Hz–2.15 kHz, H3 508 Hz–2.15 kHz, H4 508 Hz–2.15 kHz, H5 508 Hz–2.15 kHz); way 3 SB Acoustics SB34NRXL75-8 ×2 (coherent pair) (no data: H2 508 Hz–12.2 kHz, H3 508 Hz–12.2 kHz, H4 508 Hz–12.2 kHz, H5 508 Hz–12.2 kHz); way 4 SB Acoustics SB34NRXL75-8 ×2 (coherent pair)

