from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Candidate, Staff, Question, Exam, CandidateScore

User = get_user_model()

# Basic User serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']

# Candidate serializers
class CandidateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for lists"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = Candidate
        fields = ['id', 'user', 'school', 'role', 'is_verified', 'date_created']

class CandidateDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    latest_score = serializers.SerializerMethodField()
    all_scores = serializers.SerializerMethodField()
    total_score = serializers.SerializerMethodField()
    average_score = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = [
            'id', 'user', 'phone', 'school', 'profile_photo',
            'role', 'is_verified', 'is_active', 'date_created',
            'date_updated', 'latest_score', 'all_scores',
            'total_score', 'average_score'
        ]
        read_only_fields = ['id', 'date_created', 'date_updated', 'user']

    def get_latest_score(self, obj):
        try:
            latest = obj.get_latest_score()
            return {
                'exam': latest.exam.title,
                'score': latest.score,
                'date': latest.date_created
            }
        except:
            return None

    def get_all_scores(self, obj):
        from .models import CandidateScore  # Avoid circular imports
        scores = CandidateScore.objects.filter(candidate=obj)
        return [
            {
                'exam': score.exam.title,
                'score': score.score,
                'date': score.date_created
            }
            for score in scores
        ]

    def get_total_score(self, obj):
        from .models import CandidateScore
        return CandidateScore.objects.filter(candidate=obj).aggregate(total=serializers.Sum('score'))['total'] or 0

    def get_average_score(self, obj):
        from .models import CandidateScore
        from django.db.models import Avg
        return CandidateScore.objects.filter(candidate=obj).aggregate(avg=Avg('score'))['avg'] or 0


# Staff serializers
class StaffListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Staff
        fields = ['id', 'user', 'role', 'occupation', 'is_verified', 'date_created']

class StaffDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Staff
        fields = ['id', 'user', 'phone', 'occupation', 'profile_photo',
                 'role', 'is_verified', 'is_active', 'date_created', 'date_updated']
        read_only_fields = ['id', 'date_created', 'date_updated', 'user']

# Question serializer
class QuestionSerializer(serializers.ModelSerializer):
    created_by = StaffListSerializer(read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'description', 'answer', 'difficulty',
                 'date_created', 'created_by']
        read_only_fields = ['id', 'date_created', 'created_by']

# Exam serializers
class ExamListSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()
    created_by = StaffListSerializer(read_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'title', 'stage', 'description', 'exam_date',
                 'duration_minutes', 'is_published', 'question_count',
                 'created_by', 'date_created']

    def get_question_count(self, obj):
        return obj.get_question_count()

class ExamDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    created_by = StaffListSerializer(read_only=True)
    average_score = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = ['id', 'title', 'stage', 'description', 'exam_date',
                 'duration_minutes', 'is_published', 'questions',
                 'created_by', 'average_score', 'date_created']
        read_only_fields = ['id', 'date_created', 'created_by']

    def get_average_score(self, obj):
        return obj.get_average_score()

# Score serializer
class CandidateScoreSerializer(serializers.ModelSerializer):
    candidate = CandidateListSerializer(read_only=True)
    exam = ExamListSerializer(read_only=True)

    class Meta:
        model = CandidateScore
        fields = ['id', 'candidate', 'exam', 'score', 'date_created']
        read_only_fields = ['id', 'date_created']

# Registration serializers
class CandidateRegistrationSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Candidate
        fields = ['user', 'password', 'phone', 'school', 'profile_photo']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = validated_data.pop('password')

        # Create user
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            password=password
        )

        # Create candidate
        candidate = Candidate.objects.create(user=user, **validated_data)
        return candidate

class StaffRegistrationSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Staff
        fields = ['user', 'password', 'phone', 'occupation', 'profile_photo']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = validated_data.pop('password')

        # Create user
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            password=password
        )

        # Create staff
        staff = Staff.objects.create(user=user, **validated_data)
        return staff