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

from typing import Optional
import pandoc
from pandoc.types import *
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from db import DB
from ninja import Schema

api = NinjaAPI()


class Neighbour(Schema):
    title: str
    outward: bool
    description: Optional[str]


class Artist(Schema):
    title: str
    description: Optional[str] = None


class Edge(Schema):
    description: list[str]


class Path(Schema):
    stops: list[str]


@api.get("/neighbours", response=list[Neighbour])
def neighbours(request, title: str):
    return [record.data() for record in DB.get_neighbours(title)]


@api.get("/search", response=list[Artist])
def search(request, name: str):
    return [record.data()["a"] for record in DB.search_for_artist(name)]


@api.get("/edge-description", response=list[Edge])
def edge_description(request, source: str, target: str):
    response = []
    for record in DB.get_edge_description(source, target):
        data = record.data()
        description = []
        for paragraph in data["description"]:
            try:
                doc = pandoc.read(paragraph, format="mediawiki")

                matches = [
                    (elt, path)
                    for (elt, path) in pandoc.iter(doc, path=True)
                    if "Note" in str(elt.__class__)
                    or "Image" in str(elt.__class__)
                    or "Header" in str(elt.__class__)
                ]
                for elt, path in reversed(matches):
                    holder, index = path[-1]
                    del holder[index]
                doc = pandoc.write(doc, format="plain")
                description.append(doc)
            except Exception:
                pass
        data["description"] = description
        response.append(data)
    return response


@api.get("/shortest-path", response=list[Path])
def shortest_path(request, start_title: str, end_title: str):
    return [record.data() for record in DB.shortest_path(start_title, end_title)]


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
