# backend/config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse 

urlpatterns = [
    path("health/", lambda request: HttpResponse("OK"), name="health_check"),
    path('admin/', admin.site.urls),
    # This line tells Django that any URL starting with 'api/'
    # should be handled by the 'api' app's urls.
    path('api/', include('api.urls')),
]

# This is a helper that tells Django how to serve our uploaded images
# during development. It will not work in production without more setup.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)