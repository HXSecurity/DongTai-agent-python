#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <funchook.h>
#include <logger.h>
#include <utils.h>
#include <patch.h>

binaryfunc bytes_concat_origin;
binaryfunc bytearray_concat_origin;
binaryfunc bytearray_inplace_concat_origin;
binaryfunc unicode_concat_origin;
void (*unicode_append_origin)(PyObject **l, PyObject *r);

PyObject *bytes_concat_new(PyObject *l, PyObject *r) {
    PyObject *result = bytes_concat_origin(l, r);

    if (result == NULL) {
        return result;
    }

    patch_string_callback("callback_bytes_concat", l, result, r, NULL);

    return result;
}

PyObject *bytearray_concat_new(PyObject *l, PyObject *r) {
    PyObject *result = bytearray_concat_origin(l, r);

    if (result == NULL) {
        return result;
    }

    patch_string_callback("callback_bytearray_concat", l, result, r, NULL);

    return result;
}

PyObject *bytearray_inplace_concat_new(PyObject *l, PyObject *r) {
    PyObject *result = bytearray_inplace_concat_origin(l, r);

    if (result == NULL) {
        return result;
    }

    patch_string_callback("callback_bytearray_concat", l, result, r, NULL);

    return result;
}

PyObject *unicode_concat_new(PyObject *l, PyObject *r) {
    PyObject *result = unicode_concat_origin(l, r);

    if (result == NULL) {
        return result;
    }

    patch_string_callback("callback_unicode_concat", l, result, r, NULL);

    return result;
}

void unicode_append_new(PyObject **l, PyObject *r) {
    PyObject *origin_l = *l;
    Py_XINCREF(origin_l);
    unicode_append_origin(l, r);

    if (*l == NULL) {
        Py_XDECREF(origin_l);
        return;
    }

    patch_string_callback("callback_unicode_concat", origin_l, *l, r, NULL);
    Py_XDECREF(origin_l);
}

int apply_concat_patch(funchook_t *funchook) {
    bytes_concat_origin = PyBytes_Type.tp_as_sequence->sq_concat;
    funchook_prepare_wrapper(funchook, &bytes_concat_origin, bytes_concat_new);

    bytearray_concat_origin = PyByteArray_Concat;
    funchook_prepare_wrapper(funchook, &bytearray_concat_origin, bytearray_concat_new);

    bytearray_inplace_concat_origin = PyByteArray_Type.tp_as_sequence->sq_inplace_concat;
    funchook_prepare_wrapper(funchook, &bytearray_inplace_concat_origin, bytearray_inplace_concat_new);

    unicode_concat_origin = PyUnicode_Concat;
    funchook_prepare_wrapper(funchook, &unicode_concat_origin, unicode_concat_new);

    unicode_append_origin = PyUnicode_Append;
    funchook_prepare_wrapper(funchook, &unicode_append_origin, unicode_append_new);

    log_debug("------c_patch------------------ concat");

    return 0;
}
