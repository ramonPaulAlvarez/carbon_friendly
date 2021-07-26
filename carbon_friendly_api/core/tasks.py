import datetime
import os
import shutil
import urllib.request

from django.conf import settings
from celery.signals import worker_ready
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
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


@shared_task
def download_datasets(force: bool = False) -> None:
    """Download all datasets that we need."""
    for url, local_file_name in settings.DATASETS:
        download_dataset.apply_async(args=(url, local_file_name, force))


@worker_ready.connect
def at_start(sender, **kwargs):
    """Run download_datasets when the celery worker is ready."""
    with sender.app.connection() as c:
        sender.app.send_task("core.tasks.download_datasets", connection=c)