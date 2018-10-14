class BaseQueueBackend(object):
    """
    BaseQueueBackend class to inherit from when implementing
    task-worker based methods.
    """
    client = None
    queue_url = ''

    def delay(self, task, *args, **kwargs):
        raise NotImplementedError('`delay()` must be implemented.')

    def process(message):
        raise NotImplementedError('`process()` must be implemented.')
