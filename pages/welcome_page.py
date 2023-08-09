try:
	import Tkinter as tk
	from Tkinter import *
	import tkFileDialog
except ImportError:
	import tkinter as tk
	from tkinter import *
	from tkinter import filedialog as tkFileDialog

import os
import matplotlib

from .base_input import *
from .popups import QCPopup


class WelcomePage(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)
		lb_main = Label(self, text="Please select the modules you would like to perform:", font='Helvetica 14 bold')
		lb_main.grid(row=self.starting_row, column=0, columnspan=3, sticky='W')

		lf_main = LabelFrame(self, text='Main Modules', padx=15, font='Helvetica 14 bold')
		lf_main.grid(row=self.starting_row+2, column=0, columnspan=3, sticky='WE', padx=5, pady=(15, 0), ipadx=5, ipady=5)

		lb_radiological_convention = LabelToolTip(lf_main, text="1. Reorient to radiological convention", tool_tip_text=self.controller.desc.reorient)
		lb_radiological_convention.grid(row=0, column=1, sticky="W", pady=3)

		chk_radiological_convention = Checkbutton(lf_main, variable=controller.b_radiological_convention, command=lambda : self.setEntryState(en_orientation_method, self.controller.b_radiological_convention))
		chk_radiological_convention.grid(row=0, column=0, sticky='W', pady=3)

		lb_orientation_method = LabelToolTip(lf_main, text="Orientation", tool_tip_text=self.controller.desc.orientation)
		lb_orientation_method.grid(row=1, column=1, sticky="W", padx=(20,0),pady=(3,10))

		en_orientation_method = Entry(lf_main, textvariable=controller.sv_orientation_method, width = 46)
		en_orientation_method.config(state='disabled')
		en_orientation_method.grid(row=1, column=2, sticky="W", pady=(3,10))

		# lf_registration = LabelFrame(lf_main, text='')
		# lf_registration.grid(row=1, column=0, columnspan=2, sticky='W', pady=3)
		# lf_registration.grid_rowconfigure(0, weight=0)
		# lf_registration.grid_columnconfigure(3, weight=0)
		# lf_registration.configure(borderwidth=0, relief='flat')

		lb_registration = LabelToolTip(lf_main, text="2. Registration", tool_tip_text=self.controller.desc.registration)
		lb_registration.grid(row=2, column=1, sticky="W", pady=3)

		chk_registration = Checkbutton(lf_main, variable=controller.b_registration, command=lambda : self.setEntryState(en_registration_method, self.controller.b_registration))
		chk_registration.grid(row=2, column=0, sticky='W', pady=3)

		lb_registration_method = LabelToolTip(lf_main, text="Registration method", tool_tip_text=self.controller.desc.registration_method)
		lb_registration_method.grid(row=3, column=1, sticky="W", padx=(20,0),pady=(3,10))

		en_registration_method = Entry(lf_main, textvariable=controller.sv_registration_method, width = 46)
		en_registration_method.config(state='disabled')
		en_registration_method.grid(row=3, column=2, sticky="W", pady=(3,10))

		# lb_reg_method = LabelToolTip(lf_registration, text="Registration method", tool_tip_text=self.controller.desc.bet_identifier)
		# lb_reg_method.grid(row=1, column=0, sticky="W", pady=(3, 20))

		# en_bet_identifier = Entry(lf_registration, textvariable=controller.sv_bet_method, width = 20)
		# en_bet_identifier.config(state='disabled')
		# en_bet_identifier.grid(row=1, column=1, sticky="W", pady=(3, 20))

		lb_brain_extraction = LabelToolTip(lf_main, text="3. Brain extraction", tool_tip_text=self.controller.desc.brain_extraction)
		lb_brain_extraction.grid(row=4, column=1, sticky="W", pady=3)

		chk_brain_extraction = Checkbutton(lf_main, variable=controller.b_brain_extraction, command=lambda : self.setEntryState(en_brain_extraction_method, self.controller.b_brain_extraction))
		chk_brain_extraction.grid(row=4, column=0, sticky='W', pady=3)

		lb_brain_extraction_method = LabelToolTip(lf_main, text="Brain extraction method", tool_tip_text=self.controller.desc.brain_extraction_method)
		lb_brain_extraction_method.grid(row=5, column=1, sticky="W", padx=(20,0), pady=(3,10))

		en_brain_extraction_method = Entry(lf_main, textvariable=controller.sv_brain_extraction_method, width = 46)
		en_brain_extraction_method.config(state='disabled')
		en_brain_extraction_method.grid(row=5, column=2, sticky="W", pady=(3,10))

		lb_wm_segmentation = LabelToolTip(lf_main, text="4. White Matter Segmentation", tool_tip_text=self.controller.desc.white_matter_segmentation)
		lb_wm_segmentation.grid(row=6, column=1, sticky="W", pady=3)

		chk_wm_segmentation = Checkbutton(lf_main, variable=controller.b_wm_segmentation, command=lambda : controller.b_wm_segmentation_lc.set(not controller.b_wm_segmentation))
		chk_wm_segmentation.grid(row=6, column=0, sticky='W', pady=3)

		lb_wm_correction = LabelToolTip(lf_main, text="5. Lesion correction for white matter voxels", tool_tip_text=self.controller.desc.lesion_correction)
		lb_wm_correction.grid(row=7, column=1, sticky="W", pady=3)

		chk_wm_correction = Checkbutton(lf_main, variable=controller.b_wm_correction, command=self.setOne)
		chk_wm_correction.grid(row=7, column=0, sticky='W', pady=3)

		lb_lesion_load = LabelToolTip(lf_main, text="6. Lesion load calculation", tool_tip_text=self.controller.desc.lesion_load_calculation)
		lb_lesion_load.grid(row=8, column=1,  sticky="W", pady=3)

		chk_ll_calculation = Checkbutton(lf_main, variable=controller.b_ll_calculation, command=self.setOne)
		chk_ll_calculation.grid(row=8, column=0, sticky='W', pady=3)

		lb_lesion_heatmap = LabelToolTip(lf_main, text="7. Lesion Heatmap", tool_tip_text=self.controller.desc.lesion_heatmap)
		lb_lesion_heatmap.grid(row=9, column=1,  sticky="W", pady=3)

		chk_lesion_heatmap = Checkbutton(lf_main, variable=controller.b_lesion_heatmap, command=self.setOne)
		chk_lesion_heatmap.grid(row=9, column=0, sticky='W', pady=3)


		wrapper = Frame(self)
		wrapper.grid(row=self.starting_row+4, column=0, columnspan=3, sticky='w', padx=20, pady=(20, 10))

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
		i = 1
		# if self.controller.b_radiological_convention.get()\
		# 	or self.controller.b_ll_calculation.get()\
		# 	or self.controller.b_wm_correction.get():
			#self.controller.b_visual_qc.set(False)

	# def setTwo(self):
		# if self.controller.b_visual_qc.get():
		# 	self.controller.b_radiological_convention.set(False)
		# 	self.controller.b_ll_calculation.set(False)
		# 	self.controller.b_wm_correction.set(False)

	def moveToNextPage(self):
		# if self.controller.b_radiological_convention.get() \
		# 	or self.controller.b_wm_correction.get() \
		# 	or self.controller.b_ll_calculation.get() \
		# 	or self.controller.b_visual_qc.get():
		# 	super(WelcomePage, self).moveToNextPage()
		if self.controller.b_radiological_convention.get() \
			or self.controller.b_registration.get() \
			or self.controller.b_brain_extraction.get() \
			or self.controller.b_wm_segmentation.get() \
			or self.controller.b_wm_correction.get() \
			or self.controller.b_lesion_heatmap.get() \
			or self.controller.b_ll_calculation.get():
			super(WelcomePage, self).moveToNextPage()
		else:
			self.setRequiredInputError('Select at least one operation.')

