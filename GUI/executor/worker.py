try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

import os
import signal
import subprocess
from stoppable_thread import StoppableThread

class Worker(object):
	def __init__(self):
		self.threads = {}
		self.running_process = None
		self.thread_running = True

	def execute(self, command, display, parent):
		thread = StoppableThread(target=self.executeAndUpdate, args=(command, display, parent))
		self.threads[thread.name] = thread
		thread.start()
		return thread.name

	def executeAndUpdate(self, command, display, parent):
		for output in self.startExecution(command):
			display.insert(END, output)
			display.see(END)
			parent.update()
			if not self.thread_running:
				break

	def startExecution(self, cmd):
		self.running_process = subprocess.Popen('exec ' + cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
		for stdout_line in iter(self.running_process.stdout.readline, ""):
			yield stdout_line 
		self.running_process.stdout.close()
		return_code = self.running_process.wait()
		if return_code:
			raise subprocess.CalledProcessError(return_code, cmd)

	def isRunning(self):
		return not self.thread_running

	def stop(self, thread_name):
		print "Killing the thread"
		self.thread_running = False
		# os.killpg(os.getpgid(self.running_process.pid), signal.SIGTERM)
		self.running_process.kill()
		# self.threads[thread_name].stop()