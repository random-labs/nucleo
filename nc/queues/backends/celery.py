from nc.queues.backends.base import BaseQueueBackend

class CeleryQueueBackend(BaseQueueBackend):
    """
    QueueBackend implementation for celery (daemon: celeryd).
    """
    def delay(self, task, *args, **kwargs):
        """
        Use the ordinary celery delay method for queueing.
        """
        return task.delay(*args, **kwargs)

    def process(self, message):
        pass
