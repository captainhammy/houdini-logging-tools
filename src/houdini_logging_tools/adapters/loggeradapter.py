"""Custom logging adapter for Houdini."""

# Future
from __future__ import annotations

# Standard Library
import logging
from functools import wraps
from typing import Any, Callable, Self

# Houdini Logging Tools
from houdini_logging_tools.mappings import LOGGING_TO_SEVERITY_MAP

# Houdini
import hou

# Globals

# Call kwargs that should be moved into the extra data passed to process().
_KWARGS_TO_EXTRA_KEYS = (
    "node",
    "dialog",
    "status_bar",
    "title",
)


# Classes


class HoudiniLoggerAdapter(logging.LoggerAdapter):
    """Custom LoggerAdapter for Houdini.

    This adapter allows automated addition of node paths and log display in dialogs,
    status bar, etc. Also allows for automated notification.

    Args:
        base_logger:
            The base package logger.
        node:
            Optional node for prefixing messages with the path.
        dialog:
            Whether to always use the dialog option.
        status_bar:
            Whether to always use the status bar option.
        extra:
            Extra args to use to generate log messages.
    """

    def __init__(
        self,
        base_logger: logging.Logger,
        node: hou.Node = None,
        *,
        dialog: bool = False,
        status_bar: bool = False,
        extra: dict | None = None,
    ) -> None:
        extra = extra or {}

        super().__init__(base_logger, extra)

        self._dialog = dialog
        self._node = node
        self._status_bar = status_bar

    def __new__(
        cls: type[Self],
        *args: Any,
        **kwargs: Any,
    ) -> Self:  # pragma: no cover
        """Overridden __new__ that will wrap logging methods with custom function."""
        inst = super().__new__(cls)

        # We want to wrap various log calls to process args and set severities.
        for key, severity in LOGGING_TO_SEVERITY_MAP.items():
            if hasattr(inst, key):
                attr = getattr(inst, key)

                if callable(attr):
                    wrapped = _wrap_logger(attr, severity)

                    setattr(inst, key, wrapped)

        return inst

    # Class Methods

    @classmethod
    def from_name(
        cls: type[Self],
        name: str,
        node: hou.Node = None,
        *,
        dialog: bool = False,
        status_bar: bool = False,
        extra: dict | None = None,
    ) -> HoudiniLoggerAdapter:
        """Create a new HoudiniLoggerAdapter from a name.

        This is a convenience function around the following code:

        >>> base_log = logging.getLogger(name)
        >>> logger = HoudiniLoggerAdapter(base_log)

        Args:
            name:
                The name of the logger to use.
            node:
                Optional node for prefixing messages with the path.
            dialog:
                Whether to always use the dialog option.
            status_bar:
                Whether to always use the status bar option.
            extra:
                Extra args to use to generate log messages.

        Returns:
            An adapter wrapping a logger of the passed name.
        """
        # Create a base logger
        base_logger = logging.getLogger(name)

        return cls(base_logger, node=node, dialog=dialog, status_bar=status_bar, extra=extra)

    # Properties

    @property
    def dialog(self) -> bool:
        """Whether the dialog will be displayed."""
        return self._dialog

    @dialog.setter
    def dialog(self, dialog: bool) -> None:
        self._dialog = dialog

    # --------------------------------------------------------------------------

    @property
    def node(self) -> hou.Node | None:
        """A node the logger is associated with."""
        return self._node

    @node.setter
    def node(self, node: hou.Node | None) -> None:
        self._node = node

    # --------------------------------------------------------------------------

    @property
    def status_bar(self) -> bool:
        """Whether the message will be logged to the status bar."""
        return self._status_bar

    @status_bar.setter
    def status_bar(self, status_bar: bool) -> None:
        self._status_bar = status_bar

    # Methods

    def process(self, msg: str, kwargs: Any) -> tuple[str, Any]:
        """Override function to handle custom logic.

        This will possibly insert a node path or to display a dialog with the log
        message before being passed to regular logging output.

        Args:
            msg:
                The log message.
            kwargs:
                kwargs dict.

        Returns:
            The message and updated kwargs.
        """
        extra: dict = self.extra  # type: ignore

        if "extra" in kwargs:
            extra.update(kwargs["extra"])

            node = extra.pop("node", self.node)

            # Prepend the message with the node path.
            if node is not None:
                msg = f"{node.path()} - {msg}"

            dialog = extra.pop("dialog", self.dialog)
            status_bar = extra.pop("status_bar", self.status_bar)

            if hou.isUIAvailable():
                # Copy of the message for our display.
                houdini_message = msg

                # If we have message args we need to format the message with them.
                if "message_args" in extra:
                    houdini_message %= extra["message_args"]

                severity = extra.pop("severity", hou.severityType.Message)

                # Display the message as a popup.
                if dialog:
                    title = extra.pop("title", None)

                    hou.ui.displayMessage(houdini_message, severity=severity, title=title)

                if status_bar:
                    hou.ui.setStatusMessage(houdini_message, severity=severity)

        kwargs["extra"] = extra

        return msg, kwargs


# Non-Public Functions


def _wrap_logger(func: Callable, severity: hou.severityType) -> Callable:
    """Function which wraps a logger method with custom code.

    Args:
        func:
            The callable to wrap.

        severity:
            The corresponding hou.severityType value.

    Returns:
        The wrapped function.
    """

    @wraps(func)
    def func_wrapper(*args: Any, **kwargs: Any) -> Any:
        # Get the extra dictionary, or an empty one if it doesn't exist.
        extra = kwargs.setdefault("extra", {})

        # Set the severity to our passed in value.
        extra["severity"] = severity

        for key in _KWARGS_TO_EXTRA_KEYS:
            if key in kwargs:
                extra[key] = kwargs.pop(key)

        # If there is more than one arg, we want to pass them as extra data so that
        # we can use it to format the message for extra outputs.
        if len(args) > 1:
            extra["message_args"] = args[1:]

        if "stacklevel" not in kwargs:
            # Set stacklevel=4 so that the module/file/line reporting will represent
            # the calling point and not the function call inside the adapter.
            kwargs["stacklevel"] = 4

        return func(*args, **kwargs)

    return func_wrapper
