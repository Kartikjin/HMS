from django.urls import path
from . import views

# Write your patterns here

urlpatterns = [
    
    path('', views.Home.as_view(), name='doctor_home'),
    
    path('signup/', views.DoctorRegisterView.as_view(), name='doctor_signup'),
    path('activate/<uidb64>/<token>', views.activate, name='doctor_activate'),
    
    path('signin/', views.DoctorLoginView.as_view(), name='doctor_signin'),
    path('signout/', views.DoctorLogoutView.as_view(), name='doctor_signout'),
    
    # path('password_change/', views.DoctorPasswordChangeView.as_view(), name='doctor_password_change'),
    path('password_reset/', views.DoctorPasswordResetView.as_view(), name='doctor_password_reset'),
    path('reset/<uidb64>/<token>/', views.DoctorPasswordResetConfirmView.as_view(), name='doctor_password_reset_confirm'),
    
    # path('profile/', views.DoctorChangeView.as_view(), name='doctor_change'),
    # path('profile/additional', views.DoctorAdditionalChangeView.as_view(), name='doctor_profile_additional'),
    # path('apply', views.DoctorApplyView.as_view(), name='doctor_apply'),
    path('apply/', views.HospitalView.as_view(), name='doctor_apply'),
    path('doctor_applied/<int:pk>/', views.DoctorAppliedView.as_view(), name='doctor_applied'),
    path('doctor_applications/', views.DoctorApplicationView.as_view(), name='doctor_applications_status'),
    path('doctor_appointments/', views.DoctorAppointmentBookedView.as_view(), name='doctor_appointments'),
    path('doctor_appointment_delete/<int:pk>/', views.DoctorAppointmentDelete, name='doctor_appointment_delete'),    
]