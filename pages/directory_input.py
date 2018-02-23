try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

import tkFileDialog
import os

from utils.paths import isValidPath

class DirectoryInputPage(tk.Frame):
	def __init__(self, parent, controller, frame_number):
		tk.Frame.__init__(self, parent)

		self.status = StringVar(self)
		self.frame_number = frame_number

		Label(self, text="1. Input Directory").grid(row=0, sticky=W)
		en_input_dir = Entry(self, textvariable=controller.sv_input_dir)
		en_input_dir.grid(row=0, column=1)

		Label(self, text="2. Output Directory").grid(row=1, sticky=W)
		en_output_dir = Entry(self, textvariable=controller.sv_output_dir)
		en_output_dir.grid(row=1, column=1)

		Label(self, text="3. Is your data(T1 and Lesion masks) in registered to stereotaxic space ?").grid(row=2, padx=(0, 40),sticky=W)
		chk_run_normalize = tk.Checkbutton(self, variable=controller.run_normalize_status)
		chk_run_normalize.grid(row=2, column=1, sticky=W)

		Label(self, text="4. Image Identifier/Wildcard").grid(row=3, sticky=W)
		en_anatomical_id = Entry(self, textvariable=controller.sv_anatomical_id)
		en_anatomical_id.grid(row=3, column=1)

		Label(self, text="5. Lesion Mask Identifier/Wildcard").grid(row=4, sticky=W)
		en_lesion_mask = Entry(self, textvariable=controller.sv_lesion_mask)
		en_lesion_mask.grid(row=4, column=1)


		Label(self, text="", textvariable=self.status, fg="red").grid(row=5, padx=2)


		button1 = tk.Button(self, text='Select', command=lambda : self.chooseDir(self, controller, controller.sv_input_dir))
		button1.grid(row=0, column=2)

		button2 = tk.Button(self, text='Select', command=lambda : self.chooseDir(self, controller, controller.sv_output_dir))
		button2.grid(row=1, column=2)

		btn_next = tk.Button(self, text='Next', command=lambda : self.moveToNextPage(controller))
		btn_next.grid(row=5, column=1, padx=2)

		print_btn = tk.Button(self, text='Print values', command=lambda : self.checkValues(controller))
		print_btn.grid(row=6, column=1, padx=2)

	def moveToNextPage(self, controller):
		input_dir = controller.sv_input_dir.get()
		output_dir = controller.sv_output_dir.get()
		anatomical_id = controller.sv_anatomical_id.get()
		lesion_mask = controller.sv_lesion_mask.get()
		if not isValidPath(input_dir.strip())\
			 or not isValidPath(output_dir.strip())\
			 or not anatomical_id.strip() or not lesion_mask.strip():
			self.status.set("Please provide correct input in all the above fields")
		else:
			controller.show_frame(self.frame_number + 1)
			self.status.set('')

	def chooseDir(self, parent, controller, place_holder):
		current_dir = os.getcwd()
		parent.update()
		chosen_dir =  tkFileDialog.askdirectory(parent=self, initialdir = current_dir, title='Select the location of your input directory')
		place_holder.set(chosen_dir)


	def checkValues(self, controller):
		print controller.sv_input_dir.get()
		print controller.sv_output_dir.get()
		print controller.run_normalize_status.get()