import io
import boto3
import time

from PIL import Image, ImageOps

s3 = boto3.client('s3')
s3r = boto3.resource('s3', region_name='us-east-1')
bucket_name = 'bucket215841-1'
url = "https://sqs.us-east-1.amazonaws.com/716899022626/sqs215841-1"


def main_loop():
    print("Worker")
    while True:
        sqs = boto3.client('sqs', region_name='us-east-1')
        response = sqs.receive_message(QueueUrl=url)
        # print(response)
        #x = json.loads(response, object_hook=lambda d: SimpleNamespace(**d))
        receiptHandle = ''
        try:
            #body = json.loads(response.body)
            messages = response['Messages']
            receiptHandle = messages[0]['ReceiptHandle']
            print(receiptHandle)

        except Exception:
            print("Brak wiadomości...")
            time.sleep(10)
            continue
        filename = messages[0]['Body']
        print(filename)
        try:
            img = fetch_image(filename)
            img = process_image(img,filename),
            send_image(img, filename)
        except Exception:
            print('ERROR')
            continue
        finally:
            res = sqs.delete_message(
                QueueUrl=url,
                ReceiptHandle=receiptHandle
            )
            print(res)
        time.sleep(10)
        print("Wiadomosc odebrana i usunieta")

def send_image(file, filename):
    filename = 'modified-' + filename
    bucket = s3r.Bucket(bucket_name)
    bucket.put_object(Key=filename, Body=file[0])
def process_image(a_file, filename):
    print("processing image...")
    a_file.seek(0)
    image = Image.open(a_file)
    im_flip = ImageOps.grayscale(image)
    format1 = filename.split('.')[-1].upper()
    print(format1)
    img_byte_arr = io.BytesIO()
    if(format1 == "JPG"):
        format1 = 'JPEG'
    im_flip.save(img_byte_arr, format=format1)
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr
def fetch_image(filename):
    a_file = io.BytesIO()
    bucket = s3r.Bucket(bucket_name)
    object = bucket.Object(filename)
    object.download_fileobj(a_file)
    return a_file


    # plt.imshow(img)
if __name__ == "__main__":
    main_loop()
