//
// Created by kingdo on 23-3-18.
//

#ifndef STATEFUNCTION_KVShareMemory_H
#define STATEFUNCTION_KVShareMemory_H

/// 官方文档 https://docs.python.org/zh-cn/3.10/c-api/typeobj.html#examples
/// 使用c/c++编写python扩展（三）：自定义Python内置类型 https://zhuanlan.zhihu.com/p/106773873

#include <Python.h>
#include <df/shm/shm.h>

typedef struct {
    PyObject_HEAD
    uint64_t key;
    size_t size;
    std::shared_ptr<df::SHM> ShareMemory;
} ShareMemory;

static void *ShareMemory_dealloc(PyObject *obj) {
    /// We should release it manually,
    /// because free() will not call shared_ptr's destructor function
    /// see more: https://zhuanlan.zhihu.com/p/615293204
    ((ShareMemory *) obj)->ShareMemory.reset();
    Py_TYPE(obj)->tp_free(obj);
    return nullptr;
}

PyObject *ShareMemory_key(PyObject *self, void *closure);

PyObject *ShareMemory_size(PyObject *self, void *closure);

static PyGetSetDef ShareMemory_getset[] = {
        {"key", (getter) ShareMemory_key, nullptr, nullptr},
        {"size", (getter) ShareMemory_size, nullptr, nullptr},
        {nullptr}};


PyObject *ShareMemory_destroy(PyObject *self, PyObject *args);

static PyMethodDef ShareMemory_methods[] = {
        {"destroy", (PyCFunction) ShareMemory_destroy, METH_VARARGS, "destroy the ShareMemory."},
        {nullptr}};

static PyTypeObject ShareMemory_Type = {
        PyVarObject_HEAD_INIT(nullptr, 0)
        "ipc.ShareMemory",                              /* tp_name */
        sizeof(ShareMemory),                                    /* tp_basicsize */
        0,                                                 /* tp_itemsize */
        (destructor) ShareMemory_dealloc,                       /* tp_dealloc */
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
        PyDoc_STR("SystemV IPC ShareMemory"),         /* tp_doc */
        nullptr,                                           /* tp_traverse */
        nullptr,                                           /* tp_clear */
        nullptr,                                           /* tp_richcompare */
        0,                                                 /* tp_weaklistoffset */
        nullptr,                                           /* tp_iter */
        nullptr,                                           /* tp_iternext */
        ShareMemory_methods,                                     /* tp_methods */
        nullptr,                                           /* tp_members */
        ShareMemory_getset,                                     /* tp_getset */
        nullptr,                                           /* tp_base */
        nullptr,                                           /* tp_dict */
        nullptr,                                           /* tp_descr_get */
        nullptr,                                           /* tp_descr_set */
        0,                                                 /* tp_dictoffset */
        nullptr,                                           /* tp_init */
        nullptr,                                           /* tp_alloc */
        nullptr                                         /* tp_new */
};

PyObject *ShareMemory_key(PyObject *self, void *closure) {
    auto *obj = (ShareMemory *) self;
    return Py_BuildValue("i", obj->key);
}

PyObject *ShareMemory_size(PyObject *self, void *closure) {
    auto *obj = (ShareMemory *) self;
    return Py_BuildValue("i", obj->size);
}

PyObject *ShareMemory_destroy(PyObject *self, PyObject *args) {
    if (!PyArg_ParseTuple(args, ""))
        return nullptr;

    ((ShareMemory *) self)->ShareMemory->destroy();

    return Py_BuildValue("");
}

#endif //STATEFUNCTION_KVShareMemory_H
