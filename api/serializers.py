"""
Serializers for converting model instances to and from JSON representations.

Includes:
- User, Candidate, and Staff serializers
- Exam and Question serializers
- CandidateScore and registration serializers
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Candidate, Staff, Question, Exam, CandidateScore
from django.db.models import Sum

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Basic serializer for the Django User model.
    """

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined",
        )
        read_only_fields = ("id", "date_joined")


class CandidateListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing candidate info.
    """

    user = UserSerializer(read_only=True)

    class Meta:
        model = Candidate
        fields = (
            "id",
            "user",
            "phone",
            "school",
            "role",
            "is_verified",
            "date_created",
        )


class CandidateDetailSerializer(serializers.ModelSerializer):
    """
    Detailed candidate serializer including:
    - latest score
    - all scores
    - total and average score
    """

    user = UserSerializer(read_only=True)
    latest_score = serializers.SerializerMethodField()
    all_scores = serializers.SerializerMethodField()
    total_score = serializers.SerializerMethodField()
    average_score = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = (
            "id",
            "user",
            "phone",
            "school",
            "profile_photo",
            "role",
            "is_verified",
            "is_active",
            "date_created",
            "date_updated",
            "latest_score",
            "all_scores",
            "total_score",
            "average_score",
        )
        read_only_fields = ("id", "date_created", "date_updated", "user")

    def get_latest_score(self, obj):
        """
        Returns latest score for candidate if available.
        """
        try:
            latest = obj.get_latest_score()
            return {
                "exam": latest.exam.title,
                "score": latest.score,
                "date": latest.date_created,
            }
        except:
            return None

    def get_all_scores(self, obj):
        """
        Returns list of all candidate scores.
        """
        from .models import CandidateScore

        scores = CandidateScore.objects.filter(candidate=obj)
        return [
            {"exam": score.exam.title, "score": score.score, "date": score.date_created}
            for score in scores
        ]

    def get_total_score(self, obj):
        """
        Returns sum of all scores for candidate.
        """
        from .models import CandidateScore

        return (
            CandidateScore.objects.filter(candidate=obj).aggregate(total=Sum("score"))[
                "total"
            ]
            or 0
        )

    def get_average_score(self, obj):
        """
        Returns average score for candidate.
        """
        from .models import CandidateScore
        from django.db.models import Avg

        return (
            CandidateScore.objects.filter(candidate=obj).aggregate(avg=Avg("score"))[
                "avg"
            ]
            or 0
        )


class StaffListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing staff info.
    """

    user = UserSerializer(read_only=True)

    class Meta:
        model = Staff
        fields = ["id", "user", "role", "occupation", "is_verified", "date_created"]


class StaffDetailSerializer(serializers.ModelSerializer):
    """
    Detailed staff serializer.
    """

    user = UserSerializer(read_only=True)

    class Meta:
        model = Staff
        fields = (
            "id",
            "user",
            "phone",
            "occupation",
            "profile_photo",
            "role",
            "is_verified",
            "is_active",
            "date_created",
            "date_updated",
        )
        read_only_fields = ("id", "date_created", "date_updated", "user")


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for exam questions with created_by staff included.
    """

    created_by = StaffListSerializer(read_only=True)

    class Meta:
        model = Question
        fields = (
            "id",
            "description",
            "answer",
            "difficulty",
            "date_created",
            "created_by",
        )
        read_only_fields = ("id", "date_created", "created_by")


class ExamListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing exams with question count and creator.
    """

    question_count = serializers.SerializerMethodField()
    created_by = StaffListSerializer(read_only=True)

    class Meta:
        model = Exam
        fields = (
            "id",
            "title",
            "stage",
            "description",
            "exam_date",
            "duration_minutes",
            "is_published",
            "question_count",
            "created_by",
            "date_created",
        )

    def get_question_count(self, obj):
        """
        Returns the number of questions in the exam.
        """
        return obj.get_question_count()


class ExamDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a single exam, including:
    - question list
    - average score
    """

    questions = QuestionSerializer(many=True, read_only=True)
    created_by = StaffListSerializer(read_only=True)
    average_score = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = (
            "id",
            "title",
            "stage",
            "description",
            "exam_date",
            "duration_minutes",
            "is_published",
            "questions",
            "created_by",
            "average_score",
            "date_created",
        )
        read_only_fields = ("id", "date_created", "created_by")

    def get_average_score(self, obj):
        """
        Returns average score submitted for this exam.
        """
        return obj.get_average_score()


class CandidateScoreSerializer(serializers.ModelSerializer):
    """
    Serializer for candidate scores, including related candidate and exam info.
    """

    candidate = CandidateListSerializer(read_only=True)
    exam = ExamListSerializer(read_only=True)

    class Meta:
        model = CandidateScore
        fields = ("id", "candidate", "exam", "score", "date_created")
        read_only_fields = ("id", "date_created")


class CandidateRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for registering new candidates (creates User and Candidate).
    """

    user = UserSerializer()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Candidate
        fields = ("user", "password", "phone", "school", "profile_photo")

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        password = validated_data.pop("password")

        user = User.objects.create_user(
            username=user_data["username"],
            email=user_data["email"],
            first_name=user_data.get("first_name", ""),
            last_name=user_data.get("last_name", ""),
            password=password,
        )

        candidate = Candidate.objects.create(user=user, **validated_data)
        return candidate


class StaffRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for registering new staff (creates User and Staff).
    """

    user = UserSerializer()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Staff
        fields = ["user", "password", "phone", "occupation", "profile_photo"]

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        password = validated_data.pop("password")

        user = User.objects.create_user(
            username=user_data["username"],
            email=user_data["email"],
            first_name=user_data.get("first_name", ""),
            last_name=user_data.get("last_name", ""),
            password=password,
        )

        staff = Staff.objects.create(user=user, **validated_data)
        return staff
