import json

from requests_futures.sessions import FuturesSession


def main(event):
    futures = []
    actions = ['FINRA-Redis-marketdata', 'FINRA-Redis-trddate', 'FINRA-Redis-volume', 'FINRA-Redis-side', 'FINRA-Redis-lastpx']
    parallel = 4

    session = FuturesSession(max_workers=len(actions) * parallel + 1)
    for i in range(1, parallel):
        event['index'] = i
        for action in actions:
            futures.append(session.post('https://222.20.94.67/api/v1/namespaces/_/actions/{}'.format(action),
                                        params={'blocking': True, 'result': False}, auth=(
                    '23bc46b1-71f6-4ed5-8c54-816aa4f8c502',
                    '123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP'), json=event,
                                        verify=False))

    out = {"body": [], 'count': parallel}
    for future in futures:
        out["body"].append(json.loads(future.result().content.decode())['response']['result'])

    result = session.post('https://222.20.94.67/api/v1/namespaces/_/actions/FINRA-Redis-marginBalance',
                          params={'blocking': True, 'result': False}, auth=(
            '23bc46b1-71f6-4ed5-8c54-816aa4f8c502',
            '123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP'), json=out,
                          verify=False)

    return json.loads(result.result().content.decode())['response']['result']


if __name__ == '__main__':
    print(main({
        "body": {
            "portfolioType": "S&P",
            "portfolio": "1234"
        }
    }))
