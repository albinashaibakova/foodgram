import json

from django.core.management.base import BaseCommand


class BaseImportCommand(BaseCommand):
    """Команда для заполнения БД из файла формата JSON"""

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str,
                            help='The JSON file to import data from')

    def handle(self, model=None, **kwargs):
        json_file = kwargs['json_file']

        with open(json_file) as file:
            data = json.load(file)

        self.import_data(data)

    def import_data(self, data):
        raise NotImplementedError('Subclasses must implement this method')
