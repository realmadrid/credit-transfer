from django.shortcuts import render
from django.http import Http404
from django.views.decorators.cache import cache_page

from .models import Country, Partner, ANUCourse, PartnerProgram, PartnerDegree, Articulation, StudyPlan
from .utils import *


# @cache_page(60 * 60)
def index(request):
    countries = Country.objects.all()

    # the countries/regions will be displayed in a Nx4 table in the template
    country_list = [countries[i:i + 4] for i in range(0, len(countries), 4)]
    table_empty_cells = range(4 - len(countries) % 4)

    context = {'country_list': country_list, 'table_empty_cells': table_empty_cells}
    return render(request, 'advanced_standing/index.html', context)


# @cache_page(60 * 60)
def get_partners(request, country_name):
    partners = Partner.objects.filter(country__name=country_name)
    if not partners.first():
        raise Http404

    context = {'partners': partners, 'country': country_name}
    return render(request, 'advanced_standing/partners.html', context)


# @cache_page(60 * 15)
def get_partner_degrees(request, partner_id):
    try:
        partner = Partner.objects.get(id=partner_id)
    except Partner.DoesNotExist:
        raise Http404

    comp = PartnerDegree.objects.filter(partner_program__partner__id=partner_id, college='C')
    engi = PartnerDegree.objects.filter(partner_program__partner__id=partner_id, college='E')
    year = get_current_year()

    if comp.first():
        for degree in comp:
            degree.major = get_partner_degree_major_list(degree.major)

    if engi.first():
        for degree in engi:
            degree.major = get_partner_degree_major_list(degree.major)

    context = {'partner': partner, 'comp': comp, 'engi': engi, 'year': year}
    return render(request, 'advanced_standing/partner_degrees.html', context)


# @cache_page(60 * 15)
def get_articulations(request, partner_degree_id, year):
    query_year = year

    # get available years for the selector on the page
    distinct_years = Articulation.objects.filter(partner_degree__id=partner_degree_id).values_list('year', flat=True).distinct().order_by('year')
    year_selector = list(distinct_years)

    # if the year select is empty or the query year is out of valid range, raise 404
    if not year_selector or query_year < year_selector[0] or query_year > get_current_year():
        raise Http404

    artics = Articulation.objects.filter(partner_degree__id=partner_degree_id, year=query_year).order_by('partner_degree', 'anu_degree')

    # if the no articulation exists in queried year, jump to the articulations in the latest year available
    if not artics.first():
        artics = Articulation.objects.filter(partner_degree__id=partner_degree_id, year=year_selector[-1])

    for artic in artics:
        # add urls to the courses of advanced_standing_details and required_courses
        artic.advanced_standing_details_list, artic.has_mappings = append_url_and_mappings_to_courses(
            artic.advanced_standing_details.all(),
            artic.partner.course_mappings
        )
        artic.required_courses_list = append_url_to_courses(artic.partner_degree.required_courses.all())

        # add url to the major_or_spec object if it exists
        artic.ms_list = append_url_to_major_spec(artic.anu_degree.anu_major_spec.all())

        # add url to the anu program
        artic.anu_program = append_url_to_anu_program(artic.anu_degree.anu_program)

        # convert the majors of partner degree to a list
        artic.partner_degree.major = get_partner_degree_major_list(artic.partner_degree.major)

        # check if any study plan with year_type='Any' exists
        if StudyPlan.objects.filter(articulation__id=artic.id, year_type=0).count():
            artic.has_study_plan = True
            artic.has_odd_and_even = False  # doesn't need to differentiate odd and even year
        # check if any study plan with year_type='Odd' exists (if odd year exists, even year must exist)
        # For future developers: you can modify here to be more robust, or modify the the study plan section in
        # articulation template
        elif StudyPlan.objects.filter(articulation__id=artic.id, year_type=1).count() >= 2 and \
                StudyPlan.objects.filter(articulation__id=artic.id, year_type=2).count() >= 2:
            artic.has_study_plan = True
            artic.has_odd_and_even = True
        else:
            artic.has_study_plan = False

    context = {
        'artics': artics,
        'year_selector': year_selector,
        'query_year': query_year,
        'partner_degree_id': partner_degree_id,
    }
    return render(request, 'advanced_standing/articulations.html', context)


# @cache_page(60 * 15)
def get_study_plans(request, articulation_id, year_type, semester):
    studyplans = StudyPlan.objects.filter(articulation__id=articulation_id, year_type=year_type, semester=semester)

    if not studyplans.first():
        raise Http404

    # add attributes for convenience in template
    studyplans.year_type = year_type
    studyplans.semester = semester

    # add urls to the courses and major or spec
    for plan in studyplans:
        ms = append_url_to_major_spec([plan.anu_major_spec])
        plan.major_or_spec = ms[0] if ms else None

        if plan.year1_sem1:
            plan.year1_sem1 = append_url_to_text_courses(plan.year1_sem1)

        if plan.year1_sem2:
            plan.year1_sem2 = append_url_to_text_courses(plan.year1_sem2)

        if plan.year2_sem1:
            plan.year2_sem1 = append_url_to_text_courses(plan.year2_sem1)

        if plan.year2_sem2:
            plan.year2_sem2 = append_url_to_text_courses(plan.year2_sem2)

        if plan.year3_sem1:
            plan.year3_sem1 = append_url_to_text_courses(plan.year3_sem1)

        if plan.year3_sem2:
            plan.year3_sem2 = append_url_to_text_courses(plan.year3_sem2)

        if plan.summer_holiday:
            plan.summer_holiday = append_url_to_summer_holiday_course(plan.summer_holiday)

    context = {'studyplans': studyplans}
    return render(request, 'advanced_standing/study_plans.html', context)
