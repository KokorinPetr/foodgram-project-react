# Foodgram

Foodgram is a web application for food enthusiasts to discover, share, and save their favorite recipes and culinary experiences.

## Features

Create your own recipes and share them with the community.
Explore recipes from other users and get inspired.
Easily download a shopping list for your recipes before heading to the store.
Connect with fellow food enthusiasts and exchange culinary ideas and experiences.

## Installation

To set up Foodgram locally, follow these steps:

docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic
docker compose exec backend cp -r /app/collected_static/. /app/static/
docker compose exec backend python manage.py createsuperuser

## Author

- Kokorin Petr
- GitHub: [Your GitHub Profile](https://github.com/KokorinPetr)
