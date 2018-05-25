try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

from base_input import *
from popups import DefaultROIInputPopup
from popups import OwnROIInputPopup
from popups import FSROIInputPopup

class LesionLoadCalculationInputPage(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)

		self.chk_default_rois = None

		lb_main = Label(self, text="Please indicate the following.", font='Helvetica 14 bold')
		lb_main.grid(row=self.starting_row, column=0, columnspan=100, sticky='W')

		lb_main2 = Label(self, text="PALS will run FSL brain extraction (BET) if it has not already been performed. \n", font='Helvetica 14')
		lb_main2.grid(row=self.starting_row+1, column=0, columnspan=100, sticky='W')

		lf_brain_ext = tk.LabelFrame(self, text='Brain Extraction', padx=15, font='Helvetica 14 bold')
		lf_brain_ext.grid(row=self.starting_row+2, column=0, columnspan=100, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
		lf_brain_ext.grid_rowconfigure(0, weight=1)
		lf_brain_ext.grid_columnconfigure(0, weight=1)


		lb_brain_extraction = Label(lf_brain_ext, text="Has brain extraction already been performed on all subjects?") #.grid(row=self.starting_row+2, sticky=W)
		lb_brain_extraction.grid(row=0, column=0, columnspan=40, sticky="W", pady=3)
		createToolTip(lb_brain_extraction, self.controller.desc.brain_ext)

		lb_bet_identifier = Label(lf_brain_ext, text="Skull-stripped brain identifier") #.grid(row=self.starting_row+2, sticky=W)
		lb_bet_identifier.grid(row=1, column=0, columnspan=40, sticky="W", pady=(3, 20))
		createToolTip(lb_bet_identifier, self.controller.desc.bet_identifier)

		en_bet_identifier = Entry(lf_brain_ext, textvariable=controller.sv_bet_id, width = 20)
		en_bet_identifier.config(state='disabled')
		en_bet_identifier.grid(row=1, column=41, columnspan=50, sticky="W", pady=(3, 20))
		createToolTip(en_bet_identifier, self.controller.desc.bet_identifier)

		chk_brain_extraction = tk.Checkbutton(lf_brain_ext, variable=controller.b_brain_extraction, command=lambda : self.setEntryState(en_bet_identifier, self.controller.b_brain_extraction))
		chk_brain_extraction.grid(row=0, column=41, sticky='W', pady=3)
		createToolTip(chk_brain_extraction, self.controller.desc.brain_ext)

		lf_lesion_load = tk.LabelFrame(self, text='Calculate Lesion Load', padx=15, font='Helvetica 14 bold')
		lf_lesion_load.grid(row=self.starting_row+3, column=0, columnspan=100, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
		lf_lesion_load.grid_rowconfigure(0, weight=1)
		lf_lesion_load.grid_columnconfigure(0, weight=1)

		lb_lesion_load = Label(lf_lesion_load, text="Select all that apply.", font='Helvetica 13 bold')
		lb_lesion_load.grid(row=0, column=0, columnspan=100, sticky='W')

		lb_default_rois = Label(lf_lesion_load, text="Select regions of interest included in PALS") #.grid(row=self.starting_row+2, sticky=W)
		lb_default_rois.grid(row=1, column=0, columnspan=40, sticky="W", pady=3)
		createToolTip(lb_default_rois, self.controller.desc.default_rois)

		## why is just this chk button self.check? why not just chk?
		self.chk_default_rois = tk.Checkbutton(lf_lesion_load, variable=controller.b_default_rois, command=lambda: self.showDefaultROIPopup())
		self.chk_default_rois.grid(row=1, column=41, sticky='W', pady=3)
		createToolTip(self.chk_default_rois, self.controller.desc.default_rois)

		lb_own_rois= Label(lf_lesion_load, text="Import my own regions of interest") #.grid(row=self.starting_row+2, sticky=W)
		lb_own_rois.grid(row=2, column=0, columnspan=40, sticky="W", pady=3)
		createToolTip(lb_own_rois, self.controller.desc.own_rois)

		chk_own_rois = tk.Checkbutton(lf_lesion_load, variable=controller.b_own_rois, command=lambda: self.showOwnROIPopup())
		chk_own_rois.grid(row=2, column=41, sticky='W', pady=3)
		createToolTip(chk_own_rois, self.controller.desc.own_rois)

		lb_subject_specific= Label(lf_lesion_load, text="Use subject-specific FreeSurfer segmentations") #.grid(row=self.starting_row+2, sticky=W)
		lb_subject_specific.grid(row=3, column=0, columnspan=40, sticky="W", pady=(3,20))
		createToolTip(lb_subject_specific, self.controller.desc.subject_specific)

		chk_subject_specific = tk.Checkbutton(lf_lesion_load, variable=controller.b_freesurfer_rois, command=lambda: self.freesurferROIPopup())
		chk_subject_specific.grid(row=3, column=41, sticky='W', pady=(3,20))
		createToolTip(chk_subject_specific, self.controller.desc.subject_specific)

	def setFrameTitle(self):
		self.title.set('Lesion Load Calculation')


	def moveToNextPage(self):
		if True:
			super(LesionLoadCalculationInputPage, self).moveToNextPage()
		else:
			self.setRequiredInputError('Please select at least one operation')

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
			is_selected = self.checkIfAtleastOneSelected(self.controller.default_corticospinal_tract_roi\
										+ self.controller.default_freesurfer_cortical_roi\
										+ self.controller.default_freesurfer_subcortical_roi)
			is_selected = is_selected or (len(self.controller.default_custom_rois) > 0)

			self.controller.b_default_rois.set(is_selected)

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
