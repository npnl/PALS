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

from utils import isValidPath
from base_input import BaseInputPage
from executor import Worker

class WhiteMatterInputPage(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)


		lf_brain_ext = tk.LabelFrame(self, text='Brain Extraction', padx=15, font='Helvetica 14 bold')
		lf_brain_ext.grid(row=self.starting_row+1, column=0, columnspan=100, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
		lf_brain_ext.grid_rowconfigure(0, weight=1)
		lf_brain_ext.grid_columnconfigure(0, weight=1)


		lb_brain_extraction = Label(lf_brain_ext, text="Have you performed skull-stripping?") #.grid(row=self.starting_row+2, sticky=W)
		lb_brain_extraction.grid(row=0, column=0, columnspan=40, sticky="W", pady=3)

		lb_bet_identifier = Label(lf_brain_ext, text="Skull-stripped brain identifier") #.grid(row=self.starting_row+2, sticky=W)
		lb_bet_identifier.grid(row=1, column=0, columnspan=40, sticky="W", pady=(3, 20))

		en_bet_identifier = Entry(lf_brain_ext, textvariable=controller.sv_bet_id, width = 20)
		en_bet_identifier.config(state='disabled')
		en_bet_identifier.grid(row=1, column=41, columnspan=50, sticky="W", pady=(3, 20))

		chk_brain_extraction = tk.Checkbutton(lf_brain_ext, variable=controller.b_brain_extraction, command=lambda : self.setEntryState(en_bet_identifier, self.controller.b_brain_extraction))
		chk_brain_extraction.grid(row=0, column=41, sticky='W', pady=3)


		lf_wm_seg = tk.LabelFrame(self, text='White Matter Segmentation', padx=15, font='Helvetica 14 bold')
		lf_wm_seg.grid(row=self.starting_row+2, column=0, columnspan=100, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
		lf_wm_seg.grid_rowconfigure(0, weight=1)
		lf_wm_seg.grid_columnconfigure(0, weight=1)


		lb_wm_seg = Label(lf_wm_seg, text="Have you performed white matter segmentation?") #.grid(row=self.starting_row+2, sticky=W)
		lb_wm_seg.grid(row=0, column=0, columnspan=40, sticky="W", pady=3)

		lb_wm_id = Label(lf_wm_seg, text="White watter mask identifier") #.grid(row=self.starting_row+2, sticky=W)
		lb_wm_id.grid(row=1, column=0, columnspan=40, sticky="W", pady=(3, 20))

		en_wm_id = Entry(lf_wm_seg, textvariable=controller.sv_wm_id, width = 20)
		en_wm_id.config(state='disabled')
		en_wm_id.grid(row=1, column=41, columnspan=50, sticky="W", pady=(3, 20))

		chk_wm_seg = tk.Checkbutton(lf_wm_seg, variable=controller.b_wm_segmentation, command=lambda : self.setEntryState(en_wm_id, self.controller.b_wm_segmentation))
		chk_wm_seg.grid(row=0, column=41, sticky='W', pady=3)


		lb_percent = Label(self, text="What percent of the total image intensity you would like to remove?") #.grid(row=self.starting_row+2, sticky=W)
		lb_percent.grid(row=self.starting_row+3, column=0, columnspan=60, sticky="W", pady=(10, 20))

		en_percent = Entry(self, textvariable=controller.sv_percent, width = 5)
		en_percent.grid(row=self.starting_row+3, column=61, columnspan=40, sticky="E", pady=(10, 20))


	def setFrameTitle(self):
		self.title.set('White Matter Correction')

	def moveToNextPage(self):

		if self.controller.b_brain_extraction.get() and len(self.controller.sv_bet_id.get().strip()) == 0:
			self.setRequiredInputError('Provide the skull-stripped brain identifier')
			return
		if self.controller.b_wm_segmentation.get() and len(self.controller.sv_wm_id.get().strip()) == 0:
			self.setRequiredInputError('Provide the white matter mask identifier')
			return
		try:
			val = float(self.controller.sv_percent.get().strip())
			if val > 100 or val < 0:
				raise ValueError("Percent is not valid")
			self.controller.percent_intensity = val
		except Exception as e:
			self.setRequiredInputError('Percent must be a valid number between 0-100')
			return
		else:
			super(WhiteMatterInputPage, self).moveToNextPage()

	def executeCommand(self):
		self.worker = Worker()
		self.thread_name = self.worker.execute('python testScript.py', self.output, self)
		print self.thread_name

	def stopCommand(self):
		self.worker.stop(self.thread_name)
