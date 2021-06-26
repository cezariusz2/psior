from flask import Flask, render_template, request
import boto3
import io
import base64

from werkzeug.utils import redirect, secure_filename
app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
bucket_name = 'bucket215841-1'


@app.route('/', methods=['GET', 'POST'])
def index():
    s3 = boto3.client('s3')
    s3r = boto3.resource('s3')
    bucket = s3r.Bucket(bucket_name)
    images = []
    imgNames = []
    for f in bucket.objects.all():
        a_file = io.BytesIO()
        s3.download_fileobj(bucket_name, f.key, a_file)
        a_file.seek(0)
        data1 = a_file.read()
        data1 = base64.b64encode(data1)
        data1 = data1.decode()
        img1 = "data:image/png;base64,{}".format(data1)
        images.append(img1)
        imgNames.append(f.key)
    if request.method == 'POST':
        if request.form['uploadimg'] == 'Upload new file':

            if 'file' not in request.files:
                print("1")
                pass
            file = request.files['file']
            if file.filename == '':
                print("2")
            if file and allowed_file(file.filename):
                upload_img()
                filename = secure_filename(file.filename)
                bucket.put_object(Key=filename, Body=file)
                
        else:
            print("---pliki do zmiany---")
            file_list = request.form.getlist('imgselect')
            print(file_list)
            if sent_to_sqs(file_list):
                redirect('/')
    return render_template('index.html', len=len(images), files=images, filenames=imgNames)


def upload_img():
    print("przeslij plik")


def sent_to_sqs(lista):
    if len(lista) <= 0:
        return False
    c = boto3.client('sqs', region_name='us-east-1')
    for filename in lista:
        response2 = c.send_message(
            QueueUrl="https://sqs.us-east-1.amazonaws.com/716899022626/sqs-215841-1",
            MessageBody=filename)
    return True

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
