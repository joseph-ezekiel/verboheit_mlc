"""
Aggregated view imports for the API layer.

This file enables importing views from `api.views` instead of from individual modules like:
    from api.views.candidate import candidate_me_api
You can do:
    from api.views import candidate_me_api
"""

from .answers import *
from .auth import *
from .candidate import *
from .dashboard import *
from .exam import *
from .leaderboard import *
from .question import *
from .score import *
from .staff import *