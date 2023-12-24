//
// Created by kingdo on 23-3-18.
//

#ifndef STATEFUNCTION_MessageQueue_H
#define STATEFUNCTION_MessageQueue_H

/// 官方文档 https://docs.python.org/zh-cn/3.10/c-api/typeobj.html#examples
/// 使用c/c++编写python扩展（三）：自定义Python内置类型 https://zhuanlan.zhihu.com/p/106773873

#include <Python.h>
#include <df/msg/msg.h>

typedef struct {
    PyObject_HEAD
    key_t key;
    std::shared_ptr<df::MSG> MessageQueue;
} MessageQueue;

static void *MessageQueue_dealloc(PyObject *obj) {
    /// We should release it manually,
    /// because free() will not call shared_ptr's destructor function
    /// see more: https://zhuanlan.zhihu.com/p/615293204
    ((MessageQueue *) obj)->MessageQueue.reset();
    Py_TYPE(obj)->tp_free(obj);
    return nullptr;
}

PyObject *MessageQueue_key(PyObject *self, void *closure);

static PyGetSetDef MessageQueue_getset[] = {
        {"key", (getter) MessageQueue_key, nullptr, nullptr},
        {nullptr}};


PyObject *MessageQueue_destroy(PyObject *self, PyObject *args);
PyObject *MessageQueue_receive(PyObject *self, PyObject *args);
PyObject *MessageQueue_send(PyObject *self, PyObject *args);

static PyMethodDef MessageQueue_methods[] = {
        {"destroy", (PyCFunction) MessageQueue_destroy, METH_VARARGS, "destroy the MessageQueue."},
        {"receive", (PyCFunction) MessageQueue_receive, METH_VARARGS, "receive the MessageQueue."},
        {"send", (PyCFunction) MessageQueue_send, METH_VARARGS, "send the MessageQueue."},
        {nullptr}};

static PyTypeObject MessageQueue_Type = {
        PyVarObject_HEAD_INIT(nullptr, 0)
        "ipc.MessageQueue",                              /* tp_name */
        sizeof(MessageQueue),                                    /* tp_basicsize */
        0,                                                 /* tp_itemsize */
        (destructor) MessageQueue_dealloc,                       /* tp_dealloc */
        0,                                           /* tp_vectorcall_offset */
        nullptr,                                           /* tp_getattr */
        nullptr,                                           /* tp_setattr */
        nullptr,                                           /* tp_reserved */
        nullptr,                                           /* tp_repr */
        nullptr,                                           /* tp_as_number */
        nullptr,                                           /* tp_as_sequence */
        nullptr,                                           /* tp_as_mapping */
        nullptr,                                           /* tp_hash  */
        nullptr,                                           /* tp_call */
        nullptr,                                           /* tp_str */
        nullptr,                                           /* tp_getattro */
        nullptr,                                           /* tp_setattro */
        nullptr,                                           /* tp_as_buffer */
        Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,          /* tp_flags */
        PyDoc_STR("SystemV IPC MessageQueue"),         /* tp_doc */
        nullptr,                                           /* tp_traverse */
        nullptr,                                           /* tp_clear */
        nullptr,                                           /* tp_richcompare */
        0,                                                 /* tp_weaklistoffset */
        nullptr,                                           /* tp_iter */
        nullptr,                                           /* tp_iternext */
        MessageQueue_methods,                                     /* tp_methods */
        nullptr,                                           /* tp_members */
        MessageQueue_getset,                                     /* tp_getset */
        nullptr,                                           /* tp_base */
        nullptr,                                           /* tp_dict */
        nullptr,                                           /* tp_descr_get */
        nullptr,                                           /* tp_descr_set */
        0,                                                 /* tp_dictoffset */
        nullptr,                                           /* tp_init */
        nullptr,                                           /* tp_alloc */
        nullptr                                         /* tp_new */
};

PyObject *MessageQueue_key(PyObject *self, void *closure) {
    auto *obj = (MessageQueue *) self;
    return Py_BuildValue("i", obj->key);
}

PyObject *MessageQueue_destroy(PyObject *self, PyObject *args) {
    if (!PyArg_ParseTuple(args, ""))
        return nullptr;

    ((MessageQueue *) self)->MessageQueue->destroy();

    return Py_BuildValue("");
}

PyObject *MessageQueue_receive(PyObject *self, PyObject *args) {
    if (!PyArg_ParseTuple(args, ""))
        return nullptr;

    auto result = ((MessageQueue *) self)->MessageQueue->receive();

    return Py_BuildValue("s#", result.data(), result.size());
}

PyObject *MessageQueue_send(PyObject *self, PyObject *args) {
    const char *msg_name;
    size_t msg_name_len;

    if (!PyArg_ParseTuple(args, "s#", &msg_name, &msg_name_len))
        return nullptr;

    ((MessageQueue *) self)->MessageQueue->send(std::string(msg_name, msg_name_len));

    return Py_BuildValue("");
}

#endif //STATEFUNCTION_MessageQueue_H
