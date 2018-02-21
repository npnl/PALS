try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

import tkFileDialog
import os


class DirectoryInputPage(tk.Frame):
	def __init__(self, parent, controller, frame_number):
		tk.Frame.__init__(self, parent)

		self.status = StringVar(self)
		self.frame_number = frame_number

		Label(self, text="Input Directory").grid(row=0, sticky=W)
		Label(self, text="Output Directory").grid(row=1, sticky=W)
		Label(self, text="Image Identifier/Wildcard").grid(row=2, sticky=W)
		Label(self, text="Lesion Mask Identifier/Wildcard").grid(row=3, sticky=W)
		Label(self, text="", textvariable=self.status, fg="red").grid(row=4, padx=2)

		en_input_dir = Entry(self, textvariable=controller.sv_input_dir)
		en_output_dir = Entry(self, textvariable=controller.sv_output_dir)
		en_image_identi = Entry(self, textvariable=controller.sv_image_iden)
		en_lesion_mask_identi = Entry(self, textvariable=controller.sv_lesion_mask_identi)

		en_input_dir.grid(row=0, column=1)
		en_output_dir.grid(row=1, column=1)
		en_image_identi.grid(row=2, column=1)
		en_lesion_mask_identi.grid(row=3, column=1)

		button1 = tk.Button(self, text='Select', command=lambda : self.chooseDir(self, controller, controller.sv_input_dir))

		button1.grid(row=0, column=2)

		button2 = tk.Button(self, text='Select', command=lambda : self.chooseDir(self, controller, controller.sv_output_dir))
		button2.grid(row=1, column=2)

		btn_next = tk.Button(self, text='Next', command=lambda : self.moveToNextPage(controller))
		btn_next.grid(row=4, column=1, padx=2)

	def moveToNextPage(self, controller):
		input_dir = controller.sv_input_dir.get()
		if not input_dir.strip():
			self.status.set("Please select an input dir")
		else:
			controller.show_frame(self.frame_number + 1)

	def chooseDir(self, parent, controller, place_holder):
		current_dir = os.getcwd()
		parent.update()
		chosen_dir =  tkFileDialog.askdirectory(parent=self, initialdir = current_dir, title='Select the location of your input directory')
		place_holder.set(chosen_dir)

	def checkValues(self, controller):
		print controller.sv_input_dir.get()
		print controller.sv_output_dir.get()