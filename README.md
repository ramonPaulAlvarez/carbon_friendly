# Carbon Friendly API
A small personal Django project serving a climate crisis resources site.  This project will serve as a foundation for future efforts to fight the climate crisis.

# Setup
## Clone repository
This project can be ran directly or through Docker.  To begin, clone the Carbon Friendly repository:
```
git clone https://github.com/ramonPaulAlvarez/carbon_friendly.git
cd carbon_friendly/carbon_friendly_api
```

## Prepare Python environment
_If you don't plan on running this in Docker_ you need to setup your Python development environment.  It's recommended to use a virtual environment, but the important part is installing the requirements.
```
pyenv virtualenv carbon_friendly_api
pyenv activate carbon_friendly_api
pip install -r requirements.txt
```

## Configure environment variables
Copy `make_env.tmpl` to `make_env.sh` and populate `make_env.sh` with all required environment variables using the editor of your choice.  Afterwards, source the environment file:
```
cp make_env.tmpl make_env.sh
vi make_env.sh
source make_env.sh
```

# Testing
## Running tests
If you'd like to contribute to the tests they can be run like so:
```
python carbon_friendly_api/manage.py test carbon_friendly_api
```

# Starting services
## Start only the Django service
This will download the datasets, load the resource fixture, and start the Django service:
```
python carbon_friendly_api/manage.py shell -c "from core.tasks import download_datasets; download_datasets.apply()"

python carbon_friendly_api/manage.py migrate

python carbon_friendly_api/manage.py runserver
```

## Start all services (Docker)
This will start the the Django, NGINX, Redis, Celery Worker, and Celery Beat services.  Metrics will automatically be updated periodically:
```
docker-compose up --build
```

# Accessing services
## Web Service
Open your favorite browser and visit the address of the host you are running the services on.  For example, http://localhost if you're using Docker or http://localhost:8000 if you're not.  I'm currently running the services at http://carbonfriendly.earth.

## API Service
If you'd like to query the API then I recommend installing Postman and downloading the [Postman Collection](carbon_friendly_api/static/postman/CarbonFriendlyAPI.postman_collection.json) and [Environment](carbon_friendly_api/static/postman/CarbonFriendlyAPI.postman_environment.json) files for the project.  If you're working on the API be sure to adjust the `SERVER` environment variable to use your correct host.
