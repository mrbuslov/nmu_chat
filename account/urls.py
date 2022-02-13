from django.urls import path, re_path
from account import views as account_views


app_name='account'
urlpatterns = [
    path('profile/', account_views.profile, name='profile'),
    path('profile_edit/', account_views.profile_edit, name='profile_edit'),
    path('login/', account_views.user_login ,name='login'),
    path('logout/', account_views.user_logout, name='logout'),
    path('registration/', account_views.registration, name='registration'),
    path('resend_activation_email/', account_views.resend_activation_email, name='resend_activation_email'),
    path('activate/<uidb64>/<token>', account_views.VerificationView.as_view(), name = 'activate'),
    path('set_new_pswrd/<uidb64>/<token>', account_views.SetNewPswrdView.as_view(), name = 'set_new_pswrd'),
    path('reset_email/', account_views.RequestResetEmailView.as_view(), name = 'reset_email'),
]