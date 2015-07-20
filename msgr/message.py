from datetime import datetime
import uuid

import coid
import json
import pilo
from pilo.fields import Datetime, Dict, String

from . import mimes


class Message(pilo.Form):

    encoding = 'utf-8'

    mime = mimes.JSON

    id = String(default=coid.Id(prefix='MSG-', encoding='base58').encode(uuid.uuid4()))
    timestamp = Datetime(format='iso8601', default=datetime.utcnow())
    headers = Dict(String(), String(), default={
        'content-encoding': encoding,
        'content-type': mime.content_type,
        })
    body = String()

    @body.munge
    def body(self, value):
        if value:
            try:
                return self.headers.content_type.loads(value)
            except Exception as exc:
                raise pilo.FieldError(exc.message, self.body)
