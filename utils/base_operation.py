import os
import ntpath
from datetime import datetime
from shutil import copyfile, rmtree

class BaseOperation():

	def __new__(cls, *args, **kwargs):
		if cls is BaseOperation:
			raise TypeError('Base operation may not be instantiated')
		return object.__new__(cls, *args, **kwargs)

	def createUniqueDir(self):
		if self.unique_dir_name == None:
			self.unique_dir_name =  os.path.join(datetime.now().strftime('PALS_Output_%Y_%m_%d_%H_%M'))
		if (not os.path.exists(self.getBaseDirectory())) and len(self.output_directory) > 0:
			os.makedirs(self.getBaseDirectory())

	def getProjectDirectory(self):
		return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

	def getBaseDirectory(self):
		return os.path.join(self.output_directory, self.unique_dir_name)

	def getSubjectPath(self, subject):
		return os.path.join(self.getBaseDirectory(), subject)

	def getIntermediatePath(self, subject):
		return os.path.join(self.getSubjectPath(subject), self.INTERMEDIATE_FILES)

	def getOriginalPath(self, subject):
		return os.path.join(self.getIntermediatePath(subject), self.ORIGINAL_FILES)

	def updateProgressBar(self, value):
		self.controller.progressbar.step(value)

	def updateSubjects(self, subjects_to_drop):
		if len(subjects_to_drop) > 0:
			self.controller.updateGUI("Dropping subjects from further operations : " + str(subjects_to_drop))
		self.subjects = list(set(self.subjects) - set(subjects_to_drop))
		self.subjects.sort()
		self.logger.debug("Updated the subjects to " + str(self.subjects))

	def incrementStage(self, count=1):
		self.stage += count
		self.updateProgressBar((100.0/self.total_stages))

	def printQCPageUrl(self, operation_name, html_path, pause=True):
		if pause and not self.controller.b_pause_for_qc.get():
			self.incrementStage()
		pause = pause and self.controller.b_pause_for_qc.get()
		self.callback.pause(operation_name, html_path, pause)

	def _extractFileName(self, path, remove_extension=True, extension_count=1):
		head, tail = ntpath.split(path)
		filename =  tail or ntpath.basename(head)
		if remove_extension:
			for count in range(extension_count):
				filename, file_extension = os.path.splitext(filename)
		return filename

	def _getPathOfFiles(self, base_path, startswith_str='', substr='', endswith_str='', second_sub_str=''):
		all_files = []
		for item in os.listdir(base_path):
			if item.startswith(startswith_str) and substr in item and second_sub_str in item and item.endswith(endswith_str):
				all_files.append(os.path.join(base_path, item))
		return all_files

	def _setSubjectSpecificPaths_1(self, subject, anatomical_id, lesion_mask_id):
		if self.skip: return False
		anatomical_file_path, lesion_files = '', ''

		intermediate_path = self.getIntermediatePath(subject)
		params = (subject, anatomical_id, '.nii.gz')

		if self.controller.b_radiological_convention.get():
			try:
				anatomical_file_path = self._getPathOfFiles(self.getSubjectPath(subject), *params)[0]
			except:
				print "In exception block"
				anatomical_file_path = self._getPathOfFiles(intermediate_path, *params)[0]
		else:
			try:
				anatomical_file_path = self._getPathOfFiles(intermediate_path, *params)[0]
			except:
				pass

		if type(lesion_mask_id) == type([]):
			params = (subject, lesion_mask_id[0], '.nii.gz', lesion_mask_id[1])
		else:
			params = (subject, lesion_mask_id, '.nii.gz')
		lesion_files = self._getPathOfFiles(intermediate_path, *params)

		## put in a check here; if there are no T1 and/or lesion files, then set the path to the Original_Files directory.
		if not os.path.exists(anatomical_file_path):
			params = (subject, anatomical_id, '.nii.gz')
			anatomical_file_path =  self._getPathOfFiles(self.getOriginalPath(subject), *params)[0]

		if len(lesion_files) == 0 or not os.path.exists(lesion_files[0]):
			params = (subject, lesion_mask_id, '.nii.gz')
			lesion_files = self._getPathOfFiles(self.getOriginalPath(subject), *params)

		lesion_files = [x for x in lesion_files if 'custom' not in x.lower()]
		lesion_files = [x for x in lesion_files if 'mni152' not in x.lower()]
		lesion_files = [x for x in lesion_files if 'upper' not in x.lower()]
		lesion_files = [x for x in lesion_files if 'lower' not in x.lower()]

		return anatomical_file_path, lesion_files


	def _setSubjectSpecificPaths_2(self, subject):
		if self.skip: return False
		t1_mgz, seg_file, bet_brain_file, wm_mask_file = [None] * 4
		if self.controller.b_freesurfer_rois.get():
			t1_mgz = os.path.join(self.getOriginalPath(subject), 'T1.mgz')
			seg_file = os.path.join(self.getOriginalPath(subject), 'aparc+aseg.mgz')

		# Run brain extraction only if user has not run it
		if not self.controller.b_brain_extraction.get():
			bet_brain_file = os.path.join(self.getIntermediatePath(subject), subject + '_Brain.nii.gz')
		elif not self.controller.b_radiological_convention.get():
			params = (subject, self.controller.sv_bet_id.get(), '.nii.gz')
			bet_brain_file = self._getPathOfFiles(self.getOriginalPath(subject), *params)[0]
		else:
			bet_brain_file = os.path.join(self.getIntermediatePath(subject), subject + '_' + self.controller.sv_bet_id.get() + '_rad_reorient.nii.gz')

		# Run white matter segmentation only if user has not run it
		if not self.controller.b_wm_segmentation.get():
			wm_mask_file = os.path.join(self.getIntermediatePath(subject), subject + '_seg_2.nii.gz')
		elif not self.controller.b_radiological_convention.get():
			params = (subject, self.controller.sv_wm_id.get(), '', '.nii')
			wm_mask_file = self._getPathOfFiles(self.getOriginalPath(subject), *params)[0]
		else:
			wm_mask_file = os.path.join(self.getIntermediatePath(subject), subject + '_' + self.controller.sv_wm_id.get() + '_rad_reorient.nii.gz')

		return ((t1_mgz, seg_file), bet_brain_file, wm_mask_file)


	def moveOutputFiles(self):
		for subject in self.subjects:
			intermediate_path = self.getIntermediatePath(subject)
			subject_path = self.getSubjectPath(subject)
			
			files = ["%s_Reg_brain_MNI152.nii.gz",\
					 "%s_Reg_brain_custom.nii.gz",\
					 "%s_Reg_brain_MNI152.nii.gz",\
					 "%s_T12FS.nii.gz",\
					 "%s" + ("%s_rad_reorient.nii.gz"%(self.anatomical_id)),\
					 "%s_lesion*_FS_bin.nii.gz",\
					 "%s_lesion*_MNI152_bin.nii.gz",\
					 "%s_lesion*_custom*",\
					 "%s_lesion*_rad_reorient.nii.gz",\
					 "%s*overlap*"
					 ]

			files_to_move = self._getPathOfFiles(intermediate_path, startswith_str=subject, substr='_WMAdjusted_lesion', endswith_str='.nii.gz', second_sub_str='')
			files_to_move = [self._extractFileName(file_path, remove_extension=False) for file_path in files_to_move]
			filtered_files = []
			for s_file in files_to_move:
				try:
					index = len(subject + '_WMAdjusted_lesion')
					_ = int(s_file[index])
					filtered_files.append(s_file)
				except:
					pass
			files += filtered_files
			try:
				for file_name in files:
					try:
						file_path = os.path.join(intermediate_path, file_name%subject)
					except:
						file_path = os.path.join(intermediate_path, file_name)
					cmd = "mv %s %s"%(file_path, subject_path)
					self.com.runRawCommand(cmd, show_error=False)
			except:
				pass




	def logSelectedROINames(self, property_name, rois):
		roi_names = [x.name for x in rois if x.get()]
		log_line = property_name.ljust(60) + " :  " + str(roi_names)
		self.logger.debug(log_line)


	def logUserChoices(self):
		selection_mapping = {}
		selection_mapping['01. Radiological convention'] = self.controller.b_radiological_convention
		selection_mapping['02. White Matter Correction'] = self.controller.b_wm_correction
		selection_mapping['03. Lesion Load Calculation'] = self.controller.b_ll_calculation
		selection_mapping['04. Visual QC'] = self.controller.b_visual_qc
		selection_mapping['05. Pause for QC'] = self.controller.b_pause_for_qc
		selection_mapping['06. Input Directory'] = self.controller.sv_input_dir
		selection_mapping['07. Output Directory'] = self.controller.sv_output_dir
		selection_mapping['08. Anatomical Identifier'] = self.controller.sv_t1_id
		selection_mapping['09. Lesion Mask Identifier'] = self.controller.sv_lesion_mask_id
		selection_mapping['10. Is in same anatomical space'] = self.controller.b_same_anatomical_space
		selection_mapping['11. Is Brain Extraction Already Performed'] = self.controller.b_brain_extraction
		selection_mapping['12. Is White Matter Segmentation Already Performed'] = self.controller.b_wm_segmentation
		selection_mapping['13. Brain Extraction Identifier'] = self.controller.sv_bet_id
		selection_mapping['14. White Matter Identifier'] = self.controller.sv_wm_id
		selection_mapping['15. Percent Intensity'] = self.controller.sv_percent
		selection_mapping['16. Default ROIs selected'] = self.controller.b_default_rois
		selection_mapping['17. FreeSurfer ROIs selected'] = self.controller.b_freesurfer_rois
		selection_mapping['18. Own ROIs selected'] = self.controller.b_own_rois

		default_roi = self.controller.default_corticospinal_tract_roi + self.controller.default_freesurfer_cortical_roi + self.controller.default_freesurfer_subcortical_roi
		fs_rois = self.controller.freesurfer_cortical_roi + self.controller.freesurfer_subcortical_roi

		self.logger.debug('\n')
		for key in sorted(selection_mapping):
			log_line = key.ljust(60) + " :  " + str(selection_mapping[key].get())
			self.logger.debug(log_line)
		
		self.logSelectedROINames("19. Default ROIs List", default_roi)
		self.logSelectedROINames("20. FreeSurfer ROIs List", fs_rois)
		
		self.logger.debug('\n')
