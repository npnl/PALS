try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

import tkFileDialog
import os

from threading import Thread
import subprocess

from utils import isValidPath
from base_input import BaseInputPage
from executor import Worker

class WelcomePage(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)

		lb_main = Label(self, text="Please select the modules you would like to perform", font='Helvetica 14 bold')
		lb_main.grid(row=self.starting_row, column=0, columnspan=100, sticky=W)

		lf_main = LabelFrame(self, text='Main Modules', padx=15, font='Helvetica 14 bold')
		lf_main.grid(row=self.starting_row+2, column=0, columnspan=100, sticky='W', padx=3, pady=3, ipadx=5, ipady=5)
		lf_main.grid_rowconfigure(0, weight=1)
		lf_main.grid_columnconfigure(0, weight=1)


		lb_radiological_convention = Label(lf_main, text="1. Reorient to Radiological Convention")
		lb_radiological_convention.grid(row=0, column=0, sticky="W", pady=3)

		chk_radiological_convention = Checkbutton(lf_main, variable=controller.b_radiological_convention)
		chk_radiological_convention.grid(row=0, column=97, sticky='W', pady=3)

		lb_wm_correction = Label(lf_main, text="2. White Matter Intensity Correction")
		lb_wm_correction.grid(row=1, column=0, sticky="W", pady=3)

		chk_wm_correction = Checkbutton(lf_main, variable=controller.b_wm_correction)
		chk_wm_correction.grid(row=1, column=97, sticky='W', pady=3)


		lb_lesion_load = Label(lf_main, text="3. Lesion Load Calculation")
		lb_lesion_load.grid(row=2, column=0,  sticky="W", pady=3)

		chk_ll_calculation = Checkbutton(lf_main, variable=controller.b_ll_calculation)
		chk_ll_calculation.grid(row=2, column=97, sticky='W', pady=3)

		lf_visual_qc = LabelFrame(self, text='Stand Alone Module', padx=15, font='Helvetica 14 bold')
		lf_visual_qc.grid(row=self.starting_row+3, column=0, columnspan=100, sticky='W', padx=3, pady=3, ipadx=5, ipady=5)
		lf_visual_qc.grid_rowconfigure(0, weight=1)
		lf_visual_qc.grid_columnconfigure(0, weight=1)

		lb_visual_qc = Label(lf_visual_qc, text="4. Perform Visual Quality Control only")
		lb_visual_qc.grid(row=0, column=0, sticky="W", pady=3)

		chk_visual_qc = Checkbutton(lf_visual_qc, variable=controller.b_quality_control)
		chk_visual_qc.grid(row=0, column=97, sticky='W', pady=3)


		lb_opt_sout = Label(self, text="By default, PALS will pause to allow for visual QC to ensure quality assurance after each processing step. Uncheck to opt out of pausing.", padx=10)
		lb_opt_sout.grid(row=self.starting_row+4, column=0, columnspan=96, sticky="W", padx=20, pady=(20, 10))

		chk_out_out = Checkbutton(self, variable=controller.b_visual_qc)
		chk_out_out.grid(row=self.starting_row+4, column=97, sticky='W', pady=(20, 10))


	def setFrameTitle(self):
		self.title.set('Welcome to PALS!')


	def moveToNextPage(self):
		if self.controller.b_radiological_convention.get() \
			or self.controller.b_wm_correction.get() \
			or self.controller.b_ll_calculation.get() \
			or self.controller.b_quality_control.get():
			super(WelcomePage, self).moveToNextPage()
		else:
			self.setRequiredInputError('Select atleast one operation')


	def checkValues(self, controller):
		print controller.sv_input_dir.get()
		print controller.sv_output_dir.get()
		print controller.run_normalize_status.get()

	def executeCommand(self):
		self.worker = Worker()
		self.thread_name = self.worker.execute('python testScript.py', self.output, self)
		print self.thread_name

	def stopCommand(self):
		self.worker.stop(self.thread_name)
