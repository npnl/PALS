try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

import tkFileDialog
import os
import logging

from pages import WelcomePage
from pages import DirectoryInputPage
from pages import PauseOptionsInputPage
from pages import RunningOperationsPage
from pages import WhiteMatterInputPage
from pages import LesionLoadCalculationInputPage
from pages import rois

LARGE_FONT = ("Verdana", 12)


class MainWindow(tk.Tk):
	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)
		self.title("Pipeline for Analyzing Lesions after Stroke")
		# self.geometry("1200x800")

		logging.basicConfig(level=logging.INFO, format='%(levelname)s: '
							'%(message)s')
		self.logger = logging.getLogger(__name__)

		# Text area to show the logs of running operations
		self.display = None
		self.progressbar = None

		#Welcome page
		self.b_radiological_convention = BooleanVar(self)
		self.b_wm_correction = BooleanVar(self)
		self.b_ll_calculation = BooleanVar(self)
		self.b_visual_qc = BooleanVar(self)
		self.b_quality_control = BooleanVar(self)

		self.b_radiological_convention.set(False)
		self.b_wm_correction.set(False)
		self.b_ll_calculation.set(False)
		self.b_visual_qc.set(False)
		self.b_quality_control.set(True)

		#Directory Input Page
		self.sv_input_dir = StringVar(self)
		self.sv_output_dir = StringVar(self)
		self.sv_t1_id = StringVar(self)
		self.sv_lesion_mask_id = StringVar(self)
		self.b_same_anatomical_space = BooleanVar(self)

		self.sv_t1_id.set('')
		self.sv_lesion_mask_id.set('')
		self.b_same_anatomical_space.set(False)

		#White Matter Correction Page
		self.sv_bet_id = StringVar(self)
		self.sv_wm_id = StringVar(self)
		self.sv_percent = StringVar(self)
		self.b_brain_extraction = BooleanVar(self)
		self.b_wm_segmentation = BooleanVar(self)
		self.sv_bet_id.set('')
		self.sv_wm_id.set('')
		self.b_brain_extraction.set(False)
		self.b_wm_segmentation.set(False)
		self.sv_percent.set('5.0')
		self.percent_intensity = 5.0

		#Lesion Load Calculation Page
		self.b_default_rois = BooleanVar(self)
		self.b_freesurfer_rois = BooleanVar(self)
		self.b_own_rois = BooleanVar(self)
		self.b_default_rois.set(False)
		self.b_freesurfer_rois.set(False)
		self.b_own_rois.set(False)

		#Default ROI Popup
		all_rois = rois.getROIs(self)
		self.default_corticospinal_tract_roi = all_rois[0]
		self.default_freesurfer_cortical_roi = all_rois[1]
		self.default_freesurfer_subcortical_roi =  all_rois[2]
		self.default_roi_paths = None

		#FreeSurfer Rois
		all_rois = rois.getROIs(self)
		self.freesurfer_cortical_roi = all_rois[1]
		self.freesurfer_subcortical_roi =  all_rois[2]
		self.fs_roi_paths = None

		#User ROIs
		self.user_rois = []
		self.sv_user_brain_template = StringVar(self)
		self.sv_user_brain_template.set('')
		self.user_agreed = BooleanVar(self)
		self.user_agreed.set(False)

		# this container contains all the pages
		container = tk.Frame(self)
		container.pack(side="top", fill="both", expand=True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)
		self.frames = {}

		frame_number = 0
		for PageType in self.getApplicationPages():
			frame = PageType(container, self, frame_number)
			self.frames[frame_number] = frame
			frame_number += 1
			frame.grid(row=0, column=0, sticky="nsew", padx=25, pady=25)

		self.show_frame(0)

		self.bind_class("Text","<Control-a>", self.selectAll)
		self.bind_class("Text","<Command-v>", self.pasteAll)

	def updateGUI(self, text):
		self.display.insert(END, text + '\n')
		self.display.see(END)
		self.update()

	def selectAll(self, event):
		event.widget.tag_add("sel","1.0","end")

	def pasteAll(self, event):
		clipboard = self.clipboard_get()
		clipboard = clipboard.replace("\n", "\\n")

		try:
			start = event.widget.index("sel.first")
			end = event.widget.index("sel.last")
			event.widget.delete(start, end)
		except TclError as e:
			pass

		event.widget.insert("insert", clipboard)

	def show_frame(self, frame_number):
		if frame_number >= len(self.frames) or frame_number < 0:
			return
		frame = self.frames[frame_number]
		frame.event_generate("<<ShowFrame>>")
		frame.tkraise()

	def getApplicationPages(self):
		pages = [WelcomePage, DirectoryInputPage, WhiteMatterInputPage, LesionLoadCalculationInputPage, RunningOperationsPage]
		return pages

if __name__ == '__main__':
	app = MainWindow()
	app.mainloop()
