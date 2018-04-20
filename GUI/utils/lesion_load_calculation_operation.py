import os
from qc_page import generateQCPage
from base_operation import BaseOperation

class LesionLoadCalculationOperation(BaseOperation):
	def runLesionLoadCalculation(self):
		# Skip this step if user did not ask to perform this operation
		if self.controller.b_ll_calculation.get() == False or self.skip: return False

		# Need to fix these
		brain_file = None
		space = None
		self._runLesionLoadCalculationHelper(brain_file, space)

		image_files_base = os.path.join(self.getBaseDirectory(), 'QC_Registrations', space)
		generateQCPage('Registration', image_files_base)
		self.logger.info('Lesion Load Calculation completed for all subjects')

	def _runLesionLoadCalculationHelper(self, brain_file, space):
		roi_list = []
		if space == 'custom':
			roi_list = []
		elif space == 'MNI152':
			roi_list = []
		else:
			pass

		max_lesions = 0
		for subject in self.subjects:
			subject_info = [subject]
			anatomical_file_path, lesion_files = self._setSubjectSpecificPaths_1(subject)
			((t1_mgz, seg_file), bet_brain_file, wm_mask_file) = self._setSubjectSpecificPaths_2(subject)

			self.logger.info('Preforming registration...')

			reg_brain_file = os.path.join(self.getIntermediatePath(subject), '%s_Reg_brain_%s'%(subject, space))
			reg_file = os.path.join(self.getIntermediatePath(subject), '%s_Reg_%s.mat'%(subject, space))

			self.com.runFlirt(bet_brain_file, brain_file, reg_brain_file, reg_file)
			out_image_path = os.path.join(self.getBaseDirectory(), 'QC_Regitrations', space, '%s_Reg.png'%subject)
			self.com.runFslEyes(out_image_path, reg_brain_file + '.nii.gz', options='')

			lesion_files_count = len(lesion_files)

			if max_lesions < lesion_files_count:
				max_lesions = lesion_files_count
				self.logger.debug('Updated num of max lesions : ' + str(max_lesions))

			for counter, lesion_file in enumerate(lesion_files):
				lesion_name = self._extractFileName(self, lesion_file, remove_extension=True, extension_count=2)
				self.logger.info('Registering lesion to template space...')
				lesion_ss_file = os.path.join(self.getBaseDirectory(), '%s_%s_SS.nii.gz'%(lesion_name, space))
				cmd = 'flirt -in %s -applyxfm -init %s -out %s -paddingsize 0.0 -interp trilinear -ref %s'%(lesion_file, reg_file, lesion_ss_file, reg_brain_file)
				self.com.runRawCommand(cmd)

				ss_lesion_volume = self.com.runBrainVolume(lesion_file)
				subject_info.append(ss_lesion_volume)

				lesion_ss_file_output = os.path.join(self.getBaseDirectory(), '%s_SS.nii.gz'%lesion_name)
				self.com.runFslmathsOnLesionFile(lesion_ss_file, lesion_ss_file_output)

				lesion_bin = lesion_ss_file
				cog = self.com.runFslStats(lesion_ss_file, '-V')

				for roi_file in roi_list:
					roi_name = self._extractFileName(self, roi_file, remove_extension=True, extension_count=2)
					roi_volume = self.com.runFslStats(roi_file, '-V')

					#add the two binarized masks together
					output_file = os.path.join(self.getIntermediatePath(subject), '%s_combined_%s_lesion%d_%s.nii.gz'%(subject, roi_name, counter, space))
					self.com.runFslWithArgs(roi_file, lesion_bin, '', option='-add')
					

					#now that two binarized masks are added, the overlapping regions will have a value of 2 so we threshold the image to remove any region that isn't overlapping
					output_file_2 = os.path.join(self.getIntermediatePath(subject), '%s_%s_lesion%d_overlap_%s.nii.gz'%(subject, roi_name, counter, space))
					self.com.runFslWithArgs(output_file, '2', output_file_2, '-thr')

					lesion_load = self.com.runFslStats(output_file_2, '-V')

					image_output_path = os.path.join(self.getBaseDirectory(), 'QC_LL', space, roi_name, subject + '_LL.png')
					cmd = 'fsleyes render -hl -vl %s --hideCursor -of %s %s %s -cm blue -a 50 %s -cm copper -a 40'(cog, image_output_path, reg_brain_file + '.nii.gz', lesion_bin, roi_file)
					self.com.runRawCommand(cmd)

					subject_info.append(roi_volume)
					subject_info.append(lesion_load)



