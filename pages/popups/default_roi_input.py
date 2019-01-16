try:
	import Tkinter as tk
	from Tkinter import *
	import tkFileDialog
except ImportError:
	import tkinter as tk
	from tkinter import *
	from tkinter import filedialog as tkFileDialog

import os
from ..components import CheckboxList
from ..stores import NameVarStore
from ..components import ButtonToolTip

class DefaultROIInputPopup(Toplevel, object):
	def __init__(self, controller):
		Toplevel.__init__(self, controller, padx=25, pady=25)
		self.controller = controller
		self.selected_count = StringVar()


		Label(self, text='Select any ROI(s)', font=("Helvetica", 23, 'bold')).grid(row=0, columnspan=100, pady=(0, 20), sticky=W+E+N+S)

		option_heading= 'Corticospinal Tracts'
		ch_list_harvard = CheckboxList(self, controller, option_heading, controller.default_corticospinal_tract_roi, row=1, column=0)

		option_heading= 'FreeSurfer Cortical Regions of Interest'
		ch_list_freesurfer = CheckboxList(self, controller, option_heading, controller.default_freesurfer_cortical_roi, row=1, column=1)

		option_heading= 'FreeSurfer Sub-Cortical Regions of Interest'
		ch_list_freesurfer_sub = CheckboxList(self, controller, option_heading, controller.default_freesurfer_subcortical_roi, row=2, column=0, columnspan=2)

		btn_custom = ButtonToolTip(self, text='Select additional ROIs', command=self.selectCustomROIs, tool_tip_text=self.controller.desc.btn_custom)
		btn_custom.grid(row=299, column=0, sticky='w')

		lb_count = Label(self, textvariable=self.selected_count)
		lb_count.grid(row=299, column=1, sticky='e')

		btn_ok = Button(self, text='OK', command=self.cleanup)
		btn_ok.grid(row=300, column=1, sticky='e')

		self.updateSelectCount()

	def cleanup(self):
		self.destroy()

	def selectCustomROIs(self):
		self.controller.default_custom_rois = self.chooseFiles()
		self.updateSelectCount()
		self.controller.logger.debug("Custom ROIs selected : " + str(self.controller.default_custom_rois))

	def updateSelectCount(self):
		self.selected_count.set(str(len(self.controller.default_custom_rois)) + ' additional ROIs selected.')

	def chooseFiles(self):
		current_dir = os.path.join(self.controller.getProjectDirectory(), 'ROIs')
		self.update()
		chosen_files =  tkFileDialog.askopenfilenames(parent=self, initialdir = current_dir, title='Select the location of ROIs')
		chosen_files = self.controller.splitlist(chosen_files)
		return chosen_files
