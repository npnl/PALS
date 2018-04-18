import os
import ntpath
from shutil import copyfile, rmtree

from pages.stores.rois import FreesurferCorticalROINamesToFileMapping as FS_Map
from commands import Commands

from qc_page import generateQCPage

class Operations(object):
	def __init__(self, controller):
		self.controller = controller
		self.logger = controller.logger
		self.com = Commands(controller.logger)

		self.initialiseConstants()

	def initialiseConstants(self):
		self.subjects = []
		self.new_subjects = []
		self.input_directory = self.controller.sv_input_dir.get()
		self.output_directory = self.controller.sv_output_dir.get()
		self.output_directories = []

		self.INTERMEDIATE_FILES = 'Intermediate_Files'
		self.ORIGINAL_FILES = 'Original_Files'


	def initialise(self):
		self.skip = False
		self.initialiseConstants()
		self.createOutputSubjectDirectories(self.input_directory, self.output_directory)
		self.createROIDirectories()
		self.runGzip()
		self.normaliseT1Intensity()
		self.processLesionFilesForAll()
		self.reOrientToRadForAllSubjects()
		self.runBrainExtraction()
		self.runWMSegmentation()

	def getSubjectPath(self, subject):
		return os.path.join(self.output_directory, subject)

	def getIntermediatePath(self, subject):
		return os.path.join(self.getSubjectPath(subject), self.INTERMEDIATE_FILES)

	def getOriginalPath(self, subject):
		return os.path.join(self.getIntermediatePath(subject), self.ORIGINAL_FILES)

	def _copyDirectories(self, source_dir, dest_dir):
		for item in os.listdir(source_dir):
			if os.path.isdir(os.path.join(source_dir, item)):
				os.makedirs(os.path.join(dest_dir, item))
				self._copyDirecories(os.path.join(source_dir, item), os.path.join(dest_dir, item))
			else:
				copyfile(os.path.join(source_dir, item), os.path.join(dest_dir, item))

	def _createOriginalFiles(self, source_dir, target_dir):
		target_dir = os.path.join(target_dir, self.INTERMEDIATE_FILES, self.ORIGINAL_FILES)
		os.makedirs(target_dir)
		self._copyDirectories(source_dir, target_dir)

	def runGzip(self):
		if self.skip: return False
		for subject in self.subjects:
			directory = self.getOriginalPath(subject)
			self.com.runGzip(directory)
		self.logger.info('Gzip operation completed for all subjects')

	def _processLesionFilesForSubject(self, subject):
		subject_dir = self.getOriginalPath(subject)
		counter = 1
		lesion_mask_id = self.controller.sv_lesion_mask_id.get()
		for item in os.listdir(subject_dir):
			if lesion_mask_id in item:
				lesion_file_path = os.path.join(subject_dir, item)
				output_bin_path = os.path.join(self.getIntermediatePath(subject), subject + '_' + lesion_mask_id + str(counter) + '_bin.nii.gz')
				self.com.runFslmathsOnLesionFile(lesion_file_path, output_bin_path)
				counter += 1

	def processLesionFilesForAll(self):
		if self.skip: return False
		for subject in self.subjects:
			self._processLesionFilesForSubject(subject)
		self.logger.info('Lesion files processed for all subjects')

	def _normaliseSubject(self, arg_1, arg_2, arg_3):
		minimum, maximum = self.com.runFslStat(arg_1)
		scaling = 255.0/(maximum - minimum)
		self.com.runFslMath(arg_1, minimum, scaling, os.path.join(arg_3, arg_2))

	def normaliseT1Intensity(self):
		if self.skip: return False
		t1_identifier = self.controller.sv_t1_id.get()
		for subject in self.subjects:
			arg_1 = os.path.join(self.getOriginalPath(subject), subject + '*' + t1_identifier + '*.nii.gz')
			arg_2 = subject + '_' + t1_identifier
			arg_3 = os.path.join(self.getIntermediatePath(subject))
			self._normaliseSubject(arg_1, arg_2, arg_3)
		self.logger.debug('Normalization completed for all subjects')

	def createOutputSubjectDirectories(self, base_input_directory, base_output_directory):
		if self.skip: return False
		all_input_directories = os.listdir(base_input_directory)
		for directory in all_input_directories:
			if os.path.isdir(os.path.join(base_input_directory, directory)):
				self.subjects.append(directory)
				output_directory = os.path.join(base_output_directory, directory)
				if os.path.exists(output_directory):
					rmtree(output_directory)
				os.makedirs(output_directory)
				input_directory = os.path.join(base_input_directory, directory)
				self._createOriginalFiles(input_directory, output_directory)

	def _getPathOfFiles(self, base_path, startswith_str='', substr='', endswith_str='', second_sub_str=''):
		all_files = []
		for item in os.listdir(base_path):
			if item.startswith(startswith_str) and substr in item and second_sub_str in item and item.endswith(endswith_str):
				all_files.append(os.path.join(base_path, item))
		return all_files


	def _setSubjectSpecificPaths_1(self, subject):
		if self.skip: return False
		anatomical_file_path, lesion_files = None, None

		anatomical_id = self.controller.sv_t1_id.get()
		intermediate_path = self.getIntermediatePath(subject)
		if not self.controller.b_radiological_convention.get(): # Need to fix this
			params = (subject, anatomical_id, '_intNorm.nii.gz')
			anatomical_file_path = self._getPathOfFiles(intermediate_path, *params)[0]
			
			if anatomical_id == 'WMAdjusted':
				params = (subject, anatomical_id, 'bin.nii.gz')
				lesion_files = self._getPathOfFiles(self.getSubjectPath(subject), *params)
			else:
				params = (subject, anatomical_id, 'bin.nii.gz')
				lesion_files = self._getPathOfFiles(intermediate_path, *params)

		else:
			anatomical_file_path=os.path.join(self.getSubjectPath(subject), subject + '_' + anatomical_id + '_rad_reorient.nii.gz')
			if self.controller.b_wm_correction.get() or self.controller.b_ll_correction.get():
				if lesion_mask_id == 'WMAdjusted':
					params = (subject, anatomical_id, 'bin.nii.gz')
					lesion_files = self._getPathOfFiles(self.getSubjectPath(subject), *params)
				else:
					params = (subject, anatomical_id, 'rad_reorient.nii.gz')
					lesion_files = self._getPathOfFiles(intermediate_path, *params)
			else:
				params = (subject, anatomical_id, 'rad_reorient.nii.gz')
				lesion_files = self._getPathOfFiles(self.getSubjectPath(subject), *params)

		
		# if anatomical_file_path == '':
		# 	self.logger.info('Anatomical file not present. \
		# 						Make sure a with name like [%s*%s*_%s] \
		# 						is present in %s'%(params[0], params[1], params[2], intermediate_path))

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

	def performWMSegmentation(self):
		if self.skip: return False
		self.logger.info('Performing white matter segmentation...[long process]')
		for subject in self.new_subjects:
			pass
		self.logger.info('White Matter segmentation completed for all subjects') 

	def _createDirectory(self, path, parent=[''], relative=True, drop_existing=True):
		parent = os.path.join(*parent)
		path = os.path.join(parent, path)
		if relative:
			path = os.path.join(self.output_directory, path)
		if drop_existing and os.path.exists(path):
			rmtree(path)
		os.makedirs(path)

	def _extractFileName(self, path, remove_extension=True):
		head, tail = ntpath.split(path)
		filename =  tail or ntpath.basename(head)
		if remove_extension:
			filename, file_extension = os.path.splitext(filename)
		return filename

	def _createROIsHelper(self):
		pass

	def _getDefaultROIsPaths(self):
		return []

	def _getFSROIsPaths(self):
		fs_roi_paths = []
		for obj in self.controller.freesurfer_cortical_roi:
			if obj.get():
				fs_roi_paths.append(FS_Map[obj.name])
		return fs_roi_paths

	def _getUserROIsPaths(self):
		return []

	def createROIDirectories(self):
		if self.skip: return False
		if self.controller.b_wm_correction.get(): self._createDirectory('QC_Lesions')
		if not self.controller.b_brain_extraction.get(): self._createDirectory('QC_BrainExtractions')
		if not self.controller.b_wm_segmentation.get(): self._createDirectory('QC_WM')
		if self.controller.b_ll_correction.get():
			self._createDirectory('QC_LL')
			self._createDirectory('QC_Registrations')

			# User gave a list of ROIs paths
			if self.controller.b_own_rois.get():
				self._createDirectory('custom', parent=['QC_LL'])
				self._createDirectory('ROI_binarized')
				for user_roi_path in self._getUserROIsPaths():
					roi_name = self._extractFileName(user_roi_path)
					roi_output_path = os.path.join(self.output_directory, 'ROI_binarized', roi_name + '_bin')
					self.com.runFslmathsOnLesionFile(user_roi_path, roi_output_path)

				roi_output_directory = os.path.join(self.output_directory, ROI_binarized)
				params = ('', '', '_bin.nii.gz')
				user_rois_output_paths = self._getPathOfFiles(roi_output_directory, *params)

				for user_roi_output_path in user_rois_output_paths:
					roi_name = self._extractFileName(user_roi_output_path)
					self._createDirectory(roi_name, parent=['QC_LL', 'custom'])

				self._createDirectory('custom', parent=['QC_Registrations'])

			# Default ROIs
			elif self.controller.b_default_rois.get():
				self._createDirectory('MNI152', parent=['QC_LL'])
				for default_roi_path in self._getDefaultROIsPaths():
					roi_name = self._extractFileName(default_roi_path)
					self._createDirectory(roi_name, parent=['QC_LL', 'MNI152'])
				self._createDirectory('MNI152', parent=['QC_Registrations'])

			# FreeSurfer specific ROIs
			elif self.controller.b_freesurfer_rois.get():
				self._createDirectory('FS', parent=['QC_LL'])
				for fs_roi_path in self._getFSROIsPaths():
					roi_name = self._extractFileName(fs_roi_path)
					self._createDirectory(roi_name, parent=['QC_LL', 'FS'])
				self._createDirectory('FS', parent=['QC_Registrations'])
			else:
				self.logger.info('None of the ROI options selected')
		self.logger.debug('ROIs direcotory created successfully')

	def reOrientToRadForAllSubjects(self):
		if self.skip: return False
		for subject in self.subjects:
			keepSubject = self._reOrientToRadForSubject(subject)
			if not keepSubject:
				self.logger.info('The subject contains error. Check subject [%s]', subject)
			else:
				self.new_subjects.append(subject)
		self.logger.info('ReOrientToRad completed for all subjects')

	def _reOrientToRadForSubject(self, subject):
		if self.skip: return False
		subject_dir = self.getIntermediatePath(subject)

		# take in the original T1 and lesion mask images
		params = (subject, self.controller.sv_t1_id.get(), '_intNorm.nii.gz')
		original_t1_file = self._getPathOfFiles(self.getIntermediatePath(subject), *params)[0]

		# if the T1 is already radiological, this is set here. otherwise radT1 gets updated.
		rad_t1_file = original_t1_file

		params = (subject, self.controller.sv_lesion_mask_id.get(), '.nii.gz')
		original_lesion_files = self._getPathOfFiles(self.getOriginalPath(subject), *params)
		rad_lesion_files = original_lesion_files

		if self.controller.b_brain_extraction.get():
			params = (subject, self.controller.sv_bet_id.get(), '.nii.gz')
			rad_bet_file = self._getPathOfFiles(self.getOriginalPath(subject), *params)[0]

		original_t1_orientation = self.com.runFslOrient(original_t1_file)

		if original_t1_orientation == 'NEUROLOGICAL':
			output_file_path = os.path.join(self.getIntermediatePath(subject), subject + '_' + self.controller.sv_t1_id.get() + '_rad')
			self.com.runFslSwapDim(original_t1_file, output_file_path)
			self.com.runFslOrient(output_file_path + '.nii.gz')

			rad_t1_file = os.path.join(self.getIntermediatePath(subject), subject + '_' + self.controller.sv_t1_id.get() + '_rad.nii.gz')

			for index, original_lesion_file in enumerate(original_lesion_files):
				original_lesion_orientation = self.com.runFslOrient(original_lesion_file)
				if original_lesion_orientation == 'RADIOLOGICAL':
					#Don't keep the subject
					return False
				else:
					output_file_path = os.path.join(self.getIntermediatePath(subject), subject + '_' + self.controller.sv_lesion_mask_id.get() + str(index+1) +'_rad')
					self.com.runFslSwapDim(original_lesion_file, output_file_path)
					self.com.runFslOrient(output_file_path + '.nii.gz', args='-swaporient')

			params = (subject, self.controller.sv_lesion_mask_id.get(), 'rad.nii.gz')
			rad_lesion_files = self._getPathOfFiles(self.getIntermediatePath(subject), *params)

			# if user has already run BET or WMSeg, and they're in NEUROLOGICAL, then convert to RADIOLOGICAl
			if self.controller.b_brain_extraction.get():
				params = (subject, self.controller.sv_bet_id.get(), '.nii.gz')
				original_bet_file = self._getPathOfFiles(self.getOriginalPath(subject), *params)[0]
				original_bet_orientation = self.com.runFslOrient(original_bet_file)

				if original_bet_orientation == 'RADIOLOGICAl':
					self.controller.b_brain_extraction.set(False)
				else:
					output_file_path = os.path.join(self.getIntermediatePath(subject), subject + '_' + self.controller.sv_bet_id.get() + '_rad')
					self.com.runFslSwapDim(original_bet_file, output_file_path)
					rad_bet_file = output_file_path + '.nii.gz'
					self.com.runFslOrient(rad_bet_file, args='-swaporient')

			if self.controller.b_wm_segmentation.get():
				# origWM=$(ls ${SUBJECTOPDIR}/Intermediate_Files/Original_Files/${1}*"${WM_ID}"*.nii*);
				params = (subject, self.controller.sv_wm_id.get(), '', '.nii')
				original_wm_file = self._getPathOfFiles(self.getOriginalPath(subject), *params)[0]
				original_wm_orientation =self.com.runFslOrient(original_wm_file)

				if original_wm_orientation == 'RADIOLOGICAl':
					self.controller.b_wm_segmentation.set(False)
				else:
					output_file_path = os.path.join(self.getIntermediatePath(subject), subject + '_' + self.controller.sv_wm_id.get() + '_rad')
					self.com.runFslSwapDim(original_wm_file, output_file_path)
					rad_wm_file = output_file_path + '.nii.gz'
					self.com.runFslOrient(rad_wm_file, args='-swaporient')

		self.com.runFslOrient2Std(rad_t1_file, os.path.join(self.getSubjectPath(subject), subject + '_' + self.controller.sv_t1_id.get() + '_rad_reorient'))
		
		if self.controller.b_brain_extraction.get():
			self.com.runFslOrient2Std(rad_bet_file, os.path.join(self.getIntermediatePath(subject), subject + '_' +  self.controller.sv_bet_id.get() + '_rad_reorient'))
		
		if self.controller.b_wm_segmentation.get():
			self.com.runFslOrient2Std(rad_wm_file, os.path.join(self.getIntermediatePath(subject), subject + '_' +  self.controller.sv_wm_id.get() + '_rad_reorient'))


		for index, lesion_file in enumerate(rad_lesion_files):
			if self.controller.b_wm_correction.get() or self.controller.b_ll_correction.get():
				output_path = os.path.join(self.getIntermediatePath(subject), subject + '_' + self.controller.sv_lesion_mask_id.get() + str(index + 1) + '_rad_reorient')
			else:
				output_path = os.path.join(self.getSubjectPath(subject), subject + '_' + self.controller.sv_lesion_mask_id.get() + str(index + 1) + '_rad_reorient')
			self.com.runFslOrient2Std(lesion_file, output_path)

		return True


	def runBrainExtraction(self):
		# Skip this step if user has already performed brain extraction
		if self.controller.b_brain_extraction.get() == True or self.skip: return False
		for subject in self.subjects:
			anatomical_file_path, lesion_files = self._setSubjectSpecificPaths_1(subject)
			((t1_mgz, seg_file), bet_brain_file, wm_mask_file) = self._setSubjectSpecificPaths_2(subject)
			
			self.com.runBet(anatomical_file_path, os.path.join(self.getIntermediatePath(subject), subject + '_Brain'))

			image_files_base = os.path.join(self.output_directory, 'QC_BrainExtractions')
			image_path = os.path.join(image_files_base, subject + '_BET.png')
			self.com.runFslEyes(anatomical_file_path, bet_brain_file, image_path)
		generateQCPage('bet', image_files_base)
		self.logger.info('Brain extraction completed for all subjects')


	def runWMSegmentation(self):
		# Skip this step if user has already performed brain extraction
		if self.controller.b_wm_segmentation.get() == True or self.skip: return False
		for subject in self.subjects:
			anatomical_file_path, lesion_files = self._setSubjectSpecificPaths_1(subject)
			((t1_mgz, seg_file), bet_brain_file, wm_mask_file) = self._setSubjectSpecificPaths_2(subject)
			
			self.com.runFast(os.path.join(self.getIntermediatePath(subject), subject), bet_brain_file)

			image_files_base = os.path.join(self.output_directory, 'QC_WM')
			image_path = os.path.join(image_files_base, subject + '_WM.png')
			self.com.runFslEyes(anatomical_file_path, wm_mask_file, image_path)
		generateQCPage('WM', image_files_base)
		self.logger.info('White Matter segmentation completed for all subjects')


	def getTemplateBrainROIS(self):
		parent_dir =  os.path.abspath(os.path.join(os.getcwd(), os.pardir))
		template_roi_dir = os.path.join(parent_dir, 'ROIs')
		template_rois = None
		for item in os.listdir(template_roi_dir):
			if item.startswith('MNI152_T1_2mm_brain'):
				template_rois = os.path.join(template_roi_dir, item)
				break
		return template_rois

def isValidPath(filePath):
	if os.path.exists(filePath):
		pass
	elif os.access(os.path.dirname(filePath), os.W_OK):
		pass
	else:
		return False
	return True

if __name__ == '__main__':
	pass

