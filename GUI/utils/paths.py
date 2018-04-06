import os
from shutil import copyfile, rmtree

from commands import Commands
com = Commands()

class Operations(object):
	def __init__(self, controller):
		self.controller = controller

		self.initialiseConstants()

	def initialiseConstants(self):
		self.subjects = []
		self.input_directory = self.controller.sv_input_dir.get()
		self.output_directory = self.controller.sv_output_dir.get()
		self.output_directories = []

		self.INTERMEDIATE_FILES = 'Intermediate_Files'
		self.ORIGINAL_FILES = os.path.join(self.INTERMEDIATE_FILES,'Original_Files')


	def initialise(self):
		self.createOutputSubjectDirectories(self.input_directory, self.output_directory, self.controller.sv_t1_id.get())

	def _copyDirectories(self, source_dir, dest_dir):
		for item in os.listdir(source_dir):
			if os.path.isdir(os.path.join(source_dir, item)):
				os.makedirs(os.path.join(dest_dir, item))
				self._copyDirecories(os.path.join(source_dir, item), os.path.join(dest_dir, item))
			else:
				copyfile(os.path.join(source_dir, item), os.path.join(dest_dir, item))

	def _createOriginalFiles(self, source_dir, target_dir):
		target_dir = os.path.join(target_dir, self.ORIGINAL_FILES)
		os.makedirs(target_dir)
		self._copyDirectories(source_dir, target_dir)

	def intermediatePath(self, subject):
		return os.path.join(self.base_output_directory, subject, self.INTERMEDIATE_FILES)

	def originalPath(self, subject):
		return os.path.join(self.intermediatePath(subject), self.ORIGINAL_FILES)

	def _runGzip(self, directory):
		com.runGzip(directory)

	def _normaliseSubject(self, arg1, arg2, arg3):
		minimum, maximum = com.runFslStat(arg1)
		scaling = 255.0/(maximum - minimum)
		com.runFslMath(arg1, minimum, scalling, os.path.join(arg_3, arg2))

	def _fslmathsOnLesionFile(self):
		pass

	def processLesionFiles(self, subject):
		# LesionFiles=`ls ${SUBJECTOPDIR}/Intermediate_Files/Original_Files/$1*${LESION_MASK}*.nii.gz`;

		#   count=1;
		#   for lesion in $LesionFiles; do
		#       fslmaths $lesion -bin ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_${LESION_MASK}${count}_bin.nii.gz;
		#       count=$((count+1));
		#   done
		subject_dir = self.originalPath(subject)
		counter = 1
		lesion_mask_id = controller.sv_lesion_mask_id.get()
		for item in os.listdir(subject_dir):
			if lesion_mask_id in item:
				lesion_file_path = os.path.join(subject_dir, item)
				output_bin_path = os.path.join(self.intermediatePath(subject), subject + '_' + lesion_mask_id + str(counter) + '_bin.nii.gz')
				com.runFslmathsOnLesionFile(lesion_file_path, output_bin_path)
				counter += 1



	def normaliseT1Intensity(self, t1_identifier):
		for subject in self.subjects:
			arg_1 = os.path.join(self.output_directory, self.ORIGINAL_FILES, subject + '*' + t1_identifier + '*.nii.gz')
			arg_2 = subject + '_' + t1_identifier
			arg_3 = os.path.join(self.output_directory, subject, self.INTERMEDIATE_FILES)

	def createOutputSubjectDirectories(self, base_input_directory, base_output_directory, identifier):
		all_input_directories = os.listdir(base_input_directory)
		for directory in all_input_directories:
			print directory
			if os.path.isdir(os.path.join(base_input_directory, directory)) and directory.startswith(identifier):
				self.subjects.append(directory)
				output_directory = os.path.join(base_output_directory, directory)
				if os.path.exists(output_directory):
					rmtree(output_directory)
				os.makedirs(output_directory)
				input_directory = os.path.join(base_input_directory, directory)
				self._createOriginalFiles(input_directory, output_directory)

	def getTemplateBrainROIS(self):
		parent_dir =  os.path.abspath(os.path.join(os.getcwd(), os.pardir))
		template_roi_dir = os.path.join(parent_dir, 'ROIs')
		template_rois = None
		for item in os.listdir(template_roi_dir):
			if item.startswith('MNI152_T1_2mm_brain'):
				template_rois = os.path.join(template_roi_dir, item)
				break
		return template_rois

def isValidPath(filePath):
	if os.path.exists(filePath):
		pass
	elif os.access(os.path.dirname(filePath), os.W_OK):
		pass
	else:
		return False
	return True

if __name__ == '__main__':
	directory = raw_input("Enter directory")
	_runGzip(directory)