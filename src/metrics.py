from prometheus_client import Counter, Histogram

CONVERSION_DURATION = Histogram(
    'conversion_duration_seconds',
    'Time spent converting files',
    ['source_format', 'target_format']
)

FILES_PROCESSED = Counter(
    'files_processed_total',
    'Total number of files processed',
    ['category', 'status']
)

CONVERSION_ERRORS = Counter(
    'conversion_errors_total',
    'Total number of conversion errors',
    ['exception_type']
)
