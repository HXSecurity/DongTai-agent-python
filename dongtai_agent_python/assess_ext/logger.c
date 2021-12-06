#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>

#include <logger.h>

static PyObject *logger = NULL;
static const char *log_level_map[] = {
    "info",
    "warning",
    "error",
    "debug",
};

void set_logger(PyObject *_logger) {
    Py_XINCREF(_logger);
    logger = _logger;
}

void teardown_logger() {
    Py_XDECREF(logger);
    logger = NULL;
}

void log_message(log_level_t level, const char *msg, ...) {
    PyObject *string = NULL;
    PyObject *result = NULL;
    va_list arg_p;

    if (logger == NULL) {
        return;
    }

    va_start(arg_p, msg);
    string = PyUnicode_FromFormatV(msg, arg_p);
    va_end(arg_p);

    if (string == NULL) {
        fprintf(stderr, "Failed to format log message\n");
        return;
    }

    result = PyObject_CallMethod(logger, (char *)log_level_map[level], "O", string);
    if (result == NULL) {
        fprintf(stderr, "Failed to call log method\n");
    }
}
