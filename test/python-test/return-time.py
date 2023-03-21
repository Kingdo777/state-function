import numpy as np
import json, time

def func1():
    return time.time() * 1000

def func2():
    body = json.loads(json.dumps(np.zeros((1024, 1014)).tolist()))
    return time.time() * 1000

def func3():
    json.loads(json.dumps(np.zeros((1024, 1014)).tolist()))
    return time.time() * 1000

def func4():
    body = json.loads(json.dumps(np.zeros((1024, 1014)).tolist()))
    del body
    return time.time() * 1000

if __name__ == '__main__':
    print("1: {:.2f}".format(func1() - 1000 * time.time()))
    print("2: {:.2f}".format(func2() - 1000 * time.time()))
    print("3: {:.2f}".format(func3() - 1000 * time.time()))
    print("4: {:.2f}".format(func4() - 1000 * time.time()))
