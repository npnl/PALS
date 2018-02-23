try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

import tkFileDialog
import os


class QualityControlInputPage(tk.Frame):
	def __init__(self, parent, controller, frame_number):
		tk.Frame.__init__(self, parent)
		self.bind("<<ShowFrame>>", self.onShowFrame)

		self.controller = controller

		self.title = StringVar(self)
		self.status = StringVar(self)
		self.frame_number = frame_number

		Label(self, text='', textvariable=self.title, font=("Helvetica", 23)).grid(row=0, columnspan=2, sticky=W+E+N+S)

		Label(self, text='1. Indicate the percentage of intensity values you would like to have removed from your mask.').grid(row=1, sticky=W, rowspan=2)
		en_intensity_percent = Entry(self, textvariable=self.controller.sv_intensity_percent)
		en_intensity_percent.grid(row=1, column=1)

		Label(self, text="", textvariable=self.status, fg="red").grid(row=3)

		btn_prev = tk.Button(self, text='Prev', command=lambda : self.moveToPrevPage())
		btn_prev.grid(row=4, column=0)

		btn_next2 = tk.Button(self, text='Next', command=lambda : self.moveToNextPage())
		btn_next2.grid(row=4, column=1)

		print_btn = tk.Button(self, text='Print values', command=lambda : self.checkValues(controller))
		print_btn.grid(row=5, column=1, padx=2)

	def onShowFrame(self, event):
		self.setFrameTitle()

	def setFrameTitle(self):
		self.title.set('Quality Control Options')

	def setStatusMessage(self, message):
		self.status.set(message)


	def moveToNextPage(self):
		try:
			val = float(self.controller.sv_intensity_percent)
		except:
			self.setStatusMessage('Percent must be a valid number')
			return
		print "Moving to next page"
		self.setStatusMessage('')
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


