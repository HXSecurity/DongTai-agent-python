#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <funchook.h>
#include <logger.h>
#include <utils.h>
#include <patch.h>

#define PATCH_MODULE_NAME "dongtai_agent_python.assess.c_api_hook"

static PyObject *patch_module = NULL;

int init_patch() {
    if (patch_module != NULL) {
        log_error("%s module already initialized", PATCH_MODULE_NAME);
        return -1;
    }

    patch_module = PyImport_ImportModule(PATCH_MODULE_NAME);
    if (patch_module == NULL) {
        log_error("Failed to import %s", PATCH_MODULE_NAME);
        return -1;
    }

    return 0;
}

#define apply_patch(apply_func, hook)                               \
    do {                                                            \
        if ((apply_func)((hook)) != 0) {                            \
            teardown_patch();                                       \
            funchook_destroy((hook));                               \
            return NULL;                                            \
        }                                                           \
    } while (0);

void teardown_patch() {
    Py_XDECREF(patch_module);
    patch_module = NULL;
}

PyObject *initialize(PyObject *self, PyObject *args) {
    PyObject *_log;
    if (!PyArg_ParseTuple(args, "O", &_log)) {
        return NULL;
    }
    set_logger(_log);

    if (init_patch() != 0) {
        return NULL;
    }

    funchook_t *funchook = NULL;
    if ((funchook = funchook_create()) == NULL) {
        log_error("Failed to create funchook object");
        return NULL;
    }

    log_debug("Initialized C API patch");

    return PyCapsule_New((void *)funchook, NULL, NULL);
}

PyObject *enable_patches(PyObject *self, PyObject *arg) {
    funchook_t *funchook = NULL;

    UNPACK_FUNCHOOK_CAPSULE;

    apply_patch(apply_cformat_patch, funchook);
    apply_patch(apply_fstring_patch, funchook);
    apply_patch(apply_cast_patch, funchook);
    apply_patch(apply_concat_patch, funchook);

    Py_RETURN_NONE;
}

PyObject *install(PyObject *self, PyObject *arg) {
    funchook_t *funchook = NULL;

    UNPACK_FUNCHOOK_CAPSULE;

    if (funchook_install(funchook, 0) != FUNCHOOK_ERROR_SUCCESS) {
        log_error("Failed to install C API patch: %s", funchook_error_message(funchook));
        funchook_destroy(funchook);
        return NULL;
    }

    log_debug("Installed C API patch");

    Py_RETURN_NONE;
}

void patch_string_callback(char *prop_method_name, PyObject *source, PyObject *target, PyObject *hook_args, PyObject *hook_kwargs) {
    if (!PyObject_HasAttrString(patch_module, prop_method_name)) {
        return;
    }

    PyObject *result;
    PyObject *prop_hook_args;
    int free_hook_args = 0;

    if (hook_args == NULL) {
        prop_hook_args = Py_None;
    } else if (need_to_pack(hook_args)) {
        prop_hook_args = PyTuple_Pack(1, hook_args);
        free_hook_args = 1;
    } else {
        prop_hook_args = hook_args;
    }

    result = PyObject_CallMethod(
        patch_module,
        prop_method_name,
        "OOOOO",
        target,                                         /* target */
        (source == NULL ? Py_None : source),            /* self_obj */
        target,                                         /* ret */
        prop_hook_args,                                 /* args */
        (hook_kwargs == NULL ? Py_None : hook_kwargs)); /* kwargs */

    if (result == NULL) {
        PyErr_PrintEx(0);
        log_error("String method callback failed: %s", prop_method_name);
    }

    Py_XDECREF(result);
    if (free_hook_args) {
        Py_XDECREF(prop_hook_args);
    }
}
