from recipes.management.commands.migrate_from_json import BaseImportCommand

from recipes.models import Ingredient


class Command(BaseImportCommand):
    """Команда для заполнения БД ингредиентами из файла формата JSON"""

    def import_data(self, data):

        try:
            Ingredient.objects.bulk_create(Ingredient(**ingredient) for ingredient in data)
            print('Ингредиенты успешно загружены')

        except Exception as e:
            print(f'Error: {e}')
