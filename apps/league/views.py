from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages

from .models import Player, Team, Match


# =========================
# HOME / PUBLIC INFO
# =========================

def home(request):
    teams = Team.objects.all().order_by("name")
    players = Player.objects.select_related("team").all().order_by("name")
    matches = Match.objects.select_related("home_team", "away_team").all().order_by("match_date")

    total_teams = teams.count()
    total_players = players.count()
    total_matches = matches.count()
    played_matches = matches.filter(status="PLAYED").count()
    scheduled_matches = matches.filter(status="SCHEDULED").count()

    starter_teams = teams.filter(category="STARTER").count()
    junior_teams = teams.filter(category="JUNIOR").count()
    upper_teams = teams.filter(category="UPPER").count()

    context = {
        "teams": teams,
        "players": players,
        "matches": matches,
        "total_teams": total_teams,
        "total_players": total_players,
        "total_matches": total_matches,
        "played_matches": played_matches,
        "scheduled_matches": scheduled_matches,
        "starter_teams": starter_teams,
        "junior_teams": junior_teams,
        "upper_teams": upper_teams,
    }
    return render(request, "league/home.html", context)


# =========================
# LOGIN VIEW
# =========================

class MyLoginView(LoginView):
    template_name = "league/login.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        user_name = self.request.user.get_full_name() or self.request.user.username
        messages.success(self.request, f"Welcome, {user_name}!")
        return response

    def get_success_url(self):
        return reverse_lazy("home")


# =========================
# PLAYERS CRUD
# =========================

class PlayerListView(LoginRequiredMixin, ListView):
    model = Player
    template_name = "league/player_list.html"
    context_object_name = "players"

    def get_queryset(self):
        return (
            Player.objects
            .select_related("team", "team__owner")
            .order_by("team__name", "name")
        )

class PlayerCreateView(LoginRequiredMixin, CreateView):
    model = Player
    fields = ["name", "number", "position", "birth_date", "team"]
    template_name = "league/player_form.html"
    success_url = reverse_lazy("player_list")

    def dispatch(self, request, *args, **kwargs):
        # Admin y Coach pueden crear jugadores
        if not request.user.is_superuser and not request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_form(self):
        form = super().get_form()

        # Coach solo puede asignar jugadores a sus equipos
        if not self.request.user.is_superuser:
            form.fields["team"].queryset = Team.objects.filter(owner=self.request.user)

        return form


class PlayerUpdateView(LoginRequiredMixin, UpdateView):
    model = Player
    fields = ["name", "number", "position", "birth_date", "team"]
    template_name = "league/player_form.html"
    success_url = reverse_lazy("player_list")

    def dispatch(self, request, *args, **kwargs):
        player = self.get_object()

        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        # Coach solo puede editar jugadores de su equipo
        if request.user.is_staff and player.team.owner == request.user:
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied

    def get_form(self):
        form = super().get_form()

        if not self.request.user.is_superuser:
            form.fields["team"].queryset = Team.objects.filter(owner=self.request.user)

        return form


class PlayerDeleteView(LoginRequiredMixin, DeleteView):
    model = Player
    template_name = "league/player_confirm_delete.html"
    success_url = reverse_lazy("player_list")

    def dispatch(self, request, *args, **kwargs):
        player = self.get_object()

        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        # Coach solo puede eliminar jugadores de su equipo
        if request.user.is_staff and player.team.owner == request.user:
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied


# =========================
# TEAMS CRUD
# =========================

class TeamListView(LoginRequiredMixin, ListView):
    model = Team
    template_name = "league/team_list.html"
    context_object_name = "teams"

    def get_queryset(self):
        # La práctica pide mostrar todos los equipos registrados
        return Team.objects.select_related("owner").all().order_by("name")


class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    fields = ["name", "city", "owner", "category"]
    template_name = "league/team_form.html"
    success_url = reverse_lazy("team_list")

    def dispatch(self, request, *args, **kwargs):
        # Solo Admin puede crear equipos
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class TeamUpdateView(LoginRequiredMixin, UpdateView):
    model = Team
    fields = ["name", "city", "owner", "category"]
    template_name = "league/team_form.html"
    success_url = reverse_lazy("team_list")

    def dispatch(self, request, *args, **kwargs):
        team = self.get_object()

        # Admin puede editar cualquier equipo
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        # Coach solo puede editar su equipo
        if request.user.is_staff and team.owner == request.user:
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied

    def get_form(self):
        form = super().get_form()

        # Coach no debe poder cambiar el owner
        if not self.request.user.is_superuser:
            form.fields["owner"].queryset = form.fields["owner"].queryset.filter(
                pk=self.request.user.pk
            )

        return form


class TeamDeleteView(LoginRequiredMixin, DeleteView):
    model = Team
    template_name = "league/team_confirm_delete.html"
    success_url = reverse_lazy("team_list")

    def dispatch(self, request, *args, **kwargs):
        # Solo Admin puede eliminar equipos
        if not request.user.is_superuser:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


# =========================
# MATCHES (SOLO VISUALIZACIÓN)
# =========================

class MatchListView(LoginRequiredMixin, ListView):
    model = Match
    template_name = "league/match_list.html"
    context_object_name = "matches"

    def get_queryset(self):
        return Match.objects.select_related("home_team", "away_team").all().order_by("match_date")


class MatchCreateView(LoginRequiredMixin, CreateView):
    model = Match
    fields = [
        "home_team",
        "away_team",
        "match_date",
        "location",
        "home_score",
        "away_score",
        "status",
    ]
    template_name = "league/match_form.html"
    success_url = reverse_lazy("match_list")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class MatchUpdateView(LoginRequiredMixin, UpdateView):
    model = Match
    fields = [
        "home_team",
        "away_team",
        "match_date",
        "location",
        "home_score",
        "away_score",
        "status",
    ]
    template_name = "league/match_form.html"
    success_url = reverse_lazy("match_list")

    def dispatch(self, request, *args, **kwargs):
        # La práctica indica que no deben editarse partidos/resultados
        raise PermissionDenied


class MatchDeleteView(LoginRequiredMixin, DeleteView):
    model = Match
    template_name = "league/match_confirm_delete.html"
    success_url = reverse_lazy("match_list")

    def dispatch(self, request, *args, **kwargs):
        # La práctica indica que no deben eliminarse partidos/resultados
        raise PermissionDenied