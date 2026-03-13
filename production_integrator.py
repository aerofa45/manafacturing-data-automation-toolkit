import argparse
import sqlite3
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "Timestamp",
    "Shift",
    "Machine_ID",
    "Product_Code",
    "Total_Produced",
    "Good_Units",
    "Scrap_Count",
    "Downtime_Minutes",
    "Planned_Production_Minutes",
    "Ideal_Run_Rate_Per_Min",
]


NUMERIC_COLUMNS = [
    "Total_Produced",
    "Good_Units",
    "Scrap_Count",
    "Downtime_Minutes",
    "Planned_Production_Minutes",
    "Ideal_Run_Rate_Per_Min",
]


def validate_columns(df: pd.DataFrame) -> None:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def clean_factory_data(df: pd.DataFrame) -> pd.DataFrame:
    validate_columns(df)

    cleaned = df.copy()
    cleaned["Timestamp"] = pd.to_datetime(cleaned["Timestamp"], errors="coerce")

    for col in NUMERIC_COLUMNS:
        cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")

    cleaned = cleaned.dropna(subset=["Timestamp"] + NUMERIC_COLUMNS)

    cleaned = cleaned[cleaned["Total_Produced"] >= 0]
    cleaned = cleaned[cleaned["Good_Units"] >= 0]
    cleaned = cleaned[cleaned["Scrap_Count"] >= 0]
    cleaned = cleaned[cleaned["Planned_Production_Minutes"] > 0]
    cleaned = cleaned[cleaned["Ideal_Run_Rate_Per_Min"] > 0]

    cleaned["Shift"] = cleaned["Shift"].astype(str).str.strip()
    cleaned["Machine_ID"] = cleaned["Machine_ID"].astype(str).str.strip()
    cleaned["Product_Code"] = cleaned["Product_Code"].astype(str).str.strip()

    return cleaned


def add_kpis(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["Run_Time_Minutes"] = (
        result["Planned_Production_Minutes"] - result["Downtime_Minutes"]
    ).clip(lower=0)

    result["Quality_Yield"] = result["Good_Units"] / result["Total_Produced"].replace(0, pd.NA)
    result["Scrap_Rate"] = result["Scrap_Count"] / result["Total_Produced"].replace(0, pd.NA)
    result["Availability"] = result["Run_Time_Minutes"] / result["Planned_Production_Minutes"]

    theoretical_output = result["Run_Time_Minutes"] * result["Ideal_Run_Rate_Per_Min"]
    result["Performance"] = result["Total_Produced"] / theoretical_output.replace(0, pd.NA)
    result["Estimated_OEE"] = (
        result["Availability"] * result["Performance"] * result["Quality_Yield"]
    )

    result["Downtime_Status"] = result["Downtime_Minutes"].apply(classify_downtime)
    result["Load_Timestamp"] = pd.Timestamp.now()

    percentage_columns = [
        "Quality_Yield",
        "Scrap_Rate",
        "Availability",
        "Performance",
        "Estimated_OEE",
    ]
    for col in percentage_columns:
        result[col] = result[col].round(4)

    return result


def classify_downtime(minutes: float) -> str:
    if minutes >= 60:
        return "Critical"
    if minutes >= 30:
        return "Warning"
    return "Normal"


def load_to_sqlite(df: pd.DataFrame, database_path: str, table_name: str = "master_production") -> None:
    with sqlite3.connect(database_path) as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)


def summarize(df: pd.DataFrame) -> str:
    summary = {
        "rows_loaded": len(df),
        "machines": df["Machine_ID"].nunique(),
        "avg_quality_yield": round(df["Quality_Yield"].mean(), 4),
        "avg_scrap_rate": round(df["Scrap_Rate"].mean(), 4),
        "avg_estimated_oee": round(df["Estimated_OEE"].mean(), 4),
        "critical_events": int((df["Downtime_Status"] == "Critical").sum()),
    }

    lines = ["Process completed successfully."]
    for key, value in summary.items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)


def run_pipeline(input_path: str, database_path: str) -> pd.DataFrame:
    source = Path(input_path)
    if not source.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    raw_df = pd.read_csv(source)
    cleaned_df = clean_factory_data(raw_df)
    final_df = add_kpis(cleaned_df)
    load_to_sqlite(final_df, database_path)
    return final_df


def main() -> None:
    parser = argparse.ArgumentParser(description="Manufacturing production data integration pipeline")
    parser.add_argument("--input", default="mock_production_data.csv", help="Path to source CSV file")
    parser.add_argument("--database", default="factory_ops.db", help="SQLite database output path")
    args = parser.parse_args()

    final_df = run_pipeline(args.input, args.database)
    print(summarize(final_df))


if __name__ == "__main__":
    main()
