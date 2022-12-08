import json

from django.core.management.base import BaseCommand

from bot.models.tag import Tag

import os
from config.settings.common import DATA_DIR


class Command(BaseCommand):
    help = 'Load tags in tags.json file and update database'

    # def add_arguments(self, parser):
    #     parser.add_argument('jsonfile', type=str, help='Indicates the JSON file to export entities')

    def handle(self, *args, **options):

        with open(os.path.join(DATA_DIR, 'tags.json')) as f:
            tag_list = json.loads(f.read())
            for tag_item in tag_list['tag']:
                tag = Tag()
                tag.id = tag_item['id']
                tag.name = tag_item['name']
                tag.color = tag_item['color']
                print(f'Saving tag: {tag.name}, id: {tag.id}')
                tag.save()

