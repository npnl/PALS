try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

import tkFileDialog
import os, subprocess
import logging
from datetime import datetime

from pages import WelcomePage
from pages import SettingsInput
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

		self.setupLogger()

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
		self.fs_roi_codes = None

		#User ROIs
		self.user_rois = []
		self.user_roi_paths = None
		self.sv_user_brain_template = StringVar(self)
		self.sv_user_brain_template.set('')
		self.user_agreed = BooleanVar(self)
		self.user_agreed.set(False)

		#Settings Page
		self.sv_fsl_binaries_msg = StringVar(self)
		self.sv_fsl_binaries_msg.set('')

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

	def setupLogger(self):
		project_path = os.path.dirname(os.path.realpath(__file__))
		logs_dir = os.path.join(project_path, 'logs')
		if not os.path.exists(logs_dir):
			os.makedirs(logs_dir)
		logging.basicConfig(level=logging.DEBUG,
					format='%(levelname)s %(message)s',
					filename=os.path.join(logs_dir, datetime.now().strftime('logfile_%H_%M_%d_%m_%Y.log')),
					filemode='w')
		console = logging.StreamHandler()
		console.setLevel(logging.INFO)
		formatter = logging.Formatter('%(levelname)-8s %(message)s')
		console.setFormatter(formatter)
		logging.getLogger('').addHandler(console)
		self.logger = logging.getLogger(__name__)

	def show_frame(self, frame_number):
		if frame_number >= len(self.frames) or frame_number < 0:
			return
		frame = self.frames[frame_number]
		frame.event_generate("<<ShowFrame>>")
		frame.tkraise()

	def getApplicationPages(self):
		pages = [WelcomePage, DirectoryInputPage, WhiteMatterInputPage, LesionLoadCalculationInputPage, RunningOperationsPage] 
		if not self.checkFslInstalled():
			pages = [SettingsInput]
		return pages

	def checkFslInstalled(self, path=''):
		commands = ['fslmaths', 'fsleyes', 'mri_convert', 'flirt', 'fslstats', 'fast', 'bet', 'fslswapdim', 'fslreorient2std', 'fslorient', 'gzip']
		flag = True
		msg = ''
		FNULL = open(os.devnull, 'w')
		for cmd in commands:
			cmd_to_exe = 'which ' + cmd
			try:
				exit_code = subprocess.call([cmd_to_exe], shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
				if exit_code != 0:
					raise
			except Exception as e:
				flag = False
				msg += cmd + '\n'
		msg = 'The following binaries location is not set in the path:\n' + msg if len(msg) != 0 else '' 
		self.sv_fsl_binaries_msg.set(msg)
		return flag

if __name__ == '__main__':
	app = MainWindow()
	app.mainloop()
