try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

import os
import tkFileDialog
from .components import LabelToolTip

class BaseInputPage(tk.Frame):
	def __init__(self, parent, controller, frame_number):
		tk.Frame.__init__(self, parent)
		self.bind("<<ShowFrame>>", self.onShowFrame)
		self.grid_rowconfigure(1000, weight=1)
		self.grid_columnconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=1)
		self.grid_columnconfigure(2, weight=1)
		# self.grid_columnconfigure(4, weight=1)

		self.title = StringVar(self)
		self.status = StringVar(self)
		self.frame_number = frame_number
		self.controller = controller
		self.parent = parent
		self.starting_row = 1

		self.empty_status = ' '*80

		lb_title = Label(self, text='', textvariable=self.title, font=("Helvetica", 23, 'bold'), pady=20)
		lb_title.grid(row=0, columnspan=3, sticky=W+E)

		self.setFrameTitle()
		self.setStatusMessage(self.empty_status)
		self.showNavigationBtns()

	def showNavigationBtns(self):
		last_row = 1000

		empty = Frame(self)
		empty.grid(row=last_row, column=0, columnspan=3, sticky=W+E+N+S)

		Label(self, text='', textvariable=self.status, fg="red").grid(row=last_row+1, column=0, columnspan=3, sticky='nwes',)

		if self.frame_number > 0:
			self.btn_prev = tk.Button(self, text='< Back', command=lambda : self.moveToPrevPage())
			self.btn_prev.grid(row=last_row+1, column=0, sticky='W')

		self.btn_next = tk.Button(self, text='Next >', command=lambda : self.moveToNextPage())
		self.btn_next.grid(row=last_row+1, column=2, columnspan=2, sticky='E')

	def onShowFrame(self, event):
		self.setFrameTitle()
		self.setStatusMessage(self.empty_status)

	def setFrameTitle(self):
		self.title.set('Base Model Title')

	def setStatusMessage(self, message):
		self.status.set(message)

	def setRequiredInputError(self, error_msg=None):
		if error_msg == None:
			error_msg = 'Please provide correct input in all the above fields'
		self.setStatusMessage(error_msg)

	def moveToNextPage(self, is_parent=True):
		if is_parent:
			self.controller.pushFrameToStack(self.frame_number)
		self.controller.show_frame(self.frame_number + 1)
		self.setStatusMessage(self.empty_status)

	def moveToPrevPage(self):
		parent_frame_number = self.controller.getParentFrame()
		self.controller.show_frame(parent_frame_number)
		self.setStatusMessage(self.empty_status)

	def chooseDir(self, parent, controller, place_holder, message):
		current_dir = os.getcwd()
		parent.update()
		chosen_dir =  tkFileDialog.askdirectory(parent=self, initialdir = current_dir, title='Select the location of ' + message)
		place_holder.set(chosen_dir)

	def chooseFile(self, parent, controller, place_holder, message, default_dir=''):
		current_dir = default_dir or os.getcwd()
		parent.update()
		chosen_file =  tkFileDialog.askopenfilename(parent=self, initialdir = current_dir, title='Select the location of ' + message)
		place_holder.set(chosen_file)

	def setEntryState(self, entry, flag):
		if flag.get():
			entry.config(state='normal')
		else:
			entry.config(state='disabled')

	def checkValues(self, controller):
		print controller.sv_input_dir.get()
		print controller.sv_output_dir.get()
		print controller.run_normalize_status.get()
