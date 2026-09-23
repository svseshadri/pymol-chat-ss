import threading
import time
import unittest

from pymol.Qt import QtCore, QtWidgets

import pymol_chat
from pymol_chat.ui import MainThreadPyMOLExecutor, PyMOLChatDock


class PluginWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_resolves_real_qt_window_without_using_pmgapp(self):
        window = QtWidgets.QMainWindow()
        window.pymolwidget = object()
        window.show()
        self.application.processEvents()
        try:
            self.assertIs(pymol_chat._qt_main_window(), window)
        finally:
            window.close()

    def test_executor_marshals_worker_calls_to_qt_thread(self):
        class RecordingExecutor:
            def scene_summary(self):
                return QtCore.QThread.currentThread()

        bridge = MainThreadPyMOLExecutor(delegate=RecordingExecutor())
        results = []
        worker = threading.Thread(target=lambda: results.append(bridge.scene_summary()))
        worker.start()
        deadline = time.monotonic() + 2
        while worker.is_alive() and time.monotonic() < deadline:
            self.application.processEvents()
            time.sleep(0.01)
        worker.join(timeout=0.1)

        self.assertFalse(worker.is_alive())
        self.assertEqual(results, [self.application.thread()])

    def test_chat_dock_constructs(self):
        window = QtWidgets.QMainWindow()
        dock = PyMOLChatDock(window)
        try:
            self.assertEqual(dock.input.placeholderText(), "Ask PyMOL…")
            self.assertFalse(dock.debug_view.isVisible())
            self.assertEqual(
                [action.text() for action in dock.options_menu.actions() if not action.isSeparator()],
                ["API Key Settings…", "Spoken Replies", "Show Command Log"],
            )
            self.assertTrue(dock.debug_action.isCheckable())
        finally:
            dock.close()
            window.close()
