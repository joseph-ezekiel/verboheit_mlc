"""
Core database models for candidate assessments and staff administration.

Includes models for:
- CustomUser with email as unique identifier
- Candidate and their role-based progression
- Staff and administrative roles
- Exams and questions
- Candidate scores with submission metadata
"""

from typing import Optional

from django.db import models
from django.db.models import Sum, Avg, Count
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

User = get_user_model()
# class CustomUser(AbstractUser):
#     """
#     Custom user model with unique email and username login support.
#     Users can log in with either username or email.
#     """
#     email = models.EmailField(unique=True)
#     # USERNAME_FIELD = "email"
#     # REQUIRED_FIELDS = []


class CandidateManager(models.Manager):
    """
    Custom manager for the Candidate model.

    Provides annotation methods for scores and prefetch optimization.
    """

    def with_scores(self):
        """
        Annotate candidates with total, average, and count of exam scores.
        """
        return self.annotate(
            total_score=Sum("scores__score"),
            average_score=Avg("scores__score"),
            exams_taken=Count("scores", distinct=True),
        )

    def with_complete_data(self):
        """
        Annotate candidates with scores and optimize related data fetching.
        """
        return (
            self.with_scores()
            .prefetch_related("scores__exam", "user")
            .select_related("user")
        )


class Candidate(models.Model):
    """
    Represents a student or participant in the exam system.
    Linked to a User, assigned a role, and tracks their profile and score history.
    """

    ROLE_CHOICES = (
        ("screening", "Screening"),
        ("league", "League"),
        ("final", "Final"),
        ("winner", "Winner"),
    )

    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    school = models.CharField(max_length=150)
    profile_photo = models.ImageField(
        upload_to="candidate_profile_photos/",
        default="candidate_profile_photos/default.png",
        null=True,
        blank=True,
    )
    id_card = models.ImageField(upload_to="candidate_id_cards/", blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    role = models.CharField(
        max_length=15, choices=ROLE_CHOICES, default="screening", db_index=True
    )

    objects = CandidateManager()
    total_score: Optional[float]
    average_score: Optional[float]
    exams_taken: Optional[int]
    class Meta:
        indexes = [
            models.Index(fields=["role", "is_active"]),
            models.Index(fields=["school"]),
        ]

    @property
    def score_data(self):
        """
        Returns score summary (total and average) if annotated via `with_scores()`.
        """
        if hasattr(self, "total_score"):
            return {
                "total_score": float(self.total_score or 0),
                "average_score": float(self.average_score or 0),
            }
        return None

    @property
    def is_winner(self):
        """
        Returns True if candidate has 'winner' role.
        """
        return self.role == "winner"

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.school}"

    @classmethod
    def active_candidates(cls):
        """
        Returns all currently active candidates.
        """
        return cls.objects.filter(is_active=True)

    @classmethod
    def candidates_by_role(cls, role):
        """
        Returns active candidates filtered by role.
        """
        return cls.objects.filter(role=role, is_active=True)

    def get_latest_score(self):
        """
        Returns the most recent score submitted for this candidate.
        """
        return self.scores.latest("date_recorded")

    def get_score_dict(self):
        """
        Returns a dictionary of total, average, and per-exam scores for this candidate.
        """
        return {
            "total_score": float(getattr(self, "total_score", 0)),
            "average_score": float(getattr(self, "average_score", 0)),
            "scores": [
                {
                    "exam_id": s.exam.id,
                    "exam_title": s.exam.title,
                    "score": float(s.score),
                    "date_recorded": s.date_recorded.isoformat(),
                    "submitted_by": (
                        s.submitted_by.user.get_full_name() if s.submitted_by else None
                    ),
                    "auto_score": s.auto_score,
                }
                for s in self.scores.all()
            ],
        }


class Staff(models.Model):
    """
    Administrative user with a specific role for managing candidates, exams, and scores.
    """

    ROLE_CHOICES = (
        ("owner", "Owner"),
        ("admin", "Admin"),
        ("moderator", "Moderator"),
        ("sponsor", "Sponsor"),
        ("volunteer", "Volunteer"),
    )

    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    occupation = models.CharField(max_length=50, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    profile_photo = models.ImageField(
        upload_to="staff_profile_photos/",
        default="staff_profile_photos/default.png",
        blank=True,
        null=True,
    )
    id_card = models.ImageField(upload_to="staff_id_cards/", blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default="volunteer", db_index=True
    )
    is_active = models.BooleanField(default=True, db_index=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role})"


class Question(models.Model):
    """
    A question belonging to one or more exams. Includes text, difficulty, and staff author.
    """

    QUESTION_OPTIONS = [
        ("A", "Option A"),
        ("B", "Option B"),
        ("C", "Option C"),
        ("D", "Option D"),
    ]

    text = models.TextField()
    option_a = models.CharField(max_length=255, blank=True)
    option_b = models.CharField(max_length=255, blank=True)
    option_c = models.CharField(max_length=255, blank=True)
    option_d = models.CharField(max_length=255, blank=True)
    correct_answer = models.CharField(max_length=1, choices=QUESTION_OPTIONS)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "Staff",
        blank=True,
        null=True,
        related_name="questions_created",
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        "Staff",
        blank=True,
        null=True,
        related_name="questions_updated",
        on_delete=models.SET_NULL,
    )
    difficulty = models.CharField(
        max_length=10,
        choices=[("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")],
        default="medium",
    )

    def __str__(self):
        return f"Q{self.id}: {self.text[:50]}..."


class Exam(models.Model):
    """
    Represents a collection of questions scheduled at a specific date for a stage of competition.
    """

    STAGE_CHOICES = (
        ("screening", "Screening"),
        ("league", "League"),
    )

    stage = models.CharField(
        max_length=20, choices=STAGE_CHOICES, default="league", db_index=True
    )
    title = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=False, db_index=True)
    exam_date = models.DateTimeField(blank=True, null=True, db_index=True)
    open_duration_hours = models.PositiveIntegerField(default=12)
    countdown_minutes = models.PositiveIntegerField(default=60)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    questions = models.ManyToManyField("Question", blank=True)
    created_by = models.ForeignKey(
        "Staff",
        blank=True,
        null=True,
        related_name="exams_created",
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        "Staff",
        blank=True,
        null=True,
        related_name="exams_updated",
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return f"{self.title} ({self.id})"

    @classmethod
    def active_exams(cls):
        """
        Returns only exams marked as active.
        """
        return cls.objects.filter(is_active=True)

    @property
    def is_currently_open(self):
        """
        Exam is open only if it's active, and either:
        - exam_date is None (always open)
        - or current time is within open window
        """
        from django.utils import timezone
        from datetime import timedelta

        if not self.is_active:
            return False
        if self.exam_date is None:
            return True
        now = timezone.now()
        end_time = self.exam_date + timedelta(hours=self.open_duration_hours)
        return self.exam_date <= now <= end_time

    def get_question_count(self):
        """
        Returns the number of questions in the exam.
        """
        return self.questions.count()

    def get_average_score(self):
        """
        Calculates the average score for all submissions tied to this exam.
        """
        return self.scores.aggregate(avg_score=Avg("score"))["avg_score"]


class CandidateScore(models.Model):
    """
    A score representing a candidate's performance in an exam.

    Links to candidate, exam, and submitting staff member.
    """

    candidate = models.ForeignKey(
        "Candidate", on_delete=models.CASCADE, related_name="scores"
    )
    exam = models.ForeignKey("Exam", on_delete=models.CASCADE, related_name="scores")
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    date_recorded = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    submitted_by = models.ForeignKey(
        "Staff", on_delete=models.SET_NULL, null=True, blank=True
    )
    auto_score = models.BooleanField(default=False, db_index=True)

    class Meta:
        unique_together = ("candidate", "exam")
        ordering = ["-date_recorded"]


class CandidateAnswer(models.Model):
    candidate_score = models.ForeignKey(
        "CandidateScore", related_name="answers", on_delete=models.CASCADE
    )
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    selected_option = models.CharField(
        max_length=1,
        choices=Question.QUESTION_OPTIONS,
        blank=True,
        null=True,
    )
    answered_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['candidate_score', 'question'], name='unique_answer_per_candidate_score')
        ]



class LeaderboardSnapshot(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()

    published_by = models.ForeignKey(
        "Staff", on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["-created_at"]

class FeatureFlag(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.BooleanField(default=True)

    @classmethod
    def get_bool(cls, key, default=True):
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default
        
