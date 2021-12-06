#ifndef _LOGGER_H_
#define _LOGGER_H_

#define PY_SSIZE_T_CLEAN
#include <Python.h>

typedef enum log_level
{
    LOG_INFO = 0,
    LOG_WARNING,
    LOG_ERROR,
    LOG_DEBUG,
} log_level_t;

#define log_info(...) log_message(LOG_INFO, __VA_ARGS__)
#define log_warning(...) log_message(LOG_WARNING, __VA_ARGS__)
#define log_error(...) log_message(LOG_ERROR, __VA_ARGS__)
#define log_debug(...) log_message(LOG_DEBUG, __VA_ARGS__)

void set_logger(PyObject *_logger);
void teardown_logger(void);
void log_message(log_level_t level, const char *msg, ...);

#endif /* _LOGGER_H_ */
