import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    """Команда для заполнения БД из файла формата JSON"""

    @classmethod
    def from_json(cls, **kwargs):
        json_file = kwargs['json_file']
        return json_file

    json_file = from_json()

    def __init__(self, json_file):
        self.from_json = json_file
        super().__init__()

    print(cls.from_json)
    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str,
                            help='The JSON file to import data from')



    def handle(self, model=None, **kwargs):
        json_file = self.from_json()
        print(self.from_json())
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
