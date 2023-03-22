from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("result", views.search, name="entry_search"),
    path("new", views.new, name="new"),
    path("edit", views.edit, name="edit"),
    path("random", views.random_pick, name="random"),
    path("<str:title>", views.entry, name="view_entry"),
    
    
    
]
