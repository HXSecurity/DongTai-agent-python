#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <patch.h>

static PyMethodDef methods[] = {
    {
        "initialize",
        (PyCFunction)initialize,
        METH_VARARGS,
        "Initialize C API patcher"
    },
    {
        "enable_patches",
        enable_patches,
        METH_O,
        "Patch relevant non-method functions"
    },
    {"install", install, METH_O, "Install patches"},
    {"str_origin", (PyCFunction)str_origin, METH_VARARGS, "Origin str cast method"},
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef c_api_module = {
    PyModuleDef_HEAD_INIT,
    "c_api",
    "C API patch",
    -1,
    methods,
    NULL,
    NULL,
    NULL,
    NULL,
};

PyMODINIT_FUNC PyInit_c_api(void) {
    PyObject *module;

    Py_Initialize();
    module = PyModule_Create(&c_api_module);

    return module;
}
