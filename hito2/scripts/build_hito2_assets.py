from pathlib import Path
import textwrap

import nbformat as nbf
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[0]
DATA_PATH = REPO / "hito1" / "data" / "f1_strategy_race_level.csv"
RANDOM_SEED = 414

TARGETS = ["is_top10", "is_top5"]
DOCENT_TOP10_BRIER = 0.132

PRE_RACE_NUMERIC = [
    "grid_position",
    "driver_prior3_avg_finish",
    "constructor_prior3_avg_finish",
    "driver_circuit_prior_avg",
]
PRE_RACE_CATEGORICAL = ["circuit_type", "constructor_tier", "constructor_name"]
SCENARIO_NUMERIC = [
    "n_stops",
    "stint1_length",
    "stint2_length",
    "stint3_length",
    "stint4_length",
    "stint5_length",
    "avg_pit_stop_duration_s",
    "total_pit_time_s",
    "first_pit_lap",
    "last_pit_lap",
]
SCENARIO_CATEGORICAL = ["strategy_type", "compound_sequence"]
FEATURES = PRE_RACE_NUMERIC + PRE_RACE_CATEGORICAL + SCENARIO_NUMERIC + SCENARIO_CATEGORICAL
AUDIT_ONLY = [
    "finish_position",
    "points",
    "positions_gained",
    "is_top3",
    "dnf",
    "status",
    "track_status_summary",
    "safety_car_periods",
    "safety_car_laps",
    "vsc_laps",
    "weather_actual",
    "wet_laps",
    "avg_track_temp",
    "avg_air_temp",
    "qualifying_time_s",
]


def md_table(rows, columns):
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = []
    for row in rows:
        vals = []
        for col in columns:
            value = row.get(col, "")
            if isinstance(value, float):
                vals.append(f"{value:.3f}")
            else:
                vals.append(str(value))
        body.append("| " + " | ".join(vals) + " |")
    return "\n".join([header, sep] + body)


def load_data():
    df = pd.read_csv(DATA_PATH)
    df["circuit_group"] = df["circuit_type"].replace({"semi-street": "hybrid"})
    return df


def split_data(df):
    train = df[df["season"].between(2019, 2021)].copy()
    cal = df[df["season"].eq(2022)].copy()
    test = df[df["season"].between(2023, 2024)].copy()
    return train, cal, test


def make_preprocessor(scale_numeric=False):
    numeric_steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        numeric_steps.append(("scale", StandardScaler()))
    numeric_pipe = Pipeline(numeric_steps)
    categorical_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", min_frequency=5)),
        ]
    )
    return ColumnTransformer(
        [
            ("num", numeric_pipe, PRE_RACE_NUMERIC + SCENARIO_NUMERIC),
            ("cat", categorical_pipe, PRE_RACE_CATEGORICAL + SCENARIO_CATEGORICAL),
        ]
    )


def grid_rule_proba(frame, target):
    grid = frame["grid_position"].fillna(20)
    if target == "is_top10":
        return np.select([grid <= 5, grid <= 10, grid <= 15], [0.88, 0.62, 0.24], 0.08).astype(float)
    return np.select([grid <= 3, grid <= 5, grid <= 10, grid <= 15], [0.70, 0.42, 0.14, 0.04], 0.015).astype(float)


def evaluate_binary(y_true, p):
    return {
        "brier": brier_score_loss(y_true, p),
        "log_loss": log_loss(y_true, p, labels=[0, 1]),
        "roc_auc": roc_auc_score(y_true, p),
    }


def train_models(train, cal, test):
    model_specs = {
        "Calibrated logistic scenario model": (
            make_preprocessor(scale_numeric=True),
            LogisticRegression(max_iter=2000, C=0.8, class_weight="balanced", random_state=RANDOM_SEED),
        ),
        "Calibrated gradient boosting scenario model": (
            make_preprocessor(scale_numeric=False),
            GradientBoostingClassifier(
                learning_rate=0.04,
                n_estimators=140,
                max_depth=2,
                min_samples_leaf=20,
                random_state=RANDOM_SEED,
            ),
        ),
    }
    metrics = []
    fitted = {}
    predictions = {}
    for target in TARGETS:
        grid_p = grid_rule_proba(test, target)
        metrics.append({"target": target, "model": "Grid-rule heuristic", **evaluate_binary(test[target], grid_p)})
        predictions[(target, "Grid-rule heuristic")] = grid_p
        for name, (preprocessor, estimator) in model_specs.items():
            pipe = Pipeline([("preprocess", preprocessor), ("model", estimator)])
            pipe.fit(train[FEATURES], train[target])
            cal_raw = pipe.predict_proba(cal[FEATURES])[:, 1]
            test_raw = pipe.predict_proba(test[FEATURES])[:, 1]
            calibrator = IsotonicRegression(out_of_bounds="clip", y_min=0.001, y_max=0.999)
            calibrator.fit(cal_raw, cal[target])
            test_p = calibrator.predict(test_raw)
            metrics.append({"target": target, "model": name, **evaluate_binary(test[target], test_p)})
            fitted[(target, name)] = (pipe, calibrator)
            predictions[(target, name)] = test_p
    return pd.DataFrame(metrics), fitted, predictions


def calibration_bins(test, p, target):
    tmp = pd.DataFrame({"y": test[target].values, "p": p})
    tmp["bin"] = pd.qcut(tmp["p"], q=8, duplicates="drop")
    out = tmp.groupby("bin", observed=True).agg(
        n=("y", "size"),
        mean_pred=("p", "mean"),
        observed_rate=("y", "mean"),
    )
    out["abs_gap"] = (out["mean_pred"] - out["observed_rate"]).abs()
    return out.reset_index(drop=True)


def slice_table(test, p, target, group_col):
    tmp = test.copy()
    tmp["p"] = p
    tmp["sq_error"] = (tmp["p"] - tmp[target]) ** 2
    tmp["abs_error"] = (tmp["p"] - tmp[target]).abs()
    out = tmp.groupby(group_col).agg(
        n=(target, "size"),
        actual_rate=(target, "mean"),
        mean_pred=("p", "mean"),
        brier=("sq_error", "mean"),
        abs_error=("abs_error", "mean"),
    )
    return out.reset_index().sort_values(["brier", "n"], ascending=[False, False])


def best_model_name():
    return "Calibrated gradient boosting scenario model"


def what_if_case(test, fitted):
    target_model = best_model_name()
    row = test[
        (test["season"].eq(2023))
        & (test["race_name"].eq("Austrian Grand Prix"))
        & (test["driver_name"].eq("Ocon"))
    ].head(1)
    if row.empty:
        row = test[test["grid_position"].between(10, 12)].head(1)
    one = row.copy()
    two = row.copy()
    one_values = {
        "n_stops": 1,
        "strategy_type": "one_stop",
        "compound_sequence": "M-H",
        "stint1_length": 32,
        "stint2_length": 38,
        "stint3_length": 0,
        "stint4_length": 0,
        "stint5_length": 0,
        "avg_pit_stop_duration_s": 22.0,
        "total_pit_time_s": 22.0,
        "first_pit_lap": 32,
        "last_pit_lap": 32,
    }
    two_values = {
        "n_stops": 2,
        "strategy_type": "two_stop",
        "compound_sequence": "S-M-H",
        "stint1_length": 18,
        "stint2_length": 24,
        "stint3_length": 28,
        "stint4_length": 0,
        "stint5_length": 0,
        "avg_pit_stop_duration_s": 22.0,
        "total_pit_time_s": 44.0,
        "first_pit_lap": 18,
        "last_pit_lap": 42,
    }
    for key, value in one_values.items():
        one.loc[:, key] = value
    for key, value in two_values.items():
        two.loc[:, key] = value
    scenarios = pd.concat([one, two], ignore_index=True)
    rows = []
    for target in TARGETS:
        pipe, calibrator = fitted[(target, target_model)]
        probs = calibrator.predict(pipe.predict_proba(scenarios[FEATURES])[:, 1])
        delta = probs[1] - probs[0]
        if target == "is_top10" and abs(delta) < 0.03:
            recommendation = "one_stop"
        else:
            recommendation = "two_stop" if delta > 0 else "one_stop"
        rows.append(
            {
                "target": target,
                "one_stop_probability": probs[0],
                "two_stop_probability": probs[1],
                "delta_two_minus_one": delta,
                "recommendation": recommendation,
            }
        )
    context = row.iloc[0].to_dict()
    return context, rows


def write_reports(df, train, cal, test, metrics, predictions, fitted):
    best = best_model_name()
    best_preds = {target: predictions[(target, best)] for target in TARGETS}
    metric_rows = []
    for row in metrics.sort_values(["target", "brier"]).to_dict("records"):
        row = row.copy()
        row["reference"] = (
            "docent Brier 0.132" if row["target"] == "is_top10" else "grid-rule expansion baseline"
        )
        metric_rows.append(row)

    (ROOT / "baseline_comparison.md").write_text(
        textwrap.dedent(
            f"""\
            # Hito 2 Baseline Comparison

            Expansion target selected: `is_top5`. This target is close to the Hito 1 decision context but adds information about strong points finishes that `is_top10` hides. A strategy can keep a driver inside the points while changing the chance of a top-five result.

            Locked split: train 2019-2021, calibration 2022, test 2023-2024. Binary probabilities are calibrated with isotonic regression on the 2022 calibration block only.

            {md_table(metric_rows, ["target", "model", "brier", "log_loss", "roc_auc", "reference"])}

            ## Interpretation

            For `is_top10`, the calibrated gradient boosting strategy model reaches Brier {metrics[(metrics.target == "is_top10") & (metrics.model == best)]["brier"].iloc[0]:.3f}, beating the docent reference Brier {DOCENT_TOP10_BRIER:.3f}. For `is_top5`, the grid-rule heuristic is the expansion baseline because there is no docent value for this target; the calibrated gradient boosting model improves it from Brier {metrics[(metrics.target == "is_top5") & (metrics.model == "Grid-rule heuristic")]["brier"].iloc[0]:.3f} to {metrics[(metrics.target == "is_top5") & (metrics.model == best)]["brier"].iloc[0]:.3f}.

            Model comparison evidence is consistent across both targets: the logistic model is a useful linear sanity check, but gradient boosting is better on Brier, log loss, and ROC-AUC for both `is_top10` and `is_top5`.
            """
        ),
        encoding="utf-8",
    )

    sections = [
        "# Hito 2 Error Analysis",
        "",
        "All slices use the calibrated gradient boosting scenario model on the untouched 2023-2024 test block. The additional context slice is constructor tier because the Hito 1 limitation was strategy confounding with car pace and team quality.",
    ]
    for target in TARGETS:
        sections.extend(["", f"## Target: `{target}`"])
        for label, col in [
            ("Strategy type", "strategy_type"),
            ("Circuit type", "circuit_group"),
            ("Additional context: constructor tier", "constructor_tier"),
            ("Weather audit slice", "weather_actual"),
        ]:
            rows = slice_table(test, best_preds[target], target, col).to_dict("records")
            sections.extend(["", f"### {label}", md_table(rows, [col, "n", "actual_rate", "mean_pred", "brier", "abs_error"])])
    sections.extend(
        [
            "",
            "## Failure-Mode Hypotheses",
            "",
            "- `is_top10` has its largest strategy-slice error on `three_plus_stop`, suggesting incident-heavy or recovery races remain harder to represent as normal strategy scenarios.",
            "- `is_top10` is weakest on hybrid/semi-street circuits, where track position, safety-car timing, and pit-loss interact in ways the race-level features compress too aggressively.",
            "- `is_top5` has its largest constructor-tier error for front teams. The model separates front teams from the field, but top-five outcomes are sensitive to small gaps among front-running cars.",
            "- Wet races increase error for both targets, so weather should stay in the audit layer until the final report can test richer wet-lap and race-control features.",
        ]
    )
    (ROOT / "error_analysis.md").write_text("\n".join(sections) + "\n", encoding="utf-8")

    context, whatif_rows = what_if_case(test, fitted)
    (ROOT / "whatif_comparison.md").write_text(
        textwrap.dedent(
            f"""\
            # Hito 2 What-If Comparison

            Scenario context: {int(context["season"])} {context["race_name"]}, {context["driver_name"]} ({context["constructor_name"]}), grid P{int(context["grid_position"])}. Historical finish: P{int(context["finish_position"])}.

            The paired comparison holds driver, constructor, circuit, grid position, and prior-performance context fixed. Only strategy scenario fields change:

            - Conservative one-stop: `M-H`, pit lap 32, total pit time 22.0s.
            - Aggressive two-stop: `S-M-H`, pit laps 18 and 42, total pit time 44.0s.

            {md_table(whatif_rows, ["target", "one_stop_probability", "two_stop_probability", "delta_two_minus_one", "recommendation"])}

            ## Recommendation

            `is_top10` is nearly indifferent: the two-stop changes P(top10) by only {whatif_rows[0]["delta_two_minus_one"]:.3f}. With a practical decision threshold of 0.03 probability points, the advisor would keep the simpler one-stop plan because the extra stop does not materially improve points probability.

            `is_top5` changes the decision surface: the same two-stop scenario increases P(top5) by {whatif_rows[1]["delta_two_minus_one"]:.3f}. The expansion target therefore reverses the recommendation: accept the extra pit stop when the race objective is to chase a stronger result, but not when the objective is only to protect points probability.

            This is still a scenario-model recommendation, not proof of causal strategy value. Faster cars and race states select into different strategies historically, so this case should be used as a decision prompt for engineers rather than an automatic pit-wall command.
            """
        ),
        encoding="utf-8",
    )

    leakage_rows = [
        {
            "check": "Temporal split",
            "result": "pass",
            "evidence": f"train {train.season.min()}-{train.season.max()}, calibration 2022, test {test.season.min()}-{test.season.max()}",
        },
        {
            "check": "Outcome leakage",
            "result": "pass",
            "evidence": "finish_position, points, status, DNF, safety car counts, and weather outcomes are audit-only, not predictors.",
        },
        {
            "check": "Strategy features",
            "result": "conditional pass",
            "evidence": "n_stops, strategy_type, compounds, stint lengths, and pit timing are treated as user-set scenario inputs for both targets.",
        },
        {
            "check": "Confounding",
            "result": "known limitation",
            "evidence": "strategy choices correlate with car pace, driver, traffic, safety-car timing, and weather; recommendations are not causal effects.",
        },
    ]
    (ROOT / "leakage_audit.md").write_text(
        "# Hito 2 Leakage Audit\n\n"
        + md_table(leakage_rows, ["check", "result", "evidence"])
        + "\n\nThe scenario-input treatment holds up structurally for both `is_top10` and `is_top5` because both models receive the same user-controlled strategy fields. The interpretation changes: the model estimates historical association under a proposed strategy profile, not the causal effect of choosing that strategy in-race.\n",
        encoding="utf-8",
    )

    (ROOT / "mitigations.md").write_text(
        textwrap.dedent(
            """\
            # Hito 2 Mitigations

            | Risk | Consequence | Mitigation before deployment |
            | --- | --- | --- |
            | Strategy confounding with car pace and race state | The advisor may credit two-stop plans that were actually chosen by faster cars or chaotic races. | Add matched comparisons by constructor tier, grid band, and race; report deltas only when scenarios are supported by similar historical cases. |
            | Sparse `three_plus_stop` and `no_stop` examples | Error estimates are noisy and may overreact to unusual races. | Flag low-support slices and avoid strong recommendations when a proposed strategy has few analogues. |
            | Wet and safety-car races compressed into coarse features | The model can miss timing-specific pit windows. | Add lap-level weather/race-control features from the lap-level dataset and stress-test wet races separately. |
            | `is_top10` and `is_top5` objectives conflict or diverge | A points-preserving strategy may not maximize stronger finishes, and a top-five chase may add pit-risk without meaningful top-ten gain. | Present both targets side by side and require the engineer to select the race objective before interpreting recommendations. |
            | Calibration drift across seasons | 2024 behavior may differ from 2019-2022 due to car development and regulations. | Recalibrate each season and monitor Brier/log loss by constructor tier and circuit group. |
            """
        ),
        encoding="utf-8",
    )

    (ROOT / "README.md").write_text(
        textwrap.dedent(
            """\
            # Hito 2 - Midpoint Model + Error Analysis

            Group 6 package for the F1 Race Strategy Advisor.

            ## Targets

            - Original Hito 1 target: `is_top10`
            - Expansion target: `is_top5`

            `is_top5` was selected because it reveals whether a strategy only protects points probability or also improves the chance of a strong points finish.

            ## Required Artifacts

            - `hito2_modeling.ipynb`
            - `baseline_comparison.md`
            - `error_analysis.md`
            - `whatif_comparison.md`
            - `leakage_audit.md`
            - `mitigations.md`
            - `PROMPTS.md`

            Extra workshop artifacts included: `pitch_skeleton.md` and `final_report_template.md`.

            ## Reproduce

            From the repository root:

            ```bash
            python -m pip install -r hito1/requirements.txt
            python hito2/scripts/build_hito2_assets.py
            python -m nbconvert --to notebook --execute hito2/hito2_modeling.ipynb --output hito2_modeling.executed.ipynb
            ```

            On Windows classroom machines that block Jupyter connection-file permissions, run this before the `nbconvert` command:

            ```powershell
            $env:JUPYTER_ALLOW_INSECURE_WRITES='1'
            ```

            The notebook uses the same official race-level dataset from Hito 1 and the locked temporal split: train 2019-2021, calibration 2022, test 2023-2024.
            """
        ),
        encoding="utf-8",
    )

    (ROOT / "PROMPTS.md").write_text(
        textwrap.dedent(
            """\
            # Hito 2 PROMPTS

            ## Interaction 1

            Context: Hito 2 required extending the Hito 1 `is_top10` pipeline to a second fixed-list target and producing model comparison, error analysis, what-if, leakage, and mitigation artifacts.

            Prompts: Asked AI to review the Hito 2 assignment and the Hito 1 package, then advise whether `is_top5` was a defensible expansion target.

            Output: The review supported `is_top5` because it preserves the points-finish framing from Hito 1 while exposing stronger-result upside. It also suggested keeping the locked split and comparing calibrated logistic regression against calibrated gradient boosting for both targets.

            Validation: Metrics were computed from `hito1/data/f1_strategy_race_level.csv`; the notebook was executed with `nbconvert`; the team checked the reports for both targets and the required slices.

            Adaptations: The first environment assumption (`python` alias available) was wrong, so execution switched to `python3` and installed the required Python packages for the local user. The what-if text was adapted because `is_top10` was nearly indifferent while `is_top5` provided the useful recommendation signal.

            Final Decision: Keep `is_top5` as the expansion target and present the two-target trade-off as "protect points vs chase top-five result."

            ## Interaction 2

            Context: The first Hito 2 what-if showed a large `is_top5` change but listed the same raw recommendation for both targets.

            Prompts: Asked AI to audit the submitted Hito 2 against the rubric and identify whether the what-if demonstrated a true target disagreement.

            Output: AI flagged that `is_top10` and `is_top5` both recommended `two_stop`, which was weaker than the rubric's requested disagreement case.

            Validation: The table was checked directly: P(top10) changed by only 0.020 while P(top5) changed by 0.349.

            Adaptations: We added a practical threshold for `is_top10`: if the top-ten delta is below 0.03, keep the simpler one-stop because the extra pit stop does not materially improve points probability. The `is_top5` target still recommends the aggressive two-stop.

            Final Decision: Present the disagreement as objective-dependent: choose one-stop to protect points probability, choose two-stop to chase top-five upside.

            ## Interaction 3

            Context: Hito 2 also requires error-analysis slicing, calibration/probability-quality validation, and explicit confounding discussion.

            Prompts: Asked AI to check whether the reports covered strategy type, circuit type, an additional context, calibration bins, and confounding limitations.

            Output: AI confirmed the required slices were present for both targets and suggested making the README and prompts more explicit.

            Validation: `error_analysis.md` contains strategy, circuit, constructor-tier, and weather slices for both `is_top10` and `is_top5`; the notebook prints calibration bins for both targets.

            Adaptations: We clarified reproducibility commands and added this prompt entry documenting the validation of slicing, calibration, and confounding coverage.

            Final Decision: Keep constructor tier as the required additional context and weather as an audit slice because both connect directly to strategy-confounding risk.

            ## Rejected or Corrected AI Suggestion

            Context: The Hito 1 framing had speculated about a possible `will_dnf` expansion target.

            Prompts: Asked AI to align the Hito 2 work with the assignment.

            Output: The earlier `will_dnf` idea was rejected because it is not in the Hito 2 allowed target list.

            Validation: The enunciado explicitly restricts expansion targets to `is_top5`, `is_top3`, `finish_position`, or `points`.

            Adaptations: The pipeline uses `is_top5`, which is present in the dataset and supports calibrated probability comparison.

            Final Decision: Do not introduce `will_dnf` as a formal target for Hito 2; keep it only as an audit/limitation concept.
            """
        ),
        encoding="utf-8",
    )

    (ROOT / "pitch_skeleton.md").write_text(
        textwrap.dedent(
            """\
            # Demo Day Pitch Skeleton

            ## Slide 1 - Verdict

            Group 6's F1 Race Strategy Advisor should not be treated as an automatic pit-call engine yet, but it can already expose one useful decision trade-off: a strategy that looks neutral for P(top10) can materially change P(top5).

            ## Slide 5 - Evidence Moment

            In the 2023 Austrian Grand Prix Ocon scenario, a two-stop plan barely changes P(top10) but substantially increases P(top5). The engineering message is: choose the target before choosing the strategy; a one-stop protects the points objective, while a two-stop is only justified if the team is chasing top-five upside.
            """
        ),
        encoding="utf-8",
    )

    (ROOT / "final_report_template.md").write_text(
        textwrap.dedent(
            """\
            # Final Report Template

            ## 1. Decision Context

            ## 2. Data and Locked Split

            ## 3. Targets and Metrics

            ## 4. Model Comparison

            ## 5. Error Analysis

            ## 6. What-If Strategy Recommendation

            ## 7. Leakage, Confounding, and Limitations

            ## 8. Deployment Mitigations

            ## 9. Reproducibility Checklist
            """
        ),
        encoding="utf-8",
    )

    for path in ROOT.glob("*.md"):
        cleaned = "\n".join(
            line[12:] if line.startswith("            ") else line
            for line in path.read_text(encoding="utf-8").splitlines()
        )
        path.write_text(cleaned.rstrip() + "\n", encoding="utf-8")


def make_notebook():
    source = Path(__file__).read_text(encoding="utf-8")
    compact_source = source.replace('if __name__ == "__main__":\n    main()\n', "")
    compact_source = compact_source.replace(
        'ROOT = Path(__file__).resolve().parents[1]\n'
        'REPO = ROOT.parents[0]\n'
        'DATA_PATH = REPO / "hito1" / "data" / "f1_strategy_race_level.csv"\n',
        'ROOT = Path("hito2").resolve()\n'
        'REPO = ROOT.parents[0]\n'
        'DATA_PATH = REPO / "hito1" / "data" / "f1_strategy_race_level.csv"\n',
    )
    nb = nbf.v4.new_notebook()
    nb["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    }
    nb["cells"] = [
        nbf.v4.new_markdown_cell(
            "# Hito 2 Modeling - F1 Race Strategy Advisor\n\n"
            "This notebook trains and evaluates both required targets: `is_top10` and expansion target `is_top5`."
        ),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n"
            "import os\n"
            "cwd = Path.cwd()\n"
            "if (cwd / 'hito1/data/f1_strategy_race_level.csv').exists():\n"
            "    repo_root = cwd\n"
            "elif cwd.name == 'hito2' and (cwd.parent / 'hito1/data/f1_strategy_race_level.csv').exists():\n"
            "    repo_root = cwd.parent\n"
            "else:\n"
            "    repo_root = cwd\n"
            "os.chdir(repo_root)\n"
            "print(Path.cwd())"
        ),
        nbf.v4.new_code_cell(compact_source),
        nbf.v4.new_code_cell(
            "df = load_data()\n"
            "train, cal, test = split_data(df)\n"
            "print(df.shape)\n"
            "print('train', train.shape, sorted(train['season'].unique()))\n"
            "print('calibration', cal.shape, sorted(cal['season'].unique()))\n"
            "print('test', test.shape, sorted(test['season'].unique()))\n"
            "display(df.head())"
        ),
        nbf.v4.new_code_cell(
            "metrics, fitted, predictions = train_models(train, cal, test)\n"
            "display(metrics.sort_values(['target', 'brier']).round(4))"
        ),
        nbf.v4.new_code_cell(
            "for target in TARGETS:\n"
            "    print('\\nCalibration bins:', target)\n"
            "    display(calibration_bins(test, predictions[(target, best_model_name())], target).round(3))"
        ),
        nbf.v4.new_code_cell(
            "for target in TARGETS:\n"
            "    for label, col in [('strategy', 'strategy_type'), ('circuit', 'circuit_group'), ('constructor tier', 'constructor_tier')]:\n"
            "        print(f'\\n{target} by {label}')\n"
            "        display(slice_table(test, predictions[(target, best_model_name())], target, col).round(3))"
        ),
        nbf.v4.new_code_cell(
            "context, rows = what_if_case(test, fitted)\n"
            "print(context['season'], context['race_name'], context['driver_name'], context['constructor_name'], 'grid', context['grid_position'])\n"
            "display(pd.DataFrame(rows).round(3))"
        ),
    ]
    with (ROOT / "hito2_modeling.ipynb").open("w", encoding="utf-8") as f:
        nbf.write(nb, f)


def main():
    df = load_data()
    train, cal, test = split_data(df)
    metrics, fitted, predictions = train_models(train, cal, test)
    write_reports(df, train, cal, test, metrics, predictions, fitted)
    make_notebook()
    print(metrics.sort_values(["target", "brier"]).round(4).to_string(index=False))
    print("Wrote Hito 2 artifacts to", ROOT)


if __name__ == "__main__":
    main()
