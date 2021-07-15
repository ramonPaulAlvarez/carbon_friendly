# Carbon Friendly API
A small personal Django project serving a climate crisis resources site.  This project will serve as a foundation for future efforts to fight the climate crisis.

# Setup
Clone Carbon Friendly Repository:
```
git clone https://github.com/ramonPaulAlvarez/carbon_friendly.git
```

Create Virtual Environment:
```
cd carbon_friendly/carbon_friendly_api
pyenv virtualenv carbon_friendly_api
pyenv activate carbon_friendly_api
pip install -r requirements.txt
```

Start Server (without Docker):
```
python carbon_friendly_api/manage.py runserver
```