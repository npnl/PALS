try:
	import Tkinter as tk
	from Tkinter import *
	import tkFileDialog
except ImportError:
	import tkinter as tk
	from tkinter import *
	from tkinter import filedialog as tkFileDialog

import os

from utils import isValidPath
from .base_input import *
from .popups import QCPopup


class WelcomePage(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)

		lb_main = Label(self, text="Please select the modules you would like to perform:", font='Helvetica 14 bold')
		lb_main.grid(row=self.starting_row, column=0, columnspan=3, sticky='W')

		lf_main = LabelFrame(self, text='Main Modules', padx=15, font='Helvetica 14 bold')
		lf_main.grid(row=self.starting_row+2, column=0, columnspan=3, sticky='WE', padx=5, pady=(15, 0), ipadx=5, ipady=5)

		lb_radiological_convention = LabelToolTip(lf_main, text="1. Reorient to radiological convention", tool_tip_text=self.controller.desc.rad_reorient)
		lb_radiological_convention.grid(row=0, column=1, sticky="W", pady=3)

		chk_radiological_convention = Checkbutton(lf_main, variable=controller.b_radiological_convention, command=self.setOne)
		chk_radiological_convention.grid(row=0, column=0, sticky='W', pady=3)

		lb_wm_correction = LabelToolTip(lf_main, text="2. Lesion correction for white matter voxels", tool_tip_text=self.controller.desc.wm_correction)
		lb_wm_correction.grid(row=1, column=1, sticky="W", pady=3)

		chk_wm_correction = Checkbutton(lf_main, variable=controller.b_wm_correction, command=self.setOne)
		chk_wm_correction.grid(row=1, column=0, sticky='W', pady=3)

		lb_lesion_load = LabelToolTip(lf_main, text="3. Lesion load calculation", tool_tip_text=self.controller.desc.lesion_load)
		lb_lesion_load.grid(row=2, column=1,  sticky="W", pady=3)

		chk_ll_calculation = Checkbutton(lf_main, variable=controller.b_ll_calculation, command=self.setOne)
		chk_ll_calculation.grid(row=2, column=0, sticky='W', pady=3)

		lf_visual_qc = LabelFrame(self, text='Stand Alone Module', padx=15, font='Helvetica 14 bold')
		lf_visual_qc.grid(row=self.starting_row+3, column=0, columnspan=3, sticky='WE', padx=5, pady=(15, 0), ipadx=5, ipady=5)
		lf_visual_qc.grid_rowconfigure(0, weight=1)

		lb_visual_qc = LabelToolTip(lf_visual_qc, text="4. Perform visual quality control only", tool_tip_text=self.controller.desc.visual_qc)
		lb_visual_qc.grid(row=0, column=1, sticky="W", pady=3)

		chk_visual_qc = Checkbutton(lf_visual_qc, variable=controller.b_visual_qc, command=self.setTwo)
		chk_visual_qc.grid(row=0, column=0, sticky='W', pady=3)


		wrapper = Frame(self)
		wrapper.grid(row=self.starting_row+4, column=0, columnspan=3, sticky='w', padx=20, pady=(20, 10))

		lb_opt_out = Label(wrapper, text="By default, PALS will pause to allow for visual QC to ensure quality assurance after each processing step.\nUncheck to opt out of pausing.", justify="left")
		lb_opt_out.grid(row=0, column=1, sticky="W")

		self.chk_out_out = Checkbutton(wrapper, variable=controller.b_pause_for_qc, command=lambda: self.pauseQCPopup())
		self.chk_out_out.grid(row=0, column=0, sticky='W')

		# self.silentMode()

	def onShowFrame(self, event):
		super(WelcomePage, self).onShowFrame(event)
		self.silentMode()

	def setFrameTitle(self):
		self.title.set('Welcome to PALS!')


	def pauseQCPopup(self):
		if not self.controller.b_pause_for_qc.get():
			qc_popup = QCPopup(self.controller)
			qc_popup.grab_set()
			self.chk_out_out["state"] = "disabled"
			self.controller.wait_window(qc_popup)
			self.chk_out_out["state"] = "normal"
			qc_popup.grab_release()

	def setOne(self):
		if self.controller.b_radiological_convention.get()\
			or self.controller.b_ll_calculation.get()\
			or self.controller.b_wm_correction.get():
			self.controller.b_visual_qc.set(False)

	def setTwo(self):
		if self.controller.b_visual_qc.get():
			self.controller.b_radiological_convention.set(False)
			self.controller.b_ll_calculation.set(False)
			self.controller.b_wm_correction.set(False)

	def moveToNextPage(self):
		if self.controller.b_radiological_convention.get() \
			or self.controller.b_wm_correction.get() \
			or self.controller.b_ll_calculation.get() \
			or self.controller.b_visual_qc.get():
			super(WelcomePage, self).moveToNextPage()
		else:
			self.setRequiredInputError('Select at least one operation.')

