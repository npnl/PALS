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

class LesionCorrInputPage(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)

		lb_main = Label(self, text="Please indicate if you have already performed the following.", font='Helvetica 14 bold')
		lb_main.grid(row=self.starting_row, column=0, columnspan=3, sticky='W')
		lb_main2 = Label(self, text="PALS will run FSL brain extraction (BET) and white matter segmentation (FAST) if they have not already been performed. \n", font='Helvetica 14')
		lb_main2.grid(row=self.starting_row+1, column=0, columnspan=3, sticky='W')

		lf_brain_ext = tk.LabelFrame(self, text='Brain Extraction', padx=15, font='Helvetica 14 bold')
		lf_brain_ext.grid(row=self.starting_row+3, column=0, columnspan=3, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
		lf_brain_ext.grid_rowconfigure(0, weight=1)
		lf_brain_ext.grid_columnconfigure(3, weight=1)


		lb_brain_extraction = LabelToolTip(lf_brain_ext, text="Has brain extraction already been performed on all subjects?", tool_tip_text=self.controller.desc.brain_ext)
		lb_brain_extraction.grid(row=0, column=1, columnspan=2, sticky="W", pady=3)

		lb_bet_identifier = LabelToolTip(lf_brain_ext, text="Skull-stripped brain identifier", tool_tip_text=self.controller.desc.bet_identifier)
		lb_bet_identifier.grid(row=1, column=1, sticky="W", pady=(3, 20))

		en_bet_identifier = Entry(lf_brain_ext, textvariable=controller.sv_bet_id, width = 20)
		en_bet_identifier.config(state='disabled')
		en_bet_identifier.grid(row=1, column=2, sticky="W", pady=(3, 20))

		chk_brain_extraction = tk.Checkbutton(lf_brain_ext, variable=controller.b_brain_extraction, command=lambda : self.setEntryState(en_bet_identifier, self.controller.b_brain_extraction))
		chk_brain_extraction.grid(row=0, column=0, sticky='W', pady=3)

		lf_wm_seg = tk.LabelFrame(self, text='White Matter Segmentation', padx=15, font='Helvetica 14 bold')
		lf_wm_seg.grid(row=self.starting_row+4, column=0, columnspan=3, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
		lf_wm_seg.grid_rowconfigure(0, weight=1)
		lf_wm_seg.grid_columnconfigure(3, weight=1)

		lb_wm_seg = LabelToolTip(lf_wm_seg, text="Has white matter segmentation already been performed on all subjects?", tool_tip_text=self.controller.desc.wm_seg)
		lb_wm_seg.grid(row=0, column=1, columnspan=2, sticky="W", pady=3)

		lb_wm_id = LabelToolTip(lf_wm_seg, text="White watter mask identifier", tool_tip_text=self.controller.desc.wm_identifier)
		lb_wm_id.grid(row=1, column=1, sticky="W", pady=(3, 20))

		en_wm_id = Entry(lf_wm_seg, textvariable=controller.sv_wm_id, width = 20)
		en_wm_id.config(state='disabled')
		en_wm_id.grid(row=1, column=2, sticky="W", pady=(3, 20))

		chk_wm_seg = tk.Checkbutton(lf_wm_seg, variable=controller.b_wm_segmentation, command=lambda : self.setEntryState(en_wm_id, self.controller.b_wm_segmentation))
		chk_wm_seg.grid(row=0, column=0, sticky='W', pady=3)

		lb_percent = LabelToolTip(self, text="Indicate the percentage of T1 image intensity values you want to remove from your lesion mask (0-100).", tool_tip_text=self.controller.desc.percent)
		lb_percent.grid(row=self.starting_row+5, column=0, sticky="W", pady=(10, 20))

		en_percent = Entry(self, textvariable=controller.sv_percent, width = 5)
		en_percent.grid(row=self.starting_row+5, column=2, sticky="E", pady=(10, 20))

		

	def onShowFrame(self, event):
		super(LesionCorrInputPage, self).onShowFrame(event)
		if not self.controller.b_wm_correction.get():
			super(LesionCorrInputPage, self).moveToNextPage(is_parent=False)

	def setFrameTitle(self):
		self.title.set('Lesion Correction')

	def moveToNextPage(self):

		if self.controller.b_brain_extraction.get() and len(self.controller.sv_bet_id.get().strip()) == 0:
			self.setRequiredInputError('Provide the skull-stripped brain identifier.')
			return
		if self.controller.b_wm_segmentation.get() and len(self.controller.sv_wm_id.get().strip()) == 0:
			self.setRequiredInputError('Provide the white matter mask identifier.')
			return
		try:
			val = float(self.controller.sv_percent.get().strip())
			if val > 100 or val < 0:
				raise ValueError("Percent is not valid.")
			self.controller.percent_intensity = val
		except Exception as e:
			self.setRequiredInputError('Percent must be a valid number between 0-100.')
			return
		else:
			super(LesionCorrInputPage, self).moveToNextPage()
