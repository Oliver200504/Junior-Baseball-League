from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views


urlpatterns = [
    # HOME
    path("", views.home, name="home"),

    # LOGIN / LOGOUT
    path("login/", views.MyLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="home"), name="logout"),

    # PLAYERS
    path("players/", views.PlayerListView.as_view(), name="player_list"),
    path("players/new/", views.PlayerCreateView.as_view(), name="player_create"),
    path("players/edit/<int:pk>/", views.PlayerUpdateView.as_view(), name="player_update"),
    path("players/delete/<int:pk>/", views.PlayerDeleteView.as_view(), name="player_delete"),

    # TEAMS
    path("teams/", views.TeamListView.as_view(), name="team_list"),
    path("teams/new/", views.TeamCreateView.as_view(), name="team_create"),
    path("teams/edit/<int:pk>/", views.TeamUpdateView.as_view(), name="team_update"),
    path("teams/delete/<int:pk>/", views.TeamDeleteView.as_view(), name="team_delete"),

    # MATCHES
    path("matches/", views.MatchListView.as_view(), name="match_list"),
    path("matches/new/", views.MatchCreateView.as_view(), name="match_create"),
    path("matches/edit/<int:pk>/", views.MatchUpdateView.as_view(), name="match_update"),
    path("matches/delete/<int:pk>/", views.MatchDeleteView.as_view(), name="match_delete"),
]