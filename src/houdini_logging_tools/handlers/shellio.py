"""Custom logging stream handler which writes to Houdini Python Shell panels."""

# Standard Library
import logging
import sys

# Houdini
import hou

# Classes


class PythonShellHandler(logging.StreamHandler):
    """Custom stream handler which outputs to the interactive Python shell when it is open.

    Houdini will redirect sys.stdout to be an instance of hou.ShellIO when there
    is a Python Shell panel active and displayed.  This handler works by checking
    that sys.stdout is a hou.ShellIO and writes output to it accordingly.  Otherwise,
    no output will be written.
    """

    # Methods

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log message.

        Args:
            record:
                The log record to emit.
        """
        try:
            # Get the current stdout stream. Houdini will muck around with
            # this depending on whether a PythonShell panel is open.
            stream = sys.stdout

            # If the stream is really an output to a Python Shell, then we know
            # that we want to write the message to it. Otherwise, a panel isn't
            # open, so we don't have anything to write to.
            if isinstance(stream, hou.ShellIO):
                # Format the message
                msg = self.format(record)

                stream.write(msg)
                stream.write("\n")
                stream.flush()

        # Re-raise these as we don't want to actually handle them.
        except KeyboardInterrupt:
            raise

        except SystemExit:
            raise

        # Otherwise, handle the error.
        except Exception:  # noqa: BLE001
            self.handleError(record)
