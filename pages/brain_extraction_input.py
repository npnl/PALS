try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

from .base_input import *


class BrainExtractionInputPage(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)

		lf_brain = tk.LabelFrame(self, text='Configuration for BET', font='Helvetica 14 bold', padx=15)
		lf_brain.grid(row=self.starting_row+1, column=0, columnspan=3, sticky='nsew', ipadx=10, ipady=10)
		lf_brain.grid_rowconfigure(0, weight=1)
		lf_brain.grid_columnconfigure(3, weight=1)

		lb_start_reg_space = LabelToolTip(lf_brain, text="1. Mask")
		lb_start_reg_space.grid(row=0, column=1, sticky="W", pady=3)

		chk_brain_extraction = Checkbutton(lf_brain, variable=controller.b_brain_extraction)
		chk_brain_extraction.grid(row=0, column=0, sticky='W', pady=3)

		lb_output = LabelToolTip(lf_brain, text="2. Frac")
		lb_output.grid(row=1, column=1, sticky="W", pady=3)

		en_output_dir = Entry(lf_brain, textvariable=controller.sv_brain_ext_frac, width = 46)
		en_output_dir.grid(row=1, column=2, sticky="W", pady=3)

		wrapper = Frame(lf_brain)
		wrapper.grid(row=3, column=0, sticky="WE", columnspan=3, pady=(3, 20))
		wrapper.grid_rowconfigure(0, weight=1)
		wrapper.grid_columnconfigure(2, weight=1)

	def onShowFrame(self, event):
		super(BrainExtractionInputPage, self).onShowFrame(event)
		if not self.controller.b_brain_extraction.get():
			super(BrainExtractionInputPage, self).moveToNextPage(is_parent=False)
		elif not (self.controller.sv_brain_extraction_method.get().strip().lower() == 'bet'):
			super(BrainExtractionInputPage, self).moveToNextPage(is_parent=False)
		else:
			self.silentMode()


	def setFrameTitle(self):
		self.title.set('Brain Extraction')

	def moveToNextPage(self):
		if self.controller.b_brain_extraction.get() and (self.controller.sv_brain_extraction_method.get().strip().lower() == 'bet') \
			and not self.isValidNumberOrInteger(self.controller.sv_brain_ext_frac.get().strip()):
			self.setRequiredInputError('Provide valid inputs for BET')
			return
		if not self.isValidNumberOrInteger(self.controller.sv_brain_ext_frac.get().strip()):
			self.setRequiredInputError('Frac value must be integer or decimal')
			return
		super(BrainExtractionInputPage, self).moveToNextPage()

