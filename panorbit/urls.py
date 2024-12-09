from django.contrib import admin
from django.urls import path, include  # Use path() instead of url()

urlpatterns = [
    path('admin/', admin.site.urls),  # Updated to path()
    path('', include('world.urls')),  # Updated to path()
]
