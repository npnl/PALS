import os
from .config_reader import *

class NameVarStore(object):
	def __init__(self, name='', value=True):
		self.name = name
		self.value = value

	def get(self):
		return self.value

	def set(self, value):
		self.value = value

class Application(object):
	def __init__(self, logger, project_dir, need_display):
		self.silent = True
		self.need_display = need_display
		self.logger = logger
		self.project_dir = project_dir

		self.configs_present = True
		self.errors = []

		self.b_radiological_convention = NameVarStore('', False)
		self.b_wm_correction = NameVarStore('', False)
		self.b_ll_calculation = NameVarStore('', False)
		self.b_visual_qc = NameVarStore('', False)
		self.b_pause_for_qc = NameVarStore('', False)


		self.sv_input_dir = NameVarStore('', '')
		self.sv_output_dir = NameVarStore('', '')
		self.sv_t1_id = NameVarStore('', '')
		self.sv_lesion_mask_id = NameVarStore('', '')
		self.b_same_anatomical_space = NameVarStore('', False)

		self.sv_bet_id = NameVarStore('', '')
		self.sv_wm_id = NameVarStore('', '')
		self.b_brain_extraction = NameVarStore('', False)
		self.b_wm_segmentation = NameVarStore('', False)
		self.sv_percent = NameVarStore('', '5.0')
		self.percent_intensity = 5.0

		self.b_default_rois = NameVarStore('', False)
		self.b_freesurfer_rois = NameVarStore('', False)
		self.b_own_rois = NameVarStore('', False)

		self.default_corticospinal_tract_roi = []
		self.default_freesurfer_cortical_roi = []
		self.default_freesurfer_subcortical_roi =  []
		self.default_custom_rois = []
		self.default_roi_paths = None

		#FreeSurfer Rois
		self.freesurfer_cortical_roi = []
		self.freesurfer_subcortical_roi =  []
		self.fs_roi_paths = None
		self.fs_roi_codes = None

		#User ROIs
		self.user_rois = []
		self.user_roi_paths = None

		self.sv_user_brain_template = NameVarStore('', '')
		self.user_agreed = NameVarStore('', False)

		#Running Operations
		self.selected_subjects = NameVarStore('', '')

		#Settings Page
		self.sv_fsl_binaries_msg = NameVarStore('', '')

	def updateMessage(self, text, log_level='DEBUG'):
		if log_level == 'DEBUG':
			self.logger.debug(text)
		if log_level == 'ERROR':
			self.logger.error(text)

	def getProjectDirectory(self):
		return self.project_dir

	def updateProgressBar(self, value):
		pass

	def update(self):
		pass

		
	def buildRoi(self, name):
		return NameVarStore(name, True)

	def setLogger(self, logger):
		self.logger = logger


		