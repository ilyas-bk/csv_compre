from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("room/<uuid:room_id>/", views.upload_and_match_view, name="match_room"),
    path(
        "room/<uuid:room_id>/invite/<str:invite_token>/",
        views.party_b_upload_view,
        name="party_b_upload",
    ),
    path("room/<uuid:room_id>/download/", views.download_results, name="download_results"),
    path(
        "room/<uuid:room_id>/invite/<str:invite_token>/download/",
        views.download_results_party_b,
        name="download_results_party_b",
    ),
]
