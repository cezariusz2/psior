from botocore.exceptions import ClientError
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
        print("---pliki do zmiany---")
        file_list = request.form.getlist('imgselect')
        print(file_list)
        if sent_to_sqs(file_list):
            redirect('/')
    return render_template('index.html', len=len(images), files=images, filenames=imgNames)


def sent_to_sqs(lista):
    if len(lista) <= 0:
        return False
    c = boto3.client('sqs', region_name='us-east-1')
    for filename in lista:
        response2 = c.send_message(
            QueueUrl="https://sqs.us-east-1.amazonaws.com/716899022626/sqs215841-1",
            MessageBody=filename)
    return True


@app.route("/generate_url", methods=['POST', 'PUT','GET'])
def create_presigned_post():
    object_name = request.args.get('filename')
    print('Generowanie url dla:')
    print(object_name)
    s3 = boto3.client('s3')
    try:
        response = s3.generate_presigned_post(bucket_name,
                                                     object_name,
                                                     Fields=None,
                                                     Conditions=None,
                                                     ExpiresIn=3600)
        
    except ClientError as e:
        print(e)
        return None
    return response
if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
