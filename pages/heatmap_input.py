try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

from .base_input import *


class HeatmapInputPage(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)

		lf_heatmap = tk.LabelFrame(self, text='Heatmap Inputs', font='Helvetica 14 bold', padx=15)
		lf_heatmap.grid(row=self.starting_row+1, column=0, columnspan=3, sticky='nsew', ipadx=10, ipady=10)
		lf_heatmap.grid_rowconfigure(0, weight=1)
		lf_heatmap.grid_columnconfigure(3, weight=1)

		lb_heatmap_transp = LabelToolTip(lf_heatmap, text="1. Transparency", tool_tip_text=self.controller.desc.output_dir)
		lb_heatmap_transp.grid(row=0, column=0, sticky="W", pady=3)

		en_heatmap_transp = Entry(lf_heatmap, textvariable=controller.sv_heatmap_transparency, width = 46)
		en_heatmap_transp.grid(row=0, column=1, sticky="W", pady=3)

		lb_heatmap_ref = LabelToolTip(lf_heatmap, text="2. Reference", tool_tip_text=self.controller.desc.t1_identifier)
		lb_heatmap_ref.grid(row=1, column=0, sticky="W", pady=3)

		en_heatmap_ref = Entry(lf_heatmap, textvariable=controller.sv_heatmap_reference, width = 46)
		en_heatmap_ref.grid(row=1, column=1, sticky="W", pady=3)

		button_heatmap_ref = tk.Button(lf_heatmap, text='Browse', command=lambda : self.chooseFile(self, controller, controller.sv_heatmap_reference, 'Registration Reference'))
		button_heatmap_ref.grid(row=1, column=2, sticky='W', padx=5, pady=3)

		wrapper = Frame(lf_heatmap)
		wrapper.grid(row=3, column=0, sticky="WE", columnspan=3, pady=(3, 20))
		wrapper.grid_rowconfigure(0, weight=1)
		wrapper.grid_columnconfigure(2, weight=1)

	def onShowFrame(self, event):
		super(HeatmapInputPage, self).onShowFrame(event)
		if not self.controller.b_lesion_heatmap.get():
			super(HeatmapInputPage, self).moveToNextPage(is_parent=False)
		else:
			self.silentMode()


	def setFrameTitle(self):
		self.title.set('Heatmap:')

	def moveToNextPage(self):
		if self.controller.b_lesion_heatmap.get() \
			and (not self.isValidNumberOrInteger(self.controller.sv_heatmap_transparency.get().strip()) \
			or not self.isValidPath(self.controller.sv_heatmap_reference.get().strip())):
			self.setRequiredInputError('Provide valid inputs for leasion heatmap generation')
			return
		super(HeatmapInputPage, self).moveToNextPage()

