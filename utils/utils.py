import time

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication


def timeit(method):
    """
    Utility decorator to compute function execution time
    """
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print('[{}]  {} ms'.format(method.__name__, (te - ts) * 1000))
        return result

    return timed


def waiting_effects(fun):
    """
    Utility decorator to show loading cursor in GUI
    """
    def wrap_function(*args, **kwarg):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        try:
            fun(*args, **kwarg)
        except Exception as e:
            raise e
            print("Error {}".format(e.args[0]))
        finally:
            QApplication.restoreOverrideCursor()

    return wrap_function
