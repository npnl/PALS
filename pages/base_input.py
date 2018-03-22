try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

import os

class BaseInputPage(tk.Frame):
	def __init__(self, parent, controller, frame_number):
		tk.Frame.__init__(self, parent)
		self.bind("<<ShowFrame>>", self.onShowFrame)

		self.title = StringVar(self)
		self.status = StringVar(self)
		self.frame_number = frame_number
		self.controller = controller
		self.parent = parent

		self.empty_status = ' '*80

		Label(self, text='', textvariable=self.title, font=("Helvetica", 23)).grid(row=0, columnspan=2, sticky=W+E+N+S)

		last_row = 1000
		Label(self, text='', textvariable=self.status, fg="red").grid(row=last_row, padx=2)

		btn_prev = tk.Button(self, text='Prev', command=lambda : self.moveToPrevPage())
		btn_prev.grid(row=last_row+1, column=0)

		btn_next = tk.Button(self, text='Next', command=lambda : self.moveToNextPage())
		btn_next.grid(row=last_row+1, column=1, padx=2)

		# print_btn = tk.Button(self, text='Print values', command=lambda : self.checkValues(controller))
		# print_btn.grid(row=6, column=1, padx=2)

		self.setFrameTitle()
		self.setStatusMessage(self.empty_status)

	def onShowFrame(self, event):
		self.setFrameTitle()
		self.setStatusMessage(self.empty_status)

	def setFrameTitle(self):
		self.title.set('Base Model Title')

	def setStatusMessage(self, message):
		self.status.set(message)

	def setRequiredInputError(self):
		self.setStatusMessage('Please provide correct input in all the above fields')

	def moveToNextPage(self):
		self.controller.show_frame(self.frame_number + 1)
		self.setStatusMessage(self.empty_status)

	def moveToPrevPage(self):
		self.controller.show_frame(self.frame_number-1)
		self.setStatusMessage(self.empty_status)

	def checkValues(self, controller):
		print controller.sv_input_dir.get()
		print controller.sv_output_dir.get()
		print controller.run_normalize_status.get()

