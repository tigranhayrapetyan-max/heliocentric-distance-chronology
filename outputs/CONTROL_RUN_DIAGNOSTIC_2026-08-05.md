# Control-run diagnostic — 2026-08-05

The first network control run did **not** complete root generation.

Observed output:

- `outputs/control/series/1_8/mercury.csv`: 80 returned epochs
- `outputs/control/series/1_8/neptune.csv`: 160 returned epochs, representing 80 epochs from each large request chunk
- no `roots_*.csv`
- no `control_case_validation.json`

Replay of the intermediate CSV files failed with:

`RuntimeError: Fewer than two outer-body perihelia detected; increase padding or interval`

The requested grids were larger than the returned series. The implementation had sent the Horizons run-stream as a normal form field instead of the multipart file upload shown in the official JPL File API example, and it did not verify that all requested TLIST epochs were returned.

Corrective changes in v0.9.1 RC:

1. send the input run-stream as a multipart `text/plain` file;
2. reject any response whose parsed epoch count differs from the requested count;
3. validate first and last returned JDs;
4. clear stale control caches before every Windows control run;
5. preserve stdout/stderr in `outputs/control/control_run.log`.
