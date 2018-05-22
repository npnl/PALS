import os, traceback
from qc_page import generateQCPage
from base_operation import BaseOperation

class BrainExtractionOperation(BaseOperation):
	def runBrainExtraction(self, anatomical_id, lesion_mask_id):
		# Skip this step if user has already performed brain extraction
		if self.controller.b_brain_extraction.get() == True or self.skip: self.incrementStage(); return False
		
		image_files_base = os.path.join(self.getBaseDirectory(), 'QC_BrainExtractions')
		
		self.logger.info('Brain extraction has been initiated')
		for subject in self.subjects:
			try:
				anatomical_file_path, lesion_files = self._setSubjectSpecificPaths_1(subject, anatomical_id, lesion_mask_id)
				((t1_mgz, seg_file), bet_brain_file, wm_mask_file) = self._setSubjectSpecificPaths_2(subject)

				self.com.runBet(anatomical_file_path, os.path.join(self.getIntermediatePath(subject), subject + '_Brain'))

				image_path = os.path.join(image_files_base, subject + '_BET.png')
				self.com.runFslEyes(anatomical_file_path, bet_brain_file, image_path)
			except:
				self.logger.debug(traceback.format_exc())
				pass
		html_file_path = generateQCPage('BET', image_files_base)
		self.printQCPageUrl('Brain extraction', html_file_path)
		self.logger.info('Brain extraction completed for all subjects')
