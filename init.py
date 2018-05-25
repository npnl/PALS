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
from pages import RunningOperationsPage
from pages import LesionCorrInputPage
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
		self.b_pause_for_qc = BooleanVar(self)

		self.b_radiological_convention.set(False)
		self.b_wm_correction.set(False)
		self.b_ll_calculation.set(False)
		self.b_visual_qc.set(False)
		self.b_pause_for_qc.set(True)

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
		self.default_custom_rois = []
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

		#Running Operations
		self.selected_subjects = StringVar(self)
		self.selected_subjects.set('')

		#Settings Page
		self.sv_fsl_binaries_msg = StringVar(self)
		self.sv_fsl_binaries_msg.set('')

		# for welcome page
		self.desc_rad_reorient = "This module will check that all subject inputs are in the same orientation, flag subjects that have mismatched input orientations, and convert all remaining inputs to radiological convention. This is recommended for all datasets, and especially for multi-site data."

		self.desc_wm_correction = "This module is for manually segmented lesions. This aims to correct for intact white matter voxels that may have been inadvertently included in a manually segmented mask by removing voxels in the lesion mask that are within the intensity range of a white matter mask."

		self.desc_lesion_load = "This module will perform lesion load for several different ROI selections: default ROIs, freesurfer segmentations, and user-input ROIs."

		self.desc_visual_qc = "This module can only be selected if none of the other modules are selected. This will create a visual inspection page with lesion masks overlaid on T1s."

		# for inputs page
		self.desc_input_dir = "Provide the path to your input directory. The input directory should contain separate subject directories, each with at least a T1 anatomical and lesion mask file in nifti format."

		self.desc_output_dir = "Provide the path to your desired output directory."

		self.desc_t1_identifier = "Provide the T1 identifier to your whole-brain anatomical images. Note: this identifier should be unique to the anatomical whole-brain image only. For example, put 'T1' if subject1's T1 file is subj01_T1.nii.gz."

		self.desc_lm_identifier = "Provide the identifier for your lesion mask. For example, put 'Lesion' if subject1's lesion mask files is subj01_Lesion.nii.gz."

		# for lesion correction input page and lesion load input page
		self.desc_brain_ext = "Indicate if you have already performed brain extraction for all subjects. Each subject directory should contain a skull-stripped brain with your skull-stripped brain identifier. If not, PALS will perform brain extraction for every subject using FSL BET. NOTE: Skull-stripped brain files must be present in each subject directory. If any subject is missing a brain file, PALS will run brain extraction on all subjects."

		self.desc_bet_identifier = "If you have performed brain extraction for all subjects, indicate the unique identifier for skull-stripped brain files. For example, 'Brain' if subject1's brain file is subj01_Brain.nii.gz. NOTE: Skull-stripped brain files must be present in each subject directory. If any subject is missing a brain file, PALS will run brain extraction on all subjects."

		self.desc_percent = "Please provide a value between 0-100. This will be used to calculate the total number of voxels to remove above and below the average white matter mask intensity. A value of 0 means only intensity values that are equal to the average white matter intensity will be removed."

		# for lesion load input page only
		self.desc_default_rois = "Select if you would like to calculate lesion load using regions of interest included in PALS. NOTE: all of these template ROIs are in 2mm MNI152 template space."

		self.desc_own_rois = "Select if you would like import your own regions of interest to calculate lesion load. NOTE: these ROIs must all be in the same space."

		self.subject_specific = "Select if you would like to use subject-specific Freesurfer segmentations to calculate lesion load. This operation requires that Freesurfer cortical and subcortical segmentation has already been performed for each subject, and each subject directory must contain an aparc+aseg.mgz and T1.mgz file."

		# for running operations page
		self.desc_lf_subject_file = "This is for QC only. Once a QC page has been generated by PALS, a link to the page will show up. Use the link to visually inspect the outputs and select subjects that do not pass inspection. At this point, you will be able to download a textfile containing the subjects you flagged. If you would like to remove these subjects from analysis, import the downloaded textfile into the space below. If you would like to keep all subjects in the analysis pipeline, click on 'Continue with all subjects'."

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
					format='%(asctime)s %(levelname)s %(message)s',
					filename=os.path.join(logs_dir, datetime.now().strftime('logfile_%Y%m%d_%H_%M.log')),
					filemode='w')
		console = logging.StreamHandler()
		console.setLevel(logging.INFO)
		formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
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
		pages = [WelcomePage, DirectoryInputPage, LesionCorrInputPage, LesionLoadCalculationInputPage, RunningOperationsPage]
		if not self.checkFslInstalled():
			pages = [SettingsInput]
		return pages

	def getProjectDirectory(self):
		return os.path.dirname(os.path.realpath(__file__))

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
		msg = 'The following binaries location are not set in the path:\n' + msg if len(msg) != 0 else ''
		self.sv_fsl_binaries_msg.set(msg)
		return flag

if __name__ == '__main__':
	app = MainWindow()
	app.mainloop()
