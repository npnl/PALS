import argparse
import json
import logging
import os
import pathlib
import shutil
import tempfile
from os.path import join

import bids

bids.config.set_option('extension_initial_dot', True)  # future setting

from datetime import datetime
from utils import Application, readApplicationConfigs
from utils import Operations


def setupLogger(debug, is_docker):
	project_path = getProjectDirectory()
	logs_dir = os.path.join('/output', 'logs') if is_docker else os.path.join(project_path, 'logs')
	if not os.path.exists(logs_dir):
		os.makedirs(logs_dir)
	logging.basicConfig(level=logging.DEBUG,
				format='%(asctime)s %(levelname)s %(message)s',
				filename=os.path.join(logs_dir, datetime.now().strftime('logfile_%Y%m%d_%H_%M.log')),
				filemode='w')
	console = logging.StreamHandler()
	if debug:
		console.setLevel(logging.DEBUG)
	else:
		console.setLevel(logging.INFO)
	formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
	console.setFormatter(formatter)
	logging.getLogger('').addHandler(console)
	return logging.getLogger(__name__)


def getProjectDirectory():
	return os.path.dirname(os.path.realpath(__file__))


def silentMode(logger, config_file, need_display):
	project_dir = getProjectDirectory()
	application = Application(logger, project_dir, need_display=need_display)
	readApplicationConfigs(application, config_file)
	operations = Operations(application)
	return operations.startThreads(None)



def uiMode(logger):
	DeprecationWarning('This mode of operation is no longer supported.')
	from gui_init import MainWindow
	project_dir = getProjectDirectory()
	app = MainWindow(logger, project_dir)
	app.mainloop()


def adapt_bids(bids_input: str, bids_lesion: str,
			   lesionmask_derivative_name: str = 'lesionmask',
			   lesionmask_label: str = 'lesionmask') -> str:
	'''
	Creates a temporary structure to change a data structure from BIDS to the expected structure.
	Parameters
	----------
	bids_input : str
		Path to the root directory of the BIDS dataset containing the T1 images.
	bids_lesion : str
		Path to the root directory of the BIDS dataset containing the lesion masks.
	lesionmask_derivative_name : str
		Name of pipeline given to the lesionmask. This is the top-level name for the directory below BIDS/derivatives/.
		Default: 'lesionmask'
	lesionmask_label : str
		Label value for the 'desc' entity identifying the lesion mask. Default: 'lesionmask'
	Returns
	-------
	str
		Path to temporary data directory.
	'''

	# First deal with T1 images; create temp directory, identify T1 images, symlink to data
	data_dir = tempfile.mkdtemp()

	bids_data = bids.BIDSLayout(root=bids_input)
	# Store BIDS objects identifying T1 data
	t1_data = bids_data.get(suffix='T1w')
	tmp = bids.BIDSLayout(root=bids_lesion, derivatives=True)
	lesions = tmp.derivatives.get(lesionmask_derivative_name)

	# For each T1 image, fetch the corresponding lesion mask
	for t1 in t1_data:
		sub = t1.entities['subject']
		ses = t1.entities['session']
		lesion_data = lesions.get(subject=sub, session=ses, desc=lesionmask_label)
		subject_prefix = f'subj{sub}_{ses}_'
		subject_dir = join(data_dir, subject_prefix)
		pathlib.Path(subject_dir).mkdir(parents=True, exist_ok=True)
		ext = t1.entities['extension']
		os.symlink(join(t1.dirname, t1.filename), join(subject_dir, f'{subject_prefix}_T1{ext}'))

		for ind, les in enumerate(lesion_data):
			ext = les.entities['extension']
			if(ind == 0):
				os.symlink(join(les.dirname, les.filename), join(subject_dir, f'{subject_prefix}_Lesion{ext}'))
			else:
				os.symlink(join(les.dirname, les.filename), join(subject_dir, f'{subject_prefix}_Lesion{ind}{ext}'))
	return data_dir


def convert_subj_to_bids(subj: str, return_sub: bool = False) -> str:
	'''
	Converts PALS's adapted subj[subject_id]_[session_id]_* naming convention to BIDS.
	Parameters
	----------
	subj : str
		PALS name starting with 'subj'
	return_sub : bool
		If True, return subject ID and session along with the filename.
	Returns
	-------
	str
		BIDS filename.
	str
		If return_sub is set to true, return subject_id as second value.
	str
		If return_sub is set to true, return session_id as third value.
	'''

	first_ = subj.index('_')
	second_ = subj.index('_', first_ + 1)
	subid = subj[4:first_]
	sesid = subj[first_ + 1:second_]
	desc = subj[second_ + 1:].replace('-', '')
	desc = desc.replace('_', '')
	if(not return_sub):
		return f'sub-{subid}_ses-{sesid}_desc-{desc}'
	else:
		return f'sub-{subid}_ses-{sesid}_desc-{desc}', subid, sesid


if __name__ == '__main__':
	# Parse arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--debug', help='Set the logging level as DEBUG', action='store_true')
	parser.add_argument('-c', '--config',
						help='Pass a config file to the application. Default config file is [config.json] in current directory',
						default='')
	parser.add_argument('--docker',
						help='Create a virtual display for fsleyes and fsl binaries in dockerized environment',
						action='store_true')
	parser.add_argument('-b', '--bids', help='Whether to treat input/lesion directories as BIDS directories',
						action='store_true')
	parser.add_argument('-s', help='DEPRECATED. Backwards-compatibility for ''silent'' running. Has no effect.')
	arguments = parser.parse_args()

	# BIDS parsing
	# Note: This bit of code converts BIDS -> PALS using symlinks and a temporary config file, then feeds it to PALS.
	# Later parts of the code then take PALS output and converts it to BIDS.
	# This is sub-optimal and likely to cause errors if there are any modifications to the original code.
	if(arguments.bids):
		# Load config file
		if(arguments.config == ''):
			conf = 'config.json'
		else:
			conf = arguments.config
		configs = json.load(open(conf, 'r'))

		# Get input/lesion settings
		input_dir = configs['common_settings']['input_dir']
		# If defined in config file, take it from there; otherwise assume it's in the same BIDS dir as input
		if('lesion_dir' in configs['common_settings']):
			lesion_dir = configs['common_settings']['lesion_dir']
		else:
			lesion_dir = input_dir

		if('lesionmask_derivative_name' in configs['common_settings']):
			lesionmask_derivative_name = configs['common_settings']['lesionmask_derivative_name']
		else:
			lesionmask_derivative_name = 'lesionmask'
		lesionmask_label = configs['common_settings']['lesion_mask_id']

		# Send to BIDS adapter
		intermediate_dir = adapt_bids(bids_input=input_dir,
									  bids_lesion=lesion_dir,
									  lesionmask_derivative_name=lesionmask_derivative_name,
									  lesionmask_label=lesionmask_label)
		pals_output = tempfile.mkdtemp()
		# Need to modify config file.
		configs['common_settings']['input_dir'] = intermediate_dir
		configs['common_settings']['lesion_mask_id'] = 'Lesion'
		configs['common_settings']['t1_id'] = 'T1'
		configs['common_settings']['output_dir'] = pals_output
		config_file = join(intermediate_dir, 'config.json')
		json.dump(configs, open(config_file, 'w'))

	debug = arguments.debug
	docker = arguments.docker
	logger = setupLogger(debug, docker)
	if(not arguments.bids):
		config_file = arguments.config

	if config_file == '':
		logger.info('Using the default [config.json] file for application configurations as no external config file was passed in commandline arguments')
		config_file = 'config.json'
	else:
		logger.info('Reading application configurations from file [%s]'%(config_file))

	tmp_output_dir = silentMode(logger, config_file, arguments.docker)

	# Convert output to BIDS
	# Note: This bit of code converts PALS -> BIDS
	# This is sub-optimal and likely to cause errors if there are any modifications to the original code or the
	# underlying pipelines.
	if(arguments.bids):
		# Need to convert tmp_output_dir contents to BIDS
		# Data is placed in pals_output/tmp_output_dir
		# Subject/session is set as subj[subject id]_[session]

		output_dir = join(pals_output, tmp_output_dir)
		for dirpath, dirnames, filenames in os.walk(output_dir, topdown=False):
			# Rename files
			for f in filenames:
				if(f.startswith('subj')):
					file = pathlib.Path(join(dirpath, f))
					new_file = convert_subj_to_bids(f)
					file.rename(join(dirpath, new_file))
			for d in dirnames:
				# Rename 'subj'
				if(d.startswith('_subject_id')):
					direct = pathlib.Path(join(dirpath, d))
					newname = d[len('_subject_id_'):]
					new_dir, subid, sesid = convert_subj_to_bids(newname, return_sub=True)
					pathlib.Path(join(dirpath, f'sub-{subid}')).mkdir(exist_ok=True, parents=True)
					pathlib.Path(join(dirpath, d)).rename(join(dirpath, f'sub-{subid}', f'ses-{sesid}'))
				if(d.startswith('subj')):
					direct = pathlib.Path(join(dirpath, d))
					# Directory needs to be split into sub-123/ses-456
					# Create new directory sub-123, then rename direct as sub-123/ses-1
					new_dir, subid, sesid = convert_subj_to_bids(d, return_sub=True)
					pathlib.Path(join(dirpath, f'sub-{subid}')).mkdir(parents=True, exist_ok=True)
					direct.rename(join(dirpath, f'sub-{subid}', f'ses-{sesid}'))
				if(d.startswith('QC_')):
					# Place QC directories together
					pathlib.Path(join(dirpath, 'QC')).mkdir(parents=True, exist_ok=True)
					new_dir = d[3:]
					pathlib.Path(join(dirpath, d)).rename(join(dirpath, 'QC', new_dir))
		# There are top-level .csv files.
		configs = json.load(open(arguments.config, 'r'))
		pathlib.Path(configs['common_settings']['output_dir']).mkdir(parents=True, exist_ok=True)
		shutil.copytree(join(pals_output, tmp_output_dir),
						join(configs['common_settings']['output_dir'], os.path.basename(tmp_output_dir)))
#