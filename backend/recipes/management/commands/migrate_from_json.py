import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    """Команда для заполнения БД из файла формата JSON"""

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str,
                            help='The JSON file to import data from')

    def handle(self, *args, **kwargs):
        model = None
        json_file = kwargs['json_file']
        if 'ingredients' in json_file:
            model = Ingredient
        if 'tags' in json_file:
            model = Tag

        with open(json_file) as file:
            if model:
                items = json.load(file)

                for item in items:
                    model.objects.create(**item)

            else:
                print("Не получилось загрузить элементы из файла JSON")
