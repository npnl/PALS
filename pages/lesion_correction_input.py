try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

import tkFileDialog
import os

from utils import isValidPath
from base_input import *

class LesionCorrInputPage(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)

		lb_main = Label(self, text="Please indicate if you have already performed the following.", font='Helvetica 14 bold')
		lb_main.grid(row=self.starting_row, column=0, columnspan=100, sticky='W')
		lb_main2 = Label(self, text="PALS will run FSL brain extraction (BET) and white matter segmentation (FAST) if they have not already been performed. \n", font='Helvetica 14')
		lb_main2.grid(row=self.starting_row+1, column=0, columnspan=100, sticky='W')

		lf_brain_ext = tk.LabelFrame(self, text='Brain Extraction', padx=15, font='Helvetica 14 bold')
		lf_brain_ext.grid(row=self.starting_row+3, column=0, columnspan=100, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
		lf_brain_ext.grid_rowconfigure(0, weight=1)
		lf_brain_ext.grid_columnconfigure(0, weight=1)


		lb_brain_extraction = Label(lf_brain_ext, text="Has brain extraction already been performed on all subjects?") #.grid(row=self.starting_row+2, sticky=W)
		lb_brain_extraction.grid(row=0, column=0, columnspan=40, sticky="W", pady=3)
		createToolTip(lb_brain_extraction, '')

		lb_bet_identifier = Label(lf_brain_ext, text="Skull-stripped brain identifier") #.grid(row=self.starting_row+2, sticky=W)
		lb_bet_identifier.grid(row=1, column=0, columnspan=40, sticky="W", pady=(3, 20))
		createToolTip(lb_bet_identifier, '')

		en_bet_identifier = Entry(lf_brain_ext, textvariable=controller.sv_bet_id, width = 20)
		en_bet_identifier.config(state='disabled')
		en_bet_identifier.grid(row=1, column=41, columnspan=50, sticky="W", pady=(3, 20))
		createToolTip(en_bet_identifier, '')

		chk_brain_extraction = tk.Checkbutton(lf_brain_ext, variable=controller.b_brain_extraction, command=lambda : self.setEntryState(en_bet_identifier, self.controller.b_brain_extraction))
		chk_brain_extraction.grid(row=0, column=41, sticky='W', pady=3)
		createToolTip(chk_brain_extraction, '')

		lf_wm_seg = tk.LabelFrame(self, text='White Matter Segmentation', padx=15, font='Helvetica 14 bold')
		lf_wm_seg.grid(row=self.starting_row+4, column=0, columnspan=100, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
		lf_wm_seg.grid_rowconfigure(0, weight=1)
		lf_wm_seg.grid_columnconfigure(0, weight=1)


		lb_wm_seg = Label(lf_wm_seg, text="Has white matter segmentation already been performed on all subjects?") #.grid(row=self.starting_row+2, sticky=W)
		lb_wm_seg.grid(row=0, column=0, columnspan=40, sticky="W", pady=3)
		createToolTip(lf_wm_seg, '')

		lb_wm_id = Label(lf_wm_seg, text="White watter mask identifier") #.grid(row=self.starting_row+2, sticky=W)
		lb_wm_id.grid(row=1, column=0, columnspan=40, sticky="W", pady=(3, 20))
		createToolTip(lb_wm_id, '')

		en_wm_id = Entry(lf_wm_seg, textvariable=controller.sv_wm_id, width = 20)
		en_wm_id.config(state='disabled')
		en_wm_id.grid(row=1, column=41, columnspan=50, sticky="W", pady=(3, 20))
		createToolTip(en_wm_id, '')

		chk_wm_seg = tk.Checkbutton(lf_wm_seg, variable=controller.b_wm_segmentation, command=lambda : self.setEntryState(en_wm_id, self.controller.b_wm_segmentation))
		chk_wm_seg.grid(row=0, column=41, sticky='W', pady=3)
		createToolTip(chk_wm_seg, '')


		lb_percent = Label(self, text="Indicate the percentage of T1 image intensity values you want to remove from your lesion mask (0-100).") #.grid(row=self.starting_row+2, sticky=W)
		lb_percent.grid(row=self.starting_row+5, column=0, columnspan=60, sticky="W", pady=(10, 20))
		createToolTip(lb_percent, '')

		en_percent = Entry(self, textvariable=controller.sv_percent, width = 5)
		en_percent.grid(row=self.starting_row+5, column=61, columnspan=40, sticky="E", pady=(10, 20))
		createToolTip(en_percent, '')


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
