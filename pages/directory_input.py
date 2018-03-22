try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

import tkFileDialog
import os

from utils.paths import isValidPath
from base_input import BaseInputPage

class DirectoryInputPage(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)

		Label(self, text="1. Input Directory").grid(row=1, sticky=W)

		button1 = tk.Button(self, text='Select', command=lambda : self.chooseDir(self, controller, controller.sv_input_dir))
		button1.grid(row=1, column=2)

		en_input_dir = Entry(self, textvariable=controller.sv_input_dir)
		en_input_dir.grid(row=1, column=1)

		
		Label(self, text="2. Output Directory").grid(row=2, sticky=W)
		
		button2 = tk.Button(self, text='Select', command=lambda : self.chooseDir(self, controller, controller.sv_output_dir))
		button2.grid(row=2, column=2)

		en_output_dir = Entry(self, textvariable=controller.sv_output_dir)
		en_output_dir.grid(row=2, column=1)

	def setFrameTitle(self):
		self.title.set('Provide Input and Output Directories')

	def moveToNextPage(self):
		input_dir = self.controller.sv_input_dir.get()
		output_dir = self.controller.sv_output_dir.get()
		if not isValidPath(input_dir.strip()) or not isValidPath(output_dir.strip()):
			self.setRequiredInputError()
		else:
			super(DirectoryInputPage, self).moveToNextPage()

	def chooseDir(self, parent, controller, place_holder):
		current_dir = os.getcwd()
		parent.update()
		chosen_dir =  tkFileDialog.askdirectory(parent=self, initialdir = current_dir, title='Select the location of your input directory')
		place_holder.set(chosen_dir)


	def checkValues(self, controller):
		print controller.sv_input_dir.get()
		print controller.sv_output_dir.get()
		print controller.run_normalize_status.get()