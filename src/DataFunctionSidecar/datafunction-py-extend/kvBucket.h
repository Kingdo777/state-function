//
// Created by kingdo on 23-3-18.
//

#ifndef DATAFUNCTION_KVBUCKET_H
#define DATAFUNCTION_KVBUCKET_H

/// 官方文档 https://docs.python.org/zh-cn/3.10/c-api/typeobj.html#examples
/// 使用c/c++编写python扩展（三）：自定义Python内置类型 https://zhuanlan.zhihu.com/p/106773873

#include <Python.h>
#include <kvstore/DataFunctionKVStoreBucket.h>

typedef struct {
    PyObject_HEAD
    std::string name;
    size_t size;
    std::shared_ptr<df::dataStruct::KV_Store::DataFunctionKVStoreBucket> bucket;
} Bucket;

static void *bucket_dealloc(PyObject *obj) {
    /// We should release it manually,
    /// because free() will not call shared_ptr's destructor function
    /// see more: https://zhuanlan.zhihu.com/p/615293204
    ((Bucket *) obj)->bucket.reset();
    Py_TYPE(obj)->tp_free(obj);
    return nullptr;
}

PyObject *bucket_name(PyObject *self, void *closure);

PyObject *bucket_size(PyObject *self, void *closure);

static PyGetSetDef bucket_getset[] = {
        {"name", (getter) bucket_name, nullptr, nullptr},
        {"size", (getter) bucket_size, nullptr, nullptr},
        {nullptr}};

PyObject *Bucket_get(PyObject *self, PyObject *args);

PyObject *Bucket_set(PyObject *self, PyObject *args);

PyObject *Bucket_destroy(PyObject *self, PyObject *args);

static PyMethodDef bucket_methods[] = {
        {"get",     (PyCFunction) Bucket_get,     METH_VARARGS, "get value from bucket."},
        {"set",     (PyCFunction) Bucket_set,     METH_VARARGS, "set value to bucket."},
        {"destroy", (PyCFunction) Bucket_destroy, METH_VARARGS, "destroy the bucket."},
        {nullptr}};

static PyTypeObject Bucket_Type = {
        PyVarObject_HEAD_INIT(nullptr, 0)
        "datafunction.bucket",                             /* tp_name */
        sizeof(Bucket),                                    /* tp_basicsize */
        0,                                                 /* tp_itemsize */
        (destructor) bucket_dealloc,                       /* tp_dealloc */
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
        PyDoc_STR("DataFunction KV Store Bucket"),         /* tp_doc */
        nullptr,                                           /* tp_traverse */
        nullptr,                                           /* tp_clear */
        nullptr,                                           /* tp_richcompare */
        0,                                                 /* tp_weaklistoffset */
        nullptr,                                           /* tp_iter */
        nullptr,                                           /* tp_iternext */
        bucket_methods,                                     /* tp_methods */
        nullptr,                                           /* tp_members */
        bucket_getset,                                     /* tp_getset */
        nullptr,                                           /* tp_base */
        nullptr,                                           /* tp_dict */
        nullptr,                                           /* tp_descr_get */
        nullptr,                                           /* tp_descr_set */
        0,                                                 /* tp_dictoffset */
        nullptr,                                           /* tp_init */
        nullptr,                                           /* tp_alloc */
        nullptr                                         /* tp_new */
};

PyObject *bucket_name(PyObject *self, void *closure) {
    auto *obj = (Bucket *) self;
    return Py_BuildValue("s", obj->name.c_str());
}

PyObject *bucket_size(PyObject *self, void *closure) {
    auto *obj = (Bucket *) self;
    return Py_BuildValue("i", obj->size);
}

PyObject *Bucket_set(PyObject *self, PyObject *args) {

    const char *key_data;
    size_t key_size;

    const char *value_data;
    size_t value_size;

    if (!PyArg_ParseTuple(args, "s#s#", &key_data, &key_size, &value_data, &value_size))
        return nullptr;

    ((Bucket *) self)->bucket->set(key_data, key_size, value_data, value_size);

    return Py_BuildValue("");
}

PyObject *Bucket_get(PyObject *self, PyObject *args) {
    const char *key_data;
    size_t key_size;

    if (!PyArg_ParseTuple(args, "s#", &key_data, &key_size))
        return nullptr;

    std::string key{key_data, key_size};


    void *value_data;
    size_t value_size;

    value_size = ((Bucket *) self)->bucket->get(key, &value_data);

    return Py_BuildValue("s#", value_data, value_size);
}

PyObject *Bucket_destroy(PyObject *self, PyObject *args) {
    if (!PyArg_ParseTuple(args, ""))
        return nullptr;

    ((Bucket *) self)->bucket->destroy();

    return Py_BuildValue("");
}

#endif //DATAFUNCTION_KVBUCKET_H
