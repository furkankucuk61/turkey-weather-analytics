
import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "turkey_weather_air_quality.csv"
)

OUTPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "cleaned_weather_air_quality.csv"
)


def clean_data():

    print("\nStarting data cleaning...")

    # 1. Load dataset
    df = pd.read_csv(INPUT_FILE)

    print(f"Original rows: {len(df)}")

    # 2. Standardize column names
    df.columns = df.columns.str.strip().str.lower()

    # 3. Convert time column
    df["time"] = pd.to_datetime(
        df["time"],
        errors="coerce"
    )

    # 4. Convert numeric columns
    numeric_columns = [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
        "weather_code",
        "pm10",
        "pm2_5",
        "nitrogen_dioxide",
        "ozone",
        "european_aqi"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # 5. Remove invalid records
    df = df.dropna(
        subset=["city", "time"]
    )

    # 6. Remove duplicate records
    df = df.drop_duplicates(
        subset=["city", "time"]
    )

    # 7. Validate physical ranges
    valid_ranges = {
        "relative_humidity_2m": (0, 100),
        "precipitation": (0, None),
        "wind_speed_10m": (0, None),
        "pm10": (0, None),
        "pm2_5": (0, None),
        "nitrogen_dioxide": (0, None),
        "ozone": (0, None),
        "european_aqi": (0, None)
    }

    for column, (minimum, maximum) in valid_ranges.items():

        invalid = df[column] < minimum

        if maximum is not None:
            invalid |= df[column] > maximum

        df.loc[invalid, column] = pd.NA

    # 8. Add date-related columns
    df["date"] = df["time"].dt.date

    df["hour"] = df["time"].dt.hour

    df["day_name"] = df["time"].dt.day_name()

    # 9. Data quality report
    quality_report = pd.DataFrame({
        "column": df.columns,
        "missing_count": df.isna().sum().values,
        "missing_percentage": (
            df.isna().mean().values * 100
        ).round(2)
    })

    quality_report.to_csv(
        BASE_DIR / "reports" / "data_quality_report.csv",
        index=False
    )

    # 10. Save cleaned dataset
    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Cleaned rows: {len(df)}")
    print("\nData cleaning completed!")

    return df


if __name__ == "__main__":

    clean_data()
