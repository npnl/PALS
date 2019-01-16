import os
from .qc_page import generateQCPage

from .base_operation import BaseOperation

class WMSegmentationOperation(BaseOperation):
	def runWMSegmentation(self, anatomical_id, lesion_mask_id):
		# Skip this step if user has already performed brain extraction
		if self.controller.b_wm_segmentation.get() == True or self.skip: self.incrementStage(); return False

		image_files_base = os.path.join(self.getBaseDirectory(), 'QC_WMSegmentations')

		self.logger.info('White matter segmentation has been initiated')
		for subject in self.subjects:
			try:
				anatomical_file_path, lesion_files = self._setSubjectSpecificPaths_1(subject, anatomical_id, lesion_mask_id)
				((t1_mgz, seg_file), bet_brain_file, wm_mask_file) = self._setSubjectSpecificPaths_2(subject)

				self.com.runFast(os.path.join(self.getIntermediatePath(subject), subject), bet_brain_file)

				image_path = os.path.join(image_files_base, subject + '_WM.png')
				self.com.runFslEyes(anatomical_file_path, wm_mask_file, image_path)
			except:
				pass

		html_file_path = generateQCPage('WM', image_files_base)
		self.printQCPageUrl('WM Segmentation', html_file_path)
		self.logger.info('White matter segmentation completed for all subjects')
