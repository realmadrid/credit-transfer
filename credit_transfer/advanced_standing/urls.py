from django.urls import path

from . import views

app_name = 'advanced_standing'
urlpatterns = [
    path('', views.index, name='index'),
    path('<str:country_name>/', views.get_partners, name='get_partners'),
    path('institution/<int:partner_id>/', views.get_partner_degrees, name='get_partner_degrees'),
    # path('institution/<int:partner_id>/', views.get_partner_programs, name='get_partner_programs'),
    path('articulations/<int:partner_degree_id>/<int:year>/', views.get_articulations, name='get_articulations'),
    path('study_plan/<int:articulation_id>/<int:year_type>/<int:semester>', views.get_study_plans, name='get_study_plans'),
]
