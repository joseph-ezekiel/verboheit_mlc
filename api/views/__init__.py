"""
Aggregated view imports for the API layer.

This file enables importing views from `api.views` instead of from individual modules like:
    from api.views.candidate import candidate_me_api
You can do:
    from api.views import candidate_me_api
"""

from .dashboard import *
from .candidate import *
from .staff import *
from .exam import *
from .question import *
from .score import *
from .leaderboard import *
