from django.urls import path
from . import views

# Write your patterns here

urlpatterns = [
    
    path('', views.Home.as_view(), name='admin_home'),
    # path('success', views.AdminSuccess.as_view(), name='admin_home'),
    
    path('signup/', views.AdminRegisterView.as_view(), name='admin_signup'),
    path('activate/<uidb64>/<token>', views.activate, name='admin_activate'),
    
    path('signin/', views.AdminLoginView.as_view(), name='admin_signin'),
    path('signout/', views.AdminLogoutView.as_view(), name='admin_signout'),
    
    path('password_change/', views.AdminPasswordChangeView.as_view(), name='admin_password_change'),
    path('password_reset/', views.AdminPasswordResetView.as_view(), name='admin_password_reset'),
    path('reset/<uidb64>/<token>/', views.AdminPasswordResetConfirmView.as_view(), name='admin_password_reset_confirm'),
    
    path('profile/', views.AdminChangeView.as_view(), name='admin_change'),
    path('profile/additional', views.AdminAdditionalChangeView.as_view(), name='admin_profile_additional'),
    
    path('doctors', views.DoctorView.as_view(), name='all_doctors'),
    path('doctors/applications', views.DoctorApplicationView.as_view(), name='doctor_applications'),
    path('doctor_update/<int:pk>', views.DoctorUpdateView.as_view(), name='doctor_update'),
    path('doctor_delete/<int:pk>', views.delete_doctor, name='doctor_delete'),


    path('patient/appointment/', views.HospitalAppointmentBookedView.as_view(), name='patient_appointment'),
    path('patient/appointment/<int:pk>', views.delete_appointment, name='patient_appointment_delete'),

]