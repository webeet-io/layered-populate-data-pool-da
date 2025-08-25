# data_processor


Reusable Python utilities to  **standardize** ,  **light-clean** ,  **validate** , and **prepare** tabular data for ML and downstream pipelines – with a single, friendly orchestrator: `DataProcessor`.

This repo is designed so newcomers can succeed with a single call (`clean_simple`) while power users can compose richer pipelines (`process`, or helper methods).

---

## Table of Contents

* [What&#39;s inside](https://claude.ai/chat/280a7dcd-6826-4a29-8174-f818b514104b#whats-inside)
* [Folder layout (important)](https://claude.ai/chat/280a7dcd-6826-4a29-8174-f818b514104b#folder-layout-important)
* [Install (editable) + quick self-check](https://claude.ai/chat/280a7dcd-6826-4a29-8174-f818b514104b#install-editable--quick-self-check)
* [Zero-risk Quick Start: `clean_simple`](https://claude.ai/chat/280a7dcd-6826-4a29-8174-f818b514104b#zero-risk-quick-start-clean_simple)
* [Examples you can run](https://claude.ai/chat/280a7dcd-6826-4a29-8174-f818b514104b#examples-you-can-run)
* [API Reference](https://claude.ai/chat/280a7dcd-6826-4a29-8174-f818b514104b#api-reference)
  * [DataProcessor (orchestrator)](https://claude.ai/chat/280a7dcd-6826-4a29-8174-f818b514104b#dataprocessor-orchestrator)
  * [ColumnStandardizer](https://claude.ai/chat/280a7dcd-6826-4a29-8174-f818b514104b#columnstandardizer)
  * [WebscrapingDataCleaner](https://claude.ai/chat/280a7dcd-6826-4a29-8174-f818b514104b#webscrapingdatacleaner)
  * [BasicGeoValidator](https://claude.ai/chat/280a7dcd-6826-4a29-8174-f818b514104b#basicgeovalidator)
  * [MLDataPreparer](https://claude.ai/chat/280a7dcd-6826-4a29-8174-f818b514104b#mldatapreparer)
  * [Utilities](https://claude.ai/chat/280a7dcd-6826-4a29-8174-f818b514104b#utilities)
* [Testing &amp; Coverage](https://claude.ai/chat/280a7dcd-6826-4a29-8174-f818b514104b#testing--coverage)
* [Troubleshooting](https://claude.ai/chat/280a7dcd-6826-4a29-8174-f818b514104b#troubleshooting)
* [Contributing](https://claude.ai/chat/280a7dcd-6826-4a29-8174-f818b514104b#contributing)
* [License](https://claude.ai/chat/280a7dcd-6826-4a29-8174-f818b514104b#license)

---

## What's inside

* **Orchestrator:** `DataProcessor` — a single entry point to standardize columns, optionally clean artifacts, cast types, validate geo, de-duplicate, add stable IDs, and prepare for ML.
* **Core utilities:** `ColumnStandardizer`, `WebscrapingDataCleaner`, `BasicGeoValidator` (Berlin-friendly defaults via `GeoBounds`), `MLDataPreparer`.
* **Examples:** runnable, tiny scripts demonstrating safe usage.
* **Tests:** integration/basic tests (pytest).

> **Note:** A previous `BerlinDataValidator` (deep domain checks) is not used by this pipeline. Everything shown here uses the simpler, reusable `BasicGeoValidator`.

---

## Folder layout (important)

This project is delivered as a **Python package** inside a subfolder:

```
layered-populate-data-pool-da/
└─ db_population_utils/                 # ← package project root (has pyproject.toml)
   ├─ pyproject.toml
   └─ db_population_utils/              # ← the actual Python package
      ├─ __init__.py
      ├─ data_processor/
      │  ├─ __init__.py
      │  ├─ data_processor.py           # DataProcessor, GeoBounds (orchestrator)
      │  ├─ column_standardizer.py
      │  ├─ webscraping_cleaner.py
      │  ├─ basic_geo_validator.py
      │  ├─ ml_data_preparer.py
      │  └─ utils.py
      ├─ examples/
      │  ├─ __init__.py
      │  ├─ clean_simple_demo.py        # ← "for dummies" tutorial (basic, safe)
      │  ├─ end_to_end.py               # end-to-end pipeline via .process(...)
      │  └─ ml_prep_via_dp.py           # ML prep strategies (minimal/full)
      └─ tests/
         └─ ...
```

> The **outer** `db_population_utils/` holds `pyproject.toml`.
>
> The **inner** `db_population_utils/` is the importable package.

---

## Install (editable) + quick self-check

From the **outer** `db_population_utils\` (where `pyproject.toml` lives):

```powershell
# Windows PowerShell
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

Quick sanity check (must print a module path inside the inner package):

```powershell
python -c "import db_population_utils, inspect; print(db_population_utils.__file__)"
```

## Zero-risk Quick Start: `clean_simple`

This is the safest entry point for beginners. It only standardizes column names (lowercase, spaces→_, safe chars, uniqueness). No artifact cleanup, no type casting, no geo rules — data stays as-is.

Run the demo (after installing with `pip install -e .`):

```powershell
python -m db_population_utils.examples.clean_simple_demo
```

What you'll see:

Input columns like `" Address "`, `"PLZ (Zip)"`, `"Total Price€"`, `"Notes"` become
`address`, `plz_zip`, `total_price`, `notes`.

Values are unchanged (`"N/A"` stays `"N/A"`, `"1200"` stays a string). That's intentional.

## Examples you can run

All commands assume you're in:
`layered-populate-data-pool-da\db_population_utils` (the folder with `pyproject.toml`)
and your venv is activated.

**For dummies (only standardize columns):**

* File: `db_population_utils/db_population_utils/examples/clean_simple_demo.py`
* Run:

```powershell
python -m db_population_utils.examples.clean_simple_demo
```

**End to end via `DataProcessor.process(...)`:**

* File: `db_population_utils/db_population_utils/examples/end_to_end.py`
* What it does: standardize → (optional) web-scraping cleanup → cast → geo validate (mark/drop) → dedupe → stable id → minimal ML prep.
* Run:

```powershell
python -m db_population_utils.examples.end_to_end
```

**ML preparation strategies (minimal vs full):**

* File: `db_population_utils/db_population_utils/examples/ml_prep_via_dp.py`
* Shows: null handling, dtype optimization, (for full) feature analysis + recommendations.
* Run:

```powershell
python -m db_population_utils.examples.ml_prep_via_dp
```

If you run any example directly (double-click / `python path\to\file.py`), each script includes a tiny fallback header that adds the correct package root to `sys.path`.

## API Reference

Below is a concise reference of the most used classes and methods. All examples assume:

```python
from db_population_utils.data_processor import DataProcessor, GeoBounds
```

### DataProcessor (orchestrator)

The one you'll likely use the most.

#### `clean_simple(df) -> (df_out, info)`

**What it does:** standardizes column names; returns a report (info) with a `steps["standardize"]` block.

**What it does not:** no artifact cleanup, no casting, no geo rules, no dedupe/IDs.

**Example:**

```python
df_out, info = DataProcessor(verbose=True).clean_simple(df)
print(df_out.columns)  # standardized names
print(info["steps"]["standardize"])  # report
```

#### `process(df, *, clean_webscraping=False, cast_spec=None, validate_geo=False, geo_action="mark", berlin_only_plz=True, bounds=None, dedupe_keys=None, add_id_cols=None, id_col="stable_id", stable_id_salt=None, prepare_for_ml="minimal", null_strategy="preserve", target_column=None) -> (df_out, info)`

**Pipeline (in order):**

1. **Standardize columns** (always)
   → `info["steps"]["standardize"]`
2. **Parameter standardization** (maps user-provided keys like "PLZ" → "plz")
   → `info["steps"]["param_standardization"]`
3. **Web-scraping cleanup** (if `clean_webscraping=True`)
4. **Type casting** (if `cast_spec` given), e.g. `{"price": "float32"}`
5. **Geo validation** (if `validate_geo=True`): mark/drop rows using `BasicGeoValidator`
6. **De-duplication** (if `dedupe_keys` provided)
7. **Stable ID** (if `add_id_cols` provided)
8. **ML prep** (always, based on `prepare_for_ml` and `null_strategy`)

**Key parameters:**

* `clean_webscraping`: replace common null-like tokens ("N/A", "null", `--` …) with NaN.
* `cast_spec`: dict of col -> dtype string (e.g., "float32", "int32").
* `validate_geo`: check lat/lng in bounds (defaults suitable for Berlin) and optional PLZ range (10115–14199).
* `geo_action`: "mark" adds validity columns; "drop" removes invalid rows.
* `dedupe_keys`: list of columns to drop duplicates on (after standardization).
* `add_id_cols`, `id_col`, `stable_id_salt`, `length`: create a deterministic, salted row id from selected columns.
* `prepare_for_ml`: "preserve" | "minimal" | "full".
* `null_strategy`: "preserve" | "drop" | "mark" | "impute" | "smart_drop".
* `target_column`: optional; improves ML recommendations/scoring.

**Example:**

```python
df_out, info = DataProcessor(verbose=True).process(
    df,
    clean_webscraping=True,
    cast_spec={"price": "float32"},        # either raw ("Price") or std ("price") is ok
    validate_geo=True,
    geo_action="mark",
    berlin_only_plz=True,
    bounds=GeoBounds(),                    # default Berlin-ish bounds
    dedupe_keys=["Address", "PLZ"],        # raw names accepted; mapped to std
    add_id_cols=["Address", "PLZ"],
    id_col="stable_id",
    stable_id_salt="demo",
    prepare_for_ml="minimal",
    null_strategy="mark",
)
```

#### Helper methods (can be used standalone)

* `standardize_columns(df) -> df_out`
* `clean_webscraping_artifacts(df, custom_null_values: list[str] | None = None) -> df_out`
* `cast_types(df, spec: dict[col, dtype]) -> (df_out, report)`
* `dedupe(df, keys, keep="first") -> (df_out, report)`
* `add_stable_id(df, cols, id_col="stable_id", salt=None, length=16) -> (df_out, report)`
* `prepare_for_ml(df, strategy="minimal", null_strategy="preserve", target_column=None) -> (df_out, info)`
* `get_processing_summary() -> dict` (compact stats across steps)

**Parameter standardization:** after step 1 the processor automatically maps any user-provided column names ("PLZ", "Price") to their standardized form ("plz", "price"). This prevents KeyError in later steps.

### ColumnStandardizer

**Purpose:** Normalize header names only.

* Lowercase, trim, collapse spaces to `_`
* Remove unsafe characters (€, (), etc.)
* Ensure uniqueness (name, name_2, …)
* History + Report with original → cleaned → final names

**Key method:**

```python
df_out, report = ColumnStandardizer(verbose=True).standardize_columns(df)
```

### WebscrapingDataCleaner

**Purpose:** Replace a configurable set of common null-like tokens with NaN and trim strings. Keeps cleaning history and stats.

* Defaults include: `["", "N/A", "null", "None", "undefined", "-", "--", "nan", "nil", ...]`
* `custom_null_values` can be provided per call.

**Key method:**

```python
df_out, report = WebscrapingDataCleaner(verbose=True).clean_webscraping_artifacts(
    df, custom_null_values=["—"]
)
```

### BasicGeoValidator

**Purpose:** Lightweight, source-agnostic coordinate + optional PLZ checks.

* Auto-detects lat/lng columns by common names (lat, latitude, lng, lon, longitude).
* Validates lat/lng within `GeoBounds(lat_min, lat_max, lng_min, lng_max)`.
* Optional Berlin-only PLZ range (10115–14199).
* Two actions:
  * "mark": add `*_is_valid` + `geo_row_is_valid` columns
  * "drop": keep only fully valid rows

Typical usage via `DataProcessor.process` (recommended), or directly:

```python
df_mark, rep = BasicGeoValidator(bounds=GeoBounds(), berlin_only_plz=True, action="mark").validate(df)
```

### MLDataPreparer

**Purpose:** Null handling + dtype optimization + (for full) feature analysis & ML recommendations.

* **Null strategies:** "preserve", "drop", "mark" (adds `*_was_missing`), "impute" (median/mode), "smart_drop" (drop columns with too many nulls).
* **Strategies:**
  * "preserve": minimal changes.
  * "minimal": dtype optimization + memory report.
  * "full": + feature analysis (numeric/categorical, low variance, high cardinality) and ML recommendations (preprocessing steps, model hints, validation plan).

Usage via `DataProcessor.prepare_for_ml` or inside `.process(...)`:

```python
df_full, info_full = DataProcessor().prepare_for_ml(
    df, strategy="full", null_strategy="impute", target_column="target"
)

# Detailed (nested) results:
si = info_full.get("strategy_info", {})
print(si.get("feature_analysis", {}))
print(si.get("ml_recommendations", {}))
```

### Utilities

* **GeoBounds:** simple container for lat/lng bounds (defaults are Berlin-friendly).
* **count_true, col_null_counts:** robust helpers used internally and in reports.

---

## Testing & Coverage

From `db_population_utils\` (outer folder):

```powershell
.venv\Scripts\activate
pytest -q
pytest --cov=db_population_utils --cov-report=term-missing
```

The test suite includes integration tests for the orchestrator and focused tests for components like `ColumnStandardizer`. Current internal baseline is around ~84% coverage; you can raise `ml_data_preparer.py` coverage by adding matrix tests over null strategies and the full analysis path.

---

## Troubleshooting

**`ModuleNotFoundError: db_population_utils`**

Run `pip install -e .` from the outer `db_population_utils\` (that has `pyproject.toml`). Confirm with:

```powershell
python -c "import db_population_utils, inspect; print(db_population_utils.__file__)"
```

**Examples don't find the package when run directly**

Run them as modules:

```powershell
python -m db_population_utils.examples.clean_simple_demo
```

(Each example also ships a tiny fallback header to fix `sys.path` for direct runs.)

**KeyError in pipeline arguments after standardization**

You can pass raw names ("PLZ", "Price"). The processor maps them to standardized names right after step 1. If you still see a KeyError, verify the exact standardized column names in `info["steps"]["standardize"]["final_columns"]`.

**Verbose console lines from geo validation**

Set `verbose=False` on `DataProcessor` if you prefer silent runs.

**Old stubs elsewhere in the project**

If another folder named `db_population_utils` exists in your Python path, imports may resolve there. Check:

```powershell
python -c "import db_population_utils, inspect; print(db_population_utils.__file__)"
```

Remove/rename any conflicting folders.

---

## Contributing

1. Create a branch: `git checkout -b feature/xyz`
2. Add code + tests.
3. Run `pytest` and keep coverage healthy.
4. Update this README if you add public APIs.
5. Open a PR with a clear "How to test" section.

---

## License

MIT (or your organization's standard license)
