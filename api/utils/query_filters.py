from django.db.models import Q

def filter_candidates(queryset, params):
    role = params.get('role')
    league = params.get('league')
    is_active = params.get('is_active')
    search = params.get('search')

    if role:
        queryset = queryset.filter(role=role)

    if league:
        queryset = queryset.filter(league=league)

    if is_active is not None:
        if is_active.lower() == 'true':
            queryset = queryset.filter(user__is_active=True)
        elif is_active.lower() == 'false':
            queryset = queryset.filter(user__is_active=False)

    if search:
        queryset = queryset.filter(user__username__icontains=search)

    return queryset

def filter_staffs(queryset, params):
    role = params.get('role')
    is_active = params.get('is_active')
    search = params.get('search')

    if role:
        queryset = queryset.filter(role=role)

    if is_active is not None:
        if is_active.lower() == 'true':
            queryset = queryset.filter(user__is_active=True)
        elif is_active.lower() == 'false':
            queryset = queryset.filter(user__is_active=False)

    if search:
        queryset = queryset.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__email__icontains=search)
        )

    return queryset

def filter_questions(queryset, params):
    search = params.get('search')
    difficulty = params.get('difficulty')

    if search:
        queryset = queryset.filter(Q(description__icontains=search))

    if difficulty:
        queryset = queryset.filter(difficulty=difficulty)

    return queryset

def filter_exams(queryset, params):
    search = params.get('search')
    date_created = params.get('date_created')

    if search:
        queryset = queryset.filter(Q(title__icontains=search) | Q(stage__icontains=search))

    if date_created:
        queryset = queryset.filter(date_created=date_created)

    return queryset