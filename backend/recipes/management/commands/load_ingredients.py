from csv import DictReader
from pathlib import Path

from django.core.management.base import BaseCommand
from foodgram.settings import BASE_DIR
from recipes.models import Ingredient

ALREADY_LOADED_ERROR_MESSAGE = """
Если вам необходимо перезагрузить данные об ингредиентах из файла CSV,
сначала удалите файл db.sqlite3, чтобы уничтожить базу данных.
Затем выполните `python manage.py migrate` для создания новой пустой
базы данных с таблицами"""

DATA_FILE_PATH = Path(
    # Путь для локальной разработки:
    # Path(BASE_DIR).parent.parent, 'data', 'recipes_ingredient.csv')
    Path(BASE_DIR),
    "recipes_ingredient.csv",
)


class Command(BaseCommand):
    """Загружает данные об ингредиентах из файла csv в базу данных."""

    help = "Загружает данные об ингредиентах из файла csv в базу данных"

    def handle(self, *args, **options):
        if Ingredient.objects.exists():
            self.stderr.write("Данные об ингредиентах уже загружены... выход.")
            self.stderr.write(ALREADY_LOADED_ERROR_MESSAGE)
            return

        self.stdout.write("Загрузка данных об ингредиентах")

        for row in DictReader(open(DATA_FILE_PATH, encoding="utf-8")):
            ingr = Ingredient(
                name=row["name"], measurement_unit=row["measurement_unit"]
            )
            ingr.save()
