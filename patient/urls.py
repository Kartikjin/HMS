from django.urls import path
from . import views

# Write your patterns here

urlpatterns = [
    
    path('', views.Home.as_view(), name='patient_home'),
    
    path('signup/', views.PatientRegisterView.as_view(), name='patient_signup'),
    path('activate/<uidb64>/<token>', views.activate, name='patient_activate'),
    
    path('signin/', views.PatientLoginView.as_view(), name='patient_signin'),
    path('signout/', views.PatientLogoutView.as_view(), name='patient_signout'),
    
    # path('password_change/', views.AdminPasswordChangeView.as_view(), name='admin_password_change'),
    path('password_reset/', views.PatientPasswordResetView.as_view(), name='patient_password_reset'),
    path('reset/<uidb64>/<token>/', views.PatientPasswordResetConfirmView.as_view(), name='patient_password_reset_confirm'),
    
    # path('profile/', views.AdminChangeView.as_view(), name='admin_change'),
    # path('profile/additional', views.AdminAdditionalChangeView.as_view(), name='admin_profile_additional'),
    
    path('appointment/doctors', views.DoctorView.as_view(), name='patient_appointment_book'),
    path('appointment/<int:pk>/book', views.AppointmentBookView.as_view(), name='appointment_book'),
    path('appointment/done', views.AppointmentDone, name='appointment_booked'),
    path('appointment/', views.PatientAppointmentBookedView.as_view(), name='list_appointment_booked'),
    
]