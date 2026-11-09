
import requests
import pandas as pd
import json

from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo


# -----------------------------------------
# 1. PROJECT CONFIGURATION
# -----------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

WEATHER_API = "https://api.open-meteo.com/v1/forecast"

AIR_API = "https://air-quality-api.open-meteo.com/v1/air-quality"

TIMEZONE = "Europe/Istanbul"

RETRIEVED_AT = datetime.now(
    ZoneInfo(TIMEZONE)
).isoformat()


# -----------------------------------------
# 2. CITY COORDINATES
# -----------------------------------------

cities = {
    "Istanbul": {
        "latitude": 41.0082,
        "longitude": 28.9784
    },
    "Ankara": {
        "latitude": 39.9334,
        "longitude": 32.8597
    },
    "Izmir": {
        "latitude": 38.4237,
        "longitude": 27.1428
    },
    "Antalya": {
        "latitude": 36.8969,
        "longitude": 30.7133
    },
    "Bursa": {
        "latitude": 40.1885,
        "longitude": 29.0610
    }
}


# -----------------------------------------
# 3. API REQUEST FUNCTION
# -----------------------------------------

def fetch_api(url, params):

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# -----------------------------------------
# 4. WEATHER DATA
# -----------------------------------------

def get_weather_data(city, coordinates):

    params = {
        "latitude": coordinates["latitude"],
        "longitude": coordinates["longitude"],
        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "wind_speed_10m,"
            "weather_code"
        ),
        "forecast_days": 3,
        "timezone": TIMEZONE
    }

    data = fetch_api(WEATHER_API, params)

    # Save raw API response
    raw_file = RAW_DIR / f"{city.lower()}_weather.json"

    with open(raw_file, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    df = pd.DataFrame(data["hourly"])

    df["city"] = city

    df["retrieved_at"] = RETRIEVED_AT

    return df


# -----------------------------------------
# 5. AIR QUALITY DATA
# -----------------------------------------

def get_air_quality_data(city, coordinates):

    params = {
        "latitude": coordinates["latitude"],
        "longitude": coordinates["longitude"],
        "hourly": (
            "pm10,"
            "pm2_5,"
            "nitrogen_dioxide,"
            "ozone,"
            "european_aqi"
        ),
        "forecast_days": 3,
        "timezone": TIMEZONE
    }

    data = fetch_api(AIR_API, params)

    # Save raw API response
    raw_file = RAW_DIR / f"{city.lower()}_air_quality.json"

    with open(raw_file, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    df = pd.DataFrame(data["hourly"])

    df["city"] = city

    df["retrieved_at"] = RETRIEVED_AT

    return df


# -----------------------------------------
# 6. COMBINE DATASETS
# -----------------------------------------

def collect_all_data():

    weather_data = []
    air_quality_data = []

    for city, coordinates in cities.items():

        print(f"Collecting data for {city}...")

        try:

            weather_df = get_weather_data(
                city,
                coordinates
            )

            air_df = get_air_quality_data(
                city,
                coordinates
            )

            weather_data.append(weather_df)
            air_quality_data.append(air_df)

            print(f"{city}: Data collected successfully.")

        except requests.RequestException as error:

            print(f"{city}: API error - {error}")

        except (KeyError, ValueError) as error:

            print(f"{city}: Data processing error - {error}")

    if not weather_data or not air_quality_data:
        raise RuntimeError("No API data was collected.")

    weather_df = pd.concat(
        weather_data,
        ignore_index=True
    )

    air_df = pd.concat(
        air_quality_data,
        ignore_index=True
    )

    # Merge weather and air quality data
    final_df = pd.merge(
        weather_df,
        air_df,
        on=["city", "time", "retrieved_at"],
        how="inner"
    )

    # Convert time column
    final_df["time"] = pd.to_datetime(final_df["time"])

    # Sort data
    final_df = final_df.sort_values(
        by=["city", "time"]
    )

    return final_df


# -----------------------------------------
# 7. SAVE PROCESSED DATA
# -----------------------------------------

def save_data(df):

    output_file = (
        PROCESSED_DIR / "turkey_weather_air_quality.csv"
    )

    df.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nData saved successfully!")
    print(f"File location: {output_file}")


# -----------------------------------------
# 8. MAIN
# -----------------------------------------

def main():

    print("Starting Turkey Weather Analytics...\n")

    df = collect_all_data()

    save_data(df)

    print("\nDataset preview:")
    print(df.head(10).to_string(index=False))

    print("\nDataset information:")
    print(df.info())

    print("\nProject completed successfully!")


if __name__ == "__main__":
    main()
