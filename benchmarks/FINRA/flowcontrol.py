import json

from requests_futures.sessions import FuturesSession
import datafunction as df


def main(event):
    futures = []
    actions = ['FINRA-Three-marketdata', 'FINRA-Three-trddate', 'FINRA-Three-volume', 'FINRA-Three-side',
               'FINRA-Three-lastpx']
    parallel = 4

    op = event['op']
    if op == "CB":
        bucket = df.create_bucket("kingdo", 1024 * 4)

    session = FuturesSession(max_workers=len(actions) * parallel + 1)
    for i in range(1, parallel):
        event['index'] = i
        for action in actions:
            futures.append(session.post('https://222.20.94.67/api/v1/namespaces/_/actions/{}'.format(action),
                                        params={'blocking': True, 'result': False}, auth=(
                    '23bc46b1-71f6-4ed5-8c54-816aa4f8c502',
                    '123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP'), json=event,
                                        verify=False))

    out = {"body": [], 'count': parallel, "op": event["op"]}
    for future in futures:
        out["body"].append(json.loads(future.result().content.decode())['response']['result'])

    result = session.post('https://222.20.94.67/api/v1/namespaces/_/actions/FINRA-Three-marginBalance',
                          params={'blocking': True, 'result': False}, auth=(
            '23bc46b1-71f6-4ed5-8c54-816aa4f8c502',
            '123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP'), json=out,
                          verify=False)

    response = json.loads(result.result().content.decode())['response']['result']
    # if op == "CB":
    #     bucket.destroy()
    return response


if __name__ == '__main__':
    print(main({
        "op": "CB",
        "body": {
            "portfolioType": "S&P",
            "portfolio": "1234"
        }
    }))
