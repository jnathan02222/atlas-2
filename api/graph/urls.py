"""
URL configuration for graph project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from ninja import NinjaAPI
from ninja import Schema
from db import DB
from wikipedia_api.client import Client as WikipediaClient


class Neighbour(Schema):
    title: str
    outward: bool


class Artist(Schema):
    title: str


class Path(Schema):
    stops: list[str]


wikipedia_client = WikipediaClient()
api = NinjaAPI()


@api.get("/neighbours", response=list[Neighbour])
def neighbours(request, title: str):
    return [record.data() for record in DB.get_neighbours(title)]


@api.get("/search", response=list[Artist])
def search(request, name: str):
    return [record.data() for record in DB.search_for_artist(name)]


@api.get("/shortest-path", response=list[Path])
def shortest_path(request, start_title: str, end_title: str):
    return [record.data() for record in DB.shortest_path(start_title, end_title)]


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
