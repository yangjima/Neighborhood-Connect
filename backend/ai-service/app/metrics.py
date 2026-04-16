from prometheus_client import Counter, Histogram, Gauge

# Request metrics
ai_requests_total = Counter(
    'ai_requests_total',
    'Total AI search requests',
    ['intent', 'status']
)

ai_request_duration = Histogram(
    'ai_request_duration_seconds',
    'AI request duration in seconds',
    ['agent']
)

# LLM metrics
ai_llm_tokens = Counter(
    'ai_llm_tokens_total',
    'Total LLM tokens used',
    ['model', 'type']  # type: prompt/completion
)

# Cache metrics
ai_cache_hits = Counter('ai_cache_hits_total', 'Cache hits')
ai_cache_misses = Counter('ai_cache_misses_total', 'Cache misses')

# Agent metrics
ai_agent_success = Counter(
    'ai_agent_success_total',
    'Agent success count',
    ['agent']
)

ai_agent_failure = Counter(
    'ai_agent_failure_total',
    'Agent failure count',
    ['agent', 'error_type']
)

# Active requests
ai_active_requests = Gauge(
    'ai_active_requests',
    'Number of active AI requests'
)
