import os
from qc_page import generateQCPage
from base_operation import BaseOperation

class WMCorrectionOperation(BaseOperation):
	def runWMCorrection(self):
		max_lesions = 0
		for subject in self.subjects:
			anatomical_file_path, lesion_files = self._setSubjectSpecificPaths_1(subject)
			((t1_mgz, seg_file), bet_brain_file, wm_mask_file) = self._setSubjectSpecificPaths_2(subject)

			if not self.com.runFslMathToCheckInSameSpace(wm_mask_file, lesion_file[0], os.path.join(self.getIntermediatePath(subject), subject + '_corrWM')):
				self.logger.info('Check Image Orientations for T1 and Lesion Mask. Skipping Subject: %s'%subject)
				# Need to add equivivalent code
				# printf "${SUBJ} Skipped\n" >> "$WORKINGDIR"/lesion_data.csv;
				continue

			# assign the new wm seg file (with lesion removed) to corrWM
			corrected_wm_file = os.path.join(self.getIntermediatePath(subject), subject + '_corrWM.nii.gz')
			output_file = os.path.join(self.getIntermediatePath(subject), subject + '_NormRangeWM')
			# set values for healthy WM removal
			# multiply WM mask by intensity normalized T1
			self.com.runFslWithArgs(anatomical_file_path, corrected_wm_file, output_file, '-mul')
			wm_mean = self.com.runFslStats(output_file, '-M')

			lesion_files_count = len(self._getPathOfFiles(self, self.getSubjectPath(subject), startswith_str=subject, substr=self.controller.sv_lesion_mask_id.get(), endswith_str='', second_sub_str='.nii'))

			if max_lesions < lesion_files_count:
				max_lesions = lesion_files_count
				self.logger.debug('Updated num of max lesions : ' + str(max_lesions))

			subject_info_list = {}
			total_native_brain_volume = self.com.runBrainVolume(bet_brain_file)
			subject_info_list[subject] = [total_native_brain_volume, wm_mean]

			for counter, lesion_file in enumerate(lesion_files):
				# calculate original and white matter adjusted lesion volumes
				original_lesion_vol = self.com.runBrainVolume(lesion_file)
				corrected_lesion_volume, wm_adjusted_lesion = self._wmCorrection(subject, counter+1, wm_mean, anatomical_file_path, lesion_file)
				volume_removed = original_lesion_vol - corrected_lesion_volume
				percent_removed = volume_removed*1.0/total_native_brain_volume

				#determine side of lesion
				#this gets the center of gravity of the lesion using the mni coord and then extracts the first char of the X coordinate
				lesion_cog = self.com.runFslStats(lesion, '-c')
				lesion_side = 'L' if lesion_cog.startswith('-') else 'R'

				subject_info_list[subject].append(lesion_side)
				subject_info_list[subject].append(original_lesion_vol)
				subject_info_list[subject].append(corrected_lesion_volume)
				subject_info_list[subject].append(volume_removed)
				subject_info_list[subject].append(percent_removed)

				cog = ' '.join(map(int, map(round, self.com.runFslStats(lesion, '-C').strip().split())))

				self.com.runFslEyes2(anatomical_file_path, lesion_file, wm_adjusted_lesion, cog, output_image_path)
				data = ','.join(map(str, subject_info_list[subject]))
				self.com.runAppendToCSV(data, os.path.join(self.getBaseDirectory(), 'lesion_data.csv'))

		image_files_base = os.path.join(self.getBaseDirectory(), 'QC_Lesions')
		generateQCPage('lesion', image_files_base)
		self.logger.info('White Matter correction completed for all subjects')


	def _wmCorrection(self, subject, lesion_counter, wm_mean, anatomical_file_path, lesion_file):

		lower = wm_mean - self.controller.voxal_range
		upper = wm_mean + self.controller.voxal_range

		corrected_lesion_volume = 0.0

		output_file = os.path.join(self.getIntermediatePath(subject), '%s_Lesion%d_NormRange'%(subject, lesion_counter))
		if self.com.runFslWithArgs(anatomical_file_path, corrected_wm_file, output_file, '-mul'):

			lower_lesion = os.path.join(self.getIntermediatePath(subject), '%s_WMAdjusted_Lesion%d_lower'%(subject, lesion_counter))
			upper_lesion = os.path.join(self.getIntermediatePath(subject), '%s_WMAdjusted_Lesion%d_upper'%(subject, lesion_counter))

			final_output_file = os.path.join(self.getIntermediatePath(subject), '%s_WMAdjusted_Lesion%d'%(subject, lesion_counter))

			self.com.runFslWithArgs(output_file, lower, lower_lesion, '-uthr')
			self.com.runFslWithArgs(output_file, upper, upper_lesion, '-thr')
			self.com.runFslWithArgs(upper_lesion, lower_lesion, final_output_file, '-add')
			output_bin_file = os.path.join(self.getSubjectPath(subject), '%s_WMAdjusted_Lesion%d_bin'%(subject, counter))
			self.com.runFslmathsOnLesionFile(final_output_file, output_bin_file)
			corrected_lesion_volume = self.com.runBrainVolume(output_bin_file)
			self.logger.info('The Corrected lesion volume is [%f]'%corrected_lesion_volume)

		else:
			self.logger.info('Check Image Orientations for T1 and Lesion Mask. Skipping Subject: %s'%subject)
			# Need to add equivivalent code
			# printf "${SUBJ} Skipped\n" >> "$WORKINGDIR"/lesion_data.csv;
		return corrected_lesion_volume, output_bin_file


# This part is still pending
# #################################[ ADD HEADER TO DATAFILE ]###############################

# 	cd $WORKINGDIR;
# 	declare -a HeaderArray;
# 	HeaderArray=(Subject "Total_Native_Brain_Volume" "Mean_White_Matter_Intensity");

# 	for i in $(seq 1 $maxlesions); do
# 		HeaderArray+=(Lesion${i}_Hemisphere);
# 		HeaderArray+=(Lesion${i}_Original_Lesion_Volume);
# 		HeaderArray+=(Lesion${i}_Corrected_Lesion_Volume);
# 		HeaderArray+=(Lesion${i}_Volume_Removed);
# 		HeaderArray+=(Lesion${i}_Percent_Removed);
# 	done

# 	StringArray=$(IFS=, ; echo "${HeaderArray[*]}")

# 	awk -v env_var="${StringArray}" 'BEGIN{print env_var }{print}' lesion_data.csv > lesion_database.csv;

# 	rm $WORKINGDIR/lesion_data.csv;

