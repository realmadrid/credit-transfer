"""
NOTE: This file must be ran after extract_anu_courses.py
"""

import os
import sys
import django
from django.core.files import File


def persist_countries():
    print('[Country]: Begin persisting Country...')
    with open('country.txt', 'r', encoding='utf-8') as f:
        add = 0
        records = 0
        for line in f.readlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            records += 1
            if Country.objects.filter(name=line).count() == 0:
                c = Country(name=line)
                c.save()
                add += 1
    total = Country.objects.all().count()
    print('[Country]: {} records found in the data file.'.format(records))
    print('[Country]: Persisting data finished. {} records in total. {} new records added.\n'.format(total, add))


def persist_anu_program():
    print('[ANU_Program]: Begin persisting ANU_Program...')
    with open('anu_program.txt', 'r', encoding='utf-8') as f:
        add = 0
        records = 0
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            records += 1
            code, name, duration = line.split(';')
            if not ANUProgram.objects.filter(code=code).exists():
                p = ANUProgram(code=code, name=name, duration=duration)
                p.save()
                add += 1
    total = ANUProgram.objects.all().count()
    print('[ANU_Program]: {} records found in the data file.'.format(records))
    print('[ANU_Program]: Persisting data finished. {} records in total. {} new records added.\n'.format(total, add))


def persist_anu_major_or_specialisation():
    print('[ANU_Major_or_Specialisation]: Begin persisting ANU_Major_or_Specialisation...')
    with open('anu_major_or_spec.txt', 'r', encoding='utf-8') as f:
        add = 0
        records = 0
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            records += 1
            code, name, career = line.split(';')
            if not ANUMajorOrSpecialisation.objects.filter(code=code, career=career).exists():
                m = ANUMajorOrSpecialisation(code=code, name=name, career=career)
                m.save()
                add += 1
    total = ANUMajorOrSpecialisation.objects.all().count()
    print('[ANU_Major_or_Specialisation]: {} records found in the data file.'.format(records))
    print('[ANU_Major_or_Specialisation]: Persisting data finished. {} records in total. {} new records added.\n'.format(total, add))


def persist_course_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        add = 0  # the records newly added
        records = 0
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            records += 1
            values = line.strip().split(';')
            if len(values) == 2:  # no attribute is missing
                code, name = values
                if not ANUCourse.objects.filter(code__iexact=values[0]).exists():
                    c = ANUCourse(code=code, name=name)
                    c.save()
                    add += 1
                else:
                    print('Line skipped: [{} {}] exists in the database.'.format(code, name))

    print('[ANU_Course]: {} records found in the data file - {}.'.format(records, filename))
    return add


def persist_anu_course():
    print('[ANU_Course]: Begin persisting ANU_Course...')
    # COMP and ENGN courses
    count0 = persist_course_from_file('comp_course.txt')
    count1 = persist_course_from_file('engn_course.txt')
    # other ANU courses (MATH/PHYS/STAT)
    count2 = persist_course_from_file('anu_course.txt')

    add = count0 + count1 + count2
    total = ANUCourse.objects.all().count()
    print('[ANU_Course]: Persisting data finished. {} records in total. {} new records added.\n'.format(total, add))


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
                add += 1
            else:
                p = Partner.objects.get(name__iexact=values[1])
                if not p.badge:
                    if values[5]:
                        with open(badge_base_path + values[5], 'rb') as badge:
                            p.badge.save(values[5], File(badge))
                    p.save()
                else:
                    print('Line skipped: [{}] exists in the database.'.format(values[1]))

    total = Partner.objects.all().count()
    print('[Partner]: {} records found in the data file.'.format(records))
    print('[Partner]: Persisting data finished. {} records in total. {} new records added.\n'.format(total, add))


if __name__ == '__main__':
    # Append the base directory to the system path
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(BASE_DIR)

    # Load Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_transfer.settings')
    django.setup()

    # Load data models
    from advanced_standing.models import *

    persist_countries()
    persist_anu_program()
    persist_anu_major_or_specialisation()
    persist_anu_course()
    persist_partners()
