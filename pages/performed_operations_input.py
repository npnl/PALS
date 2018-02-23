try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

import tkFileDialog
import os


class PerformedOperationsInputPage(tk.Frame):
	def __init__(self, parent, controller, frame_number):
		tk.Frame.__init__(self, parent)

		self.controller = controller

		self.status = StringVar(self)
		self.frame_number = frame_number

		Label(self, text="1. Have you performed skull stripping on your anatomical images?").grid(row=0, sticky=W)

		Label(self, text="			Please specify skull stripped brain identifier (e.g., brain)").grid(row=1, sticky=W)
		en_bet_id = Entry(self, textvariable=self.controller.sv_bet_id)
		en_bet_id.grid(row=1, column=1)
		en_bet_id.config(state='disabled')

		chk_bet_status = tk.Checkbutton(self, command=lambda : self.setEntryState(en_bet_id, self.controller.run_bet))
		chk_bet_status.grid(row=0, column=1, sticky=W)
		

		Label(self, text="2. Have you performed white matter segmentation on your subjects?").grid(row=2, sticky=W)
		
		Label(self, text="			Please specify identifier for white matter mask (e.g., c1)").grid(row=3, sticky=W)
		en_wm_id = Entry(self, textvariable=self.controller.sv_wm_id)
		en_wm_id.grid(row=3, column=1)
		en_wm_id.config(state='disabled')

		chk_wm_status = tk.Checkbutton(self, command=lambda : self.setEntryState(en_wm_id, self.controller.run_wm))
		chk_wm_status.grid(row=2, column=1, sticky=W)

		

		Label(self, text="", textvariable=self.status, fg="red").grid(row=5)

		btn_prev = tk.Button(self, text='Prev', command=lambda : self.moveToPrevPage())
		btn_prev.grid(row=6, column=0)

		btn_next2 = tk.Button(self, text='Next', command=lambda : self.moveToNextPage())
		btn_next2.grid(row=6, column=1)

		print_btn = tk.Button(self, text='Print values', command=lambda : self.checkValues(controller))
		print_btn.grid(row=7, column=1, columnspan=2)

	def setEntryState(self, entry, flag):
		# entry.set('')
		if entry['state'] == 'disabled':
			entry.config(state='normal')
			flag.set(True)
		else:
			entry.config(state='disabled')
			flag.set(False)

	def setStatus(self, message):
		self.status.set(message)

	def moveToNextPage(self):
		if self.controller.run_bet.get():
			if not self.controller.sv_bet_id.get().strip():
				self.setStatus("Please specify skull stripped brain identifier")
				return
		if self.controller.run_wm.get():
			if not self.controller.sv_wm_id.get().strip():
				self.setStatus("Please specify identifier for white matter mask")
				return
		print "Moving to next page"
		self.controller.show_frame(self.frame_number+1)
		# input_dir = controller.sv_input_dir.get()
		# if not input_dir.strip():
		# 	self.status.set("Please select an input dir")

	def moveToPrevPage(self):
		print "Moving to prev page"
		self.controller.show_frame(self.frame_number-1)
		# input_dir = controller.sv_input_dir.get()
		# if not input_dir.strip():
		# 	self.status.set("Please select an input dir")

	def checkValues(self, controller):
		print controller.run_bet.get()
		print controller.run_wm.get()


