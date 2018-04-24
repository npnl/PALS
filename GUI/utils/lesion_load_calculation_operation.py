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


class LesionLoadCalculationFSOperation(BaseOperation):
	def runLesionLoadCalculation(self):
		if self.controller.b_ll_calculation.get() == False or self.skip: return False

		roi_codes = self.controller.roi_codes;

		for subject in self.subjects:
			subject_info = [subject]

			anatomical_file_path, lesion_files = self._setSubjectSpecificPaths_1(subject)
			((t1_mgz, seg_file), bet_brain_file, wm_mask_file) = self._setSubjectSpecificPaths_2(subject)

			fs_t1 = os.path.join(self.getIntermediatePath(subject), '%s_FST1.nii.gz'%subject)
			self.com.runMriConvert(t1_mgz, fs_t1)

			# perform registration to FS Space for each subject to get transformation matrix
			xfm_file = os.path.join(self.getIntermediatePath(subject), '%s_T12FS.xfm'%subject)
			t12_fs_output_file = os.path.join(self.getIntermediatePath(subject), '%s_T12FS.nii.gz'%subject)
			cmd = 'flirt -in %s -ref %s -omat %s -out %s;'%(anatomical_file_path, fs_t1, xfm_file, t12_fs_output_file)
			self.com.runRawCommand(cmd)

			output_image_path = os.path.join(self.getBaseDirectory(), 'QC_Registrations', 'FS', '%s_Reg.png'%subject)
			self.com.runFslEyes(t12_fs_output_file, output_image_path=output_image_path, options=''):

			# invert transformation matrix
			xfm_inverse_file = os.path.join(self.getIntermediatePath(subject), '%s_T12FS_inv.xfm'%subject)
			cmd = 'convert_xfm -omat %s %s;'%(xfm_inverse_file, xfm_file)
			self.com.runRawCommand(cmd)


			# extract all ROIs for each subj
			for roi_code in roi_codes:
				output_file = os.path.join(self.getIntermediatePath(subject), '%s_aparc+aseg.nii.gz'%subject)
				self.com.runMriConvert(seg_file, output_file)

				binary_file = os.path.join(self.getIntermediatePath(subject), '%s_roi%d.nii.gz'%(subject, roi_code))

				cmd = 'fslmaths %s -thr %d -uthr %d -bin %s;'%(output_file, roi_code, roi_code, binary_file)
				self.com.runRawCommand(cmd)

				# binarize roi
				new_binary_file = os.path.join(self.getIntermediatePath(subject), '%s_roi%d_bin.nii.gz'%(subject, roi_code))
				self.com.runFslWithArgs(arg_1=binary_file, arg_2=new_binary_file, arg_3='', option='-bin')

			for index, lesion_file in enumerate(lesion_files):
				lesion_fs = os.path.join(self.getIntermediatePath(subject), '%s_lesion%d_FS.nii.gz'%(subject, index+1)) 
				lesion_fs_bin = os.path.join(self.getIntermediatePath(subject), '%s_lesion%d_FS_bin.nii.gz')

				# perform transformation on lesion mask, then binarize the mask
				cmd = 'flirt -in %s -init %s -ref %s -out %s -applyxfm;'%(lesion_file, xfm_inverse_file, fs_t1, lesion_fs)
				self.com.runRawCommand(cmd)
				self.com.runFslmathsOnLesionFile(lesion_fs, lesion_fs_bin)

				fs_lesion_volume = self.com.runBrainVolume(lesion_fs_bin)
				subject_info.append(fs_lesion_volume)

				cog = self.com.runFslStats(lesion_fs_bin, '-C')

				for roi_code in roi_codes:
					# add the lesion and roi masks together
					combined_lesion = os.path.join(self.getIntermediatePath(subject), '%s_combined_lesion%d_roi%d.nii.gz'%(subject, index+1, roi_code))
					self.com.runFslWithArgs(arg_1=new_binary_file, arg_2=lesion_fs_bin, arg_3=combined_lesion, option='-add')

					# now that two binarized masks are added, the overlapping regions will have a value of 2 so we threshold the image to remove any region that isn't overlapping
					overlap_file = os.path.join(self.getIntermediatePath(subject), '%s_roi%d_lesion%d_overlap.nii.gz'%(subject, roi_code, index+1))
					self.com.runFslWithArgs(arg_1=combined_lesion, arg_2=overlap_file, arg_3='', option='-thr 1.9')

					lesion_load_volume = self.com.runBrainVolume(overlap_file)
					roi_volume = self.com.runBrainVolume(new_binary_file)

					subject_info.append(roi_volume)
					subject_info.append(lesion_load_volume)
					ll_png = os.path.join(self.getBaseDirectory(), 'QC_LL', 'FS', 'roi%d'%roi_code, '%s_LL.png'%subject)
					cmd = 'fsleyes render -hl -vl %s --hideCursor -of %s  %s %s -cm blue -a 50 %s -cm copper -a 40;'%(cog, ll_png, t12_fs_output_file, lesion_fs_bin, new_binary_file)
					self.com.runRawCommand(cmd)

			# printf '%s,' ${LLArray[@]} >> "$WORKINGDIR"/lesion_load_data.csv;
			# printf '\n' >> "$WORKINGDIR"/lesion_load_data.csv;

		# cd "$WORKINGDIR"/QC_Registrations/FS || exit;
		# makeQCPage Registration;

		# ##############################[ ADD HEADER TO CSV FILE ]##################################

		# cd $WORKINGDIR;
		# declare -a HeaderArray;
		# HeaderArray=(Subject);

		# for i in $(seq 1 $maxlesions); do
		# 	HeaderArray+=(Lesion${i}_Volume_FSSpace);
		# 	for roi in ${FSrois[@]}; do
		# 		HeaderArray+=(roi${roi}_Volume);
		# 		HeaderArray+=(Lesion${i}_roi${roi}_lesionload);
		# 	done

		# done

		# StringArray=$(IFS=, ; echo "${HeaderArray[*]}")

		# awk -v env_var="${StringArray}" 'BEGIN{print env_var}{print}' lesion_load_data.csv > lesion_load_FS_database.csv;

		# rm $WORKINGDIR/lesion_load_data.csv;

		# cd $WORKINGDIR/QC_LL/FS;

		# rois=`ls -d *`;

		# for roi in $rois; do
		# 		cd $roi;
		# 		makeQCPage LL_$roi;
		# 		cd $WORKINGDIR/QC_LL/FS/;
		# done

