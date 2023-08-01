try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

from .base_input import *

LESION_ID_EMPTY = 'this_field_is_deliberately_left_like_this'

class DirectoryInputPage(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)

		lf_inputs = tk.LabelFrame(self, text='Inputs', font='Helvetica 14 bold', padx=15)
		lf_inputs.grid(row=self.starting_row+1, column=0, columnspan=3, sticky='nsew', ipadx=10, ipady=10)
		lf_inputs.grid_rowconfigure(0, weight=1)
		lf_inputs.grid_columnconfigure(3, weight=1)

		lb_input = LabelToolTip(lf_inputs, text="1. BIDS Root Directory", tool_tip_text=self.controller.desc.input_dir)
		lb_input.grid(row=0, column=0, sticky="W", pady=3)

		button1 = tk.Button(lf_inputs, text='Browse', command=lambda : self.chooseDir(self, controller, controller.sv_input_dir, 'Input Directory'))
		button1.grid(row=0, column=2, sticky='W', padx=5, pady=3)

		en_input_dir = Entry(lf_inputs, textvariable=controller.sv_input_dir, width = 46)
		en_input_dir.grid(row=0, column=1, sticky="W", pady=3)

		lb_roi_dir = LabelToolTip(lf_inputs, text="2. ROIs Directory", tool_tip_text=self.controller.desc.input_dir)
		lb_roi_dir.grid(row=1, column=0, sticky="W", pady=3)

		button_roi = tk.Button(lf_inputs, text='Browse', command=lambda : self.chooseDir(self, controller, controller.sv_roi_dir, 'ROI Directory'))
		button_roi.grid(row=1, column=2, sticky='W', padx=5, pady=3)

		en_roi_dir = Entry(lf_inputs, textvariable=controller.sv_roi_dir, width = 46)
		en_roi_dir.grid(row=1, column=1, sticky="W", pady=3)

		# lb_output = LabelToolTip(lf_inputs, text="2. Output Directory", tool_tip_text=self.controller.desc.output_dir)
		# lb_output.grid(row=1, column=0, sticky="W", pady=3)

		# button2 = tk.Button(lf_inputs, text='Browse', command=lambda : self.chooseDir(self, controller, controller.sv_output_dir, 'Output Directory'))
		# button2.grid(row=1, column=2, sticky='E', padx=5, pady=3)

		# en_output_dir = Entry(lf_inputs, textvariable=controller.sv_output_dir, width = 46)
		# en_output_dir.grid(row=1, column=1, sticky="W", pady=3)

		lf_t1_identifier = LabelFrame(lf_inputs, text='3. T1 Anatomical Image Identifier')
		lf_t1_identifier.grid(row=2, column=0, columnspan=3, sticky='W', pady=3)
		lf_t1_identifier.grid_rowconfigure(0, weight=0)
		lf_t1_identifier.grid_columnconfigure(3, weight=0)
		lf_t1_identifier.configure(borderwidth=0, relief='flat')

		lb_t1_identifier_desc = LabelToolTip(lf_t1_identifier, text="Desc", tool_tip_text=self.controller.desc.t1_identifier)
		lb_t1_identifier_desc.grid(row=0, column=1, sticky="W", padx=(100, 20), pady=3)

		en_t1_identifier_desc = Entry(lf_t1_identifier, textvariable=controller.sv_t1_desc, width = 46)
		en_t1_identifier_desc.grid(row=0, column=2, sticky="W", pady=3)

		lb_t1_identifier_space = LabelToolTip(lf_t1_identifier, text="Space", tool_tip_text=self.controller.desc.t1_identifier)
		lb_t1_identifier_space.grid(row=1, column=1, sticky="W", padx=(100, 20), pady=3)

		en_t1_identifier_space = Entry(lf_t1_identifier, textvariable=controller.sv_t1_space, width = 46)
		en_t1_identifier_space.grid(row=1, column=2, sticky="W", pady=3)

		lf_lm_identifier = LabelFrame(lf_inputs, text='4. Lesion Mask Identifier')
		lf_lm_identifier.grid(row=3, column=0, columnspan=3, sticky='W', pady=3)
		lf_lm_identifier.grid_rowconfigure(0, weight=0)
		lf_lm_identifier.grid_columnconfigure(3, weight=0)
		lf_lm_identifier.configure(borderwidth=0, relief='flat')

		lb_lm_identifier_suffix = LabelToolTip(lf_lm_identifier, text="Suffix", tool_tip_text=self.controller.desc.lm_identifier)
		lb_lm_identifier_suffix.grid(row=0, column=1, sticky="W", padx=(100, 20), pady=3)

		en_lm_identifier_suffix = Entry(lf_lm_identifier, textvariable=controller.sv_lesion_mask_suffix, width = 46)
		en_lm_identifier_suffix.grid(row=0, column=2, sticky="W", pady=3)

		lb_lm_identifier_space = LabelToolTip(lf_lm_identifier, text="Space", tool_tip_text=self.controller.desc.lm_identifier)
		lb_lm_identifier_space.grid(row=1, column=1, sticky="W", padx=(100, 20), pady=3)

		en_lm_identifier_space = Entry(lf_lm_identifier, textvariable=controller.sv_lesion_mask_space, width = 46)
		en_lm_identifier_space.grid(row=1, column=2, sticky="W", pady=3)

		lb_lm_identifier_label = LabelToolTip(lf_lm_identifier, text="Label", tool_tip_text=self.controller.desc.lm_identifier)
		lb_lm_identifier_label.grid(row=2, column=1, sticky="W", padx=(100, 20), pady=3)

		en_lm_identifier_label = Entry(lf_lm_identifier, textvariable=controller.sv_lesion_mask_label, width = 46)
		en_lm_identifier_label.grid(row=2, column=2, sticky="W", pady=3)

		lb_subject = LabelToolTip(lf_inputs, text="5. Subject", tool_tip_text=self.controller.desc.input_dir)
		lb_subject.grid(row=4, column=0, sticky="W", pady=3)

		en_subject = Entry(lf_inputs, textvariable=controller.sv_subject, width = 46)
		en_subject.grid(row=4, column=1, sticky="W", pady=3)

		lb_session = LabelToolTip(lf_inputs, text="6. Session", tool_tip_text=self.controller.desc.input_dir)
		lb_session.grid(row=5, column=0, sticky="W", pady=3)

		en_session = Entry(lf_inputs, textvariable=controller.sv_session, width = 46)
		en_session.grid(row=5, column=1, sticky="W", pady=3)

		lb_wm_seg_root = LabelToolTip(lf_inputs, text="7. White Matter Segmentation Root", tool_tip_text=self.controller.desc.input_dir)
		lb_wm_seg_root.grid(row=6, column=0, sticky="W", pady=3)

		en_wm_seg_root = Entry(lf_inputs, textvariable=controller.sv_wm_seg_root, width = 46)
		en_wm_seg_root.grid(row=6, column=1, sticky="W", pady=3)

		button_wm_seg_root = tk.Button(lf_inputs, text='Browse', command=lambda : self.chooseDir(self, controller, controller.sv_wm_seg_root, 'WM Segmentation Root'))
		button_wm_seg_root.grid(row=6, column=2, sticky='W', padx=5, pady=3)

		lb_lesion_root = LabelToolTip(lf_inputs, text="8. Lesion Root", tool_tip_text=self.controller.desc.input_dir)
		lb_lesion_root.grid(row=7, column=0, sticky="W", pady=3)

		en_lesion_root = Entry(lf_inputs, textvariable=controller.sv_lesion_root, width = 46)
		en_lesion_root.grid(row=7, column=1, sticky="W", pady=3)

		button_lesion_root = tk.Button(lf_inputs, text='Browse', command=lambda : self.chooseDir(self, controller, controller.sv_lesion_root, 'Lesion Root'))
		button_lesion_root.grid(row=7, column=2, sticky='W', padx=5, pady=3)

		wrapper = Frame(lf_inputs)
		wrapper.grid(row=8, column=0, sticky="WE", columnspan=3, pady=(3, 20))
		wrapper.grid_rowconfigure(0, weight=1)
		wrapper.grid_columnconfigure(2, weight=1)

		lb_same_anatomical_space = Label(wrapper, text="I verify that my anatomical image and lesion masks are in the same anatomical space.")
		lb_same_anatomical_space.grid(row=0, column=1, sticky="W",  padx=10, pady=(3, 20))

		chk_same_anatomical_space = tk.Checkbutton(wrapper, variable=controller.b_same_anatomical_space)
		chk_same_anatomical_space.grid(row=0, column=0, sticky='W', pady=(3, 20))

	def onShowFrame(self, event):
		super(DirectoryInputPage, self).onShowFrame(event)
		self.silentMode()


	def setFrameTitle(self):
		self.title.set('Please indicate the following:')

	def moveToNextPage(self):
		input_dir = self.controller.sv_input_dir.get()
		if not self.isValidPath(input_dir.strip()):
			self.setRequiredInputError('Directory inputs are not valid.')
			return
		if not self.controller.sv_t1_desc.get().strip() or not self.controller.sv_t1_space.get().strip():
			self.setRequiredInputError('Provide a valid T1 Anatomical Image Identifier')
			return
		if (not self.controller.sv_lesion_mask_suffix.get().strip() \
			or not self.controller.sv_lesion_mask_space.get().strip() \
			or not self.controller.sv_lesion_mask_label.get().strip()) \
			and (self.controller.b_wm_correction.get() \
			or self.controller.b_ll_calculation.get() \
			or self.controller.b_lesion_heatmap.get()):
			self.setRequiredInputError('Provide a valid Lesion Mask Image Identifier')
			return
		if not self.isValidPath(self.controller.sv_wm_seg_root.get()) and \
			not self.controller.b_wm_segmentation.get() and \
			(self.controller.b_wm_correction.get() \
			or self.controller.b_lesion_heatmap.get() \
			or self.controller.b_ll_calculation.get()):
			self.setRequiredInputError('White Matter Segmentation Root is required for Lesion Correction, Lesion Load Calculation and Lesion heatmap')
			return
		if self.controller.b_ll_calculation.get() \
			and not self.isValidPath(self.controller.sv_lesion_root.get().strip()):
			self.setRequiredInputError('Lesion Root input is invalid and required for Lesion Load Calculation and Lesion Heatmap')
			return
		super(DirectoryInputPage, self).moveToNextPage()

