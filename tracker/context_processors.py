def next_study(request):
    """The next day of the Bible study plan, for the sidebar on every page."""
    if not request.user.is_authenticated:
        return {}
    from .views import study_progress

    return {"next_study": study_progress(request.user)["next"]}
