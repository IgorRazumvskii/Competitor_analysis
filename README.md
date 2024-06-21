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

## URLS

#### Запуск парсера
```
    http://127.0.0.1:8000/analysis
```
#### Авторизация
```
    http://127.0.0.1:8000/login
```
#### Просмотр токена
```
    http://127.0.0.1:8000/api-token-auth
```
#### История парсинга
```
    http://127.0.0.1:8000/history
```
#### История на определенный товар
```
    http://127.0.0.1:8000/product_history
```
#### Построение графика для товара
```
    http://127.0.0.1:8000/graph
```

## JSON

#### Для парсинга
```json
{
  "vendor_code": "70085281",

   "token": "СЮДА СВОЙ ТОКЕН"
}
```
#### Для регистрации 
```json
{
    "username": "username",
    "password": "password"
}
```
#### Для авторизации 
```json
{
    "username": "username",
    "password": "password"
}
```
#### Для просмотра токена 
```json
{
    "username": "username",
    "password": "password"
}
```
#### Для истории
```json
{
   "token": "СЮДА СВОЙ ТОКЕН"
}
```
#### Для истории определенного товара
```json
{
   "vendor_code": "70085281",
   "date": "2024-06-19"
}
```
#### Для построения графика 
```json
{
    "vendor_code": "70085281",
    "store": "Valta"
}
```
