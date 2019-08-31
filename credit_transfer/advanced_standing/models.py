import os
from uuid import uuid4
from datetime import datetime
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from smart_selects.db_fields import ChainedForeignKey


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'


def institution_badge_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid4().hex, ext)
    return os.path.join('institution_badge/', filename)


class Partner(models.Model):
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200, unique=True)
    abbr = models.CharField(max_length=10, blank=True, verbose_name='Abbreviation')
    description = models.TextField(verbose_name='General information')
    course_mappings = models.TextField(
        blank=True,
        verbose_name='Course mappings',
        help_text='Each line is a mapping in the following format:<br>'
                  '<b>ANU course code; Partner course name 1; Partner course name 2; ...&#8617;</b>'
    )
    url = models.URLField(max_length=200, blank=True, verbose_name='Official website')
    badge = models.ImageField(upload_to=institution_badge_path, null=True, blank=True, verbose_name='Institution badge')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Partner'
        verbose_name_plural = 'Partners'


def get_current_year():
    return datetime.now().year


# Super class of ANUProgram and PartnerProgram
class Program(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        abstract = True


class ANUProgram(Program):
    code = models.CharField(max_length=20, unique=True, verbose_name='Program code')
    duration = models.FloatField(default=4, verbose_name='Normal duration in years')

    def clean(self):
        processed_code = self.code.strip().upper()
        result = ANUProgram.objects.filter(code=processed_code)
        if result.exists():
            obj = result.first()
            if self.name == obj.name and self.duration == obj.duration:
                raise ValidationError('{} already exists in the database.'.format(processed_code))

    def save(self, *args, **kwargs):
        self.code = self.code.strip().upper()
        super(ANUProgram, self).save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        ordering = ['name', 'code']
        verbose_name = 'ANU Program'
        verbose_name_plural = 'ANU Programs'


class ANUMajorOrSpecialisation(models.Model):
    CAREER_CHOICES = (
        ('Undergraduate', 'Undergraduate'),
        ('Postgraduate', 'Postgraduate'),
    )

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    career = models.CharField(max_length=20, choices=CAREER_CHOICES, default='Undergraduate')

    def clean(self):
        processed_code = self.code.strip().upper()
        result = ANUMajorOrSpecialisation.objects.filter(code=processed_code)
        if result.exists():
            obj = result.first()
            if self.name == obj.name and self.career == obj.career:
                raise ValidationError('{} already exists in the database.'.format(processed_code))

    def save(self, *args, **kwargs):
        self.code = self.code.strip().upper()
        super(ANUMajorOrSpecialisation, self).save(*args, **kwargs)

    def __str__(self):
        return '{} - {}'.format(self.name, self.career)

    class Meta:
        ordering = ['name', 'career']
        unique_together = ('code', 'career')
        verbose_name = 'ANU Major or Specialisation'
        verbose_name_plural = 'ANU Majors or Specialisations'


class ANUDegree(models.Model):
    anu_program = models.ForeignKey(ANUProgram, on_delete=models.CASCADE)
    anu_major_spec = models.ManyToManyField(
        ANUMajorOrSpecialisation,
        blank=True,
        verbose_name='ANU Major or Specialisation'
    )

    def __str__(self):
        if not self.anu_major_spec.exists():
            return '{}'.format(
                self.anu_program.name,
            )
        else:
            return '{} - {}'.format(
                self.anu_program.name,
                ', '.join([m.name for m in self.anu_major_spec.all()]),
            )

    class Meta:
        ordering = ['anu_program']
        verbose_name = 'ANU Degree'
        verbose_name_plural = 'ANU Degrees'


class ANUCourse(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name='Course code')
    name = models.CharField(max_length=100)

    def clean(self):
        self.code = self.code.strip().upper()

    def __str__(self):
        return '{} {}'.format(self.code, self.name)

    class Meta:
        ordering = ['code']
        verbose_name = 'ANU Course'
        verbose_name_plural = 'ANU Courses'


class PartnerProgram(Program):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)

    def __str__(self):
        return '{} - {}'.format(self.partner.name, self.name)

    class Meta:
        ordering = ['partner', 'name']
        unique_together = ('partner', 'name')
        verbose_name = 'Partner Program'
        verbose_name_plural = 'Partner Programs'


class PartnerDegree(models.Model):
    DEGREE_TYPE_CHOICES = (
        ('Bachelor Degree', 'Bachelor Degree'),
        ('Master Degree', 'Master Degree'),
        ('Diploma', 'Diploma')
    )
    COLLEGE_CHOICES = (
        ('C', 'Computer Science'),
        ('E', 'Engineering'),
    )
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    partner_program = ChainedForeignKey(
        PartnerProgram,
        chained_field='partner',
        chained_model_field='partner',
        show_all=False,
        auto_choose=True,
        sort=False,
        on_delete=models.CASCADE,
    )
    college = models.CharField(max_length=1, choices=COLLEGE_CHOICES, default='C')
    degree_type = models.CharField(max_length=20, choices=DEGREE_TYPE_CHOICES, default='Bachelor Degree')
    major = models.TextField(verbose_name='Major(s)', help_text='Note: one major each line')
    anu_degrees = models.ManyToManyField(ANUDegree, through='Articulation')
    required_courses = models.ManyToManyField(ANUCourse, related_name='required_course', blank=True)
    note = models.TextField(blank=True, verbose_name='Required courses note')

    @property
    def get_majors_abbr(self):
        majors = self.major.split('\r\n')
        if len(majors) < 4:
            return '; '.join(majors)
        else:
            other_majors_str = ' and other {} majors'.format(len(majors) - 3)
            return '; '.join(majors[:3]) + other_majors_str

    def __str__(self):
        return '{} - {} in {}'.format(self.partner_program.partner.name, self.degree_type, self.get_majors_abbr)

    class Meta:
        ordering = ['partner_program', 'degree_type', 'major']
        unique_together = ('partner_program', 'degree_type', 'major')
        verbose_name = 'Partner Degree'
        verbose_name_plural = 'Partner Degrees'


class Articulation(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    partner_degree = ChainedForeignKey(
        PartnerDegree,
        chained_field='partner',
        chained_model_field='partner',
        show_all=False,
        auto_choose=True,
        sort=False,
        on_delete=models.CASCADE,
    )
    year = models.IntegerField(default=get_current_year, verbose_name='Academic year')  # IMPORTANT
    anu_degree = models.ForeignKey(ANUDegree, on_delete=models.CASCADE)
    completed_years = models.FloatField(
        default=2,
        validators=[MinValueValidator(0), MaxValueValidator(4)],
        verbose_name='Completed years in current degree',
        help_text='"0" stands for "Completion"'
    )
    time_to_complete = models.FloatField(
        default=2,
        validators=[MinValueValidator(0), MaxValueValidator(4)],
        verbose_name='Time to Complete Degree at ANU (in years)',
        help_text='"0" stands for "Case-by-case"'
    )
    advanced_standing = models.CharField(
        max_length=100,
        help_text='Example: 1 year (48 units) / 2 years (96 units) / 1.5 years (72 units) / Case-by-case / Entry only'
    )
    requirements = models.TextField(verbose_name='Academic requirements')
    note = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Note',
        help_text='E.g. Students below an average of 75% are invited to apply. '
                  'However, admission and advance standing will be assessed on a case-by-case basis.'
    )
    advanced_standing_details = models.ManyToManyField(ANUCourse, related_name='advanced_standing_course', blank=True)
    details_note = models.TextField(blank=True, verbose_name='Advanced standing details note')
    rationale = models.TextField(blank=True, verbose_name='Rationale')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='Last updated')

    @property
    def update_date(self):
        return self.updated_time.strftime('%d %B %Y')

    @property
    def get_majors_abbr(self):
        majors = self.partner_degree.major.split('\r\n')
        if len(majors) < 3:
            return '; '.join(majors)
        else:
            other_majors_str = ' and other {} majors'.format(len(majors) - 2)
            return '; '.join(majors[:2]) + other_majors_str

    def __str__(self):
        if not self.anu_degree.anu_major_spec.exists():
            return '{}: {} in {} —— ANU: {} - {}'.format(
                self.partner_degree.partner_program.partner.name,
                self.partner_degree.degree_type,
                self.get_majors_abbr,
                self.anu_degree.anu_program.name,
                self.year
            )
        else:
            return '{}: {} in {} —— ANU: {} >> {} - {}'.format(
                self.partner_degree.partner_program.partner.name,
                self.partner_degree.degree_type,
                self.get_majors_abbr,
                self.anu_degree.anu_program.name,
                ', '.join(m.name for m in self.anu_degree.anu_major_spec.all()),
                self.year
            )

    class Meta:
        ordering = ['-year', 'partner_degree']
        unique_together = ('partner_degree', 'anu_degree', 'year')
        verbose_name = 'Articulation'
        verbose_name_plural = 'Articulations'


class StudyPlan(models.Model):
    YEAR_TYPE_CHOICES = (
        ('0', 'Any'),
        ('1', 'Odd Year'),
        ('2', 'Even Year'),
    )

    SEMESTER_CHOICES = (
        ('1', 'Semester 1 (February))'),
        ('2', 'Semester 2 (July)'),
    )

    # NOTE: add partner, partner_degree for referencing in the chained selectors in the admin site
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    partner_degree = ChainedForeignKey(
        PartnerDegree,
        chained_field='partner',
        chained_model_field='partner',
        show_all=False,
        auto_choose=True,
        sort=False,
        on_delete=models.CASCADE,
    )
    articulation = ChainedForeignKey(
        Articulation,
        chained_field='partner_degree',
        chained_model_field='partner_degree',
        show_all=False,
        auto_choose=True,
        sort=False,
        on_delete=models.CASCADE,
    )

    anu_major_spec = models.ForeignKey(ANUMajorOrSpecialisation, on_delete=models.CASCADE,
                                       verbose_name='Major/Specialisation')
    year_type = models.CharField(max_length=1, choices=YEAR_TYPE_CHOICES, default='0')
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES, default='1')
    year1_sem1 = models.TextField(blank=True, verbose_name='Year 1 Semester 1')
    year1_sem2 = models.TextField(blank=True, verbose_name='Year 1 Semester 2')
    # For industrial experience in some study plans
    # e.g. https://cecs.anu.edu.au/sites/default/files/university-partnership/cqu_advanced_standing_flyer_3.pdf
    summer_holiday = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Summer Holiday',
        help_text='E.g. COMP4800 - 60 days of relevant industrial experience [1]'
    )
    year2_sem1 = models.TextField(blank=True, verbose_name='Year 2 Semester 1')
    year2_sem2 = models.TextField(blank=True, verbose_name='Year 2 Semester 2')
    year3_sem1 = models.TextField(blank=True, verbose_name='Year 3 Semester 1')
    year3_sem2 = models.TextField(blank=True, verbose_name='Year 3 Semester 2')
    note = models.TextField(blank=True)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='Last updated')

    @property
    def update_date(self):
        return self.updated_time.strftime('%d %B %Y')

    def __str__(self):
        if self.anu_major_spec is None:
            return str(self.articulation)
        else:
            return str(self.articulation) + ' ' + self.anu_major_spec.name

    class Meta:
        ordering = ['articulation', 'anu_major_spec', 'year_type', 'semester']
        unique_together = ('articulation', 'anu_major_spec', 'year_type', 'semester')
        verbose_name = 'Study Plan'
        verbose_name_plural = 'Study Plans'
