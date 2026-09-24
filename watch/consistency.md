# Consistency of the stored data

Written by `watch/check_consistency.py`. Values that should agree with each other, checked on every driver.
"differs" means the stored values disagree by more than the tolerance and need a look at the source;
"check" means the value could not be tested (text where a number belongs, or a curve that does not cover the band).

99 ok, 11 differ, 12 to check.

| Result | Check | Driver | Detail |
|---|---|---|---|
| differs | band THD | ptt525x04naa05 | 80–5000 Hz at 94 dB: table 0.254 %, from the curve 0.157 % (-4.2 dB) |
| differs | band THD | ptt525x04naa05 | 450–1800 Hz at 94 dB: table 0.095 %, from the curve 0.0774 % (-1.8 dB) |
| differs | band THD | purifi-ptt10-0x04-nab-02 | 50–300 Hz at 91 dB: table 0.156 %, from the curve 0.128 % (-1.7 dB) |
| differs | notes | purifi-ptt10-0x04-nab-02 | a note says Pe was corrected to 350, the stored Pe is 'TBD (est 400)' |
| differs | sweep | ptt13t04hag01 | H2 at 1000 Hz, 94 dB: sweep -60.9 dB, curve -69.2 dB (+8.3 dB) |
| differs | sweep | ptt13t04hag01 | H3 at 1000 Hz, 94 dB: sweep -50.9 dB, curve -66.4 dB (+15.5 dB) |
| differs | sweep | ptt13t04hag01 | H3 at 4000 Hz, 94 dB: sweep -98.2 dB, curve -91.1 dB (-7.2 dB) |
| differs | sweep | ptt13t04hag10 | H2 at 1000 Hz, 94 dB: sweep -48.8 dB, curve -54.6 dB (+5.8 dB) |
| differs | sweep | ptt13t04hag10 | H3 at 1000 Hz, 94 dB: sweep -55.4 dB, curve -66.7 dB (+11.4 dB) |
| differs | sweep | ptt13t04hag10 | H3 at 4000 Hz, 94 dB: sweep -97.1 dB, curve -91.0 dB (-6.1 dB) |
| differs | sweep | ptt65x04naa08 | H3 at 125 Hz, 94 dB: sweep -65.6 dB, curve -70.6 dB (+5.0 dB) |
| check | curves | e180he-44-coils-in-series | set 1 (IMD two-tone 40+96 Hz, 80 dB) products: 2 value(s) left empty, as captured (not readable in the source chart) |
| check | curves | e180he-44-coils-in-series | set 2 (IMD two-tone 40+96 Hz, 85 dB) products: 1 value(s) left empty, as captured (not readable in the source chart) |
| check | curves | e180he-44-coils-in-series | set 3 (IMD two-tone 40+96 Hz, 90 dB) products: 1 value(s) left empty, as captured (not readable in the source chart) |
| check | curves | e180he-44-coils-in-series | set 4 (IMD two-tone 60+144 Hz, 80 dB) products: 3 value(s) left empty, as captured (not readable in the source chart) |
| check | curves | e180he-44-coils-in-series | set 5 (IMD two-tone 60+144 Hz, 90 dB) products: 2 value(s) left empty, as captured (not readable in the source chart) |
| check | curves | mcm-55-2421 | set 0 (IMD two-tone 40+96 Hz, 70 dB) products: 1 value(s) left empty, as captured (not readable in the source chart) |
| check | curves | ps180 | set 0 (IMD two-tone 40+96 Hz, 70 dB) products: 2 value(s) left empty, as captured (not readable in the source chart) |
| check | curves | ps180 | set 1 (IMD two-tone 40+96 Hz, 80 dB) products: 1 value(s) left empty, as captured (not readable in the source chart) |
| check | curves | ps180 | set 2 (IMD two-tone 60+144 Hz, 80 dB) products: 3 value(s) left empty, as captured (not readable in the source chart) |
| check | curves | ps180 | set 3 (IMD two-tone 60+144 Hz, 90 dB) products: 1 value(s) left empty, as captured (not readable in the source chart) |
| check | curves | ptt6.5x04-nfa-01 | set 2 (IMD two-tone 40+96 Hz, 85 dB) products: 1 value(s) left empty, as captured (not readable in the source chart) |
| check | parameters | purifi-ptt10-0x04-nab-02 | not a number: Pe = 'TBD (est 400)' |
| ok | band THD | m74t-6 | 300–3500 Hz at 94 dB: table 0.408 %, from the curve 0.403 % (-0.1 dB) |
| ok | band THD | m74t-6 | 450–1800 Hz at 94 dB: table 0.237 %, from the curve 0.246 % (+0.3 dB) |
| ok | band THD | m74t-6 | 700–3500 Hz at 94 dB: table 0.077 %, from the curve 0.0776 % (+0.1 dB) |
| ok | band THD | ptt525x04naa05 | 300–3500 Hz at 94 dB: table 0.097 %, from the curve 0.0912 % (-0.5 dB) |
| ok | band THD | ptt525x04naa05 | 700–3500 Hz at 94 dB: table 0.098 %, from the curve 0.0924 % (-0.5 dB) |
| ok | band THD | ptt65x04naa08a | 80–5000 Hz at 94 dB: table 0.15 %, from the curve 0.148 % (-0.1 dB) |
| ok | band THD | ptt65x04naa08a | 300–3500 Hz at 94 dB: table 0.06 %, from the curve 0.0592 % (-0.1 dB) |
| ok | band THD | ptt65x04naa08a | 450–1800 Hz at 94 dB: table 0.055 %, from the curve 0.0547 % (-0.1 dB) |
| ok | band THD | ptt65x04naa08a | 700–3500 Hz at 94 dB: table 0.055 %, from the curve 0.0549 % (-0.0 dB) |
| ok | band THD | purifi-ptt10-0x04-nab-02 | 20–600 Hz at 91 dB: table 0.527 %, from the curve 0.596 % (+1.1 dB) |
| ok | band THD | purifi-ptt10-0x04-nab-02 | 20–200 Hz at 91 dB: table 0.64 %, from the curve 0.701 % (+0.8 dB) |
| ok | band THD | purifi-ptt8-0x04-nab-02 | 20–600 Hz at 91 dB: table 2.02 %, from the curve 2.05 % (+0.1 dB) |
| ok | band THD | purifi-ptt8-0x04-nab-02 | 20–200 Hz at 91 dB: table 2.45 %, from the curve 2.4 % (-0.2 dB) |
| ok | band THD | purifi-ptt8-0x04-nab-02 | 50–300 Hz at 91 dB: table 0.166 %, from the curve 0.173 % (+0.4 dB) |
| ok | band THD | purifi-ptt8-0x04-nab-02 | 80–5000 Hz at 94 dB: table 0.139 %, from the curve 0.136 % (-0.2 dB) |
| ok | band THD | purifi-ptt8-0x04-nab-02 | 300–3500 Hz at 94 dB: table 0.079 %, from the curve 0.0775 % (-0.2 dB) |
| ok | band THD | purifi-ptt8-0x04-nab-02 | 450–1800 Hz at 94 dB: table 0.054 %, from the curve 0.0542 % (+0.0 dB) |
| ok | band THD | purifi-ptt8-0x04-nab-02 | 700–3500 Hz at 94 dB: table 0.084 %, from the curve 0.0823 % (-0.2 dB) |
| ok | band THD | sb-satori-wo24p-8 | 20–600 Hz at 91 dB: table 2.54 %, from the curve 2.28 % (-0.9 dB) |
| ok | band THD | sb-satori-wo24p-8 | 20–200 Hz at 91 dB: table 3.09 %, from the curve 2.67 % (-1.2 dB) |
| ok | band THD | sb-satori-wo24p-8 | 50–300 Hz at 91 dB: table 0.371 %, from the curve 0.363 % (-0.2 dB) |
| ok | band THD | sb-sb34nrxl75-8 | 20–600 Hz at 91 dB: table 0.737 %, from the curve 0.741 % (+0.0 dB) |
| ok | band THD | sb-sb34nrxl75-8 | 20–200 Hz at 91 dB: table 0.893 %, from the curve 0.869 % (-0.2 dB) |
| ok | band THD | sb-sb34nrxl75-8 | 50–300 Hz at 91 dB: table 0.134 %, from the curve 0.142 % (+0.5 dB) |
| ok | band THD | sb-sb34nrxl75-8-dual | 20–600 Hz at 91 dB: table 0.45 %, from the curve 0.453 % (+0.1 dB) |
| ok | band THD | sb-sb34nrxl75-8-dual | 20–200 Hz at 91 dB: table 0.546 %, from the curve 0.531 % (-0.2 dB) |
| ok | band THD | sb-sb34nrxl75-8-dual | 50–300 Hz at 91 dB: table 0.07 %, from the curve 0.0725 % (+0.3 dB) |
| ok | band THD | sb17nbac35-8 | 80–5000 Hz at 94 dB: table 0.715 %, from the curve 0.682 % (-0.4 dB) |
| ok | band THD | sb17nbac35-8 | 300–3500 Hz at 94 dB: table 0.231 %, from the curve 0.228 % (-0.1 dB) |
| ok | band THD | sb17nbac35-8 | 450–1800 Hz at 94 dB: table 0.187 %, from the curve 0.187 % (-0.0 dB) |
| ok | band THD | sb17nbac35-8 | 700–3500 Hz at 94 dB: table 0.25 %, from the curve 0.247 % (-0.1 dB) |
| ok | excursion | ptt525x04naa05 | 20 Hz: stored 78.9 dB, from Sd and Xmax 79.0 dB |
| ok | excursion | ptt525x04naa05 | 20.5 Hz: stored 79.3 dB, from Sd and Xmax 79.4 dB |
| ok | excursion | ptt525x04naa05 | 21.1 Hz: stored 79.8 dB, from Sd and Xmax 79.9 dB |
| ok | excursion | ptt65x04naa08 | 20 Hz: stored 82.7 dB, from Sd and Xmax 82.9 dB |
| ok | excursion | ptt65x04naa08 | 20.5 Hz: stored 83.2 dB, from Sd and Xmax 83.3 dB |
| ok | excursion | ptt65x04naa08 | 21.1 Hz: stored 83.7 dB, from Sd and Xmax 83.8 dB |
| ok | excursion | ptt80x04nab01 | 20 Hz: stored 87.2 dB, from Sd and Xmax 87.4 dB |
| ok | excursion | ptt80x04nab01 | 20.5 Hz: stored 87.7 dB, from Sd and Xmax 87.8 dB |
| ok | excursion | ptt80x04nab01 | 21.1 Hz: stored 88.2 dB, from Sd and Xmax 88.3 dB |
| ok | excursion | purifi-ptt10-0x04-nab-02 | 20 Hz: stored 95.1 dB, from Sd and Xmax 95.1 dB |
| ok | excursion | purifi-ptt10-0x04-nab-02 | 30 Hz: stored 102.1 dB, from Sd and Xmax 102.1 dB |
| ok | excursion | purifi-ptt10-0x04-nab-02 | 50 Hz: stored 111.0 dB, from Sd and Xmax 111.0 dB |
| ok | excursion | purifi-ptt8-0x04-nab-02 | 20 Hz: stored 87.3 dB, from Sd and Xmax 87.4 dB |
| ok | excursion | purifi-ptt8-0x04-nab-02 | 30 Hz: stored 94.4 dB, from Sd and Xmax 94.4 dB |
| ok | excursion | purifi-ptt8-0x04-nab-02 | 50 Hz: stored 103.3 dB, from Sd and Xmax 103.3 dB |
| ok | excursion | sb-satori-wo24p-8 | 20 Hz: stored 87.3 dB, from Sd and Xmax 87.3 dB |
| ok | excursion | sb-satori-wo24p-8 | 30 Hz: stored 94.3 dB, from Sd and Xmax 94.3 dB |
| ok | excursion | sb-satori-wo24p-8 | 50 Hz: stored 103.2 dB, from Sd and Xmax 103.2 dB |
| ok | excursion | sb-sb34nrxl75-8 | 20 Hz: stored 94.7 dB, from Sd and Xmax 94.7 dB |
| ok | excursion | sb-sb34nrxl75-8 | 30 Hz: stored 101.7 dB, from Sd and Xmax 101.7 dB |
| ok | excursion | sb-sb34nrxl75-8 | 50 Hz: stored 110.6 dB, from Sd and Xmax 110.6 dB |
| ok | levels | purifi-ptt8-0x04-nab-02 | H2: 94 dB curve minus 91 dB curve = +2.6 dB on average over 4 shared frequencies (typical slope expects +3.0 dB) |
| ok | levels | purifi-ptt8-0x04-nab-02 | H3: 94 dB curve minus 91 dB curve = +5.6 dB on average over 4 shared frequencies (typical slope expects +2.1 dB) |
| ok | pair | sb-sb34nrxl75-8-dual | H2: pair minus single = -5.9 dB on average (note's slope 1.03 expects -6.2 dB); varies by 3.3 dB across frequency, so slopes per frequency were used |
| ok | pair | sb-sb34nrxl75-8-dual | H3: pair minus single = -4.2 dB on average (note's slope 0.68 expects -4.1 dB); varies by 5.4 dB across frequency, so slopes per frequency were used |
| ok | pair | sb-sb34nrxl75-8-dual | H4: pair minus single = -1.7 dB on average (note's slope 0 expects -0.0 dB); varies by 5.0 dB across frequency, so slopes per frequency were used |
| ok | pair | sb-sb34nrxl75-8-dual | H5: pair minus single = -4.1 dB on average (note's slope 0.47 expects -2.8 dB); varies by 4.3 dB across frequency, so slopes per frequency were used |
| ok | parameters | purifi-ptt10-0x04-nab-02 | Vd: stored 533, from the others 531 (0.4 % apart) |
| ok | parameters | purifi-ptt8-0x04-nab-02 | Qts: stored 0.39, from the others 0.389 (0.3 % apart) |
| ok | parameters | purifi-ptt8-0x04-nab-02 | Fs: stored 28.8, from the others 28.9 (0.2 % apart) |
| ok | parameters | purifi-ptt8-0x04-nab-02 | Vas: stored 55.4, from the others 55.6 (0.3 % apart) |
| ok | parameters | purifi-ptt8-0x04-nab-02 | Vd: stored 219, from the others 219 (0.2 % apart) |
| ok | parameters | purifi-ptt8-0x04-nab-02 | Qes: stored 0.41, from the others 0.409 (0.3 % apart) |
| ok | parameters | sb-satori-wo24p-8 | Qts: stored 0.38, from the others 0.382 (0.7 % apart) |
| ok | parameters | sb-satori-wo24p-8 | Fs: stored 24.5, from the others 24.5 (0.1 % apart) |
| ok | parameters | sb-satori-wo24p-8 | Vas: stored 87.5, from the others 87.6 (0.1 % apart) |
| ok | parameters | sb-satori-wo24p-8 | Vd: stored 217, from the others 217 (0.1 % apart) |
| ok | parameters | sb-satori-wo24p-8 | Qes: stored 0.41, from the others 0.405 (1.1 % apart) |
| ok | parameters | sb-sb34nrxl75-8 | Qts: stored 0.28, from the others 0.275 (1.6 % apart) |
| ok | parameters | sb-sb34nrxl75-8 | Fs: stored 22, from the others 22.1 (0.2 % apart) |
| ok | parameters | sb-sb34nrxl75-8 | Vas: stored 205, from the others 205 (0.0 % apart) |
| ok | parameters | sb-sb34nrxl75-8 | Vd: stored 508, from the others 508 (0.0 % apart) |
| ok | parameters | sb-sb34nrxl75-8 | Qes: stored 0.29, from the others 0.289 (0.3 % apart) |
| ok | sweep | ptt13t04hag01 | H2 at 2000 Hz, 94 dB: sweep -56.9 dB, curve -57.0 dB (+0.2 dB) |
| ok | sweep | ptt13t04hag01 | H3 at 2000 Hz, 94 dB: sweep -74.0 dB, curve -77.7 dB (+3.8 dB) |
| ok | sweep | ptt13t04hag01 | H2 at 4000 Hz, 94 dB: sweep -56.0 dB, curve -54.9 dB (-1.1 dB) |
| ok | sweep | ptt13t04hag10 | H2 at 2000 Hz, 94 dB: sweep -62.4 dB, curve -61.7 dB (-0.6 dB) |
| ok | sweep | ptt13t04hag10 | H3 at 2000 Hz, 94 dB: sweep -80.4 dB, curve -84.3 dB (+3.9 dB) |
| ok | sweep | ptt13t04hag10 | H2 at 4000 Hz, 94 dB: sweep -55.0 dB, curve -54.6 dB (-0.4 dB) |
| ok | sweep | ptt525x04naa05 | H2 at 125 Hz, 94 dB: sweep -55.1 dB, curve -53.5 dB (-1.5 dB) |
| ok | sweep | ptt525x04naa05 | H3 at 125 Hz, 94 dB: sweep -62.8 dB, curve -62.8 dB (+0.0 dB) |
| ok | sweep | ptt525x04naa05 | H2 at 1000 Hz, 94 dB: sweep -64.1 dB, curve -66.6 dB (+2.4 dB) |
| ok | sweep | ptt525x04naa05 | H3 at 1000 Hz, 94 dB: sweep -76.8 dB, curve -76.4 dB (-0.4 dB) |
| ok | sweep | ptt65x04naa08 | H2 at 125 Hz, 94 dB: sweep -56.0 dB, curve -56.1 dB (+0.1 dB) |
| ok | sweep | ptt65x04naa08 | H2 at 1000 Hz, 94 dB: sweep -63.8 dB, curve -64.9 dB (+1.1 dB) |
| ok | sweep | ptt65x04naa08 | H3 at 1000 Hz, 94 dB: sweep -75.1 dB, curve -75.7 dB (+0.7 dB) |
| ok | sweep | ptt80x04nab01 | H2 at 125 Hz, 94 dB: sweep -65.0 dB, curve -64.6 dB (-0.4 dB) |
| ok | sweep | ptt80x04nab01 | H3 at 125 Hz, 94 dB: sweep -72.5 dB, curve -73.5 dB (+1.0 dB) |
| ok | sweep | ptt80x04nab01 | H2 at 1000 Hz, 94 dB: sweep -66.5 dB, curve -64.7 dB (-1.8 dB) |
| ok | sweep | ptt80x04nab01 | H3 at 1000 Hz, 94 dB: sweep -78.7 dB, curve -77.1 dB (-1.6 dB) |
| ok | test tones | ptt525x04naa05 | 30 + 255 Hz: 255 Hz tone at 80.3 dB, stated 80 dB |
| ok | test tones | ptt525x04naa05 | 50 + 425 Hz: 425 Hz tone at 80.5 dB, stated 80 dB |
| ok | test tones | ptt65m08naa08 | Purifi conv. 250 + 2125 Hz: 2125 Hz tone at 94.0 dB, stated 94 dB |
| ok | test tones | ptt65m08naa08 | Purifi conv. 500 + 4250 Hz: 4250 Hz tone at 94.0 dB, stated 94 dB |
| ok | test tones | ptt65x04naa08 | 30 + 255 Hz: 255 Hz tone at 80.5 dB, stated 80 dB |
| ok | test tones | ptt65x04naa08 | 50 + 425 Hz: 425 Hz tone at 80.3 dB, stated 80 dB |
| ok | test tones | ptt80x04nab01 | 30 + 255 Hz: 255 Hz tone at 80.5 dB, stated 80 dB |
| ok | test tones | ptt80x04nab01 | 50 + 425 Hz: 425 Hz tone at 80.5 dB, stated 80 dB |
