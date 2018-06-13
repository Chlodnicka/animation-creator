import boto3
import os
import json
import sys
from random import choice
from string import ascii_uppercase
import datetime

from flask import Flask
from flask import render_template, request, flash, redirect
from media.s3_storage import S3MediaStorage

app = Flask(__name__)
app.secret_key = "super secret key"

s3 = boto3.resource('s3')
media_storage = S3MediaStorage(s3, os.getenv('APP_BUCKET_NAME'))


@app.route("/")
def hello():
    return render_template('upload_files.html')


@app.route("/upload", methods=['POST'])
def handle_upload():
    try:
        if len(request.files) <= 1:
            return json.dumps({
                'message': 'Jeden plik to za mało by zrobić animację',
                'status': 500
            })

        if not request.form.get('email'):
            return json.dumps({
                'message': 'Podanie adresu e-mail jest wymagane. W innym wypadku nie otrzymasz animacji.',
                'status': 500
            })

        photos_list = {'email': request.form.get('email'), 'photos': []}

        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        username_dir = request.form.get('email') + '_' + now + '_' + ''.join(choice(ascii_uppercase) for i in range(20))

        for photo in request.files:
            uploaded_file = request.files[photo]
            filename, file_extension = os.path.splitext(uploaded_file.filename)

            if file_extension in ['.png', '.jpg', '.PNG', '.JPG']:
                destination = "uploaded/" + username_dir + '/' + ''.join(
                    choice(ascii_uppercase) for i in range(20)) + file_extension

                media_storage.store(
                    dest=destination,
                    source=uploaded_file
                )

                photos_list['photos'].append(destination)

        sqs = boto3.resource('sqs', region_name="eu-central-1")

        animation_queue = sqs.get_queue_by_name(QueueName=os.getenv('APP_BUCKET_NAME'))
        animation_queue.send_message(MessageBody=json.dumps(photos_list))

        return json.dumps({
            'message': 'Poprawnie dodano pliki. Oczekuj maila zwrotnego na adres: ' + request.form.get('email'),
            'status': 200
        })

    except Exception as error:
        return json.dumps({
            'message': 'Błąd podczas dodawania plików' + error.message,
            'status': 500
        })


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
