"""Custom logging stream handler which writes to the Houdini logging API."""

# Standard Library
import logging

# Houdini Logging Tools
from houdini_logging_tools.mappings import LOGGING_TO_SEVERITY_MAP

# Houdini
import hou

# Classes


class HoudiniLoggingHandler(logging.StreamHandler):
    """Custom stream handler which outputs to the Houdini logging API."""

    def __init__(self, stream=None) -> None:  # type: ignore
        super().__init__(stream=stream)

        # Create a new source for the handler to emit to.
        hou.logging.createSource(self.__class__.__name__)

    # Methods

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log message.

        Args:
            record:
                The log record to emit.
        """
        context = f"{record.name} | {record.module}.{record.funcName}:{record.lineno}"

        entry = hou.logging.LogEntry(
            message=self.format(record),
            source_context=context,
            severity=LOGGING_TO_SEVERITY_MAP[record.levelname.lower()],
            time=record.created,
        )

        hou.logging.log(entry, self.__class__.__name__)
