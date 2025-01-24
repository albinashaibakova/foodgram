import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    """Command for migrating from json to db for Ingredient model"""

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str,
                            help='The JSON file to import data from')

    def handle(self, *args, **kwargs):

        json_file = kwargs['json_file']
        if 'ingredients' in json_file:
            model = Ingredient
        if 'tags' in json_file:
            model = Tag

        with open(json_file) as file:
            try:
                items = json.load(file)

                for item in items:
                    model.objects.create(**item)

            except:
                print("Не получилось загрузить элементы из файла JSON")
