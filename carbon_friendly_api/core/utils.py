import datetime
import logging

import pandas as pd
from django.apps import apps
from django.conf import settings


logger = logging.getLogger(__name__)
app_config = apps.get_app_config('core')


class Datasets:
    """Read locally stored third party datasets."""

    def carbon_dioxide() -> pd.Series:
        """Get CO2 trend data."""
        # year, month, day, smoothed, trend
        file_path = f"{settings.BASE_DIR}/datasets/{app_config.CO2_FILENAME}"
        dataset = pd.read_csv(file_path, comment='#')

        # Add custom timestamp column
        dataset["timestamp"] = dataset.apply(
            lambda row: "/".join([str(int(row['month'])),
                                  str(int(row['day'])), str(int(row['year']))]),
            axis=1
        )
        dataset["timestamp"] = pd.to_datetime(dataset.timestamp, utc=True)

        return dataset

    def methane() -> pd.Series:
        """Get CH4 trend data."""
        column_names = ["year", "month", "decimal", "average",
                        "average_unc", "trend", "trend_unc"]
        file_path = f"{settings.BASE_DIR}/datasets/{app_config.CH4_FILENAME}"
        dataset = pd.read_csv(file_path, comment='#',
                              delim_whitespace=True, names=column_names)

        # Add custom timestamp column
        dataset["timestamp"] = dataset.apply(
            lambda row: "/".join([str(int(row['month'])),
                                 str(int(row['year']))]),
            axis=1
        )
        dataset["timestamp"] = pd.to_datetime(dataset.timestamp, utc=True)

        return dataset

    def nitrous_oxide() -> pd.Series:
        """Get N2O trend data."""
        column_names = ["year", "month", "decimal",
                        "average", "average_unc", "trend", "trend_unc"]
        file_path = f"{settings.BASE_DIR}/datasets/{app_config.N2O_FILENAME}"
        dataset = pd.read_csv(file_path, comment='#',
                              delim_whitespace=True, names=column_names)

        # Add custom timestamp column
        dataset["timestamp"] = dataset.apply(
            lambda row: "/".join([str(int(row['month'])),
                                 str(int(row['year']))]),
            axis=1
        )
        dataset["timestamp"] = pd.to_datetime(dataset.timestamp, utc=True)

        return dataset

    def temperature_change() -> pd.Series:
        """Get temperature change trend data."""
        column_names = ["year_month", "station", "land_ocean", "land_only", "open_ocean"]
        file_path = f"{settings.BASE_DIR}/datasets/{app_config.TEMPERATURE_CHANGE_FILENAME}"
        dataset = pd.read_csv(file_path, skiprows=[0, 1], names=column_names)

        # Add custom timestamp column
        dataset["timestamp"] = dataset["year_month"].apply(
            lambda value: year_percent_to_month_year(value))
        dataset["timestamp"] = pd.to_datetime(dataset.timestamp, utc=True)

        return dataset


def get_latest_metrics() -> dict:
    """Fetch all the locally stored datasets and append display fields."""
    metrics = []

    # Iterate on all available datasets
    for metric_config in app_config.DATASETS:
        # Validate and call the configured dataset method
        metric_method = getattr(Datasets, metric_config["method"], None)
        if not callable(metric_method):
            continue

        records = metric_method()

        # Append the latest record
        latest_record = records.iloc[-1]
        metrics.append({
            "label": metric_config.get("label"),
            "value": latest_record.get(metric_config.get("field", "value")),
            "title": f"Average {metric_config['group_by']} {metric_config['name']} (Timestamp: "
            f"{latest_record['timestamp'].strftime('%Y-%m-%d')}, Source: {metric_config['source']})",
            "unit": metric_config["unit"],
        })

    return metrics


def year_percent_to_month_year(value: int) -> str:
    """Converts YEAR.PERCENT_COMPLETE to M/Y."""
    print("YEAR PERCENT TO MONTH YEAR: ", value)
    year, percentage_complete = str(value).split(".")
    datetime_obj = datetime.datetime(
        int(year), 1, 1) + datetime.timedelta(365 * (int(percentage_complete) / 100) - 1)

    return f"{datetime_obj.month}/{datetime_obj.year}"
