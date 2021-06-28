from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('contactus/', views.Contactus.as_view(), name='contactus'),
    path('aboutus/', views.Aboutus.as_view(), name='aboutus'),
    path('patient/', include('patient.urls')),
    path('doctor/', include('doctor.urls')),
    path('admins/', include('admins.urls')),
]