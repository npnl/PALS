try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

import tkFileDialog
import os


class PauseOptionsInputPage(tk.Frame):
	def __init__(self, parent, controller, frame_number):
		tk.Frame.__init__(self, parent)
		self.bind("<<ShowFrame>>", self.onShowFrame)

		self.controller = controller

		self.status = StringVar(self)
		self.frame_number = frame_number

		Label(self, text='', textvariable=self.status, font=("Helvetica", 23)).grid(row=0, columnspan=2, sticky=W+E+N+S)

		Label(self, text="Continue after brain extraction and/or segmentation without any pause").grid(row=1, sticky=W)
		chk_no_pause = tk.Checkbutton(self, variable=self.controller.no_pause)
		chk_no_pause.grid(row=1, column=1)
		

		btn_prev = tk.Button(self, text='Prev', command=lambda : self.moveToPrevPage())
		btn_prev.grid(row=2, column=0)

		btn_next2 = tk.Button(self, text='Next', command=lambda : self.moveToNextPage())
		btn_next2.grid(row=2, column=1)

		print_btn = tk.Button(self, text='Print values', command=lambda : self.checkValues(controller))
		print_btn.grid(row=3, column=1, padx=2)

	def onShowFrame(self, event):
		self.getFrameMessage()

	def getFrameMessage(self):
		if self.controller.run_bet.get() == True and self.controller.run_wm.get() == True:
			self.status.set('SRQL will run brain extraction and white matter segmentation')
		else:
			self.status.set('No input needed')

	def setEntryState(self, entry, flag):
		# entry.set('')
		if entry['state'] == 'disabled':
			entry.config(state='normal')
			flag.set(True)
		else:
			entry.config(state='disabled')
			flag.set(False)

	def moveToNextPage(self):
		print "Moving to next page"
		self.controller.show_frame(self.frame_number+1)
		# input_dir = controller.sv_input_dir.get()
		# if not input_dir.strip():
		# 	self.status.set("Please select an input dir")

	def moveToPrevPage(self):
		print "Moving to prev page"
		self.controller.show_frame(self.frame_number-1)
		# input_dir = controller.sv_input_dir.get()
		# if not input_dir.strip():
		# 	self.status.set("Please select an input dir")

	def checkValues(self, controller):
		print controller.run_bet.get()
		print controller.run_wm.get()
		print controller.no_pause.get()


