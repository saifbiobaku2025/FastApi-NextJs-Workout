import logging
import os

from opentelemetry.instrumentation.logging import LoggingInstrumentor

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def configure_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    instrumentor = LoggingInstrumentor()
    if not instrumentor.is_instrumented_by_opentelemetry:
        instrumentor.instrument(
            set_logging_format=True,
            log_level=level,
            logging_format=LOG_FORMAT,
        )
    else:
        logging.basicConfig(level=level, format=LOG_FORMAT, force=False)

    logging.getLogger().setLevel(level)
