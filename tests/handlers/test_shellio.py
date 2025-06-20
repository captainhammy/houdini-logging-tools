"""Tests for houdini_logging_tools.handlers.shellio module."""

# Standard Library
import logging

# Third Party
import pytest

# Houdini Logging Tools
import houdini_logging_tools.handlers.shellio

# Houdini
import hou

# Fixtures


@pytest.fixture
def init_handler(mocker):
    """Fixture to initialize a handler."""
    mocker.patch.object(
        houdini_logging_tools.handlers.shellio.PythonShellHandler,
        "__init__",
        return_value=None,
    )

    def _create():
        return houdini_logging_tools.handlers.shellio.PythonShellHandler(None)

    return _create


# Tests


class TestPythonShellHandler:
    """Test houdini_logging_tools.handlers.shellio.PythonShellHandler object."""

    def test_emit__shellio(self, init_handler, mocker):
        """Test when sys.stdout is an instance of hou.ShellIO."""
        mock_format = mocker.patch.object(houdini_logging_tools.handlers.shellio.PythonShellHandler, "format")

        mock_message = mocker.MagicMock(spec=str)

        mock_format.return_value = mock_message

        mock_record = mocker.MagicMock(spec=logging.LogRecord)
        inst = init_handler()

        mock_stream = mocker.patch("sys.stdout", spec=hou.ShellIO)
        inst.emit(mock_record)

        mock_format.assert_called_with(mock_record)

        calls = [mocker.call(mock_format.return_value), mocker.call("\n")]

        mock_stream.write.assert_has_calls(calls)
        mock_stream.flush.assert_called()

    def test_emit__not_shellio(self, init_handler, mocker):
        """Test when sys.stdout is not an instance of hou.ShellIO."""
        mock_format = mocker.patch.object(houdini_logging_tools.handlers.shellio.PythonShellHandler, "format")

        mock_message = mocker.MagicMock(spec=str)

        mock_format.return_value = mock_message

        mock_record = mocker.MagicMock(spec=logging.LogRecord)
        inst = init_handler()

        inst.emit(mock_record)

        mock_format.assert_not_called()

    def test_emit__keyboardinterrupt(self, init_handler, mocker):
        """Test when KeyboardInterrupt is raised."""
        mock_format = mocker.patch.object(houdini_logging_tools.handlers.shellio.PythonShellHandler, "format")
        mock_format.side_effect = KeyboardInterrupt

        mock_record = mocker.MagicMock(spec=logging.LogRecord)
        inst = init_handler()

        mocker.patch("sys.stdout", spec=hou.ShellIO)

        with pytest.raises(KeyboardInterrupt):
            inst.emit(mock_record)

        mock_format.assert_called_with(mock_record)

    def test_emit__systemexit(self, init_handler, mocker):
        """Test when SystemExit is raised."""
        mock_format = mocker.patch.object(houdini_logging_tools.handlers.shellio.PythonShellHandler, "format")
        mock_format.side_effect = SystemExit

        mock_record = mocker.MagicMock(spec=logging.LogRecord)
        inst = init_handler()

        mocker.patch("sys.stdout", spec=hou.ShellIO)

        with pytest.raises(SystemExit):
            inst.emit(mock_record)

        mock_format.assert_called_with(mock_record)

    def test_emit__generic_exception(self, init_handler, mocker):
        """Test when a generic exception is raised."""
        mock_format = mocker.patch.object(houdini_logging_tools.handlers.shellio.PythonShellHandler, "format")
        mock_format.side_effect = Exception

        mock_handle = mocker.patch.object(houdini_logging_tools.handlers.shellio.PythonShellHandler, "handleError")

        mock_record = mocker.MagicMock(spec=logging.LogRecord)
        inst = init_handler()

        mocker.patch("sys.stdout", spec=hou.ShellIO)

        inst.emit(mock_record)

        mock_format.assert_called_with(mock_record)
        mock_handle.assert_called_with(mock_record)
