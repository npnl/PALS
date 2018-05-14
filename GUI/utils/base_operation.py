import os
import ntpath
from shutil import copyfile, rmtree

class BaseOperation():

	def __new__(cls, *args, **kwargs):
		if cls is BaseOperation:
			raise TypeError('BaseOperation may not be instantiated')
		return object.__new__(cls, *args, **kwargs)

	def getBaseDirectory(self):
		return self.output_directory

	def getSubjectPath(self, subject):
		return os.path.join(self.output_directory, subject)

	def getIntermediatePath(self, subject):
		return os.path.join(self.getSubjectPath(subject), self.INTERMEDIATE_FILES)

	def getOriginalPath(self, subject):
		return os.path.join(self.getIntermediatePath(subject), self.ORIGINAL_FILES)

	def updateProgressBar(self, value):
		self.controller.progressbar.step(value)

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
			if self.controller.b_wm_correction.get() or self.controller.b_ll_calculation.get():
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

