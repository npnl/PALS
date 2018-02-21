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

		self.status = StringVar(self)
		self.frame_number = frame_number

		Label(self, text="1. Have you performed skull stripping on your anatomical images?").grid(row=0, sticky=W)
		Label(self, text="2. Have you performed white matter segmentation on your subjects?").grid(row=1, sticky=W)
		Label(self, text="3. Indicate the percentage of intensity values you would like to have removed from your mask.")\
							.grid(row=2, sticky=W)

		Label(self, text="", textvariable=self.status, fg="red").grid(row=3)

		en_bet_id = Entry(self, textvariable=controller.sv_bet_id)
		en_wm_id = Entry(self, textvariable=controller.sv_wm_id)

		en_bet_id.config(state='disabled')
		en_wm_id.config(state='disabled')

		chk_bwt_status = tk.Checkbutton(self, command=lambda entry=en_bet_id: self.setEntryState(entry))
		chk_wm_status = tk.Checkbutton(self, command=lambda entry=en_wm_id: self.setEntryState(entry))

		chk_bwt_status.grid(row=0, column=1)
		chk_wm_status.grid(row=1, column=1)

		en_bet_id.grid(row=0, column=2)
		en_wm_id.grid(row=1, column=2)


		btn_prev = tk.Button(self, text='Prev', command=lambda : self.moveToPrevPage(controller))
		btn_prev.grid(row=4, column=0)

		btn_next2 = tk.Button(self, text='Next', command=lambda : self.moveToNextPage(controller))
		btn_next2.grid(row=4, column=1)

	def setEntryState(self, entry):
		# entry.set('')
		if entry['state'] == 'disabled':
			entry.config(state='normal')
		else:
			entry.config(state='disabled')

	def moveToNextPage(self, controller):
		print "Moving to next page"
		# input_dir = controller.sv_input_dir.get()
		# if not input_dir.strip():
		# 	self.status.set("Please select an input dir")

	def moveToPrevPage(self, controller):
		print "Moving to prev page"
		controller.show_frame(self.frame_number-1)
		# input_dir = controller.sv_input_dir.get()
		# if not input_dir.strip():
		# 	self.status.set("Please select an input dir")


