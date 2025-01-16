from django.core.management.base import BaseCommand
import json

from recipes.models import Ingredient


class Command(BaseCommand):
    """Command for migrating from json to db for Ingredient model"""

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='The JSON file to import data from')

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']

        with open(json_file) as file:

            ingredients = json.load(file)

            for ingredient in ingredients:
                Ingredient.objects.create(**ingredient)
