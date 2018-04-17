from name_var_store import NameVarStore

CorticospinalTractROINames = ['Left Corticospinal Tract',
	'Right Corticospinal Tract']

CorticospinalTractROINamesToFileMapping = {
	'Left Corticospinal Tract': 'roi_L_CST_bin.nii.gz',\
	'Right Corticospinal Tract': 'roi_R_CST_bin.nii.gz'
}

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

FreesurferCorticalROINamesToFileMapping = {
 	'Left Bank of the Superior Temporal Sulcus': 'roi_FS_L_Bankssts.nii.gz',\
	'Right Bank of the Superior Temporal Sulcus': 'roi_FS_L_Caudalanteriorcingulate.nii.gz',\
	'Left Caudal Anterior Cingulate'   : 'roi_FS_L_Caudalmiddlefrontal.nii.gz',\
	'Right Caudal Anterior Cingulate'  : 'roi_FS_L_Cuneus.nii.gz',\
	'Left Caudal Middle Frontal'       : 'roi_FS_L_Entorhinal.nii.gz',\
	'Right Caudal Middle Frontal'      : 'roi_FS_L_Frontalpole.nii.gz',\
	'Left Cuneus'                      : 'roi_FS_L_Fusiform.nii.gz',\
	'Right Cuneus'                     : 'roi_FS_L_Inferiorparietal.nii.gz',\
	'Left Entorhinal'                  : 'roi_FS_L_Inferiortemporal.nii.gz',\
	'Right Entorhinal'                 : 'roi_FS_L_Insula.nii.gz',\
	'Left Frontal Pole'                : 'roi_FS_L_Isthmuscingulate.nii.gz',\
	'Right Frontal Pole'               : 'roi_FS_L_Lateraloccipital.nii.gz',\
	'Left Fusiform'                    : 'roi_FS_L_Lateralorbitofrontal.nii.gz',\
	'Right Fusiform'                   : 'roi_FS_L_Lingual.nii.gz',\
	'Left Inferior Parietal'           : 'roi_FS_L_Medialorbitofrontal.nii.gz',\
	'Right Inferior Parietal'          : 'roi_FS_L_Middletemporal.nii.gz',\
	'Left Inferior Temporal'           : 'roi_FS_L_Paracentral.nii.gz',\
	'Right Inferior Temporal'          : 'roi_FS_L_Parahippocampal.nii.gz',\
	'Left Insula'                      : 'roi_FS_L_Parsopercularis.nii.gz',\
	'Right Insula'                     : 'roi_FS_L_Parsorbitalis.nii.gz',\
	'Left Isthmus Cingulate'           : 'roi_FS_L_Parstriangularis.nii.gz',\
	'Right Isthmus Cingulate'          : 'roi_FS_L_Pericalcarine.nii.gz',\
	'Left Lateral Occipital'           : 'roi_FS_L_Postcentral.nii.gz',\
	'Right Lateral Occipital'          : 'roi_FS_L_Posteriorcingulate.nii.gz',\
	'Left Lateral Orbitofronal'        : 'roi_FS_L_Precentral.nii.gz',\
	'Right Lateral Orbitofronal'       : 'roi_FS_L_Precuneus.nii.gz',\
	'Left Lingual'                     : 'roi_FS_L_Rostralanteriorcingulate.nii.gz',\
	'Right Lingual'                    : 'roi_FS_L_Rostralmiddlefrontal.nii.gz',\
	'Left Medial Orbitofrontal'        : 'roi_FS_L_Superiorfrontal.nii.gz',\
	'Right Medial Orbitofrontal'       : 'roi_FS_L_Superiorparietal.nii.gz',\
	'Left Middle Temporal'             : 'roi_FS_L_Superiortemporal.nii.gz',\
	'Right Middle Temporal'            : 'roi_FS_L_Supramarginal.nii.gz',\
	'Left Paracentral'                 : 'roi_FS_L_Temporalpole.nii.gz',\
	'Right Paracentral'                : 'roi_FS_L_Transversetemporal.nii.gz',\
	'Left Parahippocampal'             : 'roi_FS_R_Bankssts.nii.gz',\
	'Right Parahippocampal'            : 'roi_FS_R_Caudalanteriorcingulate.nii.gz',\
	'Left Pars Opercularis'            : 'roi_FS_R_Caudalmiddlefrontal.nii.gz',\
	'Right Pars Opercularis'           : 'roi_FS_R_Cuneus.nii.gz',\
	'Left Pars Orbitalis'              : 'roi_FS_R_Entorhinal.nii.gz',\
	'Right Pars Orbitalis'             : 'roi_FS_R_Frontalpole.nii.gz',\
	'Left Pars Triangularis'           : 'roi_FS_R_Fusiform.nii.gz',\
	'Right Pars Triangularis'          : 'roi_FS_R_Inferiorparietal.nii.gz',\
	'Left Pericalcarine'               : 'roi_FS_R_Inferiortemporal.nii.gz',\
	'Right Pericalcarine'              : 'roi_FS_R_Insula.nii.gz',\
	'Left Post Central'                : 'roi_FS_R_Isthmuscingulate.nii.gz',\
	'Right Post Central'               : 'roi_FS_R_Lateraloccipital.nii.gz',\
	'Left Posterior Cingulate'         : 'roi_FS_R_Lateralorbitofrontal.nii.gz',\
	'Right Posterior Cingulate'        : 'roi_FS_R_Lingual.nii.gz',\
	'Left Precentral'                  : 'roi_FS_R_Medialorbitofrontal.nii.gz',\
	'Right Precentral'                 : 'roi_FS_R_Middletemporal.nii.gz',\
	'Left Precuneus'                   : 'roi_FS_R_Paracentral.nii.gz',\
	'Right Precuneus'                  : 'roi_FS_R_Parahippocampal.nii.gz',\
	'Left Rostral Anterior Cingulate'  : 'roi_FS_R_Parsopercularis.nii.gz',\
	'Right Rostral Anterior Cingulate' : 'roi_FS_R_Parsorbitalis.nii.gz',\
	'Left Rostral Middle Frontal'      : 'roi_FS_R_Parstriangularis.nii.gz',\
	'Right Rostral Middle Frontal'     : 'roi_FS_R_Pericalcarine.nii.gz',\
	'Left Superior Frontal'            : 'roi_FS_R_Postcentral.nii.gz',\
	'Right Superior Frontal'           : 'roi_FS_R_Posteriorcingulate.nii.gz',\
	'Left Superior Parietal'           : 'roi_FS_R_Precentral.nii.gz',\
	'Right Superior Parietal'          : 'roi_FS_R_Precuneus.nii.gz',\
	'Left Superior Temporal'           : 'roi_FS_R_Rostralanteriorcingulate.nii.gz',\
	'Right Superior Temporal'          : 'roi_FS_R_Rostralmiddlefrontal.nii.gz',\
	'Left Supramarginal'               : 'roi_FS_R_Superiorfrontal.nii.gz',\
	'Right Supramarginal'              : 'roi_FS_R_Superiorparietal.nii.gz',\
	'Left Temporal Pole'               : 'roi_FS_R_Superiortemporal.nii.gz',\
	'Right Temporal Pole'              : 'roi_FS_R_Supramarginal.nii.gz',\
	'Left Transverse Temporal'         : 'roi_FS_R_Temporalpole.nii.gz',\
	'Right Transverse Temporal'        : 'roi_FS_R_Transversetemporal.nii.gz'
 }

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