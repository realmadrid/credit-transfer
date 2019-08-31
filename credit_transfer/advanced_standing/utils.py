import re
from datetime import datetime
from .config import *


def append_url_to_courses(course_objects):
    """
    Append urls to the courses of advanced_standing_details and required_courses object for rendering in the templates.
    :param course_objects: Iterable object of a ManyRelatedManager
    :return: a list of dicts of courses in the format [{code, name[, url]}, ...]
    """
    courses = []
    for c in course_objects:
        course = {'code': c.code, 'name': c.name}
        if is_course_code(c.code):
            course['url'] = ''.join([BASE_COURSE_URL, c.code])
        courses.append(course)
    return courses


def append_url_to_text_courses(year_x_sem_x):
    """
    Append urls to the text courses of the fields of StudyPlan for rendering in the templates.
    :param year_x_sem_x: a field of StudyPlan
    :return: a list of dicts of courses in the format [{code_and_name[, url]}, ...]
    """
    courses = []
    for line in year_x_sem_x.splitlines():
        s = line[:8].upper()
        course = {'code_and_name': line}
        if is_course_code(s):
            course['url'] = ''.join([BASE_COURSE_URL, s])
        courses.append(course)
    return courses


def append_url_to_summer_holiday_course(text):
    s = text[:8].upper()
    course = {'text': text}
    if is_course_code(s):
        course['url'] = ''.join([BASE_COURSE_URL, s])
    return course


def append_url_and_mappings_to_courses(course_objects, course_mappings):
    """
    Append urls and course mappings to the courses of advanced_standing_details object for rendering in the templates.
    :param course_objects: Iterable object of a ManyRelatedManager
    :param course_mappings: The course mappings attribute of Partner
    :return: a list of courses in the format [{'code': x, 'name': x, 'mappings': x, 'url': x}, ...]
             a boolean variable to flag whether at least one ANU course has equivalent courses
    """
    courses = []
    mappings = convert_course_mappings_to_dict(course_mappings)
    has_mappings = False
    for c in course_objects:
        course = {'code': c.code, 'name': c.name, 'mappings': mappings.get(c.code)}
        if not has_mappings and course['mappings']:
            has_mappings = True
        if is_course_code(c.code):
            course['url'] = ''.join([BASE_COURSE_URL, c.code])
        courses.append(course)
    return courses, has_mappings


def convert_course_mappings_to_dict(course_mappings):
    mapping_dict = {}
    mappings = course_mappings.splitlines()
    for mapping in mappings:
        # the first one is ANU course code and the others are partner courses
        courses = mapping.split(';')
        mapping_dict[courses[0]] = '\n'.join(courses[1:])
    return mapping_dict


def is_course_code(s):
    """
    A course code consists of 4 letters and 4 digits.
    :param s: string to be checked
    :return: True if it is a course code
    """
    return re.match(r'[a-zA-Z]{4}[0-9]{4}', s)


def get_current_year():
    return datetime.now().year


def append_url_to_major_spec(major_or_spec_objects):
    """
    Append urls to the ANUMajorOrSpecialisation objects for rendering in the templates.
    :param major_or_spec_objects: Iterable object of a ManyRelatedManager
    :return: a list of dict of major_or_spec in the format [{name, url}, ...], return None if no major or specialisation
    """
    ms_objects = []
    for ms in major_or_spec_objects:
        # check if it's a code of 'No major or specialisation' instances
        if ms.code.startswith('NOMS-'):
            return None

        if is_anu_major(ms.code):
            ms_dict = {'name': ms.name, 'url': ''.join([BASE_MAJOR_URL, ms.code])}
        else:
            ms_dict = {'name': ms.name, 'url': ''.join([BASE_SPEC_URL, ms.code])}
        ms_objects.append(ms_dict)
    return ms_objects


def is_anu_major(code):
    """
    Determine the code belongs to a major or specialisation.
    The pattern of major code: XXXX-MAJ, e.g. ACCT-MAJ
    The pattern of spec code: XXXX-SPEC, e.g. AINT-SPEC
    Note that in this project we only consider major and specialisation, no minors included.
    :param code: A code of ANU Major or Specialisation.
    :return: True if it is a code of major, False for a specialisation
    """
    # 'in' operator is faster than find() and re in string search.
    # Reference: https://stackoverflow.com/questions/4901523/whats-a-faster-operation-re-match-search-or-str-find
    if '-MAJ' in code:
        return True
    else:
        return False


def append_url_to_anu_program(anu_program):
    """
    Append url to the ANUProgram object for rendering in the templates.
    [Note!] The administrators could define ANU program that startswith 'XXXX' for convenience.
    For example, 'XXXX-0 Master of Engineering' means a combination of all the Master of Engineering Programs,
    so that the administrator does not have to add an articulation for every Master of Engineering Program.
    :param anu_program: An ANUProgram object
    :return: a dict which contains name, duration, url of the ANUProgram
    """
    if anu_program.code.startswith('XXXX'):
        # XXXX means user-defined code for convenience, which isn't a real program and doesn't have a url
        url = None
    else:
        url = ''.join([BASE_PROGRAM_URL, anu_program.code])
    anu_program_dict = {
        'name': anu_program.name,
        'duration': anu_program.duration,
        'url': url
    }
    return anu_program_dict


def get_partner_degree_major_list(partner_degree_major):
    """
    Convert the 'major' field of PartnerDegree to a list.
    :param partner_degree_major: the 'major' field of PartnerDegree object
    :return: a list of majors
    """
    majors = partner_degree_major.splitlines()
    return majors
