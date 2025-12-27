import logging
from contextvars import ContextVar

# Request ID lives here during request lifecycle
request_id_var = ContextVar("request_id", default=None)

class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='{"asctime": "%(asctime)s", "levelname": "%(levelname)s", '
               '"name": "%(name)s", "message": "%(message)s", '
               '"request_id": "%(request_id)s"}'
    )

    # Apply the filter so request_id isn't null
    for handler in logging.root.handlers:
        handler.addFilter(RequestIdFilter())
