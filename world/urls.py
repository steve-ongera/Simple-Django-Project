from django.urls import path, re_path  # Import path and re_path

from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Updated to path()
    path('signup/', views.signup, name="signup"),  # Updated to path()
    path('signup/validate/', views.signup_validate, name="signup_validate"),  # Updated to path()
    path('login/', views.c_login, name="login"),  # Updated to path()
    path('login/send_otp/', views.send_otp, name="send_otp"),  # Updated to path()
    path('login/validate/', views.login_validate, name="login_validate"),  # Updated to path()
    path('search/', views.search, name="search"),  # Updated to path()
    re_path(r'country/(?P<country_name>[\w|\W]+)/$', views.get_country_details, name="country_page"),  # Use re_path for regex-based URLs
    path('logout/', views.c_logout, name="logout"),  # Updated to path()
]
