from recipes.management.commands.migrate_from_json import BaseImportCommand

from recipes.models import Ingredient


class Command(BaseImportCommand):
    """Команда для заполнения БД ингредиентами из файла формата JSON"""

    def handle(self, model=None, **kwargs):
        super().handle(model=Ingredient, **kwargs)
