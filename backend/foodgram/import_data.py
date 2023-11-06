import json
from recipes.models import Ingredient

with open('data/ingredients.json', 'r') as jsonfile:
    data = json.load(jsonfile)

    for item in data:
        ingredient = Ingredient.objects.create(
            name=item['name'],
            measurement_unit=item['measurement_unit'],
            amount=item['amount']
        )
