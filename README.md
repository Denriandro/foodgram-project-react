https://newfoodgram96.ddns.net

## Запуск проекта в dev-режиме

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Denriandro/foodgram-project-react
```

```
cd foodgram-project-react
```

Создать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```
Создать суперпользователя:

```
python3 manage.py createsuperuser
```

Запустить проект:

```
python3 manage.py runserver
```

