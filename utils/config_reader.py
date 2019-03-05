import json

def readConfig(filename):
	with open(filename) as json_data_file:
		data = json.load(json_data_file)
	return data

def readReOrientConfigs(configs, application):
	pass

def readLesionCorrectionConfigs(configs, application):
	pass

def readLesionLoadCalculationConfigs(configs, application):
	try:
		module_settings = configs['module_settings']['Lesion_load_calculation']
		application.b_brain_extraction.set(module_settings['bet_performed'])
		application.sv_bet_id.set(module_settings['bet_identifier'])
		for roi in module_settings['roi_names']['default']['corticospinal_tracts']:
			roi_obj = application.buildRoi(roi)
			application.default_corticospinal_tract_roi.append(roi_obj)

		for roi in module_settings['roi_names']['default']['fs_cortical']:
			roi_obj = application.buildRoi(roi)
			application.default_freesurfer_cortical_roi.append(roi_obj)

		for roi in module_settings['roi_names']['default']['fs_sub_cortical']:
			roi_obj = application.buildRoi(roi)
			application.default_freesurfer_subcortical_roi.append(roi_obj)

		for roi in module_settings['roi_names']['free_surfer']['fs_cortical']:
			roi_obj = application.buildRoi(roi)
			application.freesurfer_cortical_roi.append(roi_obj)

		for roi in module_settings['roi_names']['free_surfer']['fs_sub_cortical']:
			roi_obj = application.buildRoi(roi)
			application.freesurfer_subcortical_roi.append(roi_obj)

		if module_settings['roi_names']['own']['own_rois']:
			application.sv_user_brain_template = application.buildRoi(module_settings['roi_names']['own']['own_rois']["template_brain"])


		for roi in module_settings['roi_names']:
			roi_obj = application.buildRoi(roi)
			application.default_corticospinal_tract_roi.append(roi_obj)
		application.b_default_rois.set(True)
	except Exception as e:
		print('Failed to load lesion load configs : ', str(e))
		

def readApplicationConfigs(application, config_file):
	configs = readConfig(config_file)
	if 'modules' in configs:
		modules = configs['modules']
		if 'Re_orient_radiological' in modules and modules['Re_orient_radiological']:
			application.b_radiological_convention.set(True)
			readReOrientConfigs(configs, application)

		if 'Lesion_correction' in modules and modules['Lesion_correction']:
			application.b_wm_correction.set(True)
			readLesionCorrectionConfigs(configs, application)

		if 'Lesion_load_calculation' in modules and modules['Lesion_load_calculation']:
			application.b_ll_calculation.set(True)
			readLesionLoadCalculationConfigs(configs, application)
	else:
		print('Module selection is missing')

	if 'common_settings' in configs:
		common_configs = configs['common_settings']
		if 'input_dir' in common_configs:
			application.sv_input_dir.set(common_configs['input_dir'])
		else:
			print('Input Directory is missing in configs')

		if 'output_dir' in common_configs:
			application.sv_output_dir.set(common_configs['output_dir'])
		else:
			print('Output Directory is missing in configs')

		if 't1_id' in common_configs:
			application.sv_t1_id.set(common_configs['t1_id'])
		else:
			print('T1 Anatomical Identifier is missing in configs')

		if 'lesion_mask_id' in common_configs:
			application.sv_lesion_mask_id.set(common_configs['lesion_mask_id'])
		else:
			print('Lesion Mask Identifier is missing in configs')

		if 'same_anatomical_space' in common_configs:
			application.b_same_anatomical_space.set(common_configs['same_anatomical_space'])
		else:
			print('Same Anatomical Space flag is missing in configs')
	else:
		print('Common configs missing')


	application.b_visual_qc.set(False)
	application.b_pause_for_qc.set(False)


def setApplicationVariables(controller, configs):
	if 'modules' in configs:
		modules = configs['modules']
		if 'Re_orient_radiological' in modules and modules['Re_orient_radiological']:
			application.b_radiological_convention.set(True)
		if 'Lession_correction' in modules and modules['Lession_correction']:
			controller.b_wm_correction.set(True)
		if 'Lesion_load_calculation' in modules and modules['Lesion_load_calculation']:
			controller.b_ll_calculation.set(True)
	else:
		print('Module selection is missing')

	# Set common parameters
	if 'common_settings' in configs:
		common_configs = configs['common_settings']
		if 'input_dir' in common_configs:
			controller.sv_input_dir.set(common_configs['input_dir'])
		else:
			print('Input Directory is missing in configs')

		if 'output_dir' in common_configs:
			controller.sv_output_dir.set(common_configs['output_dir'])
		else:
			print('Output Directory is missing in configs')

		if 't1_id' in common_configs:
			controller.sv_t1_id.set(common_configs['t1_id'])
		else:
			print('T1 Anatomical Identifier is missing in configs')

		if 'lesion_mask_id' in common_configs:
			controller.sv_lesion_mask_id.set(common_configs['lesion_mask_id'])
		else:
			print('Lesion Mask Identifier is missing in configs')

		if 'same_anatomical_space' in common_configs:
			controller.b_same_anatomical_space.set(common_configs['same_anatomical_space'])
		else:
			print('Same Anatomical Space flag is missing in configs')
	else:
		print('Common configs missing')

	controller.b_visual_qc.set(False)
	controller.b_pause_for_qc.set(False)