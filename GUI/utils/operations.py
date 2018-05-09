import os
import ntpath
from shutil import copyfile, rmtree

from pages.stores.rois import FreesurferCorticalROINamesToFileMapping as FS_Map
from pages.stores.rois import CorticospinalTractROINamesToFileMapping as CT_Map
from commands import Commands

from qc_page import generateQCPage

from base_operation import BaseOperation
from wm_segmentation_operation import WMSegmentationOperation
from wm_correction_operation import WMCorrectionOperation
from brain_extraction_operation import BrainExtractionOperation
from lesion_load_calculation_operation import LesionLoadCalculationOperation

class Operations(object, WMSegmentationOperation,\
				WMCorrectionOperation, BrainExtractionOperation,\
				LesionLoadCalculationOperation):
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
		self.createOutputSubjectDirectories(self.input_directory, self.getBaseDirectory())
		self.createROIDirectories()
		self.runGzip()
		self.normaliseT1Intensity()
		self.binarizeLesionFilesForAll()
		self.reOrientToRadForAllSubjects()
		self.runBrainExtraction()
		self.runWMSegmentation()
		self._runWMCorrectionHelper()
		self.runLesionLoadCalculation()
		self.runLesionLoadCalculationFS()
		self.createQCPage()

	def createQCPage(self):
		# Skip this step if user has not chosen to generate QC page
		if self.controller.b_visual_qc.get() == False or self.skip: return False
		images_dir = os.path.join(self.getBaseDirectory(), 'QC_Lesions')
		generateQCPage(page_type, images_dir)

	def _runWMCorrectionHelper(self):
		# Skip this step if user has not selected to perform wm correction
		if self.controller.b_wm_correction.get() == False or self.skip: return False
		sef.controller.sv_lesion_mask_id.set('WMAdjusted') # Doubt : What should happend to the user input for lesion_mask_id
		self.runWMCorrection()

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

	def _binarizeLesionFilesForSubject(self, subject):
		subject_dir = self.getOriginalPath(subject)
		counter = 1
		lesion_mask_id = self.controller.sv_lesion_mask_id.get()
		for item in os.listdir(subject_dir):
			if lesion_mask_id in item:
				lesion_file_path = os.path.join(subject_dir, item)
				output_bin_path = os.path.join(self.getIntermediatePath(subject), subject + '_' + lesion_mask_id + str(counter) + '_bin.nii.gz')
				self.com.runFslBinarize(lesion_file_path, output_bin_path)
				counter += 1

	def binarizeLesionFilesForAll(self):
		if self.skip: return False
		for subject in self.subjects:
			self._binarizeLesionFilesForSubject(subject)
		self.logger.info('Lesion files processed for all subjects')

	def _normaliseSubject(self, arg_1, arg_2, arg_3):
		minimum, maximum = self.com.runFslStats(arg_1, '-R')
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
			path = os.path.join(self.getBaseDirectory(), path)
		if drop_existing and os.path.exists(path):
			rmtree(path)
		os.makedirs(path)

	def _getRoiFilePaths(self, roi_options, mapping):
		roi_paths = []
		for roi in roi_options:
			if roi.get():
				roi_name = roi.name
				if roi_name in mapping:
					roi_file = mapping[roi_name]
					full_path = os.path.join(self.getBaseDirectory(), 'ROIs', roi_file)
					roi_paths.append(full_path)
		return roi_paths

	def _getDefaultROIsPaths(self):
		all_rois = self.controller.default_corticospinal_tract_roi\
					+ self.controller.default_freesurfer_cortical_roi
		roi_paths = self._getRoiFilePaths(all_rois, FS_Map)
		roi_paths += self._getRoiFilePaths(all_rois, CT_Map)
		self.controller.default_roi_paths = roi_paths
		return roi_paths

	def _getFSROIsPaths(self):
		fs_roi_options = self.controller.freesurfer_cortical_roi
		fs_roi_paths = self._getRoiFilePaths(fs_roi_options, FS_Map)
		self.controller.fs_roi_paths = fs_roi_paths
		return fs_roi_paths

	def _getUserROIsPaths(self):
		return self.controller.user_rois;

	def createROIDirectories(self):
		if self.skip: return False
		if self.controller.b_wm_correction.get(): self._createDirectory('QC_Lesions')
		if not self.controller.b_brain_extraction.get(): self._createDirectory('QC_BrainExtractions')
		if not self.controller.b_wm_segmentation.get(): self._createDirectory('QC_WM')
		if self.controller.b_ll_calculation.get():
			self._createDirectory('QC_LL')
			self._createDirectory('QC_Registrations')

			# User gave a list of ROIs paths
			if self.controller.b_own_rois.get():
				self._createDirectory('custom', parent=['QC_LL'])
				self._createDirectory('ROI_binarized')
				for user_roi_path in self._getUserROIsPaths():
					roi_name = self._extractFileName(user_roi_path)
					roi_output_path = os.path.join(self.getBaseDirectory(), 'ROI_binarized', roi_name + '_bin')
					self.com.runFslBinarize(user_roi_path, roi_output_path)

				roi_output_directory = os.path.join(self.getBaseDirectory(), ROI_binarized)
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
				self.logger.info('The subject contains error. Check that files are in the same orientation for subject [%s]', subject)
			else:
				self.new_subjects.append(subject)
		self.logger.info('Reorientation to the radiological convention has been completed for all subjects.')

	def _reOrientToRadForSubject(self, subject):
		if self.skip: return False
		subject_dir = self.getIntermediatePath(subject)

		# take in the original T1 and lesion mask images
		params = (subject, self.controller.sv_t1_id.get(), '_intNorm.nii.gz')
		original_t1_file = self._getPathOfFiles(self.getIntermediatePath(subject), *params)[0]
		original_t1_orientation = self.com.runFslOrient(original_t1_file)
		# if the T1 is already radiological, this is set here. otherwise radT1 gets updated.
		rad_t1_file = original_t1_file

		params = (subject, self.controller.sv_lesion_mask_id.get(), '.nii.gz')
		original_lesion_files = self._getPathOfFiles(self.getOriginalPath(subject), *params)
		rad_lesion_files = original_lesion_files

		# if user has already performed own brain extraction
		if self.controller.b_brain_extraction.get():
			params = (subject, self.controller.sv_bet_id.get(), '.nii.gz')
			original_bet_file = self._getPathOfFiles(self.getOriginalPath(subject), *params)[0]
			# if BET file is already radiological, this is set here. Otherwise rad_bet_file is updated
			rad_bet_file = self._getPathOfFiles(self.getOriginalPath(subject), *params)[0]
			original_bet_orientation = self.com.runFslOrient(original_bet_file)
		else:
			original_bet_orientation = 'NULL';

		# if user has already performed own wm segmentation
		if self.controller.b_wm_segmentation.get():
			params = (subject, self.controller.sv_wm_id.get(), '', '.nii.gz')
			original_wm_file = self._getPathOfFiles(self.getOriginalPath(subject), *params)[0]
			rad_wm_file = self._getPathOfFiles(self.getOriginalPath(subject), *params)[0]
			original_wm_orientation =self.com.runFslOrient(original_wm_file)
		else:
			original_wm_orientation = 'NULL'

		# check that t1, bet and wm are all same orientation, if they exist.
		if original_t1_orientation == 'NEUROLOGICAL' and original_bet_orientation == 'NEUROLOGICAL' and original_wm_orientation == 'NEUROLOGICAL':
			all_orientations = 'NEUROLOGICAL'
		elif original_t1_orientation == 'RADIOLOGICAL' and original_bet_orientation == 'RADIOLOGICAL' and original_wm_orientation == 'RADIOLOGICAL':
			all_orientations = 'RADIOLOGICAL'
		elif original_t1_orientation == 'NEUROLOGICAL' and original_bet_orientation == 'NULL' and original_wm_orientation == 'NULL':
			all_orientations = 'NEUROLOGICAL'
		elif original_t1_orientation == 'RADIOLOGICAL' and original_bet_orientation == 'NULL' and original_wm_orientation == 'NULL':
			all_orientations = 'RADIOLOGICAL'
		else
			return False

		for index, original_lesion_file in enumerate(original_lesion_files):
			original_lesion_orientation = self.com.runFslOrient(original_lesion_file)
			if original_lesion_orientation != all_orientations:
				return False

		# at this point, only subjects that have files all in the same orientation are retained
		# now change all files from neurological -> radiological

		if all_orientations == 'NEUROLOGICAL':
			output_file_path = os.path.join(self.getIntermediatePath(subject), subject + '_' + self.controller.sv_t1_id.get() + '_rad')
			self.com.runFslSwapDim(original_t1_file, output_file_path)
			self.com.runFslOrient(output_file_path + '.nii.gz', args='-swaporient')
			rad_t1_file = os.path.join(self.getIntermediatePath(subject), subject + '_' + self.controller.sv_t1_id.get() + '_rad.nii.gz')

			if self.controller.b_brain_extraction.get():
				output_file_path = os.path.join(self.getIntermediatePath(subject), subject + '_' + self.controller.sv_bet_id.get() + '_rad')
				self.com.runFslSwapDim(original_bet_file, output_file_path)
				self.com.runFslOrient(rad_bet_file, args='-swaporient')
				rad_bet_file = output_file_path + '.nii.gz'

			if self.controller.b_wm_segmentation.get():
				output_file_path = os.path.join(self.getIntermediatePath(subject), subject + '_' + self.controller.sv_wm_id.get() + '_rad')
				self.com.runFslSwapDim(original_wm_file, output_file_path)
				self.com.runFslOrient(rad_wm_file, args='-swaporient')
				rad_wm_file = output_file_path + '.nii.gz'

			for index, original_lesion_file in enumerate(original_lesion_files):
				output_file_path = os.path.join(self.getIntermediatePath(subject), subject + '_' + self.controller.sv_lesion_mask_id.get() + str(index+1) +'_rad')
				self.com.runFslSwapDim(original_lesion_file, output_file_path)
				self.com.runFslOrient(output_file_path + '.nii.gz', args='-swaporient')

			params = (subject, self.controller.sv_lesion_mask_id.get(), 'rad.nii.gz')
			rad_lesion_files = self._getPathOfFiles(self.getIntermediatePath(subject), *params)


		# run reorient2standard on radiological T1, bet, wm, and lesion files
		self.com.runFslOrient2Std(rad_t1_file, os.path.join(self.getSubjectPath(subject), subject + '_' + self.controller.sv_t1_id.get() + '_rad_reorient'))

		if self.controller.b_brain_extraction.get():
			self.com.runFslOrient2Std(rad_bet_file, os.path.join(self.getIntermediatePath(subject), subject + '_' +  self.controller.sv_bet_id.get() + '_rad_reorient'))

		if self.controller.b_wm_segmentation.get():
			self.com.runFslOrient2Std(rad_wm_file, os.path.join(self.getIntermediatePath(subject), subject + '_' +  self.controller.sv_wm_id.get() + '_rad_reorient'))

		for index, lesion_file in enumerate(rad_lesion_files):
			output_path = os.path.join(self.getSubjectPath(subject), subject + '_' + self.controller.sv_lesion_mask_id.get() + str(index + 1) + '_rad_reorient')
			self.com.runFslOrient2Std(lesion_file, output_path)

		#
		# if original_t1_orientation == 'NEUROLOGICAL':
		# 	output_file_path = os.path.join(self.getIntermediatePath(subject), subject + '_' + self.controller.sv_t1_id.get() + '_rad')
		# 	self.com.runFslSwapDim(original_t1_file, output_file_path)
		# 	self.com.runFslOrient(output_file_path + '.nii.gz')
		#
		# 	rad_t1_file = os.path.join(self.getIntermediatePath(subject), subject + '_' + self.controller.sv_t1_id.get() + '_rad.nii.gz')
		#
		# 	for index, original_lesion_file in enumerate(original_lesion_files):
		# 		original_lesion_orientation = self.com.runFslOrient(original_lesion_file)
		# 		if original_lesion_orientation == 'RADIOLOGICAL':
		# 			#Don't keep the subject
		# 			return False
		# 		else:
		# 			output_file_path = os.path.join(self.getIntermediatePath(subject), subject + '_' + self.controller.sv_lesion_mask_id.get() + str(index+1) +'_rad')
		# 			self.com.runFslSwapDim(original_lesion_file, output_file_path)
		# 			self.com.runFslOrient(output_file_path + '.nii.gz', args='-swaporient')
		#
		# 	params = (subject, self.controller.sv_lesion_mask_id.get(), 'rad.nii.gz')
		# 	rad_lesion_files = self._getPathOfFiles(self.getIntermediatePath(subject), *params)
		#
		# 	# if user has already run BET or WMSeg, and they're in NEUROLOGICAL, then convert to RADIOLOGICAl
		# 	if self.controller.b_brain_extraction.get():
		# 		params = (subject, self.controller.sv_bet_id.get(), '.nii.gz')
		# 		original_bet_file = self._getPathOfFiles(self.getOriginalPath(subject), *params)[0]
		# 		original_bet_orientation = self.com.runFslOrient(original_bet_file)
		#
		# 		if original_bet_orientation == 'RADIOLOGICAl':
		# 			self.controller.b_brain_extraction.set(False)
		# 		else:
		# 			output_file_path = os.path.join(self.getIntermediatePath(subject), subject + '_' + self.controller.sv_bet_id.get() + '_rad')
		# 			self.com.runFslSwapDim(original_bet_file, output_file_path)
		# 			rad_bet_file = output_file_path + '.nii.gz'
		# 			self.com.runFslOrient(rad_bet_file, args='-swaporient')
		#
		# 	if self.controller.b_wm_segmentation.get():
		# 		# origWM=$(ls ${SUBJECTOPDIR}/Intermediate_Files/Original_Files/${1}*"${WM_ID}"*.nii*);
		# 		params = (subject, self.controller.sv_wm_id.get(), '', '.nii')
		# 		original_wm_file = self._getPathOfFiles(self.getOriginalPath(subject), *params)[0]
		# 		original_wm_orientation =self.com.runFslOrient(original_wm_file)
		#
		# 		if original_wm_orientation == 'RADIOLOGICAl':
		# 			self.controller.b_wm_segmentation.set(False)
		# 		else:
		# 			output_file_path = os.path.join(self.getIntermediatePath(subject), subject + '_' + self.controller.sv_wm_id.get() + '_rad')
		# 			self.com.runFslSwapDim(original_wm_file, output_file_path)
		# 			rad_wm_file = output_file_path + '.nii.gz'
		# 			self.com.runFslOrient(rad_wm_file, args='-swaporient')
		#
		# self.com.runFslOrient2Std(rad_t1_file, os.path.join(self.getSubjectPath(subject), subject + '_' + self.controller.sv_t1_id.get() + '_rad_reorient'))
		#
		# if self.controller.b_brain_extraction.get():
		# 	self.com.runFslOrient2Std(rad_bet_file, os.path.join(self.getIntermediatePath(subject), subject + '_' +  self.controller.sv_bet_id.get() + '_rad_reorient'))
		#
		# if self.controller.b_wm_segmentation.get():
		# 	self.com.runFslOrient2Std(rad_wm_file, os.path.join(self.getIntermediatePath(subject), subject + '_' +  self.controller.sv_wm_id.get() + '_rad_reorient'))
		#
		#
		# for index, lesion_file in enumerate(rad_lesion_files):
		# 	if self.controller.b_wm_correction.get() or self.controller.b_ll_calculation.get():
		# 		output_path = os.path.join(self.getIntermediatePath(subject), subject + '_' + self.controller.sv_lesion_mask_id.get() + str(index + 1) + '_rad_reorient')
		# 	else:
		# 		output_path = os.path.join(self.getSubjectPath(subject), subject + '_' + self.controller.sv_lesion_mask_id.get() + str(index + 1) + '_rad_reorient')
		# 	self.com.runFslOrient2Std(lesion_file, output_path)

		return True

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
