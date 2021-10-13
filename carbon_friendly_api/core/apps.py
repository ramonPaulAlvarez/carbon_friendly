from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration for all of the third party datasets."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    # Dataset Maximum File Age (Hours)
    MAX_AGE = 6

    # Dataset File Information
    CO2_FILENAME = "co2.csv"
    CO2_URL = "ftp://aftp.cmdl.noaa.gov/products/trends/co2/co2_trend_gl.csv"

    CH4_FILENAME = "ch4.csv"
    CH4_URL = "ftp://aftp.cmdl.noaa.gov/products/trends/ch4/ch4_mm_gl.txt"

    TEMPERATURE_CHANGE_FILENAME = "temperature_change.txt"
    TEMPERATURE_CHANGE_URL = "http://data.giss.nasa.gov/gistemp/graphs_v4/graph_data/"\
        "Monthly_Mean_Global_Surface_Temperature/graph.csv"

    N2O_FILENAME = "n2o.csv"
    N2O_URL = "https://gml.noaa.gov/webdata/ccgg/trends/n2o/n2o_mm_gl.txt"

    DATASETS = (
        {
            "field": "trend",
            "file": CO2_FILENAME,
            "group_by": "Daily",
            "label": "CO2",
            "method": "carbon_dioxide",
            "name": "Carbon Dioxide",
            "source": "NOAA",
            "unit": "PPM",
            "url": CO2_URL,
        },
        {
            "field": "average",
            "file": CH4_FILENAME,
            "group_by": "Monthly",
            "label": "CH4",
            "method": "methane",
            "name": "Methane",
            "source": "NOAA",
            "unit": "PPM",
            "url": CH4_URL,
        },
        {
            "field": "average",
            "file": N2O_FILENAME,
            "group_by": "Monthly",
            "label": "N2O",
            "method": "nitrous_oxide",
            "name": "Nitrous Oxide",
            "source": "NOAA",
            "unit": "PPB",
            "url": N2O_URL,
        },
        {
            "field": "station",
            "file": TEMPERATURE_CHANGE_FILENAME,
            "group_by": "Monthly",
            "label": None,
            "method": "temperature_change",
            "name": "Temperature Change",
            "source": "NOAA",
            "unit": "C",
            "url": TEMPERATURE_CHANGE_URL,
        },
    )
