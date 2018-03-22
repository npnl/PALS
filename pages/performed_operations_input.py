try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

import tkFileDialog
import os

from base_input import BaseInputPage

class PerformedOperationsInputPage(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)

		padding_x = (30, 0)
		padding_y = (0, 15)

		# Label(self, text='', textvariable=self.title, font=("Helvetica", 23)).grid(row=0, columnspan=2, sticky=W+E+N+S)

		Label(self, text="1. Have you performed skull stripping on your anatomical images?").grid(row=1, sticky=W)

		Label(self, text="			Please specify skull stripped brain identifier (e.g., brain)").grid(row=2, sticky=W, pady = padding_y)
		en_bet_id = Entry(self, textvariable=self.controller.sv_bet_id)
		en_bet_id.grid(row=2, column=1, padx = padding_x, pady = padding_y)
		en_bet_id.config(state='disabled')

		chk_bet_status = tk.Checkbutton(self, command=lambda : self.setEntryState(en_bet_id, self.controller.run_bet))
		chk_bet_status.grid(row=1, column=1, sticky=W, padx = padding_x)
		

		Label(self, text="2. Have you performed white matter segmentation on your subjects?").grid(row=3, sticky=W)
		
		Label(self, text="			Please specify identifier for white matter mask (e.g., c1)").grid(row=4, sticky=W, pady = padding_y)
		en_wm_id = Entry(self, textvariable=self.controller.sv_wm_id)
		en_wm_id.grid(row=4, column=1, padx = padding_x, pady = padding_y)
		en_wm_id.config(state='disabled')

		chk_wm_status = tk.Checkbutton(self, command=lambda : self.setEntryState(en_wm_id, self.controller.run_wm))
		chk_wm_status.grid(row=3, column=1, sticky=W, padx = padding_x)

		Label(self, text="3. Is your data(T1 and Lesion masks) in registered to stereotaxic space ?").grid(row=5, pady=padding_y,sticky=W)
		chk_run_normalize = tk.Checkbutton(self, variable=controller.run_normalize_status)
		chk_run_normalize.grid(row=5, column=1, sticky=W, padx = padding_x, pady = padding_y)

		# current_row = 5

		# Label(self, text="", textvariable=self.status, fg="red").grid(row=current_row)

		# btn_prev = tk.Button(self, text='Prev', command=lambda : self.moveToPrevPage())
		# btn_prev.grid(row=current_row+1, column=0)

		# btn_next2 = tk.Button(self, text='Next', command=lambda : self.moveToNextPage())
		# btn_next2.grid(row=current_row+1, column=1)

		# print_btn = tk.Button(self, text='Print values', command=lambda : self.checkValues(controller))
		# print_btn.grid(row=7, column=1, columnspan=2)

	# def onShowFrame(self, event):
	# 	self.setFrameTitle()

	def setFrameTitle(self):
		self.title.set('Operations Already Performed')

	# def setStatusMessage(self, message):
	# 	self.status.set(message)

	def setEntryState(self, entry, flag):
		if entry['state'] == 'disabled':
			entry.config(state='normal')
			flag.set(False)
		else:
			entry.config(state='disabled')
			flag.set(True)

	def moveToNextPage(self):
		if not self.controller.run_bet.get():
			if not self.controller.sv_bet_id.get().strip():
				self.setStatusMessage("Please specify skull stripped brain identifier")
				return
		if not self.controller.run_wm.get():
			if not self.controller.sv_wm_id.get().strip():
				self.setStatusMessage("Please specify identifier for white matter mask")
				return
		super(PerformedOperationsInputPage, self).moveToNextPage()
		# self.controller.show_frame(self.frame_number+1)

	# def moveToPrevPage(self):
	# 	print "Moving to prev page"
	# 	self.controller.show_frame(self.frame_number-1)

	# def checkValues(self, controller):
	# 	print controller.run_bet.get()
	# 	print controller.run_wm.get()


