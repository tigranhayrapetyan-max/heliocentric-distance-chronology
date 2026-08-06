# 139 BCE control-case validation

**Status:** PASSED  
**Execution date:** 2026-08-05  
**Generator script SHA-256:** `bf097e9a9979ef02d7b253edab18f2ca78f5df8a9eda35d52a7ce4bbc64dd478`  
**Declared tolerance:** 120 seconds

| Check | Expected | Observed/nearest | Difference | Status |
|---|---|---|---:|---|
| 7–9 control root | BCE 0139-02-06 02:30:31 | 0139 BCE-02-06 02:30:37 | 5.872589 s | **PASS** |
| 3–6 control root | BCE 0139-10-26 18:46:33 | 0139 BCE-10-26 18:46:35 | 2.131652 s | **PASS** |
| 1–8 roots in 139 BCE | 8 | 8 | 0 roots | **PASS** |

The control run queried NASA/JPL Horizons through the reconstructed pipeline. Responses were divided into 64-epoch TLIST chunks, and every chunk was accepted only after exact requested/returned row-count and boundary checks. The generated series, roots, query-derived manifest, validation JSON, and complete execution log are archived in `outputs/control/`.

Passing this limited control case validates the executable path and the declared 139 BCE controls. It does **not** by itself establish full end-to-end reproduction of the complete 4000 BCE–2026 CE catalogue. Full generation and root-by-root comparison remain required before a final v1.0.0 release.
