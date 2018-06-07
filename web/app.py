import boto3
import os
import json

from flask import Flask
from flask import render_template, request, flash
from media.s3_storage import S3MediaStorage
 
app = Flask(__name__)

s3 = boto3.resource('s3')
media_storage = S3MediaStorage(s3, os.getenv('APP_BUCKET_NAME'))

photos_list = {'email' : 'maja.chlodnicka@gmail.com', 'photos': []}

@app.route("/")
def hello():
    return render_template(
      'upload_files.html'
    )
@app.route("/upload", methods=['POST'])
def handle_upload():
  if 'uploaded_file' not in request.files:
    flash('No file part')
    return redirect(request.url)

  uploaded_file = request.files['uploaded_file']  
  destination = "/uploaded/%s" % uploaded_file.filename
 
  media_storage.store(
     dest=destination,
     source=uploaded_file
  )

  photos_list['photos'].append(destination)
  
  sqs = boto3.resource('sqs', region_name="eu-central-1")

  tweets = sqs.get_queue_by_name(QueueName='tweets')
  response = tweets.send_message(MessageBody='Hello World', MessageAttributes={
    'Author': {
        'StringValue': 'Jakub',
        'DataType': 'String'
    }
  })

  return json.dumps(photos_list) 


@app.route("/prepare")
def prepare():
  return render_template(
    'prepare.html',
    invitation="the only limit is yourself" 
  )

if __name__ == '__main__':
  app.run(host="0.0.0.0", port=8080, debug=True)
