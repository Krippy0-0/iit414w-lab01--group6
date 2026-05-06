from pathlib import Path
import json

import nbformat as nbf
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[1]
DATA_DIR = ROOT / "data"


DRIVER_CODE = {
    "Aitken": "AIT",
    "Albon": "ALB",
    "Alonso": "ALO",
    "Bearman": "BEA",
    "Bottas": "BOT",
    "Colapinto": "COL",
    "de Vries": "DEV",
    "Doohan": "DOO",
    "Fittipaldi": "FIT",
    "Gasly": "GAS",
    "Giovinazzi": "GIO",
    "Grosjean": "GRO",
    "Hamilton": "HAM",
    "Hülkenberg": "HUL",
    "Kubica": "KUB",
    "Kvyat": "KVY",
    "Latifi": "LAT",
    "Lawson": "LAW",
    "Leclerc": "LEC",
    "Magnussen": "MAG",
    "Mazepin": "MAZ",
    "Norris": "NOR",
    "Ocon": "OCO",
    "Piastri": "PIA",
    "Pérez": "PER",
    "Ricciardo": "RIC",
    "Russell": "RUS",
    "Räikkönen": "RAI",
    "Sainz": "SAI",
    "Sargeant": "SAR",
    "Schumacher": "MSC",
    "Stroll": "STR",
    "Tsunoda": "TSU",
    "Verstappen": "VER",
    "Vettel": "VET",
    "Zhou": "ZHO",
}


def build_dataset() -> pd.DataFrame:
    pre = pd.read_csv(WORKSPACE / "certamen2_orellana" / "f1_prerace_features_2019_2024.csv")
    pit = pd.read_csv(WORKSPACE / "miniChallenge" / "md1_pitstops_2019_2024.csv")

    pit = pit.sort_values(["season", "round", "Driver", "Stint", "LapNumber"])
    pit_agg = (
        pit.groupby(["season", "round", "Driver"], as_index=False)
        .agg(
            n_stops=("LapNumber", "count"),
            compound_sequence=("Compound", lambda s: "-".join(s.dropna().astype(str))),
            stint_lengths=("TyreLife", lambda s: "-".join(s.dropna().round(0).astype(int).astype(str))),
            avg_stint_tyre_life=("TyreLife", "mean"),
            max_stint_tyre_life=("TyreLife", "max"),
            pit_loss_total=("pit_stop_duration", "sum"),
            pit_loss_mean=("pit_stop_duration", "mean"),
        )
    )

    pre["driver_code"] = pre["driver_name"].map(DRIVER_CODE)
    df = pre.merge(
        pit_agg,
        left_on=["season", "round", "driver_code"],
        right_on=["season", "round", "Driver"],
        how="left",
    )

    strategy_defaults = {
        "n_stops": 0,
        "compound_sequence": "NO_STOP_RECORDED",
        "stint_lengths": "NO_STOP_RECORDED",
        "avg_stint_tyre_life": 0,
        "max_stint_tyre_life": 0,
        "pit_loss_total": 0,
        "pit_loss_mean": 0,
    }
    for col, value in strategy_defaults.items():
        df[col] = df[col].fillna(value)

    df["is_top10"] = (pd.to_numeric(df["position"], errors="coerce") <= 10).astype(int)
    df["grid_position"] = df["grid"].replace({0: pd.NA}).fillna(df["qualifying_position"])
    df["qualifying_time_s"] = pd.NA
    df["safety_car_periods"] = (df["practice_sc_or_vsc_lap_count"].fillna(0) > 0).astype(int)
    df["data_source_note"] = (
        "Recovered Hito 1 race-level build from Certamen 2 pre-race features "
        "plus miniChallenge pit-stop strategy observations."
    )

    keep = [
        "season",
        "round",
        "race_name",
        "circuit_id",
        "driver_id",
        "driver_code",
        "driver_name",
        "constructor_name",
        "grid",
        "grid_position",
        "qualifying_position",
        "qualifying_time_s",
        "position",
        "position_text",
        "laps",
        "status",
        "points",
        "is_top10",
        "will_dnf",
        "circuit_type",
        "driver_recent_dnf_rate",
        "driver_dnf_any_last3",
        "team_season_dnf_rate_to_date",
        "driver_experience_races",
        "constructor_recent_dnf_rate_10",
        "circuit_prior_dnf_rate",
        "driver_avg_grid_last5",
        "constructor_avg_grid_last10",
        "grid_vs_driver_avg_last5",
        "grid_vs_constructor_avg_last10",
        "back_grid_start",
        "front_grid_start",
        "practice_sessions_with_timed_laps",
        "practice_timed_laps",
        "practice_best_lap_sec",
        "practice_median_lap_sec",
        "practice_avg_gap_to_fastest_sec",
        "practice_min_gap_to_fastest_sec",
        "practice_total_laps",
        "practice_deleted_laps",
        "practice_yellow_lap_count",
        "practice_red_flag_lap_count",
        "practice_sc_or_vsc_lap_count",
        "qualifying_timed_laps",
        "qualifying_best_time_sec",
        "qualifying_lap_best_sec",
        "qualifying_lap_median_sec",
        "qualifying_total_laps",
        "qualifying_gap_to_pole_sec",
        "qualifying_deleted_laps",
        "qualifying_yellow_lap_count",
        "qualifying_red_flag_lap_count",
        "practice_sessions_available",
        "qualifying_sessions_available",
        "practice_completion_rate",
        "has_qualifying_time",
        "has_practice_time",
        "n_stops",
        "compound_sequence",
        "stint_lengths",
        "avg_stint_tyre_life",
        "max_stint_tyre_life",
        "pit_loss_total",
        "pit_loss_mean",
        "safety_car_periods",
        "data_source_note",
    ]
    return df[keep].sort_values(["season", "round", "constructor_name", "driver_name"]).reset_index(drop=True)


def make_notebook() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    nb["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    }

    cells = []
    cells.append(nbf.v4.new_markdown_cell(
        "# Hito 1 Baseline - F1 Race Strategy Advisor\n\n"
        "This notebook implements the locked Hito 1 target (`is_top10`) and temporal split: "
        "train 2019-2021, calibration 2022, test 2023-2024. Strategy fields are treated as "
        "user-controlled scenario inputs for what-if comparison, not as normal pre-race signals."
    ))
    cells.append(nbf.v4.new_code_cell(
        "from pathlib import Path\n\n"
        "import matplotlib.pyplot as plt\n"
        "import numpy as np\n"
        "import pandas as pd\n"
        "from sklearn.compose import ColumnTransformer\n"
        "from sklearn.ensemble import GradientBoostingClassifier\n"
        "from sklearn.impute import SimpleImputer\n"
        "from sklearn.isotonic import IsotonicRegression\n"
        "from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score\n"
        "from sklearn.pipeline import Pipeline\n"
        "from sklearn.preprocessing import OneHotEncoder\n\n"
        "RANDOM_SEED = 414\n"
        "DATA_PATH = Path('data/f1_strategy_race_level.csv')\n"
        "pd.set_option('display.max_columns', 120)"
    ))
    cells.append(nbf.v4.new_markdown_cell("## 1. Load Data"))
    cells.append(nbf.v4.new_code_cell(
        "df = pd.read_csv(DATA_PATH)\n"
        "print(df.shape)\n"
        "display(df.head())\n"
        "assert {'season', 'is_top10', 'n_stops', 'compound_sequence'}.issubset(df.columns)"
    ))
    cells.append(nbf.v4.new_markdown_cell("## 2. Locked Temporal Split"))
    cells.append(nbf.v4.new_code_cell(
        "train = df[df['season'].between(2019, 2021)].copy()\n"
        "cal = df[df['season'].eq(2022)].copy()\n"
        "test = df[df['season'].between(2023, 2024)].copy()\n\n"
        "print('train seasons:', sorted(train['season'].unique()), train.shape)\n"
        "print('calibration seasons:', sorted(cal['season'].unique()), cal.shape)\n"
        "print('test seasons:', sorted(test['season'].unique()), test.shape)\n\n"
        "assert set(train['season'].unique()) == {2019, 2020, 2021}\n"
        "assert set(cal['season'].unique()) == {2022}\n"
        "assert set(test['season'].unique()) == {2023, 2024}\n"
        "assert len(train) + len(cal) + len(test) == len(df)"
    ))
    cells.append(nbf.v4.new_markdown_cell("## 3. Leakage Audit"))
    cells.append(nbf.v4.new_code_cell(
        "pre_race_features = [\n"
        "    'grid_position', 'qualifying_position', 'front_grid_start', 'back_grid_start',\n"
        "    'driver_recent_dnf_rate', 'driver_dnf_any_last3', 'team_season_dnf_rate_to_date',\n"
        "    'driver_experience_races', 'constructor_recent_dnf_rate_10', 'circuit_prior_dnf_rate',\n"
        "    'driver_avg_grid_last5', 'constructor_avg_grid_last10', 'grid_vs_driver_avg_last5',\n"
        "    'grid_vs_constructor_avg_last10', 'practice_sessions_with_timed_laps',\n"
        "    'practice_timed_laps', 'practice_avg_gap_to_fastest_sec', 'practice_min_gap_to_fastest_sec',\n"
        "    'practice_total_laps', 'practice_deleted_laps', 'practice_yellow_lap_count',\n"
        "    'practice_red_flag_lap_count', 'qualifying_timed_laps', 'qualifying_gap_to_pole_sec',\n"
        "    'qualifying_deleted_laps', 'qualifying_yellow_lap_count', 'qualifying_red_flag_lap_count',\n"
        "    'practice_sessions_available', 'qualifying_sessions_available', 'practice_completion_rate',\n"
        "    'has_qualifying_time', 'has_practice_time'\n"
        "]\n"
        "scenario_inputs = ['n_stops', 'compound_sequence', 'avg_stint_tyre_life', 'max_stint_tyre_life', 'pit_loss_total']\n"
        "categorical_features = ['constructor_name', 'circuit_type', 'compound_sequence']\n"
        "audit_columns = ['season', 'round', 'race_name', 'driver_name', 'position', 'points', 'status', 'will_dnf', 'safety_car_periods', 'stint_lengths', 'data_source_note']\n\n"
        "audit = pd.DataFrame([\n"
        "    {'column_group': 'pre-race predictors', 'columns': ', '.join(pre_race_features), 'model_use': 'Allowed as information available before the race.'},\n"
        "    {'column_group': 'scenario inputs', 'columns': ', '.join(scenario_inputs), 'model_use': 'Allowed only because the product compares user-defined strategy scenarios.'},\n"
        "    {'column_group': 'audit / outcome columns', 'columns': ', '.join(audit_columns), 'model_use': 'Not used as predictors for fitting or selection.'},\n"
        "])\n"
        "display(audit)\n"
        "for col in ['position', 'points', 'status', 'will_dnf', 'safety_car_periods', 'stint_lengths']:\n"
        "    assert col not in pre_race_features + scenario_inputs + categorical_features"
    ))
    cells.append(nbf.v4.new_markdown_cell("## 4. F1-Defendable Grid-Rule Baseline"))
    cells.append(nbf.v4.new_code_cell(
        "def grid_rule_proba(frame):\n"
        "    grid = frame['grid_position'].fillna(20)\n"
        "    return np.select(\n"
        "        [grid <= 5, grid <= 10, grid <= 15],\n"
        "        [0.88, 0.62, 0.24],\n"
        "        default=0.08,\n"
        "    ).astype(float)\n\n"
        "grid_test_proba = grid_rule_proba(test)\n"
        "grid_metrics = {\n"
        "    'model': 'Grid-rule heuristic',\n"
        "    'brier': brier_score_loss(test['is_top10'], grid_test_proba),\n"
        "    'log_loss': log_loss(test['is_top10'], grid_test_proba, labels=[0, 1]),\n"
        "    'roc_auc': roc_auc_score(test['is_top10'], grid_test_proba),\n"
        "}\n"
        "grid_metrics"
    ))
    cells.append(nbf.v4.new_markdown_cell("## 5. Simple Calibrated Baseline Model"))
    cells.append(nbf.v4.new_code_cell(
        "numeric_features = pre_race_features + ['n_stops', 'avg_stint_tyre_life', 'max_stint_tyre_life', 'pit_loss_total']\n"
        "feature_cols = numeric_features + categorical_features\n\n"
        "numeric_pipe = Pipeline([('imputer', SimpleImputer(strategy='median'))])\n"
        "categorical_pipe = Pipeline([\n"
        "    ('imputer', SimpleImputer(strategy='most_frequent')),\n"
        "    ('onehot', OneHotEncoder(handle_unknown='ignore', min_frequency=5)),\n"
        "])\n"
        "preprocess = ColumnTransformer([\n"
        "    ('num', numeric_pipe, numeric_features),\n"
        "    ('cat', categorical_pipe, categorical_features),\n"
        "])\n"
        "model = GradientBoostingClassifier(\n"
        "    learning_rate=0.04,\n"
        "    n_estimators=140,\n"
        "    max_depth=2,\n"
        "    min_samples_leaf=20,\n"
        "    random_state=RANDOM_SEED,\n"
        ")\n"
        "clf = Pipeline([('preprocess', preprocess), ('model', model)])\n\n"
        "X_train, y_train = train[feature_cols], train['is_top10']\n"
        "X_cal, y_cal = cal[feature_cols], cal['is_top10']\n"
        "X_test, y_test = test[feature_cols], test['is_top10']\n\n"
        "clf.fit(X_train, y_train)\n"
        "cal_raw = clf.predict_proba(X_cal)[:, 1]\n"
        "test_raw = clf.predict_proba(X_test)[:, 1]\n\n"
        "iso = IsotonicRegression(out_of_bounds='clip', y_min=0.001, y_max=0.999)\n"
        "iso.fit(cal_raw, y_cal)\n"
        "test_proba = iso.predict(test_raw)\n\n"
        "model_metrics = {\n"
        "    'model': 'Calibrated GB baseline',\n"
        "    'brier': brier_score_loss(y_test, test_proba),\n"
        "    'log_loss': log_loss(y_test, test_proba, labels=[0, 1]),\n"
        "    'roc_auc': roc_auc_score(y_test, test_proba),\n"
        "}\n"
        "model_metrics"
    ))
    cells.append(nbf.v4.new_markdown_cell("## 6. Test Metrics vs Reference Floors"))
    cells.append(nbf.v4.new_code_cell(
        "results = pd.DataFrame([grid_metrics, model_metrics])\n"
        "results['beats_grid_rule_brier_0.208'] = results['brier'] < 0.208\n"
        "results['beats_docent_brier_0.132'] = results['brier'] < 0.132\n"
        "results['beats_docent_auc_0.892'] = results['roc_auc'] > 0.892\n"
        "display(results)\n\n"
        "best = results.sort_values('brier').iloc[0]\n"
        "print(f\"Best Hito 1 baseline by Brier: {best['model']} | Brier={best['brier']:.3f}, LogLoss={best['log_loss']:.3f}, AUC={best['roc_auc']:.3f}\")"
    ))
    cells.append(nbf.v4.new_markdown_cell("## 7. Calibration Curve on Test Set"))
    cells.append(nbf.v4.new_code_cell(
        "calibration_df = pd.DataFrame({'y': y_test, 'p': test_proba})\n"
        "calibration_df['bin'] = pd.qcut(calibration_df['p'], q=10, duplicates='drop')\n"
        "curve = calibration_df.groupby('bin', observed=True).agg(\n"
        "    mean_pred=('p', 'mean'),\n"
        "    observed_rate=('y', 'mean'),\n"
        "    n=('y', 'size'),\n"
        ").reset_index(drop=True)\n"
        "display(curve)\n\n"
        "fig, ax = plt.subplots(figsize=(6, 5))\n"
        "ax.plot([0, 1], [0, 1], linestyle='--', color='gray', label='perfect calibration')\n"
        "ax.plot(curve['mean_pred'], curve['observed_rate'], marker='o', label='calibrated baseline')\n"
        "for _, row in curve.iterrows():\n"
        "    ax.annotate(int(row['n']), (row['mean_pred'], row['observed_rate']), textcoords='offset points', xytext=(4, 4), fontsize=8)\n"
        "ax.set_xlabel('Mean predicted P(top10)')\n"
        "ax.set_ylabel('Observed top10 rate')\n"
        "ax.set_title('Test calibration curve, 2023-2024')\n"
        "ax.set_xlim(0, 1)\n"
        "ax.set_ylim(0, 1)\n"
        "ax.legend()\n"
        "plt.show()"
    ))
    cells.append(nbf.v4.new_markdown_cell("## 8. Concrete What-If Example"))
    cells.append(nbf.v4.new_code_cell(
        "example = test[(test['season'].eq(2024)) & (test['race_name'].str.contains('Monaco', case=False, na=False)) & (test['driver_name'].eq('Leclerc'))].head(1).copy()\n"
        "if len(example) == 0:\n"
        "    example = test.head(1).copy()\n"
        "scenario_a = example.copy()\n"
        "scenario_b = example.copy()\n"
        "scenario_a[['n_stops', 'compound_sequence', 'avg_stint_tyre_life', 'max_stint_tyre_life', 'pit_loss_total']] = [1, 'MEDIUM-HARD', 34, 44, 22.5]\n"
        "scenario_b[['n_stops', 'compound_sequence', 'avg_stint_tyre_life', 'max_stint_tyre_life', 'pit_loss_total']] = [2, 'MEDIUM-MEDIUM-HARD', 23, 30, 45.0]\n"
        "scenario_probs = iso.predict(clf.predict_proba(pd.concat([scenario_a, scenario_b])[feature_cols])[:, 1])\n"
        "pd.DataFrame({\n"
        "    'scenario': ['one-stop M-H', 'two-stop M-M-H'],\n"
        "    'driver': [example['driver_name'].iloc[0]] * 2,\n"
        "    'race': [example['race_name'].iloc[0]] * 2,\n"
        "    'predicted_P_top10': scenario_probs,\n"
        "})"
    ))

    nb["cells"] = cells
    return nb


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    df = build_dataset()
    df.to_csv(DATA_DIR / "f1_strategy_race_level.csv", index=False)

    nb = make_notebook()
    with (ROOT / "hito1_baseline.ipynb").open("w", encoding="utf-8") as f:
        nbf.write(nb, f)

    summary = {
        "rows": len(df),
        "columns": len(df.columns),
        "seasons": sorted(df["season"].unique().tolist()),
        "target_rate": float(df["is_top10"].mean()),
    }
    (DATA_DIR / "f1_strategy_race_level_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
