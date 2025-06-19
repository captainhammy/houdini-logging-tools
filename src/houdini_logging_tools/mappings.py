"""Mappings between logging levels and Houdini severities."""

# Houdini
import hou

LOGGING_TO_SEVERITY_MAP = {
    "critical": hou.severityType.Error,
    "debug": hou.severityType.Message,
    "error": hou.severityType.Error,
    "exception": hou.severityType.Error,
    "info": hou.severityType.ImportantMessage,
    "warning": hou.severityType.Warning,
}
"""Mapping between logging levels and Houdini severity enum values."""
