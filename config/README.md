# Configuration

`baseline/` contains immutable profiles used to reproduce released results.

`experiments/` contains named, version-controlled scientific alternatives. Each experiment must use its own `experiment_id` and `output_namespace`, so results cannot overwrite the validated baseline.

`schemas/` defines the machine-readable configuration contract.

In v1.0.0, the validated heliocentric-distance root engine retains its established CLI. The experiment templates for angular-enclosure analyses define the next configurable module and are explicitly marked as design templates until that module is implemented and validated.
