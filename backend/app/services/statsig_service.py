"""
Statsig integration for A/B testing interview system prompts.
All Statsig calls are wrapped in try/except so that if Statsig is
unreachable, the app falls back to Prompt A silently.
"""

import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

EXPERIMENT_NAME = "interview_system_prompt_v1"
PARAM_NAME = "system_prompt_variant"
DEFAULT_VARIANT = "A"

_statsig_initialized = False


def _make_user(user_id: str):
    """Create a StatsigUser object."""
    from statsig.statsig_user import StatsigUser
    return StatsigUser(user_id=user_id)


def _make_event(user_id: str, event_name: str, metadata: dict = None):
    """Create a StatsigEvent object."""
    from statsig.statsig_event import StatsigEvent
    event = StatsigEvent(_make_user(user_id), event_name)
    if metadata:
        event.metadata = metadata
    return event


def _init_statsig():
    """Initialize Statsig SDK once. Safe to call multiple times."""
    global _statsig_initialized
    if _statsig_initialized:
        return True
    if not settings.STATSIG_SERVER_KEY:
        logger.warning("STATSIG_SERVER_KEY not set - Statsig disabled, using default Prompt A")
        return False
    try:
        from statsig import statsig
        statsig.initialize(settings.STATSIG_SERVER_KEY)
        _statsig_initialized = True
        logger.info("Statsig initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Statsig initialization failed: {e}")
        return False


def get_variant(user_id: str) -> str:
    """
    Get the experiment variant for a user.
    Returns 'A' or 'B'. Falls back to 'A' on any error.
    """
    try:
        if not _init_statsig():
            return DEFAULT_VARIANT
        from statsig import statsig
        user = _make_user(user_id)
        experiment = statsig.get_experiment(user, EXPERIMENT_NAME)
        variant = experiment.get(PARAM_NAME, DEFAULT_VARIANT)
        return variant if variant in ("A", "B") else DEFAULT_VARIANT
    except Exception as e:
        logger.error(f"Statsig get_variant error: {e}")
        return DEFAULT_VARIANT


def log_session_started(user_id: str, variant: str):
    """Log that a session started for this variant."""
    try:
        if not _statsig_initialized:
            return
        from statsig import statsig
        statsig.log_event(_make_event(user_id, "session_started", {
            "variant": variant, "user_id": user_id
        }))
    except Exception as e:
        logger.error(f"Statsig log_session_started error: {e}")


def log_feedback_submitted(user_id: str, variant: str, rating: int, session_id: str):
    """
    Log thumbs up/down feedback.
    rating: 1 for thumbs up, -1 for thumbs down.
    """
    try:
        if not _statsig_initialized:
            return
        from statsig import statsig
        statsig.log_event(_make_event(user_id, "feedback_submitted", {
            "variant": variant,
            "user_id": user_id,
            "rating": str(rating),
            "session_id": session_id
        }))
    except Exception as e:
        logger.error(f"Statsig log_feedback_submitted error: {e}")


def log_session_completed(user_id: str, variant: str, duration_seconds: int, total_turns: int):
    """Log session completion with duration and turn count."""
    try:
        if not _statsig_initialized:
            return
        from statsig import statsig
        statsig.log_event(_make_event(user_id, "session_completed", {
            "variant": variant,
            "user_id": user_id,
            "session_duration_seconds": str(duration_seconds),
            "total_turns": str(total_turns)
        }))
    except Exception as e:
        logger.error(f"Statsig log_session_completed error: {e}")
