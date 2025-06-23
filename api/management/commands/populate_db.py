import os
import django
import random
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "competition_api.settings")
django.setup()

from api.models import User, Candidate, Staff, Question, Exam, CandidateScore
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Populates the database with initial data."

    def handle(self, *args, **options):
        # Create users
        user1 = User.objects.create_user(
            username="khalid",
            password="password123",
            first_name="Khalid",
            last_name="Khalid",
        )
        user2 = User.objects.create_user(
            username="bellion",
            password="password123",
            first_name="Jon",
            last_name="Bellion",
        )
        user3 = User.objects.create_user(
            username="jane", password="password123", first_name="Jane", last_name="Fox"
        )
        user4 = User.objects.create_user(
            username="ben",
            password="password123",
            first_name="Benjamin",
            last_name="Tennyson",
        )
        # Create staff
        staff1 = Staff.objects.create(
            user=user1, phone="12345", occupation="Teacher", role="admin"
        )
        staff2 = Staff.objects.create(
            user=user2, phone="67890", occupation="Engineer", role="moderator"
        )

        # Create candidates
        cand1 = Candidate.objects.create(
            user=user3, phone="55555", school="Springfield High", is_active=True
        )
        cand2 = Candidate.objects.create(
            user=user4, phone="77777", school="Riverdale High", is_active=True
        )

        # Create questions
        q1 = Question.objects.create(
            description="What is 2+2?", answer="4", created_by=staff1, difficulty="easy"
        )
        q2 = Question.objects.create(
            description="What is the capital of France?",
            answer="Paris",
            created_by=staff2,
            difficulty="medium",
        )

        # Create exams
        exam1 = Exam.objects.create(
            stage="screening",
            title="Math Test",
            description="Basic math",
            created_by=staff1,
            is_published=True,
        )
        exam2 = Exam.objects.create(
            stage="league",
            title="Geography Test",
            description="World capitals",
            created_by=staff2,
            is_published=True,
        )

        # Add questions to exams
        exam1.questions.add(q1)
        exam2.questions.add(q2)

        # Candidate scores
        CandidateScore.objects.create(
            candidate=cand1, exam=exam1, score=85.5, submitted_by=staff1
        )
        CandidateScore.objects.create(
            candidate=cand2, exam=exam2, score=90.0, submitted_by=staff2
        )

        print("Database populated successfully!")
