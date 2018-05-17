try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

from base_input import BaseInputPage
from utils import isValidPath
import os, subprocess

class SettingsInput(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)

		lf_inputs = tk.LabelFrame(self, text='Inputs', font='Helvetica 14 bold', padx=15)
		lf_inputs.grid(row=self.starting_row+1, column=0, columnspan=100, sticky='nsew', padx=30, pady=30, ipadx=10, ipady=10)
		lf_inputs.grid_rowconfigure(0, weight=1)
		lf_inputs.grid_columnconfigure(0, weight=1)

		lb_input = Label(lf_inputs, text="1. Absolute path to FSL binaries")
		lb_input.grid(row=0, column=0, sticky="W", pady=3)


		button = tk.Button(lf_inputs, text='Select', command=lambda : self.chooseDir(self, controller, controller.sv_fsl_binaries, 'FSL Binaries'))
		button.grid(row=0, column=91, sticky='W', padx=5, pady=3)

		en_input_dir = Entry(lf_inputs, textvariable=controller.sv_fsl_binaries, width = 50)
		en_input_dir.grid(row=0, column=1, columnspan=90, sticky="W", pady=3)


	def checkFslInstalled(self, path=''):
		cmd = os.path.join(path, "fslmaths")
		try:
			subprocess.call([cmd])
			return True
		except OSError as e:
			if e.errno == os.errno.ENOENT:
		return False


	def setFrameTitle(self):
		self.title.set('Please indicate the following:')

	def moveToNextPage(self):
		input_dir = self.controller.sv_fsl_binaries.get()
		if isValidPath(input_dir.strip()) and self.checkFslInstalled(input_dir):
			super(SettingsInput, self).moveToNextPage()
		else:
			with open('pals.config', 'w') as f:
				f.write(input_dir)
				f.close()
			self.setRequiredInputError('Not a valid path FSL directory path')

