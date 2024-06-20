## Installation 
```pip install -r requirements.txt```


## DRF
```
python manage.py migrate
python manage.py makemigrations
python manage.py createsuperuser
python manage.py runserver
```

## Celery
```angular2html
celery -A Competitor_analysis worker -l INFO
```

## Rabbit:
```
rabbitmq-server
```