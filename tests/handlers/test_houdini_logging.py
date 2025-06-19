"""Tests for houdini_logging_tools.handlers.houdini_logging module."""

# Standard Library
import logging

# Third Party
import pytest

# Houdini Logging Tools
import houdini_logging_tools.handlers.houdini_logging

# Houdini
import hou

# Fixtures


@pytest.fixture
def init_handler(mocker):
    """Fixture to initialize a handler."""
    mocker.patch.object(
        houdini_logging_tools.handlers.houdini_logging.HoudiniLoggingHandler,
        "__init__",
        return_value=None,
    )

    def _create():
        return houdini_logging_tools.handlers.houdini_logging.HoudiniLoggingHandler(None)

    return _create


# Tests


class TestHoudiniLoggingHandler:
    """Test houdini_logging_tools.handlers.houdini_logging.HoudiniLoggingHandler object."""

    def test___init__(self, mocker):
        """Test object initialization."""
        source_name = houdini_logging_tools.handlers.houdini_logging.HoudiniLoggingHandler.__name__

        assert source_name not in hou.logging.sources()

        mock_stream = mocker.MagicMock()

        inst = houdini_logging_tools.handlers.houdini_logging.HoudiniLoggingHandler(mock_stream)
        assert inst.stream == mock_stream

        assert source_name in hou.logging.sources()


    def test_emit(self, init_handler, mocker):
        """Test HoudiniLoggingHandler.emit()."""
        mock_record = mocker.MagicMock(spec=logging.LogRecord)
        mock_record.name = mocker.PropertyMock()
        mock_record.module = mocker.PropertyMock()
        mock_record.funcName = mocker.PropertyMock()
        mock_record.lineno = mocker.PropertyMock()
        mock_record.levelname = "error"
        mock_record.created = mocker.PropertyMock()

        mock_format = mocker.patch.object(
            houdini_logging_tools.handlers.houdini_logging.HoudiniLoggingHandler, "format"
        )
        mock_log = mocker.patch("hou.logging.log")
        mock_entry = mocker.patch("hou.logging.LogEntry")

        inst = init_handler()

        inst.emit(mock_record)

        mock_entry.assert_called_with(
            message=mock_format.return_value,
            source_context=f"{mock_record.name} | {mock_record.module}.{mock_record.funcName}:{mock_record.lineno}",
            severity=hou.severityType.Error,
            time=mock_record.created,
        )
        mock_log.assert_called_with(mock_entry.return_value, inst.__class__.__name__)
