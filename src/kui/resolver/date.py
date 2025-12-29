from datetime import datetime
from kutil.logger import get_logger
from kui.core.resolver import ContentResolver


_logger = get_logger(__name__)


class DateResolver(ContentResolver):

    def resolve(self, key: str, *args, **kw):

        if key == "year":
            return datetime.now().year

        return None
