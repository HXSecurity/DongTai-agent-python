#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <funchook.h>
#include <logger.h>
#include <utils.h>
#include <patch.h>


#define IS_TRACKABLE(X) \
    (PyUnicode_Check((X)) || PyBytes_Check((X)) || PyByteArray_Check((X)))

newfunc bytes_cast_origin;
initproc bytearray_cast_origin;
newfunc unicode_cast_origin;

PyObject *bytes_cast_new(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    PyObject *result = bytes_cast_origin(type, args, kwargs);

    if (result == NULL) {
        return result;
    }

    patch_string_callback("callback_bytes_cast", NULL, result, args, kwargs);

    return result;
}

int bytearray_cast_new(PyObject *self, PyObject *args, PyObject *kwargs) {
    int result = bytearray_cast_origin(self, args, kwargs);

    if (result == -1) {
        return result;
    }

    patch_string_callback("callback_bytearray_cast", NULL, self, args, kwargs);

    return result;
}

PyObject *str_origin(PyObject *self, PyObject *args) {
    return unicode_cast_origin(&PyUnicode_Type, args, NULL);
}

PyObject *unicode_cast_new(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    PyObject *result = unicode_cast_origin(type, args, kwargs);

    if (result == NULL) {
        return result;
    }

    patch_string_callback("callback_unicode_cast", NULL, result, args, kwargs);

    return result;
}

int apply_cast_patch(funchook_t *funchook) {
    bytes_cast_origin = (void *)PyBytes_Type.tp_new;
    funchook_prepare_wrapper(funchook, (PyCFunction)&bytes_cast_origin, bytes_cast_new);

    bytearray_cast_origin = (void *)PyByteArray_Type.tp_init;
    funchook_prepare_wrapper(funchook, (PyCFunction)&bytearray_cast_origin, bytearray_cast_new);

    unicode_cast_origin = (void *)PyUnicode_Type.tp_new;
    funchook_prepare_wrapper(funchook, (PyCFunction)&unicode_cast_origin, unicode_cast_new);

    log_debug("------c_patch------------------ cast");

    return 0;
}
