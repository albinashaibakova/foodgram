from recipes.management.commands.migrate_from_json import BaseImportCommand

from recipes.models import Ingredient


class Command(BaseImportCommand):
    """Команда для заполнения БД ингредиентами из файла формата JSON"""
    model = Ingredient

    def handle(self, model=model, **kwargs):
        super().handle(model, **kwargs)
