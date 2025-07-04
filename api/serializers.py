"""
Serializers for converting model instances to and from JSON representations.

Includes:
- User, Candidate, and Staff serializers
- Exam and Question serializers
- CandidateScore and registration serializers
"""

from django.db.models import Sum
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError
from django.db import transaction

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import (
    Candidate, Staff,
    Question, Exam,
    CandidateScore, CandidateAnswer,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Basic serializer for the Django User model.
    """
    username = serializers.CharField(max_length=14,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

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
        

class MinimalCandidateSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for listing candidate info.
    """

    user = UserSerializer(read_only=True)

    class Meta:
        model = Candidate
        fields = ["user", "school"]
    


class CandidateListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing candidate info.
    """

    user = UserSerializer(read_only=True)

    class Meta:
        model = Candidate
        fields = (
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
        read_only_fields = ("date_created", "date_updated", "user")
        
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
            {"exam": score.exam.title, "score": score.score, "date": score.date_recorded}
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

class MinimalStaffSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for listing staff info.
    """

    user = UserSerializer(read_only=True)

    class Meta:
        model = Staff
        fields = ["user"]

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "username": obj.user.username,
        }

class StaffListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing staff info.
    """

    user = UserSerializer(read_only=True)

    class Meta:
        model = Staff
        fields = ["user", "role", "occupation", "is_verified", "date_created"]


class StaffDetailSerializer(serializers.ModelSerializer):
    """
    Detailed staff serializer.
    """

    user = UserSerializer(read_only=True)

    class Meta:
        model = Staff
        fields = (
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
        read_only_fields = ("date_created", "date_updated", "user")


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for exam questions with created_by staff included.
    """

    created_by = MinimalStaffSerializer(read_only=True)

    class Meta:
        model = Question
        fields = (
            "id",
            "text",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_answer",
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
    created_by = MinimalStaffSerializer(read_only=True)

    class Meta:
        model = Exam
        fields = (
            "id",
            "title",
            "stage",
            "description",
            "exam_date",
            "countdown_minutes",
            "open_duration_hours",
            "is_active",
            "is_currently_open",
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
    questions = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.all(),
        many=True
    )
    created_by = MinimalStaffSerializer(read_only=True)
    average_score = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = (
            "id",
            "title",
            "stage",
            "description",
            "exam_date",
            "countdown_minutes",
            "open_duration_hours",
            "is_active",
            "questions",
            "created_by",
            "updated_by",
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
        fields = ("id", "candidate", "exam", "score", "date_recorded")
        read_only_fields = ("id", "date_created")


class CandidateRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for registering new candidates (creates User and Candidate).
    """

    user = UserSerializer()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = Candidate
        fields = ("user", "password1", "password2", "phone", "school", "profile_photo")

    def validate(self, attrs):
        if attrs.get("password1") != attrs.get("password2"):
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return attrs

    def validate_password1(self, value):
        """
        Custom password validation using Django's built-in validators.
        """
        try:
            password_validation.validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        password, _ = validated_data.pop("password1"), validated_data.pop("password2")

        with transaction.atomic():
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
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = Staff
        fields = ["user", "password1", "password2", "phone", "occupation", "profile_photo"]
        
    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return data
    
    def validate_password1(self, value):
        """
        Custom password validation using Django's built-in validators.
        """
        try:
            password_validation.validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        password, _ = validated_data.pop("password1"), validated_data.pop("password2")

        with transaction.atomic():
            user = User.objects.create_user(
                username=user_data["username"],
                email=user_data["email"],
                first_name=user_data.get("first_name", ""),
                last_name=user_data.get("last_name", ""),
                password=password,
            )

            staff = Staff.objects.create(user=user, **validated_data)
            return staff


class CandidateAnswerSerializer(serializers.ModelSerializer):
    """
    Represents a candidate's answer to a question.
    - If a question is unanswered, set 'selected_option' to an empty string "".
    """
    selected_option = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = CandidateAnswer
        fields = ['question', 'selected_option']

class CandidateAnswerBulkSerializer(serializers.Serializer):
    answers = CandidateAnswerSerializer(many=True)

    def validate_answers(self, value):
        if not value:
            raise serializers.ValidationError("At least one answer must be provided.")
        return value
    
class CandidateQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            "id",
            "text",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
        )

class CandidateExamSerializer(serializers.ModelSerializer):
    questions = CandidateQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Exam
        fields = (
            "id",
            "title",
            "stage",
            "description",
            "open_duration_hours",
            "exam_date",
            "countdown_minutes",
            "questions",
        )