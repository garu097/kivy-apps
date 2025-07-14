import logging
import sys
from logging import Formatter, LogRecord


class MultilineFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        # Shorten level names
        if record.levelname == "WARNING":
            record.levelname = "WARN"
        elif record.levelname == "ERROR":
            record.levelname = "ERR"

        # Call super().format for each line in the message
        lines = record.getMessage().split("\n")
        formatted_lines = []
        for line in lines:
            record.msg = line
            formatted_lines.append(super().format(record))
        return "\n".join(formatted_lines)


class MergeExtraLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        kwargs["extra"] = {**self.extra, **kwargs.get("extra", {})}
        return msg, kwargs


# Configure root logger
logging.basicConfig()

formatter = MultilineFormatter(
    fmt="%(asctime)s [%(job)-5s] %(levelname)-4s %(name)s [%(filename)s:%(lineno)d]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.handlers = [handler]
root_logger.setLevel(logging.INFO)


def get_logger(name: str, extra={"job": ""}):
    # Return configured logger if name is provided
    logger = logging.getLogger(name)
    return MergeExtraLoggerAdapter(logger, extra) if extra else logger
