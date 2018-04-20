import os
from qc_page import generateQCPage

from base_operation import BaseOperation

class SubOperation(BaseOperation):
	def runWMSegmentation(self):
		# Skip this step if user has already performed brain extraction
		if self.controller.b_wm_segmentation.get() == True or self.skip: return False
		for subject in self.subjects:
			anatomical_file_path, lesion_files = self._setSubjectSpecificPaths_1(subject)
			((t1_mgz, seg_file), bet_brain_file, wm_mask_file) = self._setSubjectSpecificPaths_2(subject)
			
			self.com.runFast(os.path.join(self.getIntermediatePath(subject), subject), bet_brain_file)

			image_files_base = os.path.join(self.getBaseDirectory(), 'QC_WM')
			image_path = os.path.join(image_files_base, subject + '_WM.png')
			self.com.runFslEyes(anatomical_file_path, wm_mask_file, image_path)
		generateQCPage('WM', image_files_base)
		self.logger.info('White Matter segmentation completed for all subjects')