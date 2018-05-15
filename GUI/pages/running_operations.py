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

		play = tk.Button(self, text='Start Execution', command=lambda : self.executeCommand())
		play.grid(row=self.starting_row, column=0, sticky='W', padx=5, pady=3)

		stop = tk.Button(self, text='Stop Execution', command=lambda : self.terminateCommand())
		stop.grid(row=self.starting_row, column=1, sticky='W', padx=5, pady=3)

		self.progressbar = ttk.Progressbar(self)
		self.progressbar.configure(mode='determinate', max=100)
		self.progressbar.grid(row=self.starting_row+1, column=0, columnspan=2, sticky='ew', padx=10, pady=10)

		self.controller.progressbar = self.progressbar

		self.output = Text(self, height=20, width=100)
		self.output.grid(row=self.starting_row+2, column=0)

		self.controller.display = self.output


	def setFrameTitle(self):
		self.title.set('Please wait')

	def moveToNextPage(self):
		super(RunningOperationsPage, self).moveToNextPage()

	def executeCommand(self):
		self.operation = Operations(self.controller)
		self.operation.startThreads()

	def terminateCommand(self):
		self.operation.stopThreads()


