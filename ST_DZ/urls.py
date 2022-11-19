"""ST_DZ URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from MINIO import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.start, name='start'),
    path('home/', views.home, name='home'),
    path('home/<str:name>/', views.object, name='object'),
    path('upload/', views.model_form_upload, name='model_form_upload'),
    path('edit/<str:name>/', views.model_form_edit, name='model_form_edit'),
    path('home/delete/<str:name>/', views.deleted, name='deleted'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
