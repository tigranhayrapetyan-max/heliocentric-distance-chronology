# Article 4 Protocol Amendment 001 — Cliopatria source coordinate and conservative identity

**Status:** PRE-OVERLAY AMENDMENT, FROZEN BEFORE ANY GLOBAL ASTRONOMICAL MATCHING  
**Applies to:** `A4_PROTOCOL_V3_PRE_FREEZE_LOCKED` §§4 and the no-year-zero subsection only  
**Astronomical overlay inspected before amendment:** **NO**  
**Reason for amendment:** direct source-schema audit during the first astronomy-blind Stage-A execution

## 1. Triggering audit findings

The first deterministic Stage-A execution against the exact Cliopatria `v0.2.0` blob exposed two source-model assumptions that were not supported by the frozen source itself.

### 1.1 Cliopatria year zero

The exact `v0.2.0` dataset contains valid rows whose `FromYear` or `ToYear` equals `0`. The official Cliopatria notebook exposes a continuous integer year control spanning negative values through zero to positive values. Therefore Stage A must not reject source year `0` or reinterpret Cliopatria's integer axis as a historical BCE/CE calendar lacking year zero.

**Amended rule:** Stage A preserves `YEAR_CLI` exactly as the Cliopatria source coordinate, including `0`. No `YEAR_ASTRO` field is generated in Stage A. Calendar/JD/astronomical-year conversion is deferred until Stage B, and then only for independently source-verified historical dates.

### 1.2 External-ID over-merging

The initial identity precedence (`Wikidata > SeshatID > Wikipedia > Name`) produced multiple cases in which substantively different Cliopatria labels or political phases shared one external identifier. Automatically merging those rows could erase encoded candidate boundaries before historical source adjudication.

**Amended rule:** provisional Stage-A identity is keyed by normalized Cliopatria `Name`, ignoring only case, whitespace, and a single pair of outer parentheses. `Wikidata`, `SeshatID`, and `Wikipedia` are retained as provenance and identity-review links, but do not automatically merge substantively different names. Potential aliases, renames, phases, and composite external-ID groupings are resolved in Stage B from historical sources.

## 2. Loss-averse rationale

The amendment is deliberately conservative. It may create additional candidate boundaries that are later merged, rejected, or classified as contextual during Stage-B historical validation. It cannot remove a candidate merely because two labels share an external identifier. This minimizes false-negative candidate loss before historical interpretation.

## 3. No analytical tuning

No Article-4 astronomical exposure, root date, compact-center date, H1 year, match table, p-value, or historical-to-astronomical comparison was inspected when this amendment was made. The amendment was triggered solely by source-schema/QC behavior and is therefore a pre-overlay data-model correction, not post hoc tuning to astronomical results.

## 4. Superseded text

This amendment supersedes only:

- the Stage-A stable identity precedence in §4; and
- the statement that Cliopatria uses no year zero, together with Stage-A generation of `YEAR_ASTRO`.

All other Article-4 event taxonomy, source-validation rules, date-precision classes, documentation scores, temporal strata, regional strata, clustering rules, astronomical hypotheses, null models, multiplicity rules, and confirmatory hierarchy remain unchanged.

## 5. Canonical Stage-A implementation after amendment

Canonical protocol ID:

`A4_GLOBAL_TRANSITIONS_V2_STAGE_A_YEAR0_NAME_CONSERVATIVE`

Canonical source remains unchanged:

- Cliopatria release: `v0.2.0`
- tag commit: `ad28a691b7c07c1fca89d0e0636d324667d2a258`
- `cliopatria.geojson.zip` Git blob SHA-1: `cefab0f4b622e2e7fb3daf68d4f461f83991204c`
- byte size: `44,231,317`
- source SHA-256 acquired on GitHub runner: `d01ae3a20d358cc5d54f69d9d725d390767d9c8759ac89ad6f90c58d106f3370`

The two earlier executions are retained as diagnostic provenance and must not be silently rewritten as the canonical run.
