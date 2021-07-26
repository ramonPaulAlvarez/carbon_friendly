# Carbon Friendly API
A small personal Django project serving a climate crisis resources site.  This project will serve as a foundation for future efforts to fight the climate crisis.

# Clone
This project can be ran directly or through Docker.  To begin, clone the Carbon Friendly repository:
```
git clone https://github.com/ramonPaulAlvarez/carbon_friendly.git
cd carbon_friendly/carbon_friendly_api
```

# Setup Python environment
_If you don't plan on running this in Docker_ you need to setup your Python development environment.  It's recommended to use a virtual environment, but the important part is installing the requirements.
```
pyenv virtualenv carbon_friendly_api
pyenv activate carbon_friendly_api
pip install -r requirements.txt
```

# Configure environment variables
Copy `make_env.tmpl` to `make_env.sh` and populate `make_env.sh` with all required environment variables using the editor of your choice.  Afterwards, source the environment file:
```
cp make_env.tmpl make_env.sh
vi make_env.sh
source make_env.sh
```

# Run tests
```
python carbon_friendly_api/manage.py test carbon_friendly_api -r
```

# Start Django service:
This will download the datasets once and start the Django service:
```
python carbon_friendly_api/manage.py shell -c "from core.tasks import download_datasets; download_datasets.apply()"

python carbon_friendly_api/manage.py runserver
```

# Start all services:
This will start the the Django, NGINX, Redis, Celery Worker, and Celery Beat services.  Metrics will automatically be updated periodically:
```
docker-compose up --build
```
