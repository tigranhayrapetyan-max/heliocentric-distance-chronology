# Paper 3 reanalysis algorithm — V2.1

1. Read the frozen compact historical input.
2. Use the frozen mixed-calendar H1 exposure-year list.
3. Keep PRIMARY and SENSITIVITY statuses distinct.
4. Principal test: PRIMARY state transitions with event class COLLAPSE or SOVEREIGNTY_LOSS against H1.
5. Exhaustively circular-shift the complete historical configuration across astronomical years -3999 through 2026, preserving interval widths and labels.
6. Compute enrichment p as the fraction of all 6026 shifts with overlap count greater than or equal to the observed count.
7. Repeat for all-primary state transitions, positive transitions, all eligible state transitions, and sovereign-accession strata; repeat with one deterministic representative per event cluster.
8. For 7–9 and 3–6, use the existing validated root catalogues in outputs/generated_roots. Compare root JD/TDB directly with independently sourced exact historical civil days. Use Julian calendar before 15 October 1582 and Gregorian thereafter. No H1 condition and no ±day tolerance.
9. Report Tigran II only as a sensitivity observation because its historical accession is a 95/94 BCE interval rather than an exact day.
10. Do not alter the historical register after inspecting astronomical results.
