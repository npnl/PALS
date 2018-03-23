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

from utils.paths import isValidPath
from base_input import BaseInputPage
from executor import Worker

class WelcomePage(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)

		Label(self, text="1. White Matter Correction").grid(row=1, sticky=W)

		button1 = tk.Button(self, text='Select', command=lambda : self.chooseDir(self, controller, controller.sv_input_dir))
		button1.grid(row=1, column=2)

		en_input_dir = Entry(self, textvariable=controller.sv_input_dir)
		en_input_dir.grid(row=1, column=1)

		
		Label(self, text="2. Lesion Load Calculation").grid(row=2, sticky=W)
		
		button2 = tk.Button(self, text='Select', command=lambda : self.chooseDir(self, controller, controller.sv_output_dir))
		button2.grid(row=2, column=2)

		en_output_dir = Entry(self, textvariable=controller.sv_output_dir)
		en_output_dir.grid(row=2, column=1)

		Label(self, text="3. Only Do Quality Check").grid(row=4, sticky=W)
		en_anatomical_id = Entry(self, textvariable=controller.sv_anatomical_id)
		en_anatomical_id.grid(row=4, column=1)


		Label(self, text="4. Lesion Mask Identifier/Wildcard").grid(row=5, sticky=W)
		en_lesion_mask = Entry(self, textvariable=controller.sv_lesion_mask)
		en_lesion_mask.grid(row=5, column=1)

		Label(self, text="5. Run WM Correction").grid(row=6, padx=(0, 40),sticky=W)
		chk_run_wm_correction = tk.Checkbutton(self, variable=controller.run_wm_correction)
		chk_run_wm_correction.grid(row=6, column=1, sticky=W)

		Label(self, text="6. Run Lesion Load Calculation").grid(row=7, padx=(0, 40),sticky=W)
		chk_run_load_calculation = tk.Checkbutton(self, variable=controller.run_load_calculation)
		chk_run_load_calculation.grid(row=7, column=1, sticky=W)

		btn_cal = tk.Button(self, text='Calculate', command=lambda : self.executeCommand())
		btn_cal.grid(row=23, column=1, padx=2)

		btn_stop = tk.Button(self, text='Stop', command=lambda : self.stopCommand())
		btn_stop.grid(row=24, column=1, padx=2)

		self.output = tk.Text(self, height=15, width=90)
		self.output.grid(row=25, column=1)

	def setFrameTitle(self):
		self.title.set('Welcome')


	def moveToNextPage(self):
		input_dir = self.controller.sv_input_dir.get()
		output_dir = self.controller.sv_output_dir.get()
		anatomical_id = self.controller.sv_anatomical_id.get()
		lesion_mask = self.controller.sv_lesion_mask.get()
		if not isValidPath(input_dir.strip())\
			 or not isValidPath(output_dir.strip())\
			 or not anatomical_id.strip() or not lesion_mask.strip():
			self.setRequiredInputError()
		else:
			super(WelcomePage, self).moveToNextPage()

	def chooseDir(self, parent, controller, place_holder):
		current_dir = os.getcwd()
		parent.update()
		chosen_dir =  tkFileDialog.askdirectory(parent=self, initialdir = current_dir, title='Select the location of your input directory')
		place_holder.set(chosen_dir)


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
