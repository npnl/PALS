import os
import logging
import argparse
from datetime import datetime
from PALS.pals_operations import Operations

def parseArguments():
	parser = argparse.ArgumentParser(description='Pipeline for Analyzing Lesions after Stroke. Runs the PALS processing'
                                                 ' pipeline on a BIDS dataset. Preprocessing includes reorientation '
                                                 'to a common direction, registration, brain extraction, white matter '
                                                 'segmentation, lesion correction, and lesion load calculation. Most '
                                                 'options are controlled via the configuration file.')
	parser.add_argument('-s','--silent', help='Starts the PALS tool without showing the UI.', action='store_true')
	parser.add_argument('-d','--debug', help='Set the logging level as DEBUG', action='store_true')
	parser.add_argument('-c', '--config', help='Pass a config file to the application. Default config file is [config.json] in current directory', default='')
	parser.add_argument('--docker', help='Create a virtual display for fsleyes and fsl binaries in dockerized environment', action='store_true')
	parser.add_argument('--root_dir', type=str, help='BIDS root directory containing the data. If set, overrides the'
                                                     ' value in the config file.', default=None, required=False)
	parser.add_argument('--subject', type=str, help='Subject ID; value of the label associated with the "subject" BIDS'
                                                    ' entity. If set, overrides the value in the config file.',
                        default=None, required=False)
	parser.add_argument('--session', type=str, help='Session ID; value of the label associated with the "session" BIDS'
                                                    ' entity. If set, overrides the value in the config file.',
                        default=None)
	parser.add_argument('--lesion_root', type=str, help='Root directory for the BIDS directory containing the lesion '
                                                        'masks. If set, overrides the value in the config file.',
                        default=None)
	#parser.add_argument('--config', type=str, help='Path to the configuration file.', required=True)

	args = parser.parse_args()
	
	return args

def setupLogger(debug, is_docker):
	project_path = getProjectDirectory()
	print(project_path)
	logs_dir = os.path.join('/output', 'logs') if is_docker else os.path.join(project_path, 'logs')
	print(logs_dir)
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

def silentMode(logger, config_file, need_display, pargs):
	project_dir = getProjectDirectory()
	operations = Operations(need_display, config_path=config_file, pargs=pargs)
	operations.startExecution()
	#application = Application(logger, project_dir, need_display=need_display)
	#readApplicationConfigs(application, config_file)
	#operations = Operations(application)
	#operations.startThreads(None)

def uiMode(logger):
	from gui_init import MainWindow
	project_dir = getProjectDirectory()
	app = MainWindow(logger, project_dir)
	app.mainloop()

if __name__ == '__main__':
	arguments = parseArguments()
	
	silent = arguments.silent
	debug = arguments.debug

	docker = arguments.docker

	logger = setupLogger(debug, docker)

	if silent:
		config_file = arguments.config
		if config_file == '':
			logger.info('Using the default [config.json] file for application configurations as no external config file was passed in commandline arguments')
			config_file = 'config.json'
		else:
			logger.info('Reading application configurations from file [%s]'%(config_file))

		silentMode(logger, config_file, arguments.docker, arguments)

	else:
		uiMode(logger)
		