import os
from .qc_page import generateQCPage
from .base_operation import BaseOperation

class LesionCorrectionOperation(BaseOperation):
	def runLesionCorrection(self, anatomical_id, lesion_mask_id):
		self.logger.info('Lesion correction has been initiated.')
		max_lesions = 0
		subject_info_all = []
		for subject in self.subjects:
			subject_info = [subject]

			anatomical_file_path, lesion_files = self._setSubjectSpecificPaths_1(subject, anatomical_id, lesion_mask_id)
			((t1_mgz, seg_file), bet_brain_file, wm_mask_file) = self._setSubjectSpecificPaths_2(subject)

			if not self.com.runFslMathToCheckInSameSpace(wm_mask_file, lesion_files[0], os.path.join(self.getIntermediatePath(subject), subject + '_corrWM')):
				self.logger.info('Check Image Orientations for T1 and Lesion Mask. Skipping Subject: %s'%subject)
				subject_info.append('Skipped')
				continue

			# assign the new wm seg file (with lesion removed) to corrWM
			corrected_wm_file = os.path.join(self.getIntermediatePath(subject), subject + '_corrWM.nii.gz')
			output_file = os.path.join(self.getIntermediatePath(subject), subject + '_NormRangeWM')
			# set values for healthy WM removal
			# multiply WM mask by intensity normalized T1
			self.com.runFslWithArgs(anatomical_file_path, corrected_wm_file, output_file, '-mul')
			wm_mean = self.com.runFslStats(output_file, '-M')

			lesion_files_count = len(lesion_files)

			if max_lesions < lesion_files_count:
				max_lesions = lesion_files_count
				self.logger.debug('Updated num of max lesions : ' + str(max_lesions))

			total_native_brain_volume = self.com.runBrainVolume(bet_brain_file)

			subject_info.append(total_native_brain_volume)
			subject_info.append(wm_mean)

			for counter, lesion_file in enumerate(lesion_files):
				# calculate original and white matter adjusted lesion volumes
				original_lesion_vol = self.com.runBrainVolume(lesion_file)
				skip_subject, corrected_lesion_volume, wm_adjusted_lesion = self._lesionCorrection(subject, counter+1, wm_mean, anatomical_file_path, lesion_file)
				if skip_subject:
					self.logger.log('Check Image Orientations for T1 and Lesion Mask. Skipping Subject: ' + subject)
					subject_info.append('Skipped')
					continue

				volume_removed = original_lesion_vol - corrected_lesion_volume
				percent_removed = volume_removed*1.0/total_native_brain_volume

				#determine side of lesion
				#this gets the center of gravity of the lesion using the mni coord and then extracts the first char of the X coordinate
				lesion_side = self.com.runFslStats(lesion_file, '-c')

				subject_info.append(lesion_side)
				subject_info.append(original_lesion_vol)
				subject_info.append(corrected_lesion_volume)
				subject_info.append(volume_removed)
				subject_info.append(percent_removed)

				cog = self.com.runFslStats(lesion_file, '-C')
				x,y,z=cog.split(' ')
				x=int(x)
				y=int(y)
				z=int(z)

				output_image_path = os.path.join(self.getBaseDirectory(), 'QC_LesionCorrection', '%s_WMAdjLesion%d.png'%(subject, counter+1))
				self.com.runFslEyes2(anatomical_file_path, lesion_file, wm_adjusted_lesion, x, y, z, output_image_path)
		subject_info_all.append(subject_info)

		header = ['Subject', 'Total_Native_Brain_Volume', 'Mean_White_Matter_Intensity']
		for lesion_counter in range(max_lesions):

			lesion_num=str(lesion_counter+1)
			header.append('Lesion%s_Hemisphere'%lesion_num)
			header.append('Lesion%s_Original_Lesion_Volume'%lesion_num)
			header.append('Lesion%s_Corrected_Lesion_Volume'%lesion_num)
			header.append('Lesion%s_Volume_Removed'%lesion_num)
			header.append('Lesion%s_Percent_Removed'%lesion_num)

		# Write data to the csv file
		subject_info_with_header = [header] + subject_info_all
		self.com.runAppendToCSV(subject_info_with_header, os.path.join(self.getBaseDirectory(), 'lesion_correction_database.csv'))

		image_files_base = os.path.join(self.getBaseDirectory(), 'QC_LesionCorrection')
		html_file_path = generateQCPage('Lesions', image_files_base)
		self.printQCPageUrl('Lesion Correction', html_file_path)

		self.logger.info('Lesion correction completed for all subjects')
		lesion_mask_id = 'WMAdjusted'
		return lesion_mask_id


	def _lesionCorrection(self, subject, lesion_counter, wm_mean, anatomical_file_path, lesion_file):

		rm_percentage = self.controller.percent_intensity / 100.0
		voxel_range = (rm_percentage * 255)/2.0

		lower = wm_mean - voxel_range
		upper = wm_mean + voxel_range

		corrected_lesion_volume = 0.0
		output_bin_file = ''
		skip_subject = False

		normRange_file = os.path.join(self.getIntermediatePath(subject), '%s_Lesion%d_NormRange'%(subject, lesion_counter))

		if self.com.runFslWithArgs(anatomical_file_path, lesion_file, normRange_file, '-mul') == '':

			lower_lesion = os.path.join(self.getIntermediatePath(subject), '%s_WMAdjusted_lesion%d_lower'%(subject, lesion_counter))
			upper_lesion = os.path.join(self.getIntermediatePath(subject), '%s_WMAdjusted_lesion%d_upper'%(subject, lesion_counter))

			final_output_file = os.path.join(self.getIntermediatePath(subject), '%s_WMAdjusted_lesion%d'%(subject, lesion_counter))

			self.com.runFslWithArgs(normRange_file, lower, lower_lesion, '-uthr')
			self.com.runFslWithArgs(normRange_file, upper, upper_lesion, '-thr')
			self.com.runFslWithArgs(upper_lesion, lower_lesion, final_output_file, '-add')
			output_bin_file = os.path.join(self.getSubjectPath(subject), '%s_WMAdjusted_lesion%d_bin'%(subject, lesion_counter))
			self.com.runFslBinarize(final_output_file, final_output_file)
			corrected_lesion_volume = self.com.runBrainVolume(final_output_file)
			self.logger.info('The Corrected lesion volume is [%f]'%corrected_lesion_volume)

		else:
			self.logger.info('Check Image Orientations for T1 and Lesion Mask. Skipping Subject: %s'%subject)
			skip_subject = True
		return skip_subject, corrected_lesion_volume, final_output_file
