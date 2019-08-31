"""
Extract ANU course information to files. Download the required HTML pages before running.
"""

from bs4 import BeautifulSoup


def extract_courses(html_name):
    """
    Extract code and name of ANU courses from a local HTML file to a text file.
    NOTE:
    1. The HTML page should be downloaded from https://programsandcourses.anu.edu.au/catalogue
    2. select 'Courses' tab, search COMP/ENGN/MATH/PHYS/STAT, click 'show all results' in the bottom of the page, save as...
    3. the filename must be [COMP/ENGN][Any other words].html  e.g.COMP courses - ANU.html
    :param html_name: the local HTML file (must under the same directory)
    """
    with open(html_name, 'r', encoding='utf-8') as html_file:
        html = html_file.read()

    soup = BeautifulSoup(html, features='html.parser')
    table = soup.find('table',
                      attrs={'class': 'catalogue-search-results__table catalogue-search-results__table--courses table'})

    course_type = html_name[:4].upper()
    courses = []
    # skip the heading and footer of the table
    # heading: CODE, TITLE, TERM, CAREER, UNITS, DELIVERY
    for row in table.find_all('tr')[2:]:
        code, name = [td.find('a').string for td in row.find_all('td')[:2]]
        if code.startswith(course_type):
            courses.append((code, name))

    # sort the course list by the code
    courses.sort(key=lambda x: x[0])

    # write to a file
    target_filename = html_name[:4].lower() + '_course.txt'
    with open(target_filename, 'w', encoding='utf-8') as f:
        for course in courses:
            f.write('%s;%s\n' % (course[0], course[1]))

    print('Finish extracting courses to [%s]' % target_filename)


if __name__ == '__main__':
    # extract COMP courses
    extract_courses('COMP courses - ANU.html')

    # extract ENGN courses
    extract_courses('ENGN courses - ANU.html')

    """
    NOTE: There aren't many MATH/PHYS/STAT courses for CECS students.
          I don't think we should import all these courses to the database.
          For the courses of MATH/PHYS/STAT, we can add manually in Django Admin.
    """
    # extract_courses('MATH courses - ANU.html')
    # extract_courses('PHYS courses - ANU.html')
    # extract_courses('STAT courses - ANU.html')
