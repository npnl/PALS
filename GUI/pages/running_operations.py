try:
	import Tkinter as tk
	from Tkinter import *
	import ttk
except ImportError:
	import tkinter as tk
	from tkinter import *


from base_input import BaseInputPage
from executor import Worker
import webbrowser
from functools import partial
from .components import HyperlinkManager

from utils import Operations


class RunningOperationsPage(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)

		self.move_back = False

		self.operation = Operations(self.controller)

		self.start = tk.Button(self, text='Start Execution', command=lambda : self.executeCommand())
		self.start.grid(row=self.starting_row, column=0, sticky='W', padx=5, pady=3)

		self.stop = tk.Button(self, text='Stop Execution', state="disabled", command=lambda : self.terminateCommand())
		self.stop.grid(row=self.starting_row, column=1, sticky='E', padx=5, pady=3)

		self.progressbar = ttk.Progressbar(self)
		self.progressbar.configure(mode='determinate', max=100)
		self.progressbar.grid(row=self.starting_row+1, column=0, columnspan=2, sticky='ew', padx=10, pady=10)

		self.controller.progressbar = self.progressbar

		self.output = Text(self, height=20, width=100)
		self.output.grid(row=self.starting_row+2, columnspan=2, sticky='ew', padx=10)
		self.hyperlink = HyperlinkManager(self.output)

		self.controller.display = self.output


	def setFrameTitle(self):
		self.title.set('Please wait')

	def onShowFrame(self, event):
		super(RunningOperationsPage, self).onShowFrame(event)
		self.resetAll()

	def resetAll(self):
		self.resetUI()
		self.operation.resetOperations()

	def moveToNextPage(self):
		super(RunningOperationsPage, self).moveToNextPage()

	def resetClickCounter(self):
		self.move_back = False
		self.setRequiredInputError('')

	def userAgreed(self):
		if self.move_back: return True
		self.setRequiredInputError('Warning: All the progress will be lost. If you wish to continue, press the button again')
		self.move_back = True
		return False

	def moveToPrevPage(self):
		if self.userAgreed():
			super(RunningOperationsPage, self).moveToPrevPage()

	def resetUI(self):
		self.start.config(state="normal")
		self.start.config(text='Start Execution')
		self.btn_prev.config(state="normal")
		self.btn_next.config(state="disabled")
		self.stop.config(state="disabled")
		self.progressbar.config(value=0)
		self.resetClickCounter()

	def executeCommand(self):
		self.start.config(state="disabled")
		self.btn_prev.config(state="disabled")
		self.stop.config(state="normal")
		self.resetClickCounter()
		if self.start['text'] == 'Continue Execution':
			print "Text is Continue"
			self.operation.incrementStage()
		self.operation.startThreads(self)

	def terminateCommand(self):
		if self.userAgreed():
			self.stop.config(state="disabled")
			self.operation.stopThreads()

	def pause(self, operation_name='', data='', need_pause=False):
		if need_pause:
			self.start.config(state="normal")
			self.start.config(text='Continue Execution')
			self.btn_prev.config(state="normal")
			self.stop.config(state="disabled")
			self.resetClickCounter()
		if data:
			self.insertHyperLink(operation_name, data)

	def finished(self, operation_name='', data=''):
		self.start.config(state="normal")
		self.btn_prev.config(state="normal")
		self.stop.config(state="disabled")
		self.resetClickCounter()
		if data:
			self.insertHyperLink(operation_name, data)

	def insertHyperLink(self, heading, link):
		self.output.insert(END, "Qc Page for : " + heading, self.hyperlink.add(partial(webbrowser.open, link)))
		self.output.insert(END, '\n')
		self.output.see(END)




