# Release checklist

## Required files

- [x] Original workbook included in `data/root_catalogue/`
- [x] Original disclosed statistical script included in `code/legacy/`
- [x] Full root catalogue CSV exports included
- [x] Reconstructed Horizons generator included
- [x] Independent CSV statistical validation script included
- [x] Protocol and fixed configuration included
- [x] Provenance table with alternative assignments included
- [x] README, licenses, CITATION.cff, and `.zenodo.json` included

## Validation

- [x] Offline unit tests pass (6/6)
- [x] Workbook counts verified: 7,863 / 447 / 42
- [x] Legacy circular-shift proportion reproduced
- [x] Independent CSV circular-shift proportion reproduced
- [x] Monte Carlo result reproduced with fixed seed
- [x] Sensitivity table deterministic columns reproduced
- [x] 139 BCE control: eight 1–8 roots
- [x] 139 BCE control: 7–9 root within declared tolerance (5.872589 s)
- [x] 139 BCE control: 3–6 root within declared tolerance (2.131652 s)
- [ ] Full roots regenerated from NASA/JPL Horizons
- [ ] Root-by-root comparison against workbook
- [ ] Independent second execution completed

## Metadata and release

- [ ] Replace GitHub username in `CITATION.cff`
- [ ] Replace repository placeholder in `.zenodo.json` if added
- [x] Run `RUN_CONTROL_CASE_WINDOWS.bat` on a network-enabled computer
- [x] Include verified control-case output
- [ ] Promote from `v0.9.3 RC` to `v1.0.0` only after full-catalogue comparison
- [ ] Create GitHub release
- [ ] Publish Zenodo record
- [ ] Insert DOI into both manuscripts and cover letters
