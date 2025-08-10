from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('', views.support_center, name='support_center'),
    path('faq/', views.faq, name='faq'),
    path('contact/', views.contact, name='contact'),
    path('feedback/', views.feedback, name='feedback'),
]

