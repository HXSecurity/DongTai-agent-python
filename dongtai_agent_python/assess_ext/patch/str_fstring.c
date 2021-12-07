#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <funchook.h>
#include <logger.h>
#include <utils.h>
#include <patch.h>

#if PY_MINOR_VERSION == 6
typedef PyObject **joinarray_items_t;
#else
typedef PyObject *const *joinarray_items_t;
#endif /* PY_MINOR_VERSION == 6 */

PyObject *(*unicode_joinarray_origin)(PyObject *, joinarray_items_t, Py_ssize_t);

static PyObject *unicode_joinarray_new(PyObject *sep, joinarray_items_t items, Py_ssize_t len) {
    PyObject *result = unicode_joinarray_origin(sep, items, len);
    PyObject *item_list = process_args(items, len);
    PyObject *args = PyTuple_Pack(1, item_list);

    if (result == NULL) {
        Py_XDECREF(args);
        Py_XDECREF(item_list);
        return result;
    }

    patch_string_callback("callback_unicode_fstring", sep, result, args, NULL);

    return result;
}

int apply_fstring_patch(funchook_t *funchook) {
    unicode_joinarray_origin = _PyUnicode_JoinArray;
    funchook_prepare_wrapper(funchook, &unicode_joinarray_origin, unicode_joinarray_new);
    log_debug("------c_patch------------------ fstring");

    return 0;
}
