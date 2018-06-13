import boto3, time, os

sqs = boto3.resource('sqs', region_name="eu-central-1")

videoQueue = sqs.get_queue_by_name(QueueName=os.getenv('APP_BUCKET_NAME'))

while True:
  for message in videoQueue.receive_messages():
    print('Message body: %s' % message.body)

    #todo: merge photos to video
    #todo: upload video to s3 and make public
    #todo: send mail to user with link to download video
    message.delete()
  time.sleep(1)

