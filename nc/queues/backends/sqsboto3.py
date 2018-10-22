import boto3, importlib, json

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

from nc import tasks as nc_tasks
from nc.queues.backends.base import BaseQueueBackend


class SQSBoto3QueueBackend(BaseQueueBackend):
    """
    QueueBackend implementation for SQS Boto3 (daemon: aws-sqsd).

    Needs celery modules to work since using celery.app.task.
    """
    def __init__(self):
        self.client = boto3.client(
            'sqs',
            region_name=settings.AWS_SQS_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        self.queue_url = settings.AWS_SQS_BROKER_URL

    def delay(self, task, *args, **kwargs):
        """
        POST to SQS queue the appropriate JSON parameters
        for worker to eventually consume task.
        """
        response = self._send_message(task, *args, **kwargs)

    def _send_message(self, task, *args, **kwargs):
        """
        Send message to queue with task and input params.

        Return response of Successful and Failed messages.
        """
        return self.client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=self._format_message_body(task, *args, **kwargs),
        )

    def _format_message_body(self, task, *args, **kwargs):
        """
        Format message body for MessageBody of SQS queue message.
        """
        return json.dumps({
            'task': task.__name__,
            'args': args,
            'kwargs': kwargs,
        }, cls=DjangoJSONEncoder)

    def process(self, message):
        """
        Process message in worker tier.
        """
        message = json.loads(message)
        task = getattr(nc_tasks, message.get('task'), None)
        if task:
            args = message.get('args', [])
            kwargs = message.get('kwargs', {})
            task(*args, **kwargs)
