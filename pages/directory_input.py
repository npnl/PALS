try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

from base_input import *
from utils import isValidPath

class DirectoryInputPage(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)

		lf_inputs = tk.LabelFrame(self, text='Inputs', font='Helvetica 14 bold', padx=15)
		lf_inputs.grid(row=self.starting_row+1, column=0, columnspan=100, sticky='nsew', padx=30, pady=30, ipadx=10, ipady=10)
		lf_inputs.grid_rowconfigure(0, weight=1)
		lf_inputs.grid_columnconfigure(0, weight=1)

		lb_input = Label(lf_inputs, text="1. Input Directory")
		lb_input.grid(row=0, column=0, sticky="W", pady=3)


		button1 = tk.Button(lf_inputs, text='Select', command=lambda : self.chooseDir(self, controller, controller.sv_input_dir, 'Input Directory'))
		button1.grid(row=0, column=91, sticky='W', padx=5, pady=3)

		en_input_dir = Entry(lf_inputs, textvariable=controller.sv_input_dir, width = 50)
		en_input_dir.grid(row=0, column=1, columnspan=90, sticky="W", pady=3)


		lb_output = Label(lf_inputs, text="2. Output Directory")
		lb_output.grid(row=1, column=0, sticky="W", pady=3)

		button2 = tk.Button(lf_inputs, text='Select', command=lambda : self.chooseDir(self, controller, controller.sv_output_dir, 'Output Directory'))
		button2.grid(row=1, column=91, sticky='E', padx=5, pady=3)

		en_output_dir = Entry(lf_inputs, textvariable=controller.sv_output_dir, width = 50)
		en_output_dir.grid(row=1, column=1, columnspan=90, sticky="W", pady=3)



		lb_t1_identifier = Label(lf_inputs, text="3. T1 Anatomical Image Identifier")
		lb_t1_identifier.grid(row=2, column=0, sticky="W", pady=3)

		en_t1_identifier = Entry(lf_inputs, textvariable=controller.sv_t1_id, width = 50)
		en_t1_identifier.grid(row=2, column=1, columnspan=90, sticky="W", pady=3)



		lb_lm_identifier = Label(lf_inputs, text="4. Lesion Mask Identifier")
		lb_lm_identifier.grid(row=3, column=0, sticky="W", pady=(3, 20))


		en_lm_identifier = Entry(lf_inputs, textvariable=controller.sv_lesion_mask_id, width = 50)
		en_lm_identifier.grid(row=3, column=1, columnspan=90, sticky="W", pady=(3, 20))


		lb_same_anatomical_space = Label(lf_inputs, text="I verify that my anatomical image and lesion masks are in the same anatomical space.")
		lb_same_anatomical_space.grid(row=4, column=0, columnspan=90, sticky="W",  padx=10, pady=(3, 20))

		chk_same_anatomical_space = tk.Checkbutton(lf_inputs, variable=controller.b_same_anatomical_space)
		chk_same_anatomical_space.grid(row=4, column=91, sticky='W', pady=(3, 20))


	def setFrameTitle(self):
		self.title.set('Please indicate the following:')

	def moveToNextPage(self):
		input_dir = self.controller.sv_input_dir.get()
		output_dir = self.controller.sv_output_dir.get()
		if not isValidPath(input_dir.strip()) or not isValidPath(output_dir.strip()):
			self.setRequiredInputError('Directory inputs are invalid')
			return
		if not self.controller.sv_lesion_mask_id.get().strip()\
			or not self.controller.sv_t1_id.get().strip():
			self.setRequiredInputError()
			return
		else:
			super(DirectoryInputPage, self).moveToNextPage()


	def checkValues(self, controller):
		print controller.sv_input_dir.get()
		print controller.sv_output_dir.get()
		print controller.run_normalize_status.get()
