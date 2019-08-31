from django.contrib import admin
from .models import Country, Partner, ANUProgram, ANUDegree, ANUCourse, PartnerProgram, PartnerDegree, Articulation, \
    ANUMajorOrSpecialisation, StudyPlan


class PartnerAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'get_country_name',
        'has_uploaded_badge',
        'has_added_url',
    )
    list_filter = (
        'country',
    )
    search_fields = (
        'country__name',
        'name',
        'abbr',
    )

    def get_country_name(self, obj):
        return obj.country.name

    get_country_name.short_description = 'Country/Region'

    def has_uploaded_badge(self, obj):
        return True if obj.badge else False

    has_uploaded_badge.short_description = 'Badge'
    has_uploaded_badge.boolean = True

    def has_added_url(self, obj):
        return True if obj.url else False

    has_added_url.short_description = 'Website'
    has_added_url.boolean = True


class ANUProgramAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'code',
        'duration',
    )
    list_filter = (
        'duration',
    )
    search_fields = (
        'code',
        'name',
    )


class ANUDegreeAdmin(admin.ModelAdmin):
    list_display = (
        'get_program_name',
        'get_major_spec_names',
    )
    list_filter = (
        'anu_program',
    )
    search_fields = (
        'anu_program__name',
    )

    def get_program_name(self, obj):
        return obj.anu_program.name

    get_program_name.short_description = 'Program'
    get_program_name.admin_order_field = 'anu_program__name'

    def get_major_spec_names(self, obj):
        return ', '.join([m.name for m in obj.anu_major_spec.all()])

    get_major_spec_names.short_description = 'Majors/Specialisations'


class ANUCourseAdmin(admin.ModelAdmin):
    search_fields = (
        'code',
        'name',
    )


class PartnerProgramAdmin(admin.ModelAdmin):
    list_display = (
        'partner',
        'name',
    )
    list_filter = (
        'partner',
    )
    search_fields = (
        'partner__name',
        'partner__abbr',
        'name',
    )


class PartnerDegreeAdmin(admin.ModelAdmin):
    list_display = (
        'get_degree_name',
        'get_majors_abbr',
        'college',
        'degree_type',
    )
    list_filter = (
        'partner',
        'college',
        'degree_type',
    )
    search_fields = (
        'partner__name',
        'partner__abbr',
        'partner_program__name',
        'major',
    )

    def get_degree_name(self, obj):
        return '{} - {}'.format(obj.partner_program.partner.name, obj.degree_type)

    get_degree_name.short_description = 'Partner Degree'
    get_degree_name.admin_order_field = 'partner'

    def get_majors_abbr(self, obj):
        majors = obj.major.split('\r\n')
        if len(majors) < 4:
            return '; '.join(majors)
        else:
            other_majors_str = ' and other {} majors'.format(len(majors) - 3)
            return '; '.join(majors[:3]) + other_majors_str

    get_majors_abbr.short_description = 'Major(s)'


class ArticulationAdmin(admin.ModelAdmin):
    list_display = (
        'get_degree_name',
        'get_majors_abbr',
        'anu_degree',
        'year',
    )
    list_filter = (
        'year',
        'partner__country',
        'partner',
        'anu_degree__anu_program',
    )
    search_fields = (
        'partner__name',
        'partner__abbr',
        'anu_degree__anu_program__name',
        'anu_degree__anu_major_spec__name',
    )
    readonly_fields = ('created_time', 'updated_time',)

    def get_degree_name(self, obj):
        return '{} - {}'.format(obj.partner_degree.partner_program.partner.name, obj.partner_degree.degree_type)

    get_degree_name.short_description = 'Partner Degree'
    get_degree_name.admin_order_field = 'partner'

    def get_majors_abbr(self, obj):
        majors = obj.partner_degree.major.split('\r\n')
        if len(majors) < 4:
            return '; '.join(majors)
        else:
            other_majors_str = ' and other {} majors'.format(len(majors) - 3)
            return '; '.join(majors[:3]) + other_majors_str

    get_majors_abbr.short_description = 'Major(s)'


class ANUMajorOrSpecialisationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'code',
        'career',
    )
    list_filter = (
        'career',
    )
    search_fields = (
        'code',
        'name',
    )


class StudyPlanAdmin(admin.ModelAdmin):
    list_display = (
        'get_partner_degree_name',
        'get_anu_degree_name',
        'get_major_spec_name',
        'get_year_type',
        'get_semester',
        'get_career_name',
        'get_year',
    )
    list_filter = (
        'articulation__year',
        'articulation__partner__country',
        'articulation__partner',
        'year_type',
        'semester',
        'articulation__anu_degree__anu_program',
    )
    search_fields = (
        'articulation__partner__name',
        'articulation__partner__abbr',
        'articulation__anu_degree__anu_program__name',
        'anu_major_spec__name',
    )
    readonly_fields = (
        'created_time',
        'updated_time',
    )

    def get_partner_degree_name(self, obj):
        return str(obj.articulation.partner_degree)

    get_partner_degree_name.short_description = 'Partner Degree'

    def get_anu_degree_name(self, obj):
        return str(obj.articulation.anu_degree)

    get_anu_degree_name.short_description = 'ANU Degree'

    def get_major_spec_name(self, obj):
        if obj.anu_major_spec.code.startswith('NOMS-'):
            # if the field starts with the code prefix of 'No major or specialisation' instances
            return 'None'
        else:
            return obj.anu_major_spec.name

    get_major_spec_name.short_description = 'Major/Specialisation'

    def get_year_type(self, obj):
        if obj.year_type == '1':
            return 'Odd'
        elif obj.year_type == '2':
            return 'Even'
        else:
            return 'Any'

    get_year_type.short_description = 'Year Type'

    def get_semester(self, obj):
        return 'Feb.' if obj.semester == '1' else 'Jul.'
    get_semester.short_description = 'Semester'

    def get_career_name(self, obj):
        return obj.anu_major_spec.career

    get_career_name.short_description = 'Career'

    def get_year(self, obj):
        return obj.articulation.year

    get_year.short_description = 'Year'


admin.site.register(Country)
admin.site.register(Partner, PartnerAdmin)
admin.site.register(ANUProgram, ANUProgramAdmin)
admin.site.register(ANUDegree, ANUDegreeAdmin)
admin.site.register(ANUCourse, ANUCourseAdmin)
admin.site.register(PartnerProgram, PartnerProgramAdmin)
admin.site.register(PartnerDegree, PartnerDegreeAdmin)
admin.site.register(Articulation, ArticulationAdmin)
admin.site.register(ANUMajorOrSpecialisation, ANUMajorOrSpecialisationAdmin)
admin.site.register(StudyPlan, StudyPlanAdmin)

admin.site.site_url = None
admin.site.index_title = ''
