import time

import numpy as np
from PIL import Image
import pickle

from utils import timestamp

FILE_DIR = '/tmp'
BUCKET = 'kingdo-serverless-test'
FOLDER = 'faastlane/prediction-pipeline'
IMAGE = 'img-src/panda.jpg'
RESIZE_IMAGE = 'img-resize/panda-resize.npy'


def main(event):
    startTime = 1000 * time.time()
    image = Image.open("data/image.jpg")
    img = np.array(image.resize((224, 224))).astype(np.float) / 128 - 1
    resize_img = img.reshape(1, 224, 224, 3)

    response = {"statusCode": 200}
    serialized_resize = pickle.dumps(resize_img)
    endTime = 1000 * time.time()
    # Baseline allows 1MB messages to be shared, use S3 to communicate messages
    response["serialized_resize"] = serialized_resize

    return timestamp(response, event, startTime, endTime)
