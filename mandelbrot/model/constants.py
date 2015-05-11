
class CheckLifecycle(object):
    INITIALIZING = 'initializing'
    JOINING = 'joining'
    KNOWN = 'known'
    RETIRED = 'retired'
    SYNTHETIC = 'synthetic'

lifecycle_types = (CheckLifecycle.INITIALIZING,
                   CheckLifecycle.JOINING,
                   CheckLifecycle.KNOWN,
                   CheckLifecycle.RETIRED,
                   CheckLifecycle.SYNTHETIC)

class CheckHealth(object):
    HEALTHY = 'healthy'
    DEGRADED = 'degraded'
    FAILED = 'failed'
    UNKNOWN = 'unknown'

health_types = (CheckHealth.HEALTHY,
                CheckHealth.DEGRADED,
                CheckHealth.FAILED,
                CheckHealth.UNKNOWN)
