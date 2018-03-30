try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

from ..components import CheckboxList
from ..stores import NameVarStore

class DefaultROIInputPopup(Toplevel, object):
	def __init__(self, controller):
		Toplevel.__init__(self, controller, padx=25, pady=25)

		Label(self, text='Select all that apply', font=("Helvetica", 23, 'bold')).grid(row=0, columnspan=100, pady=(0, 20), sticky=W+E+N+S)

		option_heading= 'Harvard-Oxford Corticospinal Tract'
		ch_list_harvard = CheckboxList(self, controller, option_heading, controller.corticospinal_tract_roi, row=1, column=0)

		option_heading= 'FreeSurfer Cortical Regions of Interest'
		options_freesurfer = [ NameVarStore(controller, 'Label_%d'%x) for x in range(15)]
		ch_list_freesurfer = CheckboxList(self, controller, option_heading, controller.freesurfer_cortical_roi, row=1, column=1)

		option_heading= 'FreeSurfer Sub-Cortical Regions of Interest'
		options_freesurfer_sub = [ NameVarStore(controller, 'Label_%d'%x) for x in range(15)]
		ch_list_freesurfer_sub = CheckboxList(self, controller, option_heading, controller.freesurfer_subcortical_roi, row=2, column=0, columnspan=2)


		btn_ok = Button(self, text='Ok', command=self.cleanup)
		btn_ok.grid(row=300, column=1, sticky='e')

	def cleanup(self):
		self.destroy()

