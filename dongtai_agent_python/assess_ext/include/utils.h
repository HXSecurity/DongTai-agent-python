#ifndef _UTILS_H_
#define _UTILS_H_

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdbool.h>

#include <funchook.h>
#include <logger.h>

static inline PyObject *process_args(PyObject *const *args, Py_ssize_t args_size) {
    PyObject *hook_args = PyList_New(0);
    Py_ssize_t i;

    for (i = 0; i < args_size; i++) {
        PyList_Append(hook_args, args[i]);
    }

    return hook_args;
}

static inline bool need_to_pack(PyObject *obj) {
    return (!PySequence_Check(obj) || PyBytes_Check(obj) || PyUnicode_Check(obj) || PyByteArray_Check(obj));
}

#define UNPACK_FUNCHOOK_CAPSULE                                                   \
    do {                                                                          \
        if (!PyCapsule_IsValid(arg, NULL)) {                                      \
            log_error("Expected funchook container");                             \
            return NULL;                                                          \
        }                                                                         \
                                                                                  \
        if ((funchook = (funchook_t *)PyCapsule_GetPointer(arg, NULL)) == NULL) { \
            log_error( "Failed to get funchook from container");                  \
            return NULL;                                                          \
        }                                                                         \
    } while (0);

#define _funchook_prepare_wrapper(fh, origin_func, new_func, ret_val)       \
    do {                                                                    \
        if (funchook_prepare((fh), (void **)(origin_func), (new_func)) !=   \
            FUNCHOOK_ERROR_SUCCESS) {                                       \
            PyErr_Format(                                                   \
                PyExc_RuntimeError,                                         \
                "Failed to prepare hook at %s:%d: %s",                      \
                __FILE__,                                                   \
                __LINE__,                                                   \
                funchook_error_message(fh));                                \
            return ret_val;                                                 \
        }                                                                   \
    } while (0)

#define funchook_prepare_wrapper(fh, origin_func, new_func) _funchook_prepare_wrapper(fh, origin_func, new_func, -1)

#endif /* _UTILS_H_ */
