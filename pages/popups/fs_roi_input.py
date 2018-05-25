try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

from ..components import CheckboxList
from ..stores import NameVarStore

class FSROIInputPopup(Toplevel, object):
	def __init__(self, controller):
		Toplevel.__init__(self, controller, padx=25, pady=25)

		self.user_agreed = controller.user_agreed

		Label(self, text='Select all that apply', font=("Helvetica", 23, 'bold')).grid(row=0, columnspan=100, pady=(0, 20), sticky=W+E+N+S)

		lb_option = Label(self, text='Each subject directory contains an aparc+aseg.mgz and T1.mgz file')
		lb_option.grid(row=1, column=0, sticky='w', pady=3)

		chk_option = Checkbutton(self, variable=self.user_agreed)
		chk_option.grid(row=1, column=1, sticky='e', pady=3)

		option_heading = 'FreeSurfer Cortical Regions of Interest'
		options_freesurfer = [ NameVarStore(controller, 'Label_%d'%x) for x in range(15)]
		ch_list_freesurfer = CheckboxList(self, controller, option_heading, controller.freesurfer_cortical_roi, row=1, column=0, user_agreed=self.user_agreed)

		option_heading = 'FreeSurfer Sub-Cortical Regions of Interest'
		options_freesurfer_sub = [ NameVarStore(controller, 'Label_%d'%x) for x in range(15)]
		ch_list_freesurfer_sub = CheckboxList(self, controller, option_heading, controller.freesurfer_subcortical_roi, row=1, column=1, user_agreed=self.user_agreed)

		btn_ok = Button(self, text='OK', command=self.cleanup)
		btn_ok.grid(row=300, column=1, sticky='e')



	def cleanup(self):
		self.destroy()
