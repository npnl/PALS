try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

from base_input import BaseInputPage
from popups import DefaultROIInputPopup
from popups import OwnROIInputPopup
from popups import FSROIInputPopup

class LesionLoadCalculationInputPage(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)

		self.chk_default_rois = None


		lf_brain_ext = tk.LabelFrame(self, text='Brain Extraction', padx=15, font='Helvetica 14 bold')
		lf_brain_ext.grid(row=self.starting_row+1, column=0, columnspan=100, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
		lf_brain_ext.grid_rowconfigure(0, weight=1)
		lf_brain_ext.grid_columnconfigure(0, weight=1)


		lb_brain_extraction = Label(lf_brain_ext, text="Have you performed brain extraction") #.grid(row=self.starting_row+2, sticky=W)
		lb_brain_extraction.grid(row=0, column=0, columnspan=40, sticky="W", pady=3)

		lb_bet_identifier = Label(lf_brain_ext, text="BET Identifier") #.grid(row=self.starting_row+2, sticky=W)
		lb_bet_identifier.grid(row=1, column=0, columnspan=40, sticky="W", pady=(3, 20))

		en_bet_identifier = Entry(lf_brain_ext, textvariable=controller.sv_bet_id, width = 20)
		en_bet_identifier.config(state='disabled')
		en_bet_identifier.grid(row=1, column=41, columnspan=50, sticky="W", pady=(3, 20))
		
		chk_brain_extraction = tk.Checkbutton(lf_brain_ext, variable=controller.b_brain_extraction, command=lambda : self.setEntryState(en_bet_identifier, self.controller.b_brain_extraction))
		chk_brain_extraction.grid(row=0, column=41, sticky='W', pady=3)


		lf_lesion_load = tk.LabelFrame(self, text='Calculate Lesion Load (Check all that apply)', padx=15, font='Helvetica 14 bold')
		lf_lesion_load.grid(row=self.starting_row+2, column=0, columnspan=100, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
		lf_lesion_load.grid_rowconfigure(0, weight=1)
		lf_lesion_load.grid_columnconfigure(0, weight=1)


		lb_default_rois = Label(lf_lesion_load, text="Default regions of interest") #.grid(row=self.starting_row+2, sticky=W)
		lb_default_rois.grid(row=0, column=0, columnspan=40, sticky="W", pady=3)

		self.chk_default_rois = tk.Checkbutton(lf_lesion_load, variable=controller.b_default_rois, command=lambda: self.showDefaultROIPopup())
		self.chk_default_rois.grid(row=0, column=41, sticky='W', pady=3)

		lb_subject_specific= Label(lf_lesion_load, text="Use subject specific Freesurfer segmentation") #.grid(row=self.starting_row+2, sticky=W)
		lb_subject_specific.grid(row=1, column=0, columnspan=40, sticky="W", pady=3)

		chk_subject_specific = tk.Checkbutton(lf_lesion_load, variable=controller.b_freesurfer_rois, command=lambda: self.freesurferROIPopup())
		chk_subject_specific.grid(row=1, column=41, sticky='W', pady=3)

		lb_own_rois= Label(lf_lesion_load, text="Use my own ROIs") #.grid(row=self.starting_row+2, sticky=W)
		lb_own_rois.grid(row=2, column=0, columnspan=40, sticky="W", pady=(3, 20))

		chk_own_rois = tk.Checkbutton(lf_lesion_load, variable=controller.b_own_rois, command=lambda: self.showOwnROIPopup())
		chk_own_rois.grid(row=2, column=41, sticky='W', pady=(3, 20))


	def setFrameTitle(self):
		self.title.set('Lesion Load Calculation')


	def moveToNextPage(self):
		if True:
			super(LesionLoadCalculationInputPage, self).moveToNextPage()
		else:
			self.setRequiredInputError('Select atleast one operation')

	def checkIfAtleastOneSelected(self, options_list):
		for option in options_list:
			if option.get():
				return True
		return False

	def updateCheckBoxState(self, chk_box_var, options_list):
		chk_box_var.set(self.checkIfAtleastOneSelected(options_list))

	def showDefaultROIPopup(self):
		if self.controller.b_default_rois.get():
			roi_popup = DefaultROIInputPopup(self.controller)
			roi_popup.grab_set()
			self.chk_default_rois["state"] = "disabled" 
			self.controller.wait_window(roi_popup)
			self.chk_default_rois["state"] = "normal"
			roi_popup.grab_release()
			self.updateCheckBoxState(self.controller.b_default_rois,\
										self.controller.default_corticospinal_tract_roi\
										+ self.controller.default_freesurfer_cortical_roi\
										+ self.controller.default_freesurfer_subcortical_roi)

	def showOwnROIPopup(self):
		if self.controller.b_own_rois.get():
			roi_popup = OwnROIInputPopup(self.controller)
			roi_popup.grab_set()
			self.chk_default_rois["state"] = "disabled" 
			self.controller.wait_window(roi_popup)
			self.chk_default_rois["state"] = "normal"
			roi_popup.grab_release()
			self.updateCheckBoxState(self.controller.b_own_rois,\
										self.controller.user_rois)

	def freesurferROIPopup(self):
		if self.controller.b_freesurfer_rois.get():
			roi_popup = FSROIInputPopup(self.controller)
			roi_popup.grab_set()
			self.chk_default_rois["state"] = "disabled" 
			self.controller.wait_window(roi_popup)
			self.chk_default_rois["state"] = "normal"
			roi_popup.grab_release()
			self.updateCheckBoxState(self.controller.b_freesurfer_rois,\
										self.controller.freesurfer_cortical_roi\
										+ self.controller.freesurfer_subcortical_roi)

