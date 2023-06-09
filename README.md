# Веб-сайт Foodgram "Помощник по продуктам"

[![foodgram_react_workflow](https://github.com/MihaRooll/foodgram-project-react/actions/workflows/yamdb_workflow.yml/badge.svg)](https://github.com/MihaRooll/foodgram-project-react/actions/workflows/yamdb_workflow.yml)

## _Онлайн-сервис для публикации рецептов_

### Описание проекта Foodgram

# Данные для входа
# <http://62.84.122.100/admin/>
# Логин - a@mail.ru
# Пароль - a


На платформе "Продуктовый помощник" пользователи имеют возможность делиться своими рецептами, подписываться на публикации других пользователей, а также добавлять понравившиеся рецепты в свой список «Избранное». Кроме того, перед походом в магазин, они могут скачать сводный список продуктов в формате PDF, необходимых для приготовления выбранных блюд.

На сайте имеется система регистрации и авторизации пользователей. Неавторизованные пользователи могут просматривать рецепты на главной странице с возможностью фильтрации по тегам. Также им доступны страницы отдельных рецептов и профили других пользователей.

Фронтенд и бекенд взаимодействуют между собой через API. Проект запускается в трёх Docker-контейнерах: nginx, PostgreSQL и Django, с использованием docker-compose. Четвёртый контейнер (frontend) используется только для подготовки файлов.

### Локальный запуск приложения в контейнерах

_Важно: При работе в операционных системах Linux или через терминал WSL2 для выполнения команд требуется использовать привилегии суперпользователя. Для этого перед каждой командой следует добавить префикс sudo.o._

Для начала, склонируйте репозиторий на свой локальный компьютер, а затем перейдите в корневую папку проекта.:

```
git clone git@github.com:MihaRooll/foodgram-project-react.git
cd foodgram-project-react
```

В корневой папке проекта необходимо создать файл с именем .env, в котором следует определить переменные окружения, необходимые для работы приложения.

Вот пример содержимого файла .env:

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY=key
```

Для выполнения сборки контейнеров необходимо перейти в папку /infra/ и запустить команду docker-compose up или docker-compose build.

```
cd infra
docker-compose up -d
```

После выполнения команды docker-compose up или docker-compose build будут созданы и запущены контейнеры (db, web, nginx) в фоновом режиме.

В контейнере web необходимо выполнить следующие действия: выполнить миграции, создать суперпользователя для доступа к административной панели, собрать статические файлы и загрузить ингредиенты из файла recipes_ingredients.csv и tags.csv в базу данных.

```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
docker-compose exec web python manage.py load_ingredients
docker-compose exec web python manage.py load_tags 
```

После выполнения этих действий, проект будет доступен по адресу <http://localhost/>.

Для подготовки сайта к работе, необходимо выполнить следующие действия:

Посетите админ-зону, используя адрес <http://localhost/admin/>.

В админ-зоне создайте теги для рецептов. Для каждого тега укажите его название, цветовой HEX-код (например, #49B64E) и slug (на английском языке).

Эти теги можно будет использовать для фильтрации рецептов на различных страницах сайта.

### Остановка контейнеров

Для остановки работы приложения можно воспользоваться следующими способами:

В терминале нажмите комбинацию клавиш Ctrl+C. Это прервёт выполнение приложения и остановит контейнеры.

Если вы работаете в нескольких терминалах, откройте новый терминал и используйте команду

```
docker-compose stop 
```

Для повторного запуска контейнеров без их пересборки можно использовать команду:

```
docker-compose start 
```

### Документация API представлена в формате Redoc.

Для просмотра спецификации API в формате Redoc вам необходимо запустить проект локально и затем перейти на страниц <http://localhost/api/docs/>

### Запуск на сервере с другим IP

Для замены IP-адреса в файле infra/nginx.conf, а также в разделе настроек Github (settings/secrets/actions) в переменной HOST, а также в последней строке данного README и файле settings.py, где указан IP, вам потребуется выполнить следующие шаги:

Откройте файл infra/nginx.conf и замените существующий IP-адрес на необходимый IP-адрес.

В разделе настроек Github (settings/secrets/actions) найдите переменную HOST и замените существующий IP-адрес на необходимый.

Перейдите к последней строке данного README и замените текущий IP-адрес на необходимый.

Откройте файл settings.py и найдите участок, где указывается IP-адрес. Замените текущий IP-адрес на необходимый.

Чтобы остановить службу nginx на сервере, выполните следующую команду после входа на сервер:

```
sudo systemctl stop nginx 
```

Для обновления файлов docker-compose.yml и nginx.conf на сервере, если в них были внесены изменения, выполните следующие действия:

На локальном компьютере (не на сервере) откройте терминал.

В терминале выполните команду копирования файлов на сервер. Вам может потребоваться ввести пароль для доступа к серверу.

```
# Приведенные команды копирования файлов позволяют скопировать файлы docker-compose.yml и nginx.conf на сервер.
scp -r /{имя диска}/{путь к папке}/foodgram-project-react/infra/docker-compose.yml {имя пользователя}@{публичный IPv4}:~/
# скопирует файл docker-compose.yml в домашнюю директорию на сервере. Для выполнения команды замените {имя диска}, {путь к папке}, {имя пользователя} и {публичный IPv4} на соответствующие значения.
scp -r /{имя диска}/{путь к папке}/foodgram-project-react/infra/nginx.conf {имя пользователя}@{публичный IPv4}:/home/{имя пользователя}/nginx/ 
скопирует файл nginx.conf в папку /nginx/ в домашней директории на сервере.
```

Для выполнения этих действий вам потребуется выполнить следующие шаги:

Сделайте коммит в ваш репозиторий на GitHub, включающий все необходимые изменения.

Перейдите на вкладку Actions в вашем репозитории на GitHub.

Проверьте, что workflow был запущен и все jobs в нем успешно выполнены.

Это позволит вам убедиться, что ваши изменения были применены и успешно прошли автоматическую проверку при помощи workflow.

### В данном проекте используются следующие технологии

В данном проекте используются следующие технологии в алфавитном порядке:

Django 4.0.6
Django REST Framework
Docker
Djoser
flake8
GitHub Actions (CI/CD)
gunicorn
nginx
PostgreSQL
Python 3.7
React
reportlab

### Проект разработан

[Гриджак Михаил](https://github.com/MihaRooll)

### Готовый проект

Проект можно найти по следующему адресу: <http://62.84.122.100>
