try:
	import Tkinter as tk
	from Tkinter import *
	import tkFileDialog
except ImportError:
	import tkinter as tk
	from tkinter import *
	from tkinter import filedialog as tkFileDialog

import os
from ..components import InputFieldList
from ..components import EntryWithPlaceholder
from ..stores import NameVarStore
from ..components import LabelToolTip
from ..components import ButtonToolTip

from utils import isValidPath

class OwnROIInputPopup(Toplevel, object):
	def __init__(self, controller):
		Toplevel.__init__(self, controller, padx=25, pady=25)
		# self.geometry("640x400")
		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)

		self.inputs = []
		self.status = StringVar(self)
		self.controller = controller

		Label(self, text='Import ROIs', font=("Helvetica", 23, 'bold')).grid(row=0, columnspan=100, pady=(0, 20), sticky=W+E+N+S)

		lb_select_dir = LabelToolTip(self, text="Indicate the path to the template brain for your ROIs.", font=('Helvetica', 13, 'bold'), tool_tip_text=self.controller.desc.select_dir)
		lb_select_dir.grid(row=1, column=0, columnspan=100, sticky='W')

		en_select_dir = EntryWithPlaceholder(self, placeholder="Path to standard brain template (Required field)", textvariable = self.controller.sv_user_brain_template, width = 50)
		en_select_dir.grid(row=2, column=0, sticky="W", padx=10, pady=3)

		button = ButtonToolTip(self, text='Browse', command=lambda : self.chooseDir(self, self.controller, self.controller.sv_user_brain_template, 'Standard brain template', en_select_dir), tool_tip_text=self.controller.desc.select_dir)
		button.grid(row=2, column=0, sticky="E", padx=5, pady=3)

		option_heading= 'Regions of Interest'
		ch_list_harvard = InputFieldList(self, self.controller, option_heading, self.inputs, row=3, column=0)

		Label(self, text='', textvariable=self.status, fg="red").grid(row=299, column=0, columnspan=100, sticky='nwes',)

		btn_ok = Button(self, text='OK', command=self.cleanup)
		btn_ok.grid(row=300, column=0, sticky='e')

	def cleanup(self):
		if not isValidPath(self.controller.sv_user_brain_template.get()):
			self.status.set("A valid brain template path is required.")
			return

		for sv in self.inputs:
			if not isValidPath(sv.get().strip()):
				self.status.set("ROI path is invalid : " + sv.get())
				return

		self.controller.user_rois = [NameVarStore(self.controller, index, default_value=sv.get().strip()) for index, sv in enumerate(self.inputs)]
		self.destroy()

	def chooseDir(self, parent, controller, place_holder, message, entry):
		current_dir = os.getcwd()
		parent.update()
		chosen_file =  tkFileDialog.askopenfilename(parent=self, initialdir = current_dir, title='Indicate the location of ' + message)
		place_holder.set(chosen_file)
		entry['fg'] = entry.default_fg_color
