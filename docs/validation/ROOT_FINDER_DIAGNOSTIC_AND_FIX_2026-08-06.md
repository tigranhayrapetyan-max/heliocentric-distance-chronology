# 1–8 Root-Finder Diagnostic and Corrective Run

Date: 2026-08-06

## Corrections applied

1. Perihelion boundaries are no longer treated as continuous root brackets. Root refinement is performed only when both bracket endpoints belong to the same Neptune revolution.
2. Each native 2-day Mercury interval is scanned at four sub-intervals (0.5-day spacing), allowing detection of short same-sign excursions containing two roots.
3. The dense scan is vectorized, reducing the offline 1–8 regeneration time to approximately 5 seconds on the audit system.
4. `residual_km` is now stored independently for every root record instead of reusing the final loop value.

## Corrective regeneration result

- Previous generated 1–8 count: 7,880
- Removed perihelion-boundary false roots: 25
- Recovered hidden double-crossing roots: 8
- Corrected generated 1–8 count: 7,863
- Reference 1–8 count: 7,863

The arithmetic closes exactly: 7,880 − 25 + 8 = 7,863.

## Catalogue comparison at 120-second tolerance

- 1–8: 7,862 / 7,863 matched; one timing discrepancy remains.
- 3–6: 447 / 447 matched.
- 7–9: 42 / 42 matched.

The sole remaining 1–8 discrepancy is the same root near 0940 CE:

- reference: 0940 CE-02-15 01:06:29
- regenerated: 0940 CE-02-15 01:09:16
- difference: approximately 167 seconds

This is not a count or root-topology discrepancy. It is a local timing difference attributable to interpolation/refinement from the archived 2-day Mercury series. It requires a denser direct Horizons query around the event for an independent timing adjudication. The 120-second comparison threshold was not relaxed in the corrected audit output.

## Tests

Existing test suite: 6 passed.
