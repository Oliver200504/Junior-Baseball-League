import re

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.timezone import now


# =========================
# TEAM MODEL
# =========================

class Team(models.Model):

    CATEGORY_CHOICES = [
        ("STARTER", "Starter 6-9"),
        ("JUNIOR", "Junior 10-13"),
        ("UPPER", "Upper 14-17"),
    ]

    name = models.CharField(
        max_length=100,
        unique=True
    )

    city = models.CharField(
        max_length=100
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="teams",
        default=1
    )

    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        default="STARTER"
    )

    def clean(self):
        if not self.name.strip():
            raise ValidationError(
                "Team name cannot be empty."
            )

        if not self.city.strip():
            raise ValidationError(
                "City cannot be empty."
            )

        # Team name cannot contain numbers
        if re.search(r"\d", self.name):
            raise ValidationError(
                "Team name cannot contain numbers."
            )

    @property
    def coach_name(self):
        full_name = self.owner.get_full_name().strip()
        return full_name if full_name else self.owner.username

    def __str__(self):
        return f"{self.name} - {self.get_category_display()}"


# =========================
# PLAYER MODEL
# =========================

class Player(models.Model):

    POSITION_CHOICES = [
        ("PITCHER", "Pitcher"),
        ("CATCHER", "Catcher"),
        ("FIRST BASE", "First Base"),
        ("SECOND BASE", "Second Base"),
        ("THIRD BASE", "Third Base"),
        ("SHORTSTOP", "Shortstop"),
        ("LEFT FIELD", "Left Field"),
        ("CENTER FIELD", "Center Field"),
        ("RIGHT FIELD", "Right Field"),
    ]

    name = models.CharField(
        max_length=100
    )

    number = models.IntegerField()

    position = models.CharField(
        max_length=50,
        choices=POSITION_CHOICES
    )

    birth_date = models.DateField()

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("team", "number")

    def clean(self):
        if not self.name.strip():
            raise ValidationError(
                "Player name cannot be empty."
            )

        if re.search(r"\d", self.name):
            raise ValidationError(
                "Player name cannot contain numbers."
            )

        if self.number <= 0:
            raise ValidationError(
                "Player number must be greater than 0."
            )

        if self.number > 99:
            raise ValidationError(
                "Player number cannot be greater than 99."
            )

        if self.birth_date > now().date():
            raise ValidationError(
                "Birth date cannot be in the future."
            )

        # Edad aproximada
        current_year = now().year
        player_age = current_year - self.birth_date.year

        if self.team.category == "STARTER":
            if player_age < 6 or player_age > 9:
                raise ValidationError(
                    "Starter category only accepts ages 6 to 9."
                )

        elif self.team.category == "JUNIOR":
            if player_age < 10 or player_age > 13:
                raise ValidationError(
                    "Junior category only accepts ages 10 to 13."
                )

        elif self.team.category == "UPPER":
            if player_age < 14 or player_age > 17:
                raise ValidationError(
                    "Upper category only accepts ages 14 to 17."
                )

    def __str__(self):
        return f"{self.name} - #{self.number}"


# =========================
# MATCH MODEL
# =========================

class Match(models.Model):

    home_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="home_matches"
    )

    away_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="away_matches"
    )

    match_date = models.DateField()

    location = models.CharField(
        max_length=150
    )

    home_score = models.IntegerField(default=0)
    away_score = models.IntegerField(default=0)

    STATUS_CHOICES = [
        ("SCHEDULED", "Scheduled"),
        ("PLAYED", "Played"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="SCHEDULED"
    )

    def clean(self):
        if self.home_team == self.away_team:
            raise ValidationError(
                "A team cannot play against itself."
            )

        if self.home_team.category != self.away_team.category:
            raise ValidationError(
                "Both teams must belong to the same category."
            )

        if not self.location.strip():
            raise ValidationError(
                "Location cannot be empty."
            )

        if self.home_score < 0 or self.away_score < 0:
            raise ValidationError(
                "Scores cannot be negative."
            )

        # Si el partido está programado, no debe tener marcador
        if self.status == "SCHEDULED":
            if self.home_score != 0 or self.away_score != 0:
                raise ValidationError(
                    "Scheduled matches cannot have scores."
                )

        # Si el partido ya fue jugado, se permiten marcadores >= 0
        # incluyendo 0-0, porque un empate sin carreras puede existir.
        if self.status == "PLAYED":
            if self.match_date > now().date():
                raise ValidationError(
                    "A played match cannot have a future date."
                )

        # Si el partido está programado, sí debe estar hoy o en el futuro
        if self.status == "SCHEDULED" and self.match_date < now().date():
            raise ValidationError(
                "A scheduled match cannot have a past date."
            )

        existing_match = Match.objects.filter(
            home_team=self.home_team,
            away_team=self.away_team,
            match_date=self.match_date
        ).exclude(pk=self.pk)

        if existing_match.exists():
            raise ValidationError(
                "This match already exists for that date."
            )

        same_day_match = Match.objects.filter(
            match_date=self.match_date
        ).filter(
            models.Q(home_team=self.home_team) |
            models.Q(away_team=self.home_team) |
            models.Q(home_team=self.away_team) |
            models.Q(away_team=self.away_team)
        ).exclude(pk=self.pk)

        if same_day_match.exists():
            raise ValidationError(
                "One of the teams already has a match that day."
            )

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name}"