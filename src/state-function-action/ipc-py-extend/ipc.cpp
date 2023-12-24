//
// Created by kingdo on 23-3-7.
//


/// C/C++扩展Python文档:(https://docs.python.org/zh-cn/3.10/c-api/)
/// 1. 概述 (https://docs.python.org/zh-cn/3.10/c-api/intro.html)
/// 2. 解析参数并构建值变量 (https://docs.python.org/zh-cn/3.10/c-api/arg.html#)
/// 3. 引用计数 (https://docs.python.org/zh-cn/3.10/c-api/refcounting.html#reference-counting)

/// 使用 C 或 C++ 扩展 Python (https://docs.python.org/zh-cn/3.10/extending/extending.html#extending-python-with-c-or-c)

/// 优秀博客
/// 1.参数解析与结果封装 https://www.cnblogs.com/jianmu/p/7367566.html
/// 2.引用计数问题的处理 https://www.cnblogs.com/jianmu/p/7367698.html
/// 1.异常和错误处理 https://www.cnblogs.com/jianmu/p/7469146.html


#define PY_SSIZE_T_CLEAN

#include <Python.h>
#include "ShareMemory.h"
#include "MessageQueue.h"
#include <df/utils/log.h>

static PyObject *IPCError;

static PyObject *
ipc_create_shm(PyObject *self, PyObject *args) {

    uint64_t Key;

    size_t shm_size;

    if (!PyArg_ParseTuple(args, "KK", &Key, &shm_size))
        return nullptr;

    auto type = &ShareMemory_Type;
    auto shm = (ShareMemory *) (type->tp_alloc(type, 0));

    shm->key = Key;
    shm->size = shm_size;
    try {
        shm->ShareMemory = std::make_shared<df::SHM>(Key, shm_size);
    } catch (std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return nullptr;
    }
    return (PyObject *) shm;
}

static PyObject *
ipc_get_shm(PyObject *self, PyObject *args) {

    uint64_t Key;

    if (!PyArg_ParseTuple(args, "K", &Key))
        return nullptr;

    auto type = &ShareMemory_Type;
    auto shm = (ShareMemory *) (type->tp_alloc(type, 0));

    try {
        shm->ShareMemory = std::make_shared<df::SHM>(Key);
        shm->key = Key;
        shm->size = shm->ShareMemory->getSHMSize();
    } catch (std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return nullptr;
    }

    return (PyObject *) shm;
}

static PyObject *
ipc_create_msg(PyObject *self, PyObject *args) {
    key_t Key;

    if (!PyArg_ParseTuple(args, "K", &Key))
        return nullptr;

    auto type = &MessageQueue_Type;
    auto msg = (MessageQueue *) (type->tp_alloc(type, 0));

    msg->key = Key;
    try {
        msg->MessageQueue = df::MSG::createMSG(msg->key);
    } catch (std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return nullptr;
    }
    return (PyObject *) msg;
}

static PyObject *
ipc_get_msg(PyObject *self, PyObject *args) {
    key_t Key;

    if (!PyArg_ParseTuple(args, "K", &Key))
        return nullptr;

    auto type = &MessageQueue_Type;
    auto msg = (MessageQueue *) (type->tp_alloc(type, 0));

    try {
        msg->key = Key;
        msg->MessageQueue = df::MSG::getMSG(msg->key);
    } catch (std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return nullptr;
    }

    return (PyObject *) msg;
}

static PyObject *
ipc_system(PyObject *self, PyObject *args) {
    const char *command;
    int sts;

    if (!PyArg_ParseTuple(args, "s", &command))
        return nullptr;

    SPDLOG_INFO("{}", command);
    sts = system(command);

    if (sts < 0) {
        PyErr_SetString(IPCError, "System command failed");
        return nullptr;
    }
    return PyLong_FromLong(sts);
}

static PyMethodDef IPCMethods[] = {
        {"system",     ipc_system,     METH_VARARGS,
                                   "Execute a shell command."},
        {"get_shm",    ipc_get_shm,    METH_VARARGS,
                                   "get shm."},
        {"create_shm", ipc_create_shm, METH_VARARGS,
                                   "Create new SHM."},
        {"get_msg",    ipc_get_msg,    METH_VARARGS,
                                   "get msg."},
        {"create_msg", ipc_create_msg, METH_VARARGS,
                                   "Create new MSG."},
        {nullptr,      nullptr, 0, nullptr}        /* Sentinel */
};

static struct PyModuleDef IPCModule = {
        PyModuleDef_HEAD_INIT,
        "ipc",   /* name of module */
        nullptr, /* module documentation, may be nullptr */
        -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
        IPCMethods
};

PyMODINIT_FUNC
PyInit_ipc(void) {
    PyObject *m;

    m = PyModule_Create(&IPCModule);
    if (m == nullptr)
        return nullptr;

    if (PyType_Ready(&ShareMemory_Type) < 0)
        return nullptr;

    if (PyType_Ready(&MessageQueue_Type) < 0)
        return nullptr;

    Py_INCREF(&ShareMemory_Type);
    if (PyModule_AddObject(m, "ShareMemory", (PyObject *) &ShareMemory_Type) < 0) {
        Py_DECREF(&ShareMemory_Type);
        Py_DECREF(m);
        return nullptr;
    }

    Py_INCREF(&MessageQueue_Type);
    if (PyModule_AddObject(m, "MessageQueue", (PyObject *) &MessageQueue_Type) < 0) {
        Py_DECREF(&MessageQueue_Type);
        Py_DECREF(m);
        return nullptr;
    }

    IPCError = PyErr_NewException("ipc.error", nullptr, nullptr);
    Py_XINCREF(IPCError);
    if (PyModule_AddObject(m, "error", IPCError) < 0) {
        Py_XDECREF(IPCError);
        Py_CLEAR(IPCError);
        Py_DECREF(m);
        return nullptr;
    }

    return m;
}
