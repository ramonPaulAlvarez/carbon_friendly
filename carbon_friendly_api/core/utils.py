import datetime
import os
import shutil
import urllib.request

import pandas as pd
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def download_dataset(url: str, file_name: str, force: bool = False) -> None:
    """Downloads the specified dataset and returns the resulting filename on success."""
    # Check if the file is old enough to re-download
    file_path = f"{settings.BASE_DIR}/datasets/{file_name}"
    if os.path.exists(file_path) and not force:
        dataset_created_at = datetime.datetime.fromtimestamp(
            os.path.getmtime(file_path))
        if dataset_created_at + datetime.timedelta(hours=settings.DATASET_MAX_AGE) > datetime.datetime.now():
            return

    # Create directory for the dataset if it doesn't exist
    if not os.path.exists(f"{settings.BASE_DIR}/datasets"):
        os.mkdir(f"{settings.BASE_DIR}/datasets")

    # Download the dataset and store locally
    logger.info(f"Downloading dataset {url}...")

    with urllib.request.urlopen(url) as response, open(file_path, 'wb') as fd:
        shutil.copyfileobj(response, fd)


def download_datasets(force: bool = False) -> None:
    """Download all datasets that we need."""
    for url, local_file_name in settings.DATASETS:
        download_dataset(url, local_file_name, force=force)


def get_carbon_dioxide() -> pd.Series:
    """Update CO2 trend data."""
    # year, month, day, smoothed, trend
    dataset = pd.read_csv(
        f"{settings.BASE_DIR}/datasets/{settings.DATASET_CO2_FILENAME}", comment='#')

    # Add custom last_updated column
    dataset["created_at"] = dataset.apply(
        lambda row: "/".join([str(int(row['month'])),
                             str(int(row['day'])), str(int(row['year']))]),
        axis=1
    )
    return dataset


def get_latest_metrics() -> dict:
    """Fetch latest metrics from downloaded datasets."""
    metrics = []

    latest_co2 = get_carbon_dioxide().iloc[-1]
    if len(latest_co2.index):
        metrics.append({
            "label": "CO2",
            "value": latest_co2["trend"],
            "title": f"Carbon Dioxide in PPM ({latest_co2['created_at']}, Source: NOAA)",
            "unit": "PPM",
        })

    latest_t_anon = get_temperature_anomaly().iloc[-1]
    if len(latest_t_anon.index):
        metrics.append({
            "label": None,
            "value": latest_t_anon["Station"],
            "title": f"Temperature Anomaly in Celsius ({latest_t_anon['created_at']}, Source: NOAA)",
            "unit": "C",
        })

    latest_ch4 = get_methane().iloc[-1]
    if len(latest_ch4.index):
        metrics.append({
            "label": "CH4",
            "value": latest_ch4["average"],
            "title": f"Methane Dioxide in PPM ({latest_ch4['created_at']}, Source: NOAA)",
            "unit": "PPM",
        })

    return metrics


def get_methane() -> pd.Series:
    """Get CH4 trend data."""
    names = ["year", "month", "decimal", "average",
             "average_unc", "trend", "trend_unc"]
    dataset = pd.read_csv(f"{settings.BASE_DIR}/datasets/{settings.DATASET_CH4_FILENAME}",
                          comment='#', delim_whitespace=True, names=names)

    # Add custom last_updated column
    dataset["created_at"] = dataset.apply(
        lambda row: "/".join([str(int(row['month'])), str(int(row['year']))]),
        axis=1
    )
    return dataset


def get_temperature_anomaly() -> pd.Series:
    """Get temperature anomaly trend data."""
    # Year+Month, Station, Land+Ocean
    dataset = pd.read_csv(
        f"{settings.BASE_DIR}/datasets/{settings.DATASET_TANON_FILENAME}", skiprows=[0])

    # Add custom last_updated column
    dataset["created_at"] = dataset["Year+Month"].apply(
        lambda value: year_percent_to_year_month_day(value))
    return dataset


def year_percent_to_year_month_day(value: int) -> str:
    """Converts YEAR.PERCENT_COMPLETE to M/D/Y."""
    year, percentage_complete = str(value).split(".")
    datetime_obj = datetime.datetime(
        int(year), 1, 1) + datetime.timedelta(365 * (int(percentage_complete) / 100) - 1)
    return f"{datetime_obj.month}/{datetime_obj.day}/{datetime_obj.year}"
