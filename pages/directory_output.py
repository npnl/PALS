try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

from .base_input import *


class DirectoryOutputPage(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)

		lf_output_inputs = tk.LabelFrame(self, text='Output', font='Helvetica 14 bold', padx=15)
		lf_output_inputs.grid(row=self.starting_row+1, column=0, columnspan=3, sticky='nsew', ipadx=10, ipady=10)
		lf_output_inputs.grid_rowconfigure(0, weight=1)
		lf_output_inputs.grid_columnconfigure(3, weight=1)

		lb_output = LabelToolTip(lf_output_inputs, text="1. Root Directory", tool_tip_text=self.controller.desc.output_dir)
		lb_output.grid(row=0, column=0, sticky="W", pady=3)

		button_out = tk.Button(lf_output_inputs, text='Browse', command=lambda : self.chooseDir(self, controller, controller.sv_output_dir, 'Output Directory'))
		button_out.grid(row=0, column=2, sticky='W', padx=5, pady=3)

		en_output_dir = Entry(lf_output_inputs, textvariable=controller.sv_output_dir, width = 46)
		en_output_dir.grid(row=0, column=1, sticky="W", pady=3)

		lb_start_reg_space = LabelToolTip(lf_output_inputs, text="2. Start Registration Space", tool_tip_text=self.controller.desc.t1_identifier)
		lb_start_reg_space.grid(row=1, column=0, sticky="W", pady=3)

		en_start_reg_space = Entry(lf_output_inputs, textvariable=controller.sv_out_start_reg_space, width = 46)
		en_start_reg_space.grid(row=1, column=1, sticky="W", pady=3)

		lb_output_reg_space = LabelToolTip(lf_output_inputs, text="3. Output Registration Space", tool_tip_text=self.controller.desc.t1_identifier)
		lb_output_reg_space.grid(row=2, column=0, sticky="W", pady=3)

		en_output_reg_space = Entry(lf_output_inputs, textvariable=controller.sv_output_reg_space, width = 46)
		en_output_reg_space.grid(row=2, column=1, sticky="W", pady=3)

		lb_reg_transform = LabelToolTip(lf_output_inputs, text="4. Registration Transform", tool_tip_text=self.controller.desc.t1_identifier)
		lb_reg_transform.grid(row=3, column=0, sticky="W", pady=3)

		en_reg_transform = Entry(lf_output_inputs, textvariable=controller.sv_out_reg_transform, width = 46)
		en_reg_transform.grid(row=3, column=1, sticky="W", pady=3)

		lb_reorient = LabelToolTip(lf_output_inputs, text="5. Reorient", tool_tip_text=self.controller.desc.t1_identifier)
		lb_reorient.grid(row=4, column=0, sticky="W", pady=3)

		en_reorient = Entry(lf_output_inputs, textvariable=controller.sv_out_reorient, width = 46)
		en_reorient.grid(row=4, column=1, sticky="W", pady=3)

		lb_brain_extraction = LabelToolTip(lf_output_inputs, text="6. Brain Registration", tool_tip_text=self.controller.desc.t1_identifier)
		lb_brain_extraction.grid(row=5, column=0, sticky="W", pady=3)

		en_brain_extraction = Entry(lf_output_inputs, textvariable=controller.sv_out_brain_registration, width = 46)
		en_brain_extraction.grid(row=5, column=1, sticky="W", pady=3)

		lb_lesion_corr = LabelToolTip(lf_output_inputs, text="7. Lesion Corrected", tool_tip_text=self.controller.desc.t1_identifier)
		lb_lesion_corr.grid(row=6, column=0, sticky="W", pady=3)

		en_lesion_corr = Entry(lf_output_inputs, textvariable=controller.sv_out_lesion_corr, width = 46)
		en_lesion_corr.grid(row=6, column=1, sticky="W", pady=3)

		wrapper = Frame(lf_output_inputs)
		wrapper.grid(row=7, column=0, sticky="WE", columnspan=3, pady=(3, 20))
		wrapper.grid_rowconfigure(0, weight=1)
		wrapper.grid_columnconfigure(2, weight=1)

	def onShowFrame(self, event):
		super(DirectoryOutputPage, self).onShowFrame(event)
		self.silentMode()


	def setFrameTitle(self):
		self.title.set('Please indicate the following:')

	def moveToNextPage(self):
		output_dir = self.controller.sv_output_dir.get()
		if not self.isValidPath(output_dir.strip()):
			self.setRequiredInputError('Output Directory is not valid.')
			return
		if not self.controller.sv_out_start_reg_space.get().strip():
			self.setRequiredInputError('Provide a valid space entity for BIDS output filename.')
			return
		if not self.controller.sv_output_reg_space.get().strip() and self.controller.b_registration.get():
			self.setRequiredInputError('Output Registration space must be provided')
			return
		super(DirectoryOutputPage, self).moveToNextPage()

