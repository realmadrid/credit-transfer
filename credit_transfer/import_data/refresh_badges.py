"""
NOTE: This file is used for refreshing the institution badges after importing the postgreSQL data file the first time.
"""

import os
import sys
import django
from django.core.files import File


def persist_partners():
    print('[Partner]: Begin persisting Partner...')
    badge_base_path = 'badges/'
    with open('partner.txt', 'r', encoding='utf-8') as f:
        add = 0
        records = 0
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            records += 1

            # Standard format for values: country;name;abbr;description;url;badge
            # Note that the delimiter is |
            # Use '\\' to separate paragraphs in description field
            values = line.split('|')

            if not Partner.objects.filter(name__iexact=values[1]).exists():
                country = Country.objects.get(name__iexact=values[0])
                des = '\n'.join(values[3].split('\\'))
                p = Partner(country=country, name=values[1], abbr=values[2], description=des, url=values[4])
                if values[5]:
                    with open(badge_base_path + values[5], 'rb') as badge:
                        p.badge.save(values[5], File(badge))
                p.save()
            else:
                p = Partner.objects.get(name__iexact=values[1])
                if values[5]:
                    with open(badge_base_path + values[5], 'rb') as badge:
                        p.badge.save(values[5], File(badge))
                        add += 1
                p.save()

    total = Partner.objects.all().count()
    print('[Partner]: {} records found in the data file.'.format(records))
    print('[Partner]: Persisting data finished. {} records in total. {} new institution badges added.\n'.format(total, add))


if __name__ == '__main__':
    # Append the base directory to the system path
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(BASE_DIR)

    # Load Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_transfer.settings')
    django.setup()

    # Load data models
    from advanced_standing.models import *

    persist_partners()
