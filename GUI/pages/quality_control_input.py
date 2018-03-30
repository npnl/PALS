try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

import tkFileDialog, os

from base_input import BaseInputPage


class QualityControlInputPage(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)

		Label(self, text='1. Indicate the percentage of intensity values you would like to have removed from your mask.').grid(row=1, sticky=W, rowspan=2)
		en_intensity_percent = Entry(self, textvariable=self.controller.sv_intensity_percent)
		en_intensity_percent.grid(row=1, column=1)

		# print_btn = tk.Button(self, text='Print values', command=lambda : self.checkValues(controller))
		# print_btn.grid(row=5, column=1, padx=2)


	def setFrameTitle(self):
		self.title.set('Quality Control Options')


	def moveToNextPage(self):
		try:
			val = float(self.controller.sv_intensity_percent)
		except:
			self.setStatusMessage('Percent must be a valid number')
			return
		super(QualityControlInputPage, self).moveToNextPage()

	def checkValues(self, controller):
		print controller.run_bet.get()
		print controller.run_wm.get()
		print controller.no_pause.get()


