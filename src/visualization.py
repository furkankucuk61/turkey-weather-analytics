
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = (
    BASE_DIR / "data" / "processed"
    / "cleaned_weather_air_quality.csv"
)

FIGURE_DIR = BASE_DIR / "reports" / "figures"
FIGURE_DIR.mkdir(parents=True, exist_ok=True)


def create_visualizations():

    df = pd.read_csv(DATA_FILE)

    sns.set_theme(style="whitegrid")

    # 1. Average temperature by city
    city_temperature = df.groupby(
        "city"
    )["temperature_2m"].mean().sort_values()

    plt.figure(figsize=(10, 6))

    city_temperature.plot(kind="bar")

    plt.title("Average Temperature by City")
    plt.xlabel("City")
    plt.ylabel("Temperature (°C)")
    plt.xticks(rotation=0)
    plt.tight_layout()

    plt.savefig(
        FIGURE_DIR / "average_temperature.png",
        dpi=300
    )

    plt.close()

    # 2. PM2.5 comparison
    city_pm25 = df.groupby(
        "city"
    )["pm2_5"].mean().sort_values()

    plt.figure(figsize=(10, 6))

    city_pm25.plot(kind="bar")

    plt.title("Average PM2.5 by City")
    plt.xlabel("City")
    plt.ylabel("PM2.5 (µg/m³)")
    plt.xticks(rotation=0)
    plt.tight_layout()

    plt.savefig(
        FIGURE_DIR / "average_pm25.png",
        dpi=300
    )

    plt.close()

    # 3. Temperature trend
    df["time"] = pd.to_datetime(df["time"])

    plt.figure(figsize=(12, 6))

    for city in df["city"].unique():

        city_df = df[df["city"] == city]

        plt.plot(
            city_df["time"],
            city_df["temperature_2m"],
            label=city
        )

    plt.title("Hourly Temperature Trends")
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(
        FIGURE_DIR / "temperature_trends.png",
        dpi=300
    )

    plt.close()

    # 4. Correlation heatmap
    columns = [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
        "pm2_5",
        "pm10",
        "european_aqi"
    ]

    correlation = df[columns].corr()

    plt.figure(figsize=(10, 8))

    sns.heatmap(
        correlation,
        annot=True,
        cmap="coolwarm",
        fmt=".2f",
        center=0
    )

    plt.title("Weather and Air Quality Correlation")

    plt.tight_layout()

    plt.savefig(
        FIGURE_DIR / "correlation_heatmap.png",
        dpi=300
    )

    plt.close()

    print("All visualizations created successfully!")


if __name__ == "__main__":

    create_visualizations()
