import csv
from utils import *


def main(event):
    startTime = 1000 * time.time()
    with open('data/few_reviews.csv') as csvFile:
        # DictReader -> convert lines of CSV to OrderedDict
        for row in csv.DictReader(csvFile):
            # return just the first loop (row) results!
            body = {}
            for k, v in row.items():
                body[k] = int(v) if k == 'reviewType' else v
    response = {'statusCode': 200, 'body': body}
    endTime = 1000 * time.time()
    return timestamp(response, event, startTime, endTime)


if __name__ == "__main__":
    print(main({}))
