import csv

from django.core.management.base import BaseCommand

from foodgram.models import Ingredient


class Command(BaseCommand):
    help = 'Import ingredients from csv file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        ingredients = []
        with open(csv_file) as f:
            reader = csv.reader(f)
            for row in reader:
                name, measurement_unit = row
                ingredient = Ingredient(
                    name=name, measurement_unit=measurement_unit
                )
                ingredients.append(ingredient)

        Ingredient.objects.bulk_create(ingredients)
