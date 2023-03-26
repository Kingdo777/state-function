import predict.__main__ as predict
import render.__main__ as render
import resize.__main__ as resize

if __name__ == '__main__':
    render.main(predict.main(resize.main({})))
