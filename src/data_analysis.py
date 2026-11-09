
import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "cleaned_weather_air_quality.csv"
)

REPORT_DIR = BASE_DIR / "reports"

REPORT_DIR.mkdir(parents=True, exist_ok=True)


def calculate_city_kpis(df):

    print("\nCalculating city KPIs...")

    kpis = df.groupby("city").agg(
        avg_temperature=("temperature_2m", "mean"),
        max_temperature=("temperature_2m", "max"),
        min_temperature=("temperature_2m", "min"),
        avg_humidity=("relative_humidity_2m", "mean"),
        total_precipitation=("precipitation", "sum"),
        avg_wind_speed=("wind_speed_10m", "mean"),
        avg_pm25=("pm2_5", "mean"),
        avg_pm10=("pm10", "mean"),
        avg_european_aqi=("european_aqi", "mean"),
        record_count=("time", "count")
    ).round(2)

    kpis = kpis.reset_index()

    kpis.to_csv(
        REPORT_DIR / "city_kpis.csv",
        index=False,
        encoding="utf-8-sig"
    )

    return kpis


def calculate_daily_metrics(df):

    daily = df.groupby(
        ["city", "date"],
        as_index=False
    ).agg(
        avg_temperature=("temperature_2m", "mean"),
        avg_pm25=("pm2_5", "mean"),
        avg_aqi=("european_aqi", "mean"),
        total_precipitation=("precipitation", "sum")
    )

    daily.to_csv(
        REPORT_DIR / "daily_metrics.csv",
        index=False,
        encoding="utf-8-sig"
    )

    return daily


def calculate_correlations(df):

    columns = [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
        "pm2_5",
        "pm10",
        "european_aqi"
    ]

    correlation = df[columns].corr(
        method="pearson"
    ).round(3)

    correlation.to_csv(
        REPORT_DIR / "correlation_matrix.csv",
        encoding="utf-8-sig"
    )

    return correlation


def detect_outliers(df):

    columns = [
        "temperature_2m",
        "pm2_5",
        "pm10",
        "european_aqi"
    ]

    results = []

    for column in columns:

        valid = df[column].dropna()

        if valid.empty:
            continue

        q1 = valid.quantile(0.25)
        q3 = valid.quantile(0.75)

        iqr = q3 - q1

        lower_limit = q1 - 1.5 * iqr
        upper_limit = q3 + 1.5 * iqr

        outliers = (
            (df[column] < lower_limit)
            | (df[column] > upper_limit)
        )

        results.append({
            "metric": column,
            "lower_limit": round(lower_limit, 2),
            "upper_limit": round(upper_limit, 2),
            "outlier_count": int(outliers.sum())
        })

    outlier_report = pd.DataFrame(results)

    outlier_report.to_csv(
        REPORT_DIR / "outlier_report.csv",
        index=False
    )

    return outlier_report


def main():

    df = pd.read_csv(INPUT_FILE)

    print("\nCITY KPI REPORT")
    print(calculate_city_kpis(df).to_string(index=False))

    print("\nCORRELATION MATRIX")
    print(calculate_correlations(df))

    print("\nOUTLIER REPORT")
    print(detect_outliers(df).to_string(index=False))

    calculate_daily_metrics(df)

    print("\nAnalysis completed successfully!")


if __name__ == "__main__":

    main()
