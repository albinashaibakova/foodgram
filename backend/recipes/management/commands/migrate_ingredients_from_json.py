from recipes.management.commands.base_migrate_from_json import Command

from recipes.models import Ingredient


class CommandIngredients(Command):
    """Команда для заполнения БД ингредиентами из файла формата JSON"""

    def __init__(self):
        super().__init__()

    json_file = self.from_json
    print(self.from_json)
