"""
car_price_model_advanced.py – FINAL FIXED VERSION
✔ Works with cleaned dataset (Price_Clean)
✔ Fully safe tuning for XGB / LGB / RandomForest
✔ Updated preprocessing for sklearn >= 1.4
✔ Ready for production
"""

import argparse, json, os
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error

import joblib

# ---------------------------------------------------------
# FIXED TARGET COLUMN (cleaned dataset)
# ---------------------------------------------------------
TARGET = "Price_Clean"

# INPUT FEATURES IN CLEANED DATASET
# Battery_Charge_Level: lower % → lower price (EVs); non-EV filled with 0.
# Km_Driven is applied in the API as a post-prediction adjustment (not in training data).
DEFAULT_FEATURES = [
    "Brand","Model","Year",
    "Fuel_Type_Clean","Transmission_Clean",
    "Mileage_Clean","Engine_CC_Clean",
    "Seating_Capacity_Clean","Service_Cost_Clean",
    "Age","Battery_Charge_Level"
]

# ---------------------------------------------------------
# TRY IMPORT XGBOOST / LIGHTGBM
# ---------------------------------------------------------
try:
    from xgboost import XGBRegressor
    _HAS_XGB = True
except:
    _HAS_XGB = False

try:
    from lightgbm import LGBMRegressor
    _HAS_LGB = True
except:
    _HAS_LGB = False

from sklearn.ensemble import RandomForestRegressor


# ---------------------------------------------------------
# PREPROCESSOR
# ---------------------------------------------------------
def build_preprocessor(X):
    categorical = X.select_dtypes(include=["object"]).columns.tolist()
    numeric = X.select_dtypes(include=[np.number]).columns.tolist()

    cat_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False))  # sklearn >= 1.4
    ])

    num_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    pre = ColumnTransformer([
        ("cat", cat_pipe, categorical),
        ("num", num_pipe, numeric)
    ])

    return pre


# ---------------------------------------------------------
# MODEL SELECTOR
# ---------------------------------------------------------
def get_model(name="xgb"):
    if name == "xgb" and _HAS_XGB:
        return XGBRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
            tree_method="hist"
        )

    if name == "lgb" and _HAS_LGB:
        return LGBMRegressor(
            n_estimators=300,
            learning_rate=0.05,
            random_state=42
        )

    # fallback → RandomForest
    return RandomForestRegressor(n_estimators=300, random_state=42)


# ---------------------------------------------------------
# TRAIN FUNCTION
# ---------------------------------------------------------
def train(data_path, out_path, model_name="xgb", test_size=0.2, tune=False, n_iter=20):

    df = pd.read_csv(data_path)

    if TARGET not in df.columns:
        raise ValueError(f"Target column '{TARGET}' not found in dataset!")

    # Ensure Battery_Charge_Level exists, fill NaN with 0 for non-electric cars
    if 'Battery_Charge_Level' not in df.columns:
        df['Battery_Charge_Level'] = np.nan
    
    # Fill NaN battery charge level with 0 for non-electric cars
    df['Battery_Charge_Level'] = df['Battery_Charge_Level'].fillna(0)
    
    X = df[DEFAULT_FEATURES].copy()
    y = df[TARGET].copy()

    pre = build_preprocessor(X)
    model = get_model(model_name)

    pipe = Pipeline([
        ("preprocessor", pre),
        ("model", model)
    ])

    # -----------------------------------------------------
    # TUNING
    # -----------------------------------------------------
    if tune:

        # XGBoost Tuning
        if model_name == "xgb" and _HAS_XGB:
            params = {
                "model__n_estimators": [200, 300, 400],
                "model__max_depth": [4, 6, 8],
                "model__learning_rate": [0.03, 0.05, 0.1],
                "model__subsample": [0.7, 0.9, 1.0],
                "model__colsample_bytree": [0.7, 1.0]
            }

        # LightGBM Tuning
        elif model_name == "lgb" and _HAS_LGB:
            params = {
                "model__n_estimators": [200, 300, 500],
                "model__num_leaves": [31, 60, 90],
                "model__learning_rate": [0.03, 0.05, 0.1]
            }

        # RandomForest fallback tuning
        else:
            params = {
                "model__n_estimators": [200, 300, 500],
                "model__max_depth": [None, 8, 12],
                "model__min_samples_split": [2, 4, 6],
                "model__min_samples_leaf": [1, 2, 4]
            }

        search = RandomizedSearchCV(
            pipe,
            params,
            n_iter=n_iter,
            cv=3,
            scoring="neg_mean_absolute_error",
            n_jobs=-1,
            verbose=1,
            random_state=42
        )
        search.fit(X, y)
        pipe = search.best_estimator_

    else:
        pipe.fit(X, y)

    # -----------------------------------------------------
    # Evaluate
    # -----------------------------------------------------
    preds = pipe.predict(X)
    mae = mean_absolute_error(y, preds)
    rmse = root_mean_squared_error(y, preds)
    r2 = r2_score(y, preds)

    metrics = {"MAE": mae, "RMSE": rmse, "R2": r2}

    with open(out_path.replace(".joblib", "_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    joblib.dump(pipe, out_path)

    print("Training Completed!")
    print("Metrics:", metrics)


# ---------------------------------------------------------
# PREDICT FUNCTION
# ---------------------------------------------------------
def predict(model_path, input_json):
    pipe = joblib.load(model_path)
    data = json.loads(input_json)
    x = pd.DataFrame([data])
    return pipe.predict(x)[0]


# ---------------------------------------------------------
# CLI
# ---------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser()

    sub = p.add_subparsers(dest="cmd")

    t = sub.add_parser("train")
    t.add_argument("--data", required=True)
    t.add_argument("--out", required=True)
    t.add_argument("--model", default="xgb")
    t.add_argument("--test-size", type=float, default=0.2)
    t.add_argument("--tune", action="store_true")
    t.add_argument("--n-iter", type=int, default=20)

    p2 = sub.add_parser("predict")
    p2.add_argument("--model", required=True)
    p2.add_argument("--input", required=True)

    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.cmd == "train":
        train(args.data, args.out, args.model, args.test_size, args.tune, args.n_iter)

    elif args.cmd == "predict":
        print(predict(args.model, args.input))
