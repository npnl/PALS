import os
import ntpath
from shutil import copyfile, rmtree

class BaseOperation():

	def __new__(cls, *args, **kwargs):
		if cls is BaseOperation:
			raise TypeError('Base operation may not be instantiated')
		return object.__new__(cls, *args, **kwargs)

	def getProjectDirectory(self):
		return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

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

	def incrementStage(self):
		self.stage += 1
		self.updateProgressBar((100.0/self.total_stages))

	def updateSubjects(self, new_subjects_file):
		new_subjects = []
		with open(new_subjects_file, 'r') as sub_file:
			new_subjects = sub_file.readlines()
		self.subjects = map(lambda x: x.strip(), new_subjects)

	def printQCPageUrl(self, operation_name, html_path, pause=True):
		pause = pause and self.controller.b_quality_control.get()
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

		print "The params are : ", params

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
		if type(lesion_mask_id) == type([]):
			print lesion_files

		## put in a check here; if there are no T1 and/or lesion files, then set the path to the Original_Files directory.
		if not os.path.exists(anatomical_file_path):
			params = (subject, anatomical_id, '.nii.gz')
			anatomical_file_path =  self._getPathOfFiles(self.getOriginalPath(subject), *params)[0]

		if len(lesion_files) == 0 or not os.path.exists(lesion_files[0]):
			params = (subject, lesion_mask_id, '.nii.gz')
			lesion_files = self._getPathOfFiles(self.getOriginalPath(subject), *params)

		lesion_files = [x for x in lesion_files if 'custom' not in x.lower()]
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
