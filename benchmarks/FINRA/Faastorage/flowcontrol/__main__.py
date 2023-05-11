import json
import pickle

import datafunction as df

from requests_futures.sessions import FuturesSession


def main(event):
    futures = []
    actions = ['FINRA-Faastorage-marketdata', 'FINRA-Faastorage-trddate', 'FINRA-Faastorage-volume',
               'FINRA-Faastorage-side',
               'FINRA-Faastorage-lastpx']
    parallel = 4

    bucket = df.create_bucket("kingdo-finra", 1024 * 4)

    session = FuturesSession(max_workers=len(actions) * parallel + 1)
    for i in range(parallel):
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

    print(out)

    result = session.post('https://222.20.94.67/api/v1/namespaces/_/actions/FINRA-Faastorage-marginBalance',
                          params={'blocking': True, 'result': False}, auth=(
            '23bc46b1-71f6-4ed5-8c54-816aa4f8c502',
            '123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP'), json=out,
                          verify=False)
    result = json.loads(result.result().content.decode())['response']['result']
    bucket.destroy()
    return result


if __name__ == '__main__':
    print(main({
        "body": {
            "portfolioType": "S&P",
            "portfolio": "1234"
        }
    }))
