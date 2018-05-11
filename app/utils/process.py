# -*- coding: utf-8 -*-

__author__ = "苦叶子"

"""

公众号: 开源优测

Email: lymking@foxmail.com

"""

import os
import time
import tempfile
import subprocess


class Process:
    def __init__(self, command):
        self._command = command
        self._process = None
        self._error = None
        self._out_file = None
        self._out_path = None
        self._out_fd = None
        print(command)

    def start(self):
        self._out_fd, self._out_path = tempfile.mkstemp(prefix='rfproc_', suffix='.txt', text=True)
        self._out_file = open(self._out_path)
        try:
            self._process = subprocess.Popen(self._command, stdout=self._out_fd,
                                             stderr=subprocess.STDOUT)
        except OSError as err:
            self._error = str(err)

    def is_finished(self):
        return self._error is not None or self._process.poll() is not None

    def stop(self):
        self._process.kill()

    def wait(self):
        if self._process is not None:
            self._process.wait()

    def get_output(self, wait_until_finished=False):
        """Returns the output produced by the process.
        If ``wait_until_finished`` is True, blocks until the process is
        finished and returns all output. Otherwise the currently available
        output is returned immediately.
        Currently available output depends on buffering and might not include
        everything that has been written by the process.
        """
        if self._error:
            self._close_outputs()
            return self._error

        if wait_until_finished:
            self._process.wait()
        output = self._out_file.read()

        if self.is_finished():
            self._close_outputs()

        return output

    def _close_outputs(self):
        self._out_file.close()
        os.close(self._out_fd)
        self._remove_tempfile()

    def _remove_tempfile(self, attempts=10):
        try:
            os.remove(self._out_path)
        except OSError:
            if not attempts:
                raise
            time.sleep(1)
            self._remove_tempfile(attempts - 1)
