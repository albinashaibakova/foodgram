from recipes.management.commands.base_migrate_from_json import BaseImportCommand

from recipes.models import Ingredient


class Command(BaseImportCommand):
    """Команда для заполнения БД ингредиентами из файла формата JSON"""

    def import_data(self, data):
        for ingredient in data:
            Ingredient.objects.create(**ingredient)

        print('Ингредиенты успешно загружены')
