# Graph Report - .  (2026-04-27)

## Corpus Check
- 105 files · ~175,511 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 307 nodes · 441 edges · 20 communities detected
- Extraction: 75% EXTRACTED · 25% INFERRED · 0% AMBIGUOUS · INFERRED: 111 edges (avg confidence: 0.63)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]

## God Nodes (most connected - your core abstractions)
1. `RULPrediction` - 14 edges
2. `Component` - 14 edges
3. `CnnModel` - 14 edges
4. `Aircraft` - 13 edges
5. `ConvMhsaModel` - 13 edges
6. `main()` - 11 edges
7. `load_data()` - 11 edges
8. `run()` - 10 edges
9. `main()` - 9 edges
10. `run()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `Maintenance alert routes.` --uses--> `Component`  [INFERRED]
  /Users/jalpatel/College/Spring2026/IFRPM/backend/app/routers/alerts.py → /Users/jalpatel/College/Spring2026/IFRPM/backend/app/models/component.py
- `Return all components in an actionable risk band (MEDIUM / HIGH / CRITICAL).` --uses--> `Component`  [INFERRED]
  /Users/jalpatel/College/Spring2026/IFRPM/backend/app/routers/alerts.py → /Users/jalpatel/College/Spring2026/IFRPM/backend/app/models/component.py
- `Intelligent Flight Readiness Prediction System Team Kansas — Phase 1: XGBoost RU` --uses--> `Base`  [INFERRED]
  /Users/jalpatel/College/Spring2026/IFRPM/phase_1/models/rul_prediction.py → /Users/jalpatel/College/Spring2026/IFRPM/backend/app/database.py
- `run()` --calls--> `init_db()`  [INFERRED]
  /Users/jalpatel/College/Spring2026/IFRPM/backend/app/seed.py → /Users/jalpatel/College/Spring2026/IFRPM/backend/app/database.py
- `run()` --calls--> `classify_risk_band()`  [INFERRED]
  /Users/jalpatel/College/Spring2026/IFRPM/backend/app/seed.py → /Users/jalpatel/College/Spring2026/IFRPM/backend/app/services/risk_service.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.09
Nodes (38): Aircraft, AircraftBase, AircraftCreate, AircraftResponse, get_components(), Aircraft request / response schemas., Return all components with health index and risk band for an aircraft., Register a new aircraft. (+30 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (35): CnnModel, 1D CNN for risk score prediction.     Architecture:         Input (batch, window, ConvMhsaModel, PositionalEncoding, Model: conv_mhsa_model.py 1D Convolutional Embedding + Multi-Head Self-Attention, Combines Conv1d features with Transformer MHSA.     Architecture:         Input, compute_integrated_gradients(), Task: explain.py Integrated Gradients attribution explainability for risk score (+27 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (25): clean_flight_data(), Preprocessing: clean.py Handle missing values for NGAFID sensor data. - Forward, Clean sensor data per-flight:     1. Forward fill within each flight group     2, apply_minmax_scaler(), assign_flight_labels(), assign_window_labels(), fit_minmax_scaler(), get_feature_columns() (+17 more)

### Community 3 - "Community 3"
Cohesion: 0.14
Nodes (18): Dataset, add_rolling_features(), BiLSTM, EngineDataset, evaluate(), get_predictions(), load_data(), main() (+10 more)

### Community 4 - "Community 4"
Cohesion: 0.12
Nodes (20): combined_stress(), metar(), pirep(), Weather routes — proxies aviationweather.gov Data API.  Docs: https://aviationwe, Return METAR-derived stress features for an ICAO station.      @param icao - Fou, Return turbulence and icing intensity from nearby PIREPs.      @param icao     -, Return merged METAR + PIREP stress vector for a station.      @param icao - Four, _empty_metar() (+12 more)

### Community 5 - "Community 5"
Cohesion: 0.18
Nodes (15): badge(), bl_content(), br_content(), bullet(), person_row(), One-liner row: Name (bold) | Role (italic) | text., Top-Left: Latest Accomplishments, Top-Right: Next Major Tasks & Owners (+7 more)

### Community 6 - "Community 6"
Cohesion: 0.16
Nodes (9): init_db(), SQLAlchemy engine, session, and declarative base., apply_overrides(), lifespan(), load_config(), main(), parse_args(), NGAFID ML Pipeline — Main Entry Point Usage:   python main.py --model cnn --size (+1 more)

### Community 7 - "Community 7"
Cohesion: 0.25
Nodes (12): add_rolling_features(), evaluate(), load_data(), main(), nasa_score(), plot_feature_importance(), plot_predictions(), plot_trajectory() (+4 more)

### Community 8 - "Community 8"
Cohesion: 0.18
Nodes (12): detect_anomaly(), predict_rul(), Model inference entry point., Return True if the sensor window is anomalous., Return estimated RUL in engine cycles for the given sensor window., get_model(), load_models(), models_loaded() (+4 more)

### Community 9 - "Community 9"
Cohesion: 0.2
Nodes (8): get_alerts(), Maintenance alert routes., Return all components in an actionable risk band (MEDIUM / HIGH / CRITICAL)., classify_risk_band(), Risk band classification., Return True when RUL is within the actionable threshold., Map a RUL value (cycles) to a maintenance urgency band., should_alert()

### Community 10 - "Community 10"
Cohesion: 0.25
Nodes (7): normalize_operating_conditions(), Preprocessing: feature_engineering.py - RUL-based flight labeling from before_af, Compute OLS slope over a rolling window for a sensor series.      @param series, Z-score normalize operating condition columns in place.      @param df, Append rolling mean and std columns for each numeric sensor.      @param df, rolling_stats(), trend_slope()

### Community 11 - "Community 11"
Cohesion: 0.38
Nodes (2): PositionalEncoding, TransformerModel

### Community 12 - "Community 12"
Cohesion: 0.33
Nodes (3): Model: cnn_model.py 1D CNN with Residual Blocks and Global Average Pooling., 1D Residual Block:     Conv1d → BN → ReLU → Conv1d → BN + skip connection → ReLU, ResidualBlock

### Community 13 - "Community 13"
Cohesion: 0.4
Nodes (5): compute_health_index(), _min_max_normalize(), Composite Health Index via weighted sensor fusion., Scale a value to [0, 1]., Return a 0–1 health score (1.0 = healthy) using weighted sensor fusion.      @pa

### Community 14 - "Community 14"
Cohesion: 0.33
Nodes (5): detect_anomaly(), predict_rul(), Stub inference — used when no .pkl models are present., Return a deterministic RUL estimate (5–120 cycles) derived from sensor mean., Return a hash-based anomaly flag (~12.5% positive rate).      @param sensor_df -

### Community 15 - "Community 15"
Cohesion: 0.47
Nodes (5): _configure_logging(), main(), Download and process all datasets in one go., Ensure the data/src/ directory is on sys.path so we can import our modules., _setup_path()

### Community 16 - "Community 16"
Cohesion: 0.4
Nodes (4): BaseSettings, Config, Application settings via environment variables or .env file., Settings

### Community 17 - "Community 17"
Cohesion: 0.6
Nodes (4): _configure_logging(), main(), Ensure the data/src/ directory is on sys.path so we can import our modules     w, _setup_path()

### Community 18 - "Community 18"
Cohesion: 0.5
Nodes (1): Service layer package.

### Community 19 - "Community 19"
Cohesion: 0.67
Nodes (3): clean_dataframe(), preprocess_all(), Preprocess all processed datasets: handle missing values, outliers, and duplicat

## Knowledge Gaps
- **75 isolated node(s):** `Draw wrapped text, return new y.`, `One-liner row: Name (bold) | Role (italic) | text.`, `Top-Left: Latest Accomplishments`, `Top-Right: Next Major Tasks & Owners`, `Bottom-Left: Risks / Barriers` (+70 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 11`** (7 nodes): `transformer_model.py`, `PositionalEncoding`, `.forward()`, `.__init__()`, `TransformerModel`, `.forward()`, `.__init__()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (4 nodes): `__init__.py`, `__init__.py`, `__init__.py`, `Service layer package.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load_data()` connect `Community 2` to `Community 1`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **Why does `NGAFIDWindowDataset` connect `Community 2` to `Community 3`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `RULPrediction` (e.g. with `Dev seed — 5-aircraft dummy fleet, auto-runs on first startup.  Usage: python -m` and `Return a deterministic degrading RUL for seed data.`) actually correct?**
  _`RULPrediction` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `Component` (e.g. with `Dev seed — 5-aircraft dummy fleet, auto-runs on first startup.  Usage: python -m` and `Return a deterministic degrading RUL for seed data.`) actually correct?**
  _`Component` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `CnnModel` (e.g. with `Task: train_classification.py Unified risk_score prediction pipeline: 1. Load da` and `Instantiate the model based on config.`) actually correct?**
  _`CnnModel` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `Aircraft` (e.g. with `Dev seed — 5-aircraft dummy fleet, auto-runs on first startup.  Usage: python -m` and `Return a deterministic degrading RUL for seed data.`) actually correct?**
  _`Aircraft` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `ConvMhsaModel` (e.g. with `Task: train_classification.py Unified risk_score prediction pipeline: 1. Load da` and `Instantiate the model based on config.`) actually correct?**
  _`ConvMhsaModel` has 9 INFERRED edges - model-reasoned connections that need verification._