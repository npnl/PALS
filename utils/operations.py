import os, traceback
import ntpath
from datetime import datetime
from shutil import copyfile, rmtree
from threading import Thread

from pages.stores.rois import FreesurferCorticalROINamesToFileMapping as FS_CT_Map
from pages.stores.rois import FreesurferSubCorticalROINamesToFileMapping as FS_SCT_Map
from pages.stores.rois import CorticospinalTractROINamesToFileMapping as CT_Map
from .commands import Commands

from .qc_page import generateQCPage

from .base_operation import BaseOperation
from .wm_segmentation_operation import WMSegmentationOperation
from .wm_correction_operation import LesionCorrectionOperation
from .brain_extraction_operation import BrainExtractionOperation
from .lesion_load_calculation_operation import LesionLoadCalculationOperation

class Operations(WMSegmentationOperation,\
				LesionCorrectionOperation, BrainExtractionOperation,\
				LesionLoadCalculationOperation):
	def __init__(self, controller):
		self.controller = controller
		self.logger = controller.logger
		self.com = Commands(controller.logger, self.controller)
		self.resetOperations()

	def startThreads(self, callback):
		self.callback = callback
		thread = Thread(target=self.startExecution, args=())
		thread.start()

	def stopThreads(self):
		self.skip = True
		self.reset_from_ui = True
		self.com.stopCurrentProcess()

	def resetOperations(self):
		self.stage = 0
		self.callback = None
		self.total_stages = 15
		self.reset_from_ui = False

	def initialiseConstants(self):
		self.subjects = []
		self.input_directory = self.controller.sv_input_dir.get()
		self.output_directory = self.controller.sv_output_dir.get()
		self.output_directories = []
		self.unique_dir_name = None
		self.createUniqueDir()

		self.INTERMEDIATE_FILES = 'Intermediate_Files'
		self.ORIGINAL_FILES = 'Original_Files'

		self.anatomical_id = self.controller.sv_t1_id.get()
		self.lesion_mask_id = self.controller.sv_lesion_mask_id.get()

	def isMajorOperationSelected(self):
		return self.controller.b_radiological_convention.get()\
				or self.controller.b_wm_correction.get()\
				or self.controller.b_ll_calculation.get()

	def startExecution(self):
		self.skip = False

		if self.stage == 0:
			self.logUserChoices()
			self.logger.debug("Stage currently executing is %d"%self.stage)
			self.controller.progressbar['value'] = 0
			self.controller.updateGUI('Selected operations initiated')
			self.initialiseConstants()
			self.controller.updateGUI('Checking for necessary files in all subject directories')
			self.createOutputSubjectDirectories(self.input_directory, self.getBaseDirectory(), only_iterate=True)
			if not self.checkAllSubjectInputs():
				self.incrementStage(15)
			else:
				self.controller.updateGUI('All subjects have necessary files')
				self.incrementStage()

		if self.stage == 1:
			self.logger.debug("Stage currently executing is %d"%self.stage)
			if self.isMajorOperationSelected():
				self.createOutputSubjectDirectories(self.input_directory, self.getBaseDirectory())
				self.createROIDirectories()
				self.runGzip()
				self.binarizeLesionFilesForAll()
			self.incrementStage()

		if self.stage == 2:
			self.logger.debug("Stage currently executing is %d"%self.stage)

			if self.controller.b_radiological_convention.get():
				try:
					self.anatomical_id, self.lesion_mask_id = self.reOrientToRadForAllSubjects()
				except Exception as e:
					self.logger.error(e.message)
					self.logger.debug(traceback.format_exc())
			self.incrementStage()

		if self.stage == 3:
			self.logger.debug("Stage currently executing is %d"%self.stage)

			if self.controller.b_wm_correction.get() or self.controller.b_ll_calculation.get():
				self.runBrainExtraction(self.anatomical_id, self.lesion_mask_id)
			else:
				self.incrementStage()

		if self.stage in (4, 5):
			self.logger.debug("Stage currently executing is %d"%self.stage)

			if self.controller.b_wm_correction.get():
				if self.stage == 4:
					try:
						self.runWMSegmentation(self.anatomical_id, self.lesion_mask_id)
					except Exception as e:
						self.logger.error(e.message)
						self.logger.debug(traceback.format_exc())

				if self.stage == 5:
					try:
						self.anatomical_id = self.normaliseT1Intensity(self.anatomical_id)
						self.lesion_mask_id = self.runLesionCorrection(self.anatomical_id, self.lesion_mask_id)
					except Exception as e:
						self.logger.error(e.message)
						self.logger.debug(traceback.format_exc())
			else:
				self.incrementStage(2)


		if self.stage in (6, 7, 8, 9, 10, 11, 12):
			self.logger.debug("Stage currently executing is %d"%self.stage)

			if self.controller.b_ll_calculation.get() and self.skip == False:
				try:
					self.runLesionLoadCalculation(self.anatomical_id, self.lesion_mask_id)
				except Exception as e:
					self.logger.error(e.message)
					self.logger.debug(traceback.format_exc())
			else:
				self.incrementStage(7)

		if self.stage == 13:
			self.logger.debug("Stage currently executing is %d"%self.stage)

			if self.controller.b_visual_qc.get() and self.skip == False:
				self.createQCPage()
			self.incrementStage()

		if self.stage == 14:
			self.logger.debug("Stage currently executing is %d"%self.stage)
			try:
				self.moveOutputFiles()
			except:
				pass
			self.incrementStage()

		if self.stage >= 15:
			self.logger.debug("Stage currently executing is %d"%self.stage)
			self.controller.progressbar['value'] = 100
			self.callback.finished('all', '')

		if self.skip and self.reset_from_ui:
			self.callback.resetAll()
			self.controller.updateGUI('PALS is reset to perform all operation from scratch')

		elif self.stage < 15:
			self.logger.debug("Waiting for stage [%d] to start"%(self.stage + 1))

	def checkAllSubjectInputs(self):
		errors = []
		flag = True
		mri_convert = True
		if self.controller.b_ll_calculation.get() and self.controller.b_freesurfer_rois.get():
			mri_convert =  self.controller.checkFslInstalled(bypass_mri_convert=False)
		if not mri_convert:
			flag = False
			errors.append("mri_convert is not in the PATH variable. Please set it to proceed.")
		for subject in self.subjects:
			if not mri_convert:
				continue
			subject_input_path = os.path.join(self.input_directory, subject)
			try:
				anatomical_file_path, lesion_files = self.getT1NLesionFromInput(subject)
				_ = anatomical_file_path[0]
			except:
				errors.append('Subject [%s] is missing the anatomical file'%subject)
				flag = False
			try:
				_ = lesion_files[0]
			except:
				errors.append('Subject [%s] is missing the lesion mask file'%subject)
				flag = False

			if self.controller.b_brain_extraction.get():
				params = (subject, self.controller.sv_bet_id.get(), '.nii.gz')
				try:
					bet_brain_file = self._getPathOfFiles(subject_input_path, *params)[0]
				except:
					self.controller.b_brain_extraction.set(False)
					errors.append('Subject [%s] is missing Brain file. PALS will run the Brain Extraction'%subject)

			if self.controller.b_wm_segmentation.get():
				params = (subject, self.controller.sv_wm_id.get(), '.nii.gz')
				try:
					wm_mask_file = self._getPathOfFiles(subject_input_path, *params)[0]
				except:
					self.controller.b_wm_segmentation.set(False)
					errors.append('Subject [%s] is missing White Matter mask file. PALS will run the White Matter Segmentation'%subject)

			if self.controller.b_freesurfer_rois.get():
				try:
					params = ('T1', '', '.mgz')
					t1_mgz = self._getPathOfFiles(subject_input_path, *params)[0]
					params = ('aparc+aseg', '', '.mgz')
					seg_file = self._getPathOfFiles(subject_input_path, *params)[0]
				except:
					self.controller.b_freesurfer_rois.set(False)
					errors.append('Subject [%s] is missing aparc+aseg.mgz/T1.mgz file. PALS will not run Lesionload calculation on Free Surfer ROIs'%subject)

		errors = '\n'.join(errors)

		self.controller.updateGUI(errors)
		return flag


	def getT1NLesionFromInput(self, subject):
		subject_input_path = os.path.join(self.input_directory, subject)
		params = (subject, self.anatomical_id, '', '.nii')
		anatomical_file_path =  self._getPathOfFiles(subject_input_path, *params)

		params = (subject, self.lesion_mask_id, '', '.nii')
		lesion_files = self._getPathOfFiles(subject_input_path, *params)

		return anatomical_file_path, lesion_files


	def createQCPage(self):
		self.logger.info('Visual QC module has been initiated.')
		images_dir = os.path.join(self.getBaseDirectory(), 'QC_Lesions')
		os.makedirs(images_dir)

		for subject in self.subjects:
			anatomical_file_path, lesion_files = self.getT1NLesionFromInput(subject)
			for counter, lesion_file in enumerate(lesion_files):
				cog = self.com.runFslStats(lesion_file, '-C')
				x,y,z=cog.split(' ')
				x=int(x)
				y=int(y)
				z=int(z)

				output_image_path = os.path.join(self.getBaseDirectory(), 'QC_Lesions', '%s_Lesion%d.png'%(subject, counter+1))
				self.com.runFslEyes2(anatomical_file_path[0], lesion_file, '', x, y, z, output_image_path)

		html_file_path = generateQCPage('Lesions', images_dir)
		self.printQCPageUrl('createQCPage', html_file_path, pause=False)
		self.logger.info('QC Page generation completed')


	def _copyDirectories(self, source_dir, dest_dir):
		for item in os.listdir(source_dir):
			if os.path.isdir(os.path.join(source_dir, item)):
				continue
				os.makedirs(os.path.join(dest_dir, item))
				self._copyDirecories(os.path.join(source_dir, item), os.path.join(dest_dir, item))
			elif item.endswith('.nii') or item.endswith('.nii.gz') or item == 'T1.mgz' or item == 'aparc+aseg.mgz':
				copyfile(os.path.join(source_dir, item), os.path.join(dest_dir, item))
			else:
				pass

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
		self.logger.info('Lesion file binarization initiated')
		for subject in self.subjects:
			self._binarizeLesionFilesForSubject(subject)
		self.logger.info('Lesion files of all subjects binarized successfully')

	def _normaliseSubject(self, arg_1, arg_2, arg_3):
		minimum, maximum = self.com.runFslStats(arg_1, '-R')
		scaling = 255.0/(maximum - minimum)
		# intNorm.nii.gz is created with runFslMath
		self.com.runFslMath(arg_1, minimum, scaling, os.path.join(arg_3, arg_2))

	def normaliseT1Intensity(self, anatomical_id):
		if self.skip: return False
		self.logger.info('Intensity normalization of subjects initiated')

		for subject in self.subjects:
			if not self.controller.b_radiological_convention.get():
				arg_1 = os.path.join(self.getOriginalPath(subject), subject + '*' + anatomical_id + '*.nii.gz')
			else:
				arg_1 = os.path.join(self.getSubjectPath(subject), subject + '*' + anatomical_id + '.nii.gz')
			arg_2 = subject + '_' + anatomical_id
			arg_3 = os.path.join(self.getIntermediatePath(subject))
			self._normaliseSubject(arg_1, arg_2, arg_3)
		self.logger.info('Intensity normalization completed for all subjects')

		anatomical_id = (anatomical_id + '_intNorm')
		return anatomical_id

	def createOutputSubjectDirectories(self, base_input_directory, base_output_directory, only_iterate=False):
		if self.skip: return False
		all_input_directories = os.listdir(base_input_directory)
		for directory in all_input_directories:
			if os.path.isdir(os.path.join(base_input_directory, directory)):
				if only_iterate:
					self.subjects.append(directory)
					continue
				output_directory = os.path.join(base_output_directory, directory)
				if os.path.exists(output_directory):
					rmtree(output_directory)
				os.makedirs(output_directory)
				input_directory = os.path.join(base_input_directory, directory)
				self._createOriginalFiles(input_directory, output_directory)
		self.subjects.sort()


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
		roi_codes = []
		for roi in roi_options:
			if roi.get():
				roi_name = roi.name
				if roi_name in mapping:
					roi_file = mapping[roi_name][1]
					roi_codes.append(mapping[roi_name][0])
					full_path = os.path.join(self.controller.getProjectDirectory(), 'ROIs', roi_file)
					roi_paths.append(full_path)
		return (roi_paths, roi_codes)

	def _getDefaultROIsPaths(self):
		all_rois = self.controller.default_corticospinal_tract_roi\
					+ self.controller.default_freesurfer_cortical_roi\
					+ self.controller.default_freesurfer_subcortical_roi

		roi_paths = self._getRoiFilePaths(all_rois, FS_CT_Map)[0]
		roi_paths = self._getRoiFilePaths(all_rois, FS_SCT_Map)[0]
		roi_paths += self._getRoiFilePaths(all_rois, CT_Map)[0]

		# Add additional ROIs that user provided
		roi_paths += self.controller.default_custom_rois

		roi_paths = list(set(roi_paths))

		self.controller.default_roi_paths = roi_paths
		return roi_paths

	def _getFSROIsPaths(self):
		fs_roi_options = self.controller.freesurfer_cortical_roi\
						+ self.controller.freesurfer_subcortical_roi

		if self.controller.b_freesurfer_rois.get():
			fs_roi_paths, fs_roi_codes = self._getRoiFilePaths(fs_roi_options, FS_CT_Map)
			fs_roi_paths_s, fs_roi_codes_s = self._getRoiFilePaths(fs_roi_options, FS_SCT_Map)

			fs_roi_paths += fs_roi_paths_s
			fs_roi_codes += fs_roi_codes_s

		else:
			fs_roi_paths = []
			fs_roi_codes = []

		self.controller.fs_roi_paths = fs_roi_paths
		self.controller.fs_roi_codes = fs_roi_codes
		return fs_roi_paths

	def _getUserROIsPaths(self):
		user_roi_paths = [roi_holder.get() for roi_holder in self.controller.user_rois]
		self.controller.user_roi_paths = user_roi_paths
		return user_roi_paths

	def createROIDirectories(self):
		if self.skip: return False
		self.logger.info('Creating Directories')
		if self.controller.b_wm_correction.get():
			self._createDirectory('QC_LesionCorrection')
			if not self.controller.b_wm_segmentation.get(): self._createDirectory('QC_WMSegmentations')
		if self.controller.b_wm_correction.get() or self.controller.b_ll_calculation.get():
			if not self.controller.b_brain_extraction.get(): self._createDirectory('QC_BrainExtractions')
		if self.controller.b_ll_calculation.get():
			self._createDirectory('QC_LesionLoad')
			self._createDirectory('QC_Registrations')

			# User gave a list of ROIs paths
			if self.controller.b_own_rois.get():
				self._createDirectory('custom', parent=['QC_LesionLoad'])
				self._createDirectory('ROI_binarized')
				# the following takes all of the user input ROIs and binarizes
				# them; placing them in "/ROI_binarized" directory
				for user_roi_path in self._getUserROIsPaths():
					roi_name = self._extractFileName(user_roi_path, remove_extension=True, extension_count=2)

					self._createDirectory(roi_name, parent=['QC_LesionLoad', 'custom'])
					roi_output_path = os.path.join(self.getBaseDirectory(), 'ROI_binarized', roi_name + '_bin')
					self.com.runFslBinarize(user_roi_path, roi_output_path)

				roi_output_directory = os.path.join(self.getBaseDirectory(), 'ROI_binarized')
				params = ('', '', '_bin.nii.gz')

				#get fullpath of all binarized user input ROIs
				user_rois_output_paths = self._getPathOfFiles(roi_output_directory, *params)

				self._createDirectory('custom', parent=['QC_Registrations'])

			# Default ROIs
			if self.controller.b_default_rois.get():
				self._createDirectory('MNI152', parent=['QC_LesionLoad'])
				for default_roi_path in self._getDefaultROIsPaths():
					roi_name = self._extractFileName(default_roi_path, remove_extension=True, extension_count=2)

					self._createDirectory(roi_name, parent=['QC_LesionLoad', 'MNI152'])
				self._createDirectory('MNI152', parent=['QC_Registrations'])

			# FreeSurfer specific ROIs
			if self.controller.b_freesurfer_rois.get():
				self._createDirectory('FS', parent=['QC_LesionLoad'])
				for fs_roi_path in self._getFSROIsPaths():
					roi_name = self._extractFileName(fs_roi_path, remove_extension=True, extension_count=2)
					self._createDirectory(roi_name, parent=['QC_LesionLoad', 'FS'])
				self._createDirectory('FS', parent=['QC_Registrations'])
		self.logger.info('ROIs directory created successfully')

	def reOrientToRadForAllSubjects(self):
		if not self.controller.b_radiological_convention.get() or self.skip: return False
		self.logger.info('Reorient to radiological module initiated.')
		new_subjects = []
		failed_subjects = []
		for subject in self.subjects:
			keepSubject = self._reOrientToRadForSubject(subject)
			if not keepSubject:
				failed_subjects.append(subject)
				self.logger.info('The subject contains error. Check that files are in the same orientation for subject [%s]', subject)
			else:
				new_subjects.append(subject)
		self.logger.info('Reorient to radiological has been completed for all subjects.')
		self.subjects = new_subjects
		self.subjects.sort()

		if len(failed_subjects) > 0:
			with open(os.path.join(self.getBaseDirectory(), 'check_subj_orientations.txt'), 'w') as f:
				f.write('\n'.join(failed_subjects))

		anatomical_id = (self.controller.sv_t1_id.get() + '_rad_reorient')
		lesion_mask_id = ['lesion','_rad_reorient']

		return anatomical_id, lesion_mask_id


	def _reOrientToRadForSubject(self, subject):
		if self.skip: return False
		subject_dir = self.getIntermediatePath(subject)

		# take in the original T1 and lesion mask images
		params = (subject, self.controller.sv_t1_id.get(), '.nii.gz')
		original_t1_file = self._getPathOfFiles(self.getOriginalPath(subject), *params)[0]
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
			if original_bet_orientation != original_t1_orientation:
				self.logger.info('Brain mask is in a different orientation from T1. Check subject %s'%subject)
				# flag subject
				return False

		# if user has already performed own wm segmentation
		if self.controller.b_wm_segmentation.get():
			params = (subject, self.controller.sv_wm_id.get(), '', '.nii.gz')
			original_wm_file = self._getPathOfFiles(self.getOriginalPath(subject), *params)[0]
			rad_wm_file = self._getPathOfFiles(self.getOriginalPath(subject), *params)[0]
			original_wm_orientation =self.com.runFslOrient(original_wm_file)
			if original_wm_orientation != original_t1_orientation:
				self.logger.info('White matter mask is in a different orientation from T1.Check subject %s'%subject)
				# flag subject
				return False

		for index, original_lesion_file in enumerate(original_lesion_files):
			original_lesion_orientation = self.com.runFslOrient(original_lesion_file)
			if original_lesion_orientation != original_t1_orientation:
				self.logger.info('Lesion is in a different orientation from T1. Check subject %s'%subject)
				# flag subject
				return False


		# at this point, only subjects that have files all in the same orientation are retained
		# now change all files from neurological -> radiological

		if original_t1_orientation == 'NEUROLOGICAL':
			output_file_path = os.path.join(self.getIntermediatePath(subject), subject + '_' + self.controller.sv_t1_id.get() + '_rad')
			self.com.runFslSwapDim(original_t1_file, output_file_path)
			self.com.runFslOrient(output_file_path + '.nii.gz', args='-swaporient')
			rad_t1_file = os.path.join(self.getIntermediatePath(subject), subject + '_' + self.controller.sv_t1_id.get() + '_rad.nii.gz')

			if self.controller.b_brain_extraction.get():
				output_file_path = os.path.join(self.getIntermediatePath(subject), subject + '_' + self.controller.sv_bet_id.get() + '_rad')
				self.com.runFslSwapDim(original_bet_file, output_file_path)
				self.com.runFslOrient(output_file_path, args='-swaporient')
				rad_bet_file = output_file_path + '.nii.gz'

			if self.controller.b_wm_segmentation.get():
				output_file_path = os.path.join(self.getIntermediatePath(subject), subject + '_' + self.controller.sv_wm_id.get() + '_rad')
				self.com.runFslSwapDim(original_wm_file, output_file_path)
				self.com.runFslOrient(output_file_path, args='-swaporient')
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
			# if white matter correction will be performed, then the lesions are in the intermediate_files directory because there will be new lesion files output from WM corr
			output_path = os.path.join(self.getIntermediatePath(subject), subject + '_lesion' + str(index + 1) + '_rad_reorient')
			self.com.runFslOrient2Std(lesion_file, output_path)

		return True

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
