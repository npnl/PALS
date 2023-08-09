try:
	import Tkinter as tk
	from Tkinter import *
	import tkFileDialog
except ImportError:
	import tkinter as tk
	from tkinter import *
	from tkinter import filedialog as tkFileDialog

import os

from .base_input import *

class LesionCorrInputPage(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)

		lb_main = Label(self, text="Please indicate if you have already performed the following.", font='Helvetica 14 bold')
		lb_main.grid(row=self.starting_row, column=0, columnspan=3, sticky='W')
		lb_main2 = Label(self, text="PALS will run FSL brain extraction (BET) and white matter segmentation (FAST) if they have not already been performed. \n", font='Helvetica 14')
		lb_main2.grid(row=self.starting_row+1, column=0, columnspan=3, sticky='W')

		lf_wm_seg = tk.LabelFrame(self, text='White Matter Segmentation', padx=15, font='Helvetica 14 bold')
		lf_wm_seg.grid(row=self.starting_row+3, column=0, columnspan=3, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
		lf_wm_seg.grid_rowconfigure(0, weight=1)
		lf_wm_seg.grid_columnconfigure(4, weight=1)

		lb_wm_seg = LabelToolTip(lf_wm_seg, text="Has white matter segmentation already been performed on all subjects?", tool_tip_text=self.controller.desc.wm_seg)
		lb_wm_seg.grid(row=0, column=1, columnspan=2, sticky="W", pady=3)

		lb_wm_id = LabelToolTip(lf_wm_seg, text="White matter segmentation root", tool_tip_text=self.controller.desc.white_matter_segmentation_root)
		lb_wm_id.grid(row=1, column=1, sticky="W", pady=(3, 20))

		button_wm_seg_root = tk.Button(lf_wm_seg, text='Browse', command=lambda : self.chooseDir(self, controller, controller.sv_wm_seg_root, 'WM Segmentation Root'))
		button_wm_seg_root.grid(row=1, column=3, sticky='W', padx=5, pady=(3, 20))

		en_wm_id = Entry(lf_wm_seg, textvariable=controller.sv_wm_seg_root, width = 46)
		en_wm_id.config(state='disabled')
		en_wm_id.grid(row=1, column=2, sticky="W", pady=(3, 20))

		chk_wm_seg = tk.Checkbutton(lf_wm_seg, variable=controller.b_wm_segmentation_lc, command=lambda : self.setEntryState(en_wm_id, self.controller.b_wm_segmentation_lc))
		chk_wm_seg.grid(row=0, column=0, sticky='W', pady=3)

		lf_lc_inputs = tk.LabelFrame(self, text='Lesion Correction Inputs', padx=15, font='Helvetica 14 bold')
		lf_lc_inputs.grid(row=self.starting_row+5, column=0, columnspan=3, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
		lf_lc_inputs.grid_rowconfigure(4, weight=1)
		lf_lc_inputs.grid_columnconfigure(3, weight=1)

		lb_img_norm_min= LabelToolTip(lf_lc_inputs, text="Image Norm Min", tool_tip_text=self.controller.desc.lc_image_norm_min)
		lb_img_norm_min.grid(row=0, column=0, sticky="W", pady=3)

		en_img_norm_min = Entry(lf_lc_inputs, textvariable=controller.sv_img_norm_min, width = 5)
		en_img_norm_min.grid(row=0, column=2, sticky="E", pady=3)

		lb_img_norm_max= LabelToolTip(lf_lc_inputs, text="Image Norm Max", tool_tip_text=self.controller.desc.lc_image_norm_max)
		lb_img_norm_max.grid(row=1, column=0, sticky="W", pady=3)

		en_img_norm_max = Entry(lf_lc_inputs, textvariable=controller.sv_img_norm_max, width = 5)
		en_img_norm_max.grid(row=1, column=2, sticky="E", pady=3)

		lb_wm_spread= LabelToolTip(lf_lc_inputs, text="White Matter Spread", tool_tip_text=self.controller.desc.lc_wm_spread)
		lb_wm_spread.grid(row=2, column=0, sticky="W", pady=3)

		en_wm_spread = Entry(lf_lc_inputs, textvariable=controller.sv_wm_spread, width = 5)
		en_wm_spread.grid(row=2, column=2, sticky="E", pady=3)

	def onShowFrame(self, event):
		super(LesionCorrInputPage, self).onShowFrame(event)
		if not self.controller.b_wm_correction.get():
			super(LesionCorrInputPage, self).moveToNextPage(is_parent=False)
		else:
			self.silentMode()

	def setFrameTitle(self):
		self.title.set('Lesion Correction')

	def moveToNextPage(self):
		img_norm_min = self.isValidInteger(self.controller.sv_img_norm_min.get().strip())
		img_norm_max = self.isValidInteger(self.controller.sv_img_norm_max.get().strip())
		if self.controller.b_wm_segmentation_lc.get() and not self.isValidPath(self.controller.sv_wm_seg_root.get().strip()):
			self.setRequiredInputError('Provide a valid path to the White Matter Segmentation Dir')
			return
		if not img_norm_min and type(img_norm_min) == bool or img_norm_min < 0:
			self.setRequiredInputError('Image Norm Min must be a number greater than or equal to 0')
			return
		if not img_norm_max or img_norm_max > 255:
			self.setRequiredInputError('Image Norm Max must be a number less than or equal to255')
			return
		if not self.isValidNumberOrInteger(self.controller.sv_wm_spread.get().strip()):
			self.setRequiredInputError('Provide valid input for White Matter Spread')
			return
		else:
			super(LesionCorrInputPage, self).moveToNextPage()
