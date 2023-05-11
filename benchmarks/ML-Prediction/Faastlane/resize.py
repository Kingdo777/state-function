import time, json
import numpy as np
from PIL import Image
from utils import timestamp

FILE_DIR = '/tmp'
BUCKET = 'kingdo-serverless-test'
FOLDER = 'faastlane/prediction-pipeline'
IMAGE = 'img-src/panda.jpg'
RESIZE_IMAGE = 'img-resize/panda-resize.npy'


def main(event):
    startTime = 1000 * time.time()
    image = Image.open("data/image.jpg")
    img = np.array(image.resize((224, 224))).astype(float) / 128 - 1
    resize_img = img.reshape(1, 224, 224, 3)

    response = {
        "statusCode": 200,
        "body": json.dumps({"resize_img": resize_img.tolist()})
    }

    endTime = 1000 * time.time()
    response["resizeExecuteTime"] = endTime - startTime

    return timestamp(response, event, startTime, endTime)
