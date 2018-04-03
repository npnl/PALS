from name_var_store import NameVarStore

CorticospinalTractROINames = ['Left Corticospinal Tract',
	'Right Corticospinal Tract']

FreesurferCorticalROINames =  ['Left Bank of the Superior Temporal Sulcus', 'Right Bank of the Superior Temporal Sulcus',\
 	'Left Caudal Anterior Cingulate', 'Right Caudal Anterior Cingulate', 'Left Caudal Middle Frontal',\
 	'Right Caudal Middle Frontal', 'Left Cuneus', 'Right Cuneus', 'Left Entorhinal', 'Right Entorhinal',\
 	'Left Frontal Pole', 'Right Frontal Pole', 'Left Fusiform', 'Right Fusiform', 'Left Inferior Parietal',\
 	'Right Inferior Parietal', 'Left Inferior Temporal', 'Right Inferior Temporal', 'Left Insula',\
 	'Right Insula', 'Left Isthmus Cingulate', 'Right Isthmus Cingulate', 'Left Lateral Occipital',\
 	'Right Lateral Occipital', 'Left Lateral Orbitofronal', 'Right Lateral Orbitofronal', 'Left Lingual',\
 	'Right Lingual', 'Left Medial Orbitofrontal', 'Right Medial Orbitofrontal', 'Left Middle Temporal',\
 	'Right Middle Temporal', 'Left Paracentral', 'Right Paracentral', 'Left Parahippocampal',\
 	'Right Parahippocampal', 'Left Pars Opercularis', 'Right Pars Opercularis', 'Left Pars Orbitalis',\
 	'Right Pars Orbitalis', 'Left Pars Triangularis', 'Right Pars Triangularis', 'Left Pericalcarine',\
 	'Right Pericalcarine', 'Left Post Central', 'Right Post Central', 'Left Posterior Cingulate',\
 	'Right Posterior Cingulate', 'Left Precentral', 'Right Precentral', 'Left Precuneus', 'Right Precuneus',\
 	'Left Rostral Anterior Cingulate', 'Right Rostral Anterior Cingulate', 'Left Rostral Middle Frontal',\
 	'Right Rostral Middle Frontal', 'Left Superior Frontal', 'Right Superior Frontal', 'Left Superior Parietal',\
 	'Right Superior Parietal', 'Left Superior Temporal', 'Right Superior Temporal', 'Left Supramarginal',\
 	'Right Supramarginal', 'Left Temporal Pole', 'Right Temporal Pole', 'Left Transverse Temporal',\
 	'Right Transverse Temporal']

FreesurferSubcorticalROINames = [
	'Left Accumbens',
	'Right Accumbens',
	'Left Amygdala',
	'Right Amygdala',
	'Left Caudate',
	'Right Caudate',
	'Left Hippocampus',
	'Right Hippocampus',
	'Left Pallidum',
	'Right Pallidum',
	'Left Putamen',
	'Right Putamen',
	'Left Thalamus',
	'Right Thalamus']

def createObjectArrays(controller, names):
	output = []
	for name in names:
		output.append(NameVarStore(controller, name))
	return output

def getROIs(controller):
	return (createObjectArrays(controller, CorticospinalTractROINames),\
			createObjectArrays(controller, FreesurferCorticalROINames),\
			createObjectArrays(controller, FreesurferSubcorticalROINames))