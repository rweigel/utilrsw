# Python's `fromisoformat`

Accepts invalid (?) time strings:

```python
from datetime import datetime
datetime.fromisoformat('2019-02-01.01')
datetime.datetime(2019, 2, 1, 1, 0)
```

# HAPI Reduced ISO 8601

See [HAPI schema](https://github.com/hapi-server/data-specification-schema/blob/main/HAPI-data-access-schema-3.3.json) for regexs for reduced ISO 8601 date-time strings.