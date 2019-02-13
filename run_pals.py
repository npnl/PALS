import os
import logging
import argparse
from datetime import datetime

from gui_init import MainWindow

from utils import Application, readApplicationConfigs

from utils import Operations

def parseArguments():
	parser = argparse.ArgumentParser()
	parser.add_argument('-q','--silent', help='Starts the PALS tool without showing the UI.', action='store_true')
	parser.add_argument('-d','--debug', help='Set the logging level as DEBUG', action='store_true')
	parser.add_argument('-c', '--config', help='Pass a config file to the application. Default config file is [config.json] in current directory', default='')
	args = parser.parse_args()
	return args

def setupLogger(debug):
	project_path = getProjectDirectory()
	logs_dir = os.path.join(project_path, 'logs')
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

def silentMode(logger, config_file):
	project_dir = getProjectDirectory()
	application = Application(logger, project_dir)
	readApplicationConfigs(application, config_file)
	operations = Operations(application)
	operations.startThreads(None)

def uiMode(logger):
	project_dir = getProjectDirectory()
	app = MainWindow(logger, project_dir)
	app.mainloop()

if __name__ == '__main__':
	arguments = parseArguments()
	
	silent = arguments.silent
	debug = arguments.debug

	logger = setupLogger(debug)

	if silent:
		config_file = arguments.config
		if config_file == '':
			logger.info('Using the default [config.json] file for application configurations as no external config file was passed in commandline arguments')
			config_file = 'config.json'
		else:
			logger.info('Reading application configurations from file [%s]'%(config_file))

		silentMode(logger, config_file)

	else:
		uiMode(logger)
		