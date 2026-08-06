.PHONY: test control full statistics checksums

test:
	pytest -q

control:
	python code/horizons_root_generation.py --start=-0140-01-01 --stop=-0137-12-31 --cache-dir cache/horizons_control --work-dir outputs/control --output-dir outputs/control/roots --validate-control

full:
	python code/run_pipeline.py --start=-3999-01-01 --stop=2026-08-03 --trials 1000000

statistics:
	python code/circular_shift_validation_from_csv.py data/root_catalogue --trials 1000000 --seed 20260804 --sensitivity-csv outputs/circular_shift_sensitivity_reproduced.csv

checksums:
	find . -type f -not -path './.git/*' -not -path './cache/*' -print0 | sort -z | xargs -0 sha256sum > outputs/checksums.sha256
