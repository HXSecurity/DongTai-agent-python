#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <funchook.h>
#include <patch.h>
#include <logger.h>
#include <utils.h>

static binaryfunc bytes_cformat_origin;
static binaryfunc bytearray_cformat_origin;
static binaryfunc unicode_cformat_origin;

BUILD_NEW_BINARYFUNC(bytes_cformat);
BUILD_NEW_BINARYFUNC(bytearray_cformat);
BUILD_NEW_BINARYFUNC(unicode_cformat);

int apply_cformat_patch(funchook_t *funchook) {
    bytes_cformat_origin = PyBytes_Type.tp_as_number->nb_remainder;
    funchook_prepare_wrapper(funchook, &bytes_cformat_origin, bytes_cformat_new);

    bytearray_cformat_origin = PyByteArray_Type.tp_as_number->nb_remainder;
    funchook_prepare_wrapper(funchook, &bytearray_cformat_origin, bytearray_cformat_new);

    unicode_cformat_origin = PyUnicode_Format;
    funchook_prepare_wrapper(funchook, &unicode_cformat_origin, unicode_cformat_new);

    log_debug("------c_patch------------------ cformat");

    return 0;
}
