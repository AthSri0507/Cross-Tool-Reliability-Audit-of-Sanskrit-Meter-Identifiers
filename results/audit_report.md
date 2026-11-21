# Tool audit: chanda vs skrutable

## T1. Corpus

| Text | Verses | Lines |
|---|---|---|
| Amarusataka | 14 | 56 |
| Bhagavadgita | 622 | 1382 |
| Bhallatasataka | 97 | 194 |
| Bhartrhari | 313 | 1199 |
| Buddhacarita | 491 | 982 |
| Kiratarjuniya | 1037 | 2074 |
| Kumarasambhava | 612 | 1224 |
| Meghaduta | 111 | 222 |
| Raghuvamsa | 1614 | 3228 |
| Saundarananda | 1058 | 2154 |
| Saundaryalahari | 102 | 204 |
| Sisupalavadha | 1643 | 3286 |
| **Total** | **7714** | **16205** |

## T2. Line-level L/G agreement with skrutable, by chanda input mode

| Text | n lines | as printed (spaced) | all spaces stripped | boundary-aware join |
|---|---|---|---|---|
| Amarusataka | 56 | 96.4 [87.9, 99.0] | 100.0 [93.6, 100.0] | 100.0 [93.6, 100.0] |
| Bhagavadgita | 1382 | 70.8 [68.3, 73.1] | 97.3 [96.2, 98.0] | 100.0 [99.7, 100.0] |
| Bhallatasataka | 194 | 43.8 [37.0, 50.8] | 97.4 [94.1, 98.9] | 100.0 [98.1, 100.0] |
| Bhartrhari | 1199 | 72.9 [70.3, 75.3] | 99.4 [98.8, 99.7] | 100.0 [99.7, 100.0] |
| Buddhacarita | 982 | 63.4 [60.4, 66.4] | 96.3 [95.0, 97.3] | 99.8 [99.3, 99.9] |
| Kiratarjuniya | 2074 | 55.1 [52.9, 57.2] | 95.1 [94.1, 95.9] | 100.0 [99.7, 100.0] |
| Kumarasambhava | 1224 | 57.2 [54.4, 59.9] | 97.9 [96.9, 98.5] | 100.0 [99.7, 100.0] |
| Meghaduta | 222 | 51.4 [44.8, 57.8] | 95.5 [91.9, 97.5] | 100.0 [98.3, 100.0] |
| Raghuvamsa | 3228 | 60.9 [59.2, 62.6] | 96.7 [96.0, 97.2] | 99.9 [99.7, 100.0] |
| Saundarananda | 2154 | 100.0 [99.8, 100.0] | 95.8 [94.8, 96.5] | 100.0 [99.8, 100.0] |
| Saundaryalahari | 204 | 43.6 [37.0, 50.5] | 96.1 [92.5, 98.0] | 100.0 [98.2, 100.0] |
| Sisupalavadha | 3286 | 99.1 [98.8, 99.4] | 96.7 [96.0, 97.3] | 99.9 [99.8, 100.0] |
| **All** | **16205** | **74.3 [73.6, 74.9]** | **96.7 [96.4, 96.9]** | **100.0 [99.9, 100.0]** |

Lines where a tool raised an error: 0

## T3. Verse-level outcomes (boundary-aware join)

| Outcome | Verses | % [95% CI] |
|---|---|---|
| A. full agreement (consensus set) | 6115 | 79.3 [78.4, 80.2] |
| B. same L/G; skrutable reports a metrical fault | 1271 | 16.5 [15.7, 17.3] |
| C. L/G sequences differ | 82 | 1.1 [0.9, 1.3] |
| D. same L/G; meter names differ | 246 | 3.2 [2.8, 3.6] |

## T4. Residual line-level disagreements (boundary-aware join)

8 of 16205 lines disagree.

| Type | Lines |
|---|---|
| same syllables, weight differs | 7 |
| syllable count differs (other) | 1 |

## Consensus set (released dataset, silver standard)

6115 verses; by class: {'samavrtta': 2422, 'ardhasama': 309, 'upajati': 1246, 'anustubh': 1991, 'vishama': 147}
