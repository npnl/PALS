try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

from ..components import InputFieldList
from ..stores import NameVarStore

from utils.paths import isValidPath

class OwnROIInputPopup(Toplevel, object):
	def __init__(self, controller):
		Toplevel.__init__(self, controller, padx=25, pady=25)
		# self.geometry("640x400")
		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)

		self.inputs = []
		self.controller = controller

		Label(self, text='Select all that apply', font=("Helvetica", 23, 'bold')).grid(row=0, columnspan=100, pady=(0, 20), sticky=W+E+N+S)

		option_heading= 'Harvard-Oxford Corticospinal Tract'
		ch_list_harvard = InputFieldList(self, controller, option_heading, self.inputs, row=1, column=0)

		btn_ok = Button(self, text='Ok', command=self.cleanup)
		btn_ok.grid(row=300, column=0, sticky='e')

	def cleanup(self):
		for sv in self.inputs:
			if not isValidPath(sv.get().strip()):
				print "Not a valid path"
				return
			else:
				print "Yes valid path"

		self.controller.user_rois = [NameVarStore(self.controller, index, default_value=sv.get().strip()) for index, sv in enumerate(self.inputs)]
		self.destroy()

