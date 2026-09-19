from app.models import ProjectDetails


def rejection_reason(details: ProjectDetails) -> str | None:
    """Why this project cannot be rendered, or None if it can."""
    reasons = []
    if details.has_registered_scripts:
        reasons.append("contains registered text scripts")
    if details.has_python_drivers:
        reasons.append("contains scripted Python drivers")
    if details.freestyle_enabled:
        reasons.append("Freestyle is enabled")
    if details.external_paths:
        n = len(details.external_paths)
        reasons.append(f"{n} external files (use File > External Data > Pack Resources)")
    return "; ".join(reasons) or None