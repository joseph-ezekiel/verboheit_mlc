"""
Core database models for candidate assessments and staff administration.

Includes models for:
- Candidate and their role-based progression
- Staff and administrative roles
- Exams and questions
- Candidate scores with submission metadata
"""

from django.db import models
from django.db.models import Sum, Avg, Count
from django.contrib.auth import get_user_model

User = get_user_model()


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

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    school = models.CharField(max_length=150)
    profile_photo = models.ImageField(
        upload_to="profiles/", default="profiles/default.png", blank=True, null=True
    )
    id_card = models.ImageField(upload_to="id_cards/", blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    role = models.CharField(
        max_length=15, choices=ROLE_CHOICES, default="screening", db_index=True
    )

    objects = CandidateManager()

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
        return self.candidatescore_set.latest("date_created")

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
                    # ... extend as needed ...
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

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    occupation = models.CharField(max_length=50, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    profile_photo = models.ImageField(
        upload_to="staff_profiles/",
        default="staff_profiles/default.png",
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

    description = models.TextField()
    answer = models.TextField(blank=True, null=True)
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
        return f"Q{self.id}: {self.description[:50]}..."


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
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    exam_date = models.DateTimeField(blank=True, null=True, db_index=True)
    duration_minutes = models.PositiveIntegerField(default=60)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
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
    questions = models.ManyToManyField("Question", blank=True)
    is_published = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f"{self.title} ({self.id})"

    @classmethod
    def published_exams(cls):
        """
        Returns only exams marked as published.
        """
        return cls.objects.filter(is_published=True)

    def get_question_count(self):
        """
        Returns the number of questions in the exam.
        """
        return self.questions.count()

    def get_average_score(self):
        """
        Calculates the average score for all submissions tied to this exam.
        """
        return self.candidatescore_set.aggregate(avg_score=Avg("score"))["avg_score"]


class CandidateScore(models.Model):
    """
    A score representing a candidate's performance in an exam.

    Links to candidate, exam, and submitting staff member.
    """

    candidate = models.ForeignKey(
        "Candidate", on_delete=models.CASCADE, related_name="scores"
    )
    exam = models.ForeignKey("Exam", on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    date_taken = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    submitted_by = models.ForeignKey(
        "Staff", on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("candidate", "exam")
        ordering = ["-date_taken"]
