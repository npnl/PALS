import os
from qc_page import generateQCPage
from base_operation import BaseOperation

class LesionLoadCalculationOperation(BaseOperation):
	def runLesionLoadCalculation(self, anatomical_id, lesion_mask_id):
		# Skip this step if user did not ask to perform this operation
		if self.controller.b_ll_calculation.get() == False or self.skip: return False

		#standard_brain = self.controller.sv_user_brain_template.get()
		#template_brain = os.path.join(self.getProjectDirectory(), 'ROIs', 'MNI_FS_T1.nii.nii.gz')

		if self.controller.b_own_rois.get() == True:
			space = 'custom'
			template_brain = self.controller.sv_user_brain_template.get()
			self.runReg(template_brain,space,anatomical_id, lesion_mask_id)
			roi_list = self.controller.user_roi_paths
			self._runLesionLoadCalculationHelper(space, roi_list, anatomical_id, lesion_mask_id)

		if self.controller.b_default_rois.get() == True:
			space = 'MNI152'
			template_brain = os.path.join(self.getProjectDirectory(), 'ROIs', 'MNI152_T1_2mm_brain.nii.gz')
			roi_list = self.controller.default_roi_paths
			self.runReg(template_brain,space,anatomical_id, lesion_mask_id)
			self._runLesionLoadCalculationHelper(space, roi_list, anatomical_id, lesion_mask_id)

		if self.controller.b_freesurfer_rois.get() == True:
			space = 'FS'
			template_brain = ''
			self.runReg(template_brain,space,anatomical_id, lesion_mask_id)
			self.runLesionLoadCalculationFS(space)

		image_files_base = os.path.join(self.getBaseDirectory(), 'QC_Registrations', space)
		html_file_path = generateQCPage('Registration', image_files_base)
		self.printQCPageUrl('LL Calculation', html_file_path)
		self.logger.info('Lesion Load Calculation completed for all subjects')
		self.updateProgressBar(8)


	def runReg(self, template_brain, space, anatomical_id, lesion_mask_id):
		self.logger.info('Performing registration...')

		if space == 'MNI152' or space == 'custom':
			#same template brain for all subject; passed in as template_brain
			for subject in self.subjects:
				anatomical_file_path, lesion_files = self._setSubjectSpecificPaths_1(subject, anatomical_id, lesion_mask_id)
				((t1_mgz, seg_file), bet_brain_file, wm_mask_file) = self._setSubjectSpecificPaths_2(subject)

				reg_brain_file = os.path.join(self.getIntermediatePath(subject), '%s_Reg_brain_%s'%(subject, space))
				reg_file = os.path.join(self.getIntermediatePath(subject), '%s_Reg_%s.mat'%(subject, space))

				self.com.runFlirt(bet_brain_file, template_brain, reg_brain_file, reg_file)
				out_image_path = os.path.join(self.getBaseDirectory(), 'QC_Registrations', space, '%s_Reg.png'%subject)
				self.com.runFslEyes(out_image_path, reg_brain_file + '.nii.gz', options='')

		if space == 'FS':
			# new template brain for each subject
			for subject in self.subjects:
				anatomical_file_path, lesion_files = self._setSubjectSpecificPaths_1(subject, anatomical_id, lesion_mask_id)
				((t1_mgz, seg_file), bet_brain_file, wm_mask_file) = self._setSubjectSpecificPaths_2(subject)

				template_brain = os.path.join(self.getIntermediatePath(subject), '%s_FST1.nii.gz'%subject)
				self.com.runMriConvert(t1_mgz, template_brain)

				# perform registration to FS Space for each subject to get transformation matrix
				reg_file = os.path.join(self.getIntermediatePath(subject), '%s_T12FS.xfm'%subject)
				reg_brain_file= os.path.join(self.getIntermediatePath(subject), '%s_T12FS'%subject)
				#cmd = 'flirt -in %s -ref %s -omat %s -out %s;'%(anatomical_file_path, template_brain, reg_file, reg_brain_file)
				#self.com.runRawCommand(cmd)
				self.com.runFlirt(anatomical_file_path, template_brain, reg_brain_file, reg_file)

				output_image_path = os.path.join(self.getBaseDirectory(), 'QC_Registrations', 'FS', '%s_Reg.png'%subject)
				self.com.runFslEyes(out_image_path, reg_brain_file + '.nii.gz', options='')
				#self.com.runFslEyes(reg_brain_file, output_image_path=output_image_path, options='')

				# invert transformation matrix
				xfm_inverse_file = os.path.join(self.getIntermediatePath(subject), '%s_T12FS_inv.xfm'%subject)
				cmd = 'convert_xfm -omat %s %s;'%(xfm_inverse_file, reg_file)
				self.com.runRawCommand(cmd)

		image_files_base = os.path.join(self.getBaseDirectory(), 'QC_Registrations', space)
		generateQCPage('Registration', image_files_base)


	def _runLesionLoadCalculationHelper(self, space, roi_list, anatomical_id, lesion_mask_id):
		all_subjects_info = []
		max_lesions = 0

		for subject in self.subjects:
			subject_info = [subject]
			anatomical_file_path, lesion_files = self._setSubjectSpecificPaths_1(subject, anatomical_id, lesion_mask_id)
			((t1_mgz, seg_file), bet_brain_file, wm_mask_file) = self._setSubjectSpecificPaths_2(subject)

			reg_brain_file = os.path.join(self.getIntermediatePath(subject), '%s_Reg_brain_%s'%(subject, space))
			reg_file = os.path.join(self.getIntermediatePath(subject), '%s_Reg_%s.mat'%(subject, space))


			lesion_files_count = len(lesion_files)

			if max_lesions < lesion_files_count:
				max_lesions = lesion_files_count
				self.logger.debug('Updated num of max lesions : ' + str(max_lesions))

			for counter, lesion_file in enumerate(lesion_files):
				lesion_name = self._extractFileName(lesion_file, remove_extension=True, extension_count=2)
				self.logger.info('Registering lesion to template space...')
				lesion_ss_file = os.path.join(self.getIntermediatePath(subject), '%s_%s.nii.gz'%(lesion_name, space))
				cmd = 'flirt -in %s -applyxfm -init %s -out %s -paddingsize 0.0 -interp trilinear -ref %s'%(lesion_file, reg_file, lesion_ss_file, reg_brain_file)
				self.com.runRawCommand(cmd)

				ss_lesion_volume = self.com.runBrainVolume(lesion_file)
				subject_info.append(ss_lesion_volume)

				lesion_ss_file_output = os.path.join(self.getIntermediatePath(subject), '%s_%s%d_%s_bin.nii.gz'%(subject, lesion_mask_id, counter+1, space))
				self.com.runFslBinarize(lesion_ss_file, lesion_ss_file_output)

				lesion_bin = lesion_ss_file_output
				cog = self.com.runFslStats(lesion_bin, '-C')

				for roi_file in roi_list:
					roi_name = self._extractFileName(roi_file, remove_extension=True, extension_count=2)
					roi_volume = self.com.runBrainVolume(roi_file)

					#add the two binarized masks together
					output_file = os.path.join(self.getIntermediatePath(subject), '%s_combined_%s_lesion%d_%s.nii.gz'%(subject, roi_name, counter+1, space))
					self.com.runFslWithArgs(roi_file, lesion_bin, output_file, option='-add')

					#now that two binarized masks are added, the overlapping regions will have a value of 2 so we threshold the image to remove any region that isn't overlapping
					output_file_2 = os.path.join(self.getIntermediatePath(subject), '%s_%s_lesion%d_overlap_%s.nii.gz'%(subject, roi_name, counter+1, space))
					self.com.runFslWithArgs(output_file, '2', output_file_2, '-thr')

					lesion_load = self.com.runBrainVolume(output_file_2)
					percent_overlap = (lesion_load * 1.0) / roi_volume

					image_output_path = os.path.join(self.getBaseDirectory(), 'QC_LesionLoad', space, roi_name, subject + '_LL.png')
					cmd = 'fsleyes render -hl -vl %s --hideCursor -of %s %s %s -cm blue -a 50 %s -cm copper -a 40'%(cog, image_output_path, reg_brain_file + '.nii.gz', lesion_bin, roi_file)
					self.com.runRawCommand(cmd)

					subject_info.append(roi_volume)
					subject_info.append(lesion_load)
					subject_info.append(percent_overlap)

			all_subjects_info.append(subject_info)
		self._writeToCSV(all_subjects_info, max_lesions, roi_list, space)

	def _writeToCSV(self, subject_info_all, max_lesions, roi_list, space):
		header = ['Subject']
		for lesion_counter in range(max_lesions):
			header.append('Lesion%s_Volume_StandardSpace'%(str(lesion_counter+1)))
			for roi in roi_list:
				roi_name = self._extractFileName(roi, remove_extension=True, extension_count=2)
				header.append('Lesion%s_%s_Volume'%(str(lesion_counter+1), roi_name))
				header.append('Lesion%s_%s_lesionload'%(str(lesion_counter+1), roi_name))
				header.append('Lesion%s_%s_PercentOverlap'%(str(lesion_counter+1),roi_name))

		# Write data to the csv file
		subject_info_with_header = [header] + subject_info_all
		self.com.runAppendToCSV(subject_info_with_header, os.path.join(self.getBaseDirectory(), 'lesion_load_%s_database.csv'%(space)))

		self._generateQCForRois(space, roi_list)


	def _generateQCForRois(self, space, roi_list):
		for roi in roi_list:
			roi_name = self._extractFileName(roi, remove_extension=True, extension_count=2)
			image_files_base = os.path.join(self.getBaseDirectory(), 'QC_LesionLoad', space, roi_name)
			html_file_path = generateQCPage('LL_%s'%(roi_name), image_files_base)
			self.printQCPageUrl('LL Calculation', html_file_path)


	def runLesionLoadCalculationFS(self, space):
		# Skip this step if user did not ask to perform this operation
		# Skip if user does not selected any free surfer rois
		if self.controller.b_ll_calculation.get() == False or\
			self.controller.b_freesurfer_rois.get() == False or self.skip: return False

		roi_codes = self.controller.fs_roi_paths
		max_lesions = 0
		all_subjects_info = []

		for subject in self.subjects:
			subject_info = [subject]

			anatomical_file_path, lesion_files = self._setSubjectSpecificPaths_1(subject)
			((t1_mgz, seg_file), bet_brain_file, wm_mask_file) = self._setSubjectSpecificPaths_2(subject)

			# template_brain = os.path.join(self.getIntermediatePath(subject), '%s_FST1.nii.gz'%subject)
			# self.com.runMriConvert(t1_mgz, template_brain)
			#
			# # perform registration to FS Space for each subject to get transformation matrix
			# reg_file = os.path.join(self.getIntermediatePath(subject), '%s_T12FS.xfm'%subject)
			# reg_brain_file= os.path.join(self.getIntermediatePath(subject), '%s_T12FS.nii.gz'%subject)
			# cmd = 'flirt -in %s -ref %s -omat %s -out %s;'%(anatomical_file_path, template_brain, reg_file, reg_brain_file)
			# self.com.runRawCommand(cmd)
			#
			# output_image_path = os.path.join(self.getBaseDirectory(), 'QC_Registrations', 'FS', '%s_Reg.png'%subject)
			# self.com.runFslEyes(reg_brain_file, output_image_path=output_image_path, options='')
			#
			# # invert transformation matrix
			# xfm_inverse_file = os.path.join(self.getIntermediatePath(subject), '%s_T12FS_inv.xfm'%subject)
			# cmd = 'convert_xfm -omat %s %s;'%(xfm_inverse_file, reg_file)
			# self.com.runRawCommand(cmd)

			lesion_files_count = len(lesion_files)

			if max_lesions < lesion_files_count:
				max_lesions = lesion_files_count
				self.logger.debug('Updated num of max lesions : ' + str(max_lesions))

			xfm_inverse_file = os.path.join(self.getIntermediatePath(subject), '%s_T12FS_inv.xfm'%subject)
			reg_brain_file = os.path.join(self.getIntermediatePath(subject), '%s_T12FS.nii.gz'%subject)

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
				cmd = 'flirt -in %s -init %s -ref %s -out %s -applyxfm;'%(lesion_file, xfm_inverse_file, template_brain, lesion_fs)
				self.com.runRawCommand(cmd)
				self.com.runFslBinarize(lesion_fs, lesion_fs_bin)

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
					percent_overlap = (lesion_load_volume * 1.0) / roi_volume

					subject_info.append(roi_volume)
					subject_info.append(lesion_load_volume)
					subject_info.append(percent_overlap)

					ll_png = os.path.join(self.getBaseDirectory(), 'QC_LesionLoad', 'FS', 'roi%d'%roi_code, '%s_LL.png'%subject)
					cmd = 'fsleyes render -hl -vl %s --hideCursor -of %s  %s %s -cm blue -a 50 %s -cm copper -a 40;'%(cog, ll_png, reg_brain_file, lesion_fs_bin, new_binary_file)
					self.com.runRawCommand(cmd)

			subject_info_all.append(subject_info)

		self._writeToCSV2(subject_info_all, max_lesions, roi_codes, space)


	def _writeToCSV2(self, subject_info_all, max_lesions, roi_list, space):
		header = ['Subject']
		for lesion_counter in range(max_lesions):
			header.append('Lesion%s_Volume_FSSpace'%str(lesion_counter+1))
			for roi in roi_list:
				roi_name = self._extractFileName(roi, remove_extension=True, extension_count=2)
				header.append('roi%s_Volume'%(roi_name))
				header.append('Lesion%s_roi%s_lesionload'%(str(lesion_counter+1), roi_name))
				header.append('Lesion%s_roi%s_PercentOverlap'%(str(lesion_counter+1), roi_name))


		# Write data to the csv file
		subject_info_with_header = [header] + subject_info_all
		self.com.runAppendToCSV(subject_info_with_header, os.path.join(self.getBaseDirectory(), 'lesion_load_%s_database.csv'%(space)))
		self._generateQCForRois(space, roi_list)
		self.updateProgressBar(8)
