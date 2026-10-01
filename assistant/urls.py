"""
URL configuration for assistant project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from assist import views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("assist.urls")),
    path("api/bp-assessment/", views.bp_assessment_api, name="bp_assessment_api"),
    path(
    "medical-document-ai/",
    views.medical_document_assessment_view,
    name="medical_document_assessment",
),
path(
    "health-vitals/",
    views.health_vitals_view,
    name="health_vitals",
),
path(
    "health-vitals/",
    views.health_vitals_view,
    name="health_vitals",
),

path(
    "health-vitals/<int:vitals_id>/edit/",
    views.health_vitals_edit,
    name="health_vitals_edit",
),

path(
    "health-vitals/<int:vitals_id>/delete/",
    views.health_vitals_delete,
    name="health_vitals_delete",
),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
