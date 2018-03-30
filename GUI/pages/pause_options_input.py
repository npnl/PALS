try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

import tkFileDialog
import os

from base_input import BaseInputPage

class PauseOptionsInputPage(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)

		Label(self, text="1. Continue after brain extraction and/or segmentation without any pause").grid(row=1, sticky=W)
		self.chk_no_pause = tk.Checkbutton(self, variable=self.controller.no_pause)
		self.chk_no_pause.grid(row=1, column=1)
		
		# btn_prev = tk.Button(self, text='Prev', command=lambda : self.moveToPrevPage())
		# btn_prev.grid(row=3, column=0)

		# btn_next2 = tk.Button(self, text='Next', command=lambda : self.moveToNextPage())
		# btn_next2.grid(row=3, column=1)

		# print_btn = tk.Button(self, text='Print values', command=lambda : self.checkValues(controller))
		# print_btn.grid(row=3, column=1, padx=2)

	def onShowFrame(self, event):
		super(PauseOptionsInputPage, self).onShowFrame(event)
		self.prepareStatusMessage()

	def setFrameTitle(self):
		self.title.set('Page Title')

	# def setStatusMessage(self, message):
	# 	self.status.set(message)

	def prepareStatusMessage(self):
		if self.controller.run_bet.get() == True and self.controller.run_wm.get() == True:
			self.setStatusMessage('SRQL will run brain extraction and white matter segmentation')
			self.setCheckBoxState(True)
		else:
			self.setStatusMessage('No input needed')
			self.setCheckBoxState(False)

	def setCheckBoxState(self, state):
		if state:
			self.chk_no_pause.config(state='normal')
		else:
			self.chk_no_pause.config(state='disabled')

	# def checkValues(self, controller):
	# 	print controller.run_bet.get()
	# 	print controller.run_wm.get()
	# 	print controller.no_pause.get()


