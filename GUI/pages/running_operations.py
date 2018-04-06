try:
	import Tkinter as tk
	from Tkinter import *
	import ttk
except ImportError:
	import tkinter as tk
	from tkinter import *


from base_input import BaseInputPage
from executor import Worker

from utils import Operations


class RunningOperationsPage(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)

		# p = ttk.Progressbar(parent, orient=HORIZONTAL, length=100, mode='determinate')
		# p.grid(row=self.starting_row)

		play = tk.Button(self, text='Play', command=lambda : self.executeCommand())
		play.grid(row=self.starting_row, column=0, sticky='W', padx=5, pady=3)

		stop = tk.Button(self, text='Stop', command=lambda : self.stopCommand())
		stop.grid(row=self.starting_row, column=1, sticky='W', padx=5, pady=3)

		test_command = tk.Button(self, text='Test Command', command=lambda : self.testCommands())
		test_command.grid(row=self.starting_row + 1, column=0, sticky='W', padx=5, pady=3)

		self.output = Text(self, height=20, width=100)
		self.output.grid(row=self.starting_row+2, column=0)


	def testCommands(self):
		operation = Operations(self.controller)
		operation.initialise()

	def setFrameTitle(self):
		self.title.set('Please wait')

	def moveToNextPage(self):
		super(RunningOperationsPage, self).moveToNextPage()

	def executeCommand(self):
		main_py.stop()
		
		self.worker = Worker()
		self.thread_name = self.worker.execute('mplayer song.wav', self.output, self)
		print self.thread_name

	def stopCommand(self):
		self.worker.stop(self.thread_name)
