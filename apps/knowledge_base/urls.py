from django.urls import path
from . import views

app_name = "knowledge_base"

urlpatterns = [
    path("", views.document_list, name="document_list"),
    path("upload/", views.document_upload, name="document_upload"),
    path("<uuid:pk>/delete/", views.document_delete, name="document_delete"),
    path("search/", views.search_view, name="search"),
]
