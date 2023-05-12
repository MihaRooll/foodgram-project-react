from csv import DictReader
from pathlib import Path

from django.core.management.base import BaseCommand

from foodgram.settings import BASE_DIR
from recipes.models import Tag

ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload the ingredients data from the CSV file,
first destroy the tags table.
Then, run `python manage.py migrate` for a new table"""

DATA_FILE_PATH = Path(
    # Path for local development:
    # Path(BASE_DIR).parent.parent, 'data', 'tags.csv')
    Path(BASE_DIR), 'data', 'tags.csv')


class Command(BaseCommand):
    """Loads tags data from csv file to database."""

    help = 'Loads tags data from csv file to database'

    def handle(self, *args, **options):

        if Tag.objects.exists():
            self.stderr.write('tags data already loaded...exiting.')
            self.stderr.write(ALREDY_LOADED_ERROR_MESSAGE)
            return

        self.stdout.write('Loading tags data')

        for row in DictReader(open(DATA_FILE_PATH, encoding='utf-8')):
            item = Tag(
                name=row['name'], color=row['color'], slug=row['slug'])
            item.save()
