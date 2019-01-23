import json

def readConfig(filename='config.json'):
	with open(filename) as json_data_file:
		data = json.load(json_data_file)
	return data

def setApplicationVariables(controller, configs):
	if 'modules' in configs:
		modules = configs['modules']
		if 'Re_orient_radiological' in modules and modules['Re_orient_radiological']:
			controller.b_radiological_convention.set(True)
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