from name_var_store import NameVarStore

CorticospinalTractROINames = ['Left Corticospinal Tract',
	'Right Corticospinal Tract']

CorticospinalTractROINamesToFileMapping = {
	'Left Corticospinal Tract': ['0', 'roi_L_CST.nii.gz'],\
	'Right Corticospinal Tract': ['0', 'roi_R_CST.nii.gz']
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
 	'Left Bank of the Superior Temporal Sulcus' : ['1001', 'roi_FS_L_Bankssts.nii.gz'],\
	'Right Bank of the Superior Temporal Sulcus': ['1002', 'roi_FS_L_Caudalanteriorcingulate.nii.gz'],\
	'Left Caudal Anterior Cingulate'   			: ['1003', 'roi_FS_L_Caudalmiddlefrontal.nii.gz'],\
	'Right Caudal Anterior Cingulate'  			: ['1005', 'roi_FS_L_Cuneus.nii.gz'],\
	'Left Caudal Middle Frontal'       			: ['1006', 'roi_FS_L_Entorhinal.nii.gz'],\
	'Right Caudal Middle Frontal'      			: ['1032', 'roi_FS_L_Frontalpole.nii.gz'],\
	'Left Cuneus'                      			: ['1007', 'roi_FS_L_Fusiform.nii.gz'],\
	'Right Cuneus'                     			: ['1008', 'roi_FS_L_Inferiorparietal.nii.gz'],\
	'Left Entorhinal'                  			: ['1009', 'roi_FS_L_Inferiortemporal.nii.gz'],\
	'Right Entorhinal'                 			: ['1035', 'roi_FS_L_Insula.nii.gz'],\
	'Left Frontal Pole'                			: ['1010', 'roi_FS_L_Isthmuscingulate.nii.gz'],\
	'Right Frontal Pole'               			: ['1011', 'roi_FS_L_Lateraloccipital.nii.gz'],\
	'Left Fusiform'                    			: ['1012', 'roi_FS_L_Lateralorbitofrontal.nii.gz'],\
	'Right Fusiform'                   			: ['1013', 'roi_FS_L_Lingual.nii.gz'],\
	'Left Inferior Parietal'           			: ['1014', 'roi_FS_L_Medialorbitofrontal.nii.gz'],\
	'Right Inferior Parietal'          			: ['1015', 'roi_FS_L_Middletemporal.nii.gz'],\
	'Left Inferior Temporal'           			: ['1017', 'roi_FS_L_Paracentral.nii.gz'],\
	'Right Inferior Temporal'          			: ['1016', 'roi_FS_L_Parahippocampal.nii.gz'],\
	'Left Insula'                      			: ['1018', 'roi_FS_L_Parsopercularis.nii.gz'],\
	'Right Insula'                     			: ['1019', 'roi_FS_L_Parsorbitalis.nii.gz'],\
	'Left Isthmus Cingulate'           			: ['1020', 'roi_FS_L_Parstriangularis.nii.gz'],\
	'Right Isthmus Cingulate'          			: ['1021', 'roi_FS_L_Pericalcarine.nii.gz'],\
	'Left Lateral Occipital'           			: ['1022', 'roi_FS_L_Postcentral.nii.gz'],\
	'Right Lateral Occipital'          			: ['1023', 'roi_FS_L_Posteriorcingulate.nii.gz'],\
	'Left Lateral Orbitofronal'        			: ['1024', 'roi_FS_L_Precentral.nii.gz'],\
	'Right Lateral Orbitofronal'       			: ['1025', 'roi_FS_L_Precuneus.nii.gz'],\
	'Left Lingual'                     			: ['1026', 'roi_FS_L_Rostralanteriorcingulate.nii.gz'],\
	'Right Lingual'                    			: ['1027', 'roi_FS_L_Rostralmiddlefrontal.nii.gz'],\
	'Left Medial Orbitofrontal'        			: ['1028', 'roi_FS_L_Superiorfrontal.nii.gz'],\
	'Right Medial Orbitofrontal'       			: ['1029', 'roi_FS_L_Superiorparietal.nii.gz'],\
	'Left Middle Temporal'             			: ['1030', 'roi_FS_L_Superiortemporal.nii.gz'],\
	'Right Middle Temporal'            			: ['1031', 'roi_FS_L_Supramarginal.nii.gz'],\
	'Left Paracentral'                 			: ['1033', 'roi_FS_L_Temporalpole.nii.gz'],\
	'Right Paracentral'                			: ['1034', 'roi_FS_L_Transversetemporal.nii.gz'],\
	'Left Parahippocampal'             			: ['2001', 'roi_FS_R_Bankssts.nii.gz'],\
	'Right Parahippocampal'            			: ['2002', 'roi_FS_R_Caudalanteriorcingulate.nii.gz'],\
	'Left Pars Opercularis'            			: ['2003', 'roi_FS_R_Caudalmiddlefrontal.nii.gz'],\
	'Right Pars Opercularis'           			: ['2005', 'roi_FS_R_Cuneus.nii.gz'],\
	'Left Pars Orbitalis'              			: ['2006', 'roi_FS_R_Entorhinal.nii.gz'],\
	'Right Pars Orbitalis'             			: ['2032', 'roi_FS_R_Frontalpole.nii.gz'],\
	'Left Pars Triangularis'           			: ['2007', 'roi_FS_R_Fusiform.nii.gz'],\
	'Right Pars Triangularis'          			: ['2008', 'roi_FS_R_Inferiorparietal.nii.gz'],\
	'Left Pericalcarine'               			: ['2009', 'roi_FS_R_Inferiortemporal.nii.gz'],\
	'Right Pericalcarine'              			: ['2035', 'roi_FS_R_Insula.nii.gz'],\
	'Left Post Central'                			: ['2010', 'roi_FS_R_Isthmuscingulate.nii.gz'],\
	'Right Post Central'               			: ['2011', 'roi_FS_R_Lateraloccipital.nii.gz'],\
	'Left Posterior Cingulate'         			: ['2012', 'roi_FS_R_Lateralorbitofrontal.nii.gz'],\
	'Right Posterior Cingulate'        			: ['2013', 'roi_FS_R_Lingual.nii.gz'],\
	'Left Precentral'                  			: ['2014', 'roi_FS_R_Medialorbitofrontal.nii.gz'],\
	'Right Precentral'                 			: ['2015', 'roi_FS_R_Middletemporal.nii.gz'],\
	'Left Precuneus'                   			: ['2017', 'roi_FS_R_Paracentral.nii.gz'],\
	'Right Precuneus'                  			: ['2016', 'roi_FS_R_Parahippocampal.nii.gz'],\
	'Left Rostral Anterior Cingulate'  			: ['2018', 'roi_FS_R_Parsopercularis.nii.gz'],\
	'Right Rostral Anterior Cingulate' 			: ['2019', 'roi_FS_R_Parsorbitalis.nii.gz'],\
	'Left Rostral Middle Frontal'      			: ['2020', 'roi_FS_R_Parstriangularis.nii.gz'],\
	'Right Rostral Middle Frontal'     			: ['2021', 'roi_FS_R_Pericalcarine.nii.gz'],\
	'Left Superior Frontal'            			: ['2022', 'roi_FS_R_Postcentral.nii.gz'],\
	'Right Superior Frontal'           			: ['2023', 'roi_FS_R_Posteriorcingulate.nii.gz'],\
	'Left Superior Parietal'           			: ['2024', 'roi_FS_R_Precentral.nii.gz'],\
	'Right Superior Parietal'          			: ['2025', 'roi_FS_R_Precuneus.nii.gz'],\
	'Left Superior Temporal'           			: ['2026', 'roi_FS_R_Rostralanteriorcingulate.nii.gz'],\
	'Right Superior Temporal'          			: ['2027', 'roi_FS_R_Rostralmiddlefrontal.nii.gz'],\
	'Left Supramarginal'               			: ['2028', 'roi_FS_R_Superiorfrontal.nii.gz'],\
	'Right Supramarginal'              			: ['2029', 'roi_FS_R_Superiorparietal.nii.gz'],\
	'Left Temporal Pole'               			: ['2030', 'roi_FS_R_Superiortemporal.nii.gz'],\
	'Right Temporal Pole'              			: ['2031', 'roi_FS_R_Supramarginal.nii.gz'],\
	'Left Transverse Temporal'         			: ['2033', 'roi_FS_R_Temporalpole.nii.gz'],\
	'Right Transverse Temporal'        			: ['2034', 'roi_FS_R_Transversetemporal.nii.gz']
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

FreesurferSubCorticalROINamesToFileMapping = {
	'Left Accumbens'		: ['26', 'roi_FS_L_Accumbens.nii.gz'],
	'Right Accumbens'		: ['58', 'roi_FS_R_Accumbens.nii.gz'],
	'Left Amygdala'			: ['18', 'roi_FS_L_Amygdala.nii.gz'],
	'Right Amygdala'		: ['54', 'roi_FS_R_Amygdala.nii.gz'],
	'Left Caudate'			: ['11', 'roi_FS_L_Caudate.nii.gz'],
	'Right Caudate'			: ['50', 'roi_FS_R_Caudate.nii.gz'],
	'Left Hippocampus'		: ['17', 'roi_FS_L_Hippocampus.nii.gz'],
	'Right Hippocampus'		: ['53', 'roi_FS_R_Hippocampus.nii.gz'],
	'Left Pallidum'			: ['13', 'roi_FS_L_Pallidum.nii.gz'],
	'Right Pallidum'		: ['52', 'roi_FS_R_Pallidum.nii.gz'],
	'Left Putamen'			: ['12', 'roi_FS_L_Putamen.nii.gz'],
	'Right Putamen'			: ['51', 'roi_FS_R_Putamen.nii.gz'],
	'Left Thalamus'			: ['10', 'roi_FS_L_Thalamus.nii.gz'],
	'Right Thalamus'		: ['49', 'roi_FS_R_Thalamus.nii.gz']
}

def createObjectArrays(controller, names):
	output = []
	for name in names:
		output.append(NameVarStore(controller, name))
	return output

def getROIs(controller):
	return (createObjectArrays(controller, CorticospinalTractROINames),\
			createObjectArrays(controller, FreesurferCorticalROINames),\
			createObjectArrays(controller, FreesurferSubcorticalROINames))

