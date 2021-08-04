import datetime

import pandas as pd
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def get_carbon_dioxide() -> pd.Series:
    """Update CO2 trend data."""
    # year, month, day, smoothed, trend
    file_path = f"{settings.BASE_DIR}/datasets/{settings.DATASET_CO2_FILENAME}"
    dataset = pd.read_csv(file_path, comment='#')

    # Add custom created_at column
    dataset["created_at"] = dataset.apply(
        lambda row: "/".join([str(int(row['month'])),
                             str(int(row['day'])), str(int(row['year']))]),
        axis=1
    )
    dataset["created_at"] = pd.to_datetime(dataset.created_at)

    return dataset


def get_latest_metrics() -> dict:
    """Fetch latest metrics from downloaded datasets."""
    metrics = []

    latest_co2 = get_carbon_dioxide().iloc[-1]
    if len(latest_co2.index):
        metrics.append({
            "label": "CO2",
            "value": latest_co2["trend"],
            "title": f"Carbon Dioxide PPM (Updated: ~{latest_co2['created_at']}, Source: NOAA)",
            "unit": "PPM",
        })

    latest_temperature_change = get_temperature_change().iloc[-1]
    if len(latest_temperature_change.index):
        metrics.append({
            "label": None,
            "value": latest_temperature_change["station"],
            "title": f"Temperature Change in Celsius (Updated: ~{latest_temperature_change['created_at']}, Source: NOAA)",
            "unit": "C",
        })

    latest_ch4 = get_methane().iloc[-1]
    if len(latest_ch4.index):
        metrics.append({
            "label": "CH4",
            "value": latest_ch4["average"],
            "title": f"Methane PPM (Updated: ~{latest_ch4['created_at']}, Source: NOAA)",
            "unit": "PPM",
        })

    return metrics


def get_methane() -> pd.Series:
    """Get CH4 trend data."""
    column_names = ["year", "month", "decimal", "average",
                    "average_unc", "trend", "trend_unc"]
    file_path = f"{settings.BASE_DIR}/datasets/{settings.DATASET_CH4_FILENAME}"
    dataset = pd.read_csv(file_path, comment='#',
                          delim_whitespace=True, names=column_names)

    # Add custom created_at column
    dataset["created_at"] = dataset.apply(
        lambda row: "/".join([str(int(row['month'])), str(int(row['year']))]),
        axis=1
    )
    dataset["created_at"] = pd.to_datetime(dataset.created_at)

    return dataset


def get_temperature_change() -> pd.Series:
    """Get temperature change trend data."""
    column_names = ["year_month", "station", "land_ocean"]
    file_path = f"{settings.BASE_DIR}/datasets/{settings.DATASET_TEMPERATURE_CHANGE_FILENAME}"
    dataset = pd.read_csv(file_path, skiprows=[0, 1], names=column_names)

    # Add custom created_at column
    dataset["created_at"] = dataset["year_month"].apply(
        lambda value: year_percent_to_year_month_day(value))
    dataset["created_at"] = pd.to_datetime(dataset.created_at)

    return dataset


def year_percent_to_year_month_day(value: int) -> str:
    """Converts YEAR.PERCENT_COMPLETE to M/D/Y."""
    year, percentage_complete = str(value).split(".")
    datetime_obj = datetime.datetime(
        int(year), 1, 1) + datetime.timedelta(365 * (int(percentage_complete) / 100) - 1)

    return f"{datetime_obj.month}/{datetime_obj.day}/{datetime_obj.year}"
