from pathlib import Path
import json
import shutil

import nbformat as nbf
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[2]
SOURCE_DIR = WORKSPACE / "excel_capstone"
DATA_DIR = ROOT / "data"


def copy_capstone_data() -> dict:
    DATA_DIR.mkdir(exist_ok=True)
    race_source = SOURCE_DIR / "f1_strategy_race_level.csv"
    lap_source = SOURCE_DIR / "f1_strategy_lap_level.csv"
    race_dest = DATA_DIR / "f1_strategy_race_level.csv"
    lap_dest = DATA_DIR / "f1_strategy_lap_level.csv"

    if race_source.exists():
        shutil.copy2(race_source, race_dest)
    elif not race_dest.exists():
        raise FileNotFoundError(
            "Missing f1_strategy_race_level.csv. Place it in data/ or excel_capstone/."
        )

    if lap_source.exists():
        shutil.copy2(lap_source, lap_dest)

    df = pd.read_csv(race_dest)
    summary = {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "seasons": sorted(df["season"].unique().astype(int).tolist()),
        "target_rate": float(df["is_top10"].mean()),
        "source": "excel_capstone/f1_strategy_race_level.csv",
        "lap_level_included": lap_dest.exists(),
    }
    (DATA_DIR / "f1_strategy_race_level_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


def make_notebook() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    nb["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    }
    cells = []
    cells.append(nbf.v4.new_markdown_cell(
        "# Hito 1 Baseline - F1 Race Strategy Advisor\n\n"
        "This notebook uses the official race-level capstone file, implements the locked "
        "target (`is_top10`) and temporal split, calibrates on 2022 only, and evaluates "
        "once on the untouched 2023-2024 test block."
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
    cells.append(nbf.v4.new_markdown_cell("## 1. Load Official Race-Level Data"))
    cells.append(nbf.v4.new_code_cell(
        "df = pd.read_csv(DATA_PATH)\n"
        "print(df.shape)\n"
        "display(df.head())\n"
        "required = {'season', 'is_top10', 'grid_position', 'n_stops', 'compound_sequence'}\n"
        "assert required.issubset(df.columns), required - set(df.columns)"
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
        "pre_race_numeric = [\n"
        "    'grid_position', 'qualifying_position', 'driver_prior3_avg_finish',\n"
        "    'constructor_prior3_avg_finish', 'driver_circuit_prior_avg'\n"
        "]\n"
        "pre_race_categorical = ['circuit_type', 'constructor_tier', 'constructor_name']\n"
        "scenario_numeric = [\n"
        "    'n_stops', 'stint1_length', 'stint2_length', 'stint3_length', 'stint4_length',\n"
        "    'stint5_length', 'avg_pit_stop_duration_s', 'total_pit_time_s',\n"
        "    'first_pit_lap', 'last_pit_lap'\n"
        "]\n"
        "scenario_categorical = ['strategy_type', 'compound_sequence']\n"
        "audit_columns = [\n"
        "    'finish_position', 'points', 'positions_gained', 'is_top3', 'is_top5', 'dnf',\n"
        "    'status', 'track_status_summary', 'safety_car_periods', 'safety_car_laps',\n"
        "    'vsc_laps', 'weather_actual', 'wet_laps', 'avg_track_temp', 'avg_air_temp',\n"
        "    'qualifying_time_s'\n"
        "]\n\n"
        "audit = pd.DataFrame([\n"
        "    {'column_group': 'pre-race predictors', 'columns': ', '.join(pre_race_numeric + pre_race_categorical), 'model_use': 'Allowed as information available before the race weekend decision.'},\n"
        "    {'column_group': 'scenario inputs', 'columns': ', '.join(scenario_numeric + scenario_categorical), 'model_use': 'Allowed only because the advisor compares user-set pit strategy scenarios.'},\n"
        "    {'column_group': 'audit / outcome columns', 'columns': ', '.join(audit_columns), 'model_use': 'Not used as predictors for fitting, calibration, or model selection.'},\n"
        "])\n"
        "display(audit)\n\n"
        "used_features = pre_race_numeric + pre_race_categorical + scenario_numeric + scenario_categorical\n"
        "for col in ['finish_position', 'points', 'positions_gained', 'dnf', 'status', 'safety_car_periods', 'weather_actual', 'wet_laps']:\n"
        "    assert col not in used_features"
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
    cells.append(nbf.v4.new_markdown_cell("## 5. Simple Calibrated Strategy Baseline"))
    cells.append(nbf.v4.new_code_cell(
        "numeric_features = pre_race_numeric + scenario_numeric\n"
        "categorical_features = pre_race_categorical + scenario_categorical\n"
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
        "    'model': 'Calibrated GB strategy baseline',\n"
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
        "scenario_a[['n_stops', 'strategy_type', 'compound_sequence', 'stint1_length', 'stint2_length', 'stint3_length', 'avg_pit_stop_duration_s', 'total_pit_time_s', 'first_pit_lap', 'last_pit_lap']] = [1, 'one_stop', 'M-H', 34, 44, 0, 22.5, 22.5, 34, 34]\n"
        "scenario_b[['n_stops', 'strategy_type', 'compound_sequence', 'stint1_length', 'stint2_length', 'stint3_length', 'avg_pit_stop_duration_s', 'total_pit_time_s', 'first_pit_lap', 'last_pit_lap']] = [2, 'two_stop', 'M-M-H', 22, 21, 35, 22.5, 45.0, 22, 43]\n"
        "scenario_probs = iso.predict(clf.predict_proba(pd.concat([scenario_a, scenario_b])[feature_cols])[:, 1])\n"
        "pd.DataFrame({\n"
        "    'scenario': ['one-stop M-H', 'two-stop M-M-H'],\n"
        "    'driver': [example['driver_name'].iloc[0]] * 2,\n"
        "    'race': [example['race_name'].iloc[0]] * 2,\n"
        "    'predicted_P_top10': scenario_probs,\n"
        "    'delta_vs_first': scenario_probs - scenario_probs[0],\n"
        "})"
    ))
    nb["cells"] = cells
    return nb


def main() -> None:
    copy_capstone_data()
    nb = make_notebook()
    with (ROOT / "hito1_baseline.ipynb").open("w", encoding="utf-8") as f:
        nbf.write(nb, f)


if __name__ == "__main__":
    main()
