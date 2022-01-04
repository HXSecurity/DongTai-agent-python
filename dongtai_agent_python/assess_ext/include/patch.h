#ifndef _PATCH_H_
#define _PATCH_H_

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <funchook.h>
#include <logger.h>

int init_patch(void);
void teardown_patch(void);

PyObject *initialize(PyObject *self, PyObject *args);
PyObject *enable_patches(PyObject *self, PyObject *arg);
PyObject *install(PyObject *self, PyObject *arg);

void patch_string_callback(char *prop_method_name, PyObject *source, PyObject *target, PyObject *hook_args, PyObject *hook_kwargs);

PyObject *str_origin(PyObject *self, PyObject *args);

int apply_cformat_patch(funchook_t *funchook);
int apply_fstring_patch(funchook_t *funchook);
int apply_cast_patch(funchook_t *funchook);
int apply_concat_patch(funchook_t *funchook);

#define BUILD_NEW_BINARYFUNC(NAME)                                            \
    static PyObject *NAME##_new(PyObject *self, PyObject *args) {             \
        PyObject *result = NAME##_origin(self, args);                         \
                                                                              \
        if (result == NULL)                                                   \
            return result;                                                    \
                                                                              \
        patch_string_callback("callback_" #NAME, self, result, args, NULL);   \
                                                                              \
        return result;                                                        \
    }

#endif /* _PATCH_H_ */
