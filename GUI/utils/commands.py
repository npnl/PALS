import os
import subprocess

class Commands(object):
	def __init__(self, logger):
		self.logger = logger

	def startExecution(self, cmd):
		self.logger.debug("Running [%s]"%cmd)
		self.running_process = subprocess.Popen('exec ' + cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
		return_code = self.running_process.wait()
		output = ''
		for stdout_line in iter(self.running_process.stdout.readline, ""):
			output += stdout_line
		self.running_process.stdout.close()
		# if return_code:
		# 	raise subprocess.CalledProcessError(return_code, cmd)
		self.logger.debug(output)
		return output

	def runGzip(self, input_directory):
		input_directory = os.path.join(input_directory, '*.nii')
		cmd = "gzip %s > /dev/null 2>&1;"%(input_directory)
		self.startExecution(cmd)


	def runFslStat(self, argument):
		cmd = 'fslstats %s -R'%(argument)
		output = self.startExecution(cmd)
		values = map(float, output.strip().split())
		return values

	def runFslMath(self, arg1, minimum, scalling, arg2):
		cmd_1 = 'fslmaths %s -sub %f -mul %f %s_scaled;'%(arg1, minimum, scalling, arg2)
		cmd_2 = 'fslmaths %s_scaled %s_intNorm.nii.gz -odt char;'%(arg2, arg2)

		output = self.startExecution(cmd_1)
		output = self.startExecution(cmd_2)

	def runFslmathsOnLesionFile(self, lesion_file_path, output_bin_path):
		cmd = 'fslmaths %s -bin %s;'%(lesion_file_path, output_bin_path)
		output = self.startExecution(cmd)
		print output

	def runPlayer(self, input_directory):
		cmd = 'mplayer %s'%(input_directory)
		self.startExecution(cmd)


if __name__ == '__main__':
	com = Commands()
	com.runFslMath("/Users/amit/WorkPro/Lily/data/OUTPUTS_FS/subjC/Intermediate_Files/Original_Files/subjC*T1*.nii.gz",0,0.2849162011173184,"/Users/amit/WorkPro/Lily/data/OUTPUTS_FS/subjC/Intermediate_Files/subjC_T1")


