# Metrics Catalog

Proposed low-cardinality service metrics:

| Metric | Meaning | Labels |
|---|---|---|
| `http_requests_total` | Request count | method, route template, status class |
| `http_request_duration_seconds` | Request latency | method, route template |
| `reading_ingest_rejections_total` | Rejected ingestion attempts | reason category |
| `dashboard_login_failures_total` | Failed login count | reason category |
| `database_operation_errors_total` | Database operation failures | operation category |

Never label metrics with device secrets, tokens, usernames, IP addresses, or reading values. These are recommendations, not evidence of current instrumentation.
