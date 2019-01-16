from .name_var_store import NameVarStore

CorticospinalTractROINames = ['Left Corticospinal Tract',
	'Right Corticospinal Tract']

CorticospinalTractROINamesToFileMapping = {
	'Left Corticospinal Tract': ['0', 'roi_L_CST_2mm.nii.gz'],\
	'Right Corticospinal Tract': ['0', 'roi_R_CST_2mm.nii.gz']
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
 	'Left Bank of the Superior Temporal Sulcus' : ['1001', 'roi_FS_L_Bankssts_2mm.nii.gz'],\
	'Right Bank of the Superior Temporal Sulcus': ['2001', 'roi_FS_R_Bankssts_2mm.nii.gz'],\
	'Left Caudal Anterior Cingulate'   			: ['1002', 'roi_FS_L_Caudalanteriorcingulate_2mm.nii.gz'],\
	'Right Caudal Anterior Cingulate'  			: ['2002', 'roi_FS_R_Caudalanteriorcingulate_2mm.nii.gz'],\
	'Left Caudal Middle Frontal'       			: ['1003', 'roi_FS_L_Caudalmiddlefrontal_2mm.nii.gz'],\
	'Right Caudal Middle Frontal'      			: ['2003', 'roi_FS_R_Caudalmiddlefrontal_2mm.nii.gz'],\
	'Left Cuneus'                      			: ['1005', 'roi_FS_L_Cuneus_2mm.nii.gz'],\
	'Right Cuneus'                     			: ['2005', 'roi_FS_R_Cuneus_2mm.nii.gz'],\
	'Left Entorhinal'                  			: ['1006', 'roi_FS_L_Entorhinal_2mm.nii.gz'],\
	'Right Entorhinal'                 			: ['2006', 'roi_FS_R_Entorhinal_2mm.nii.gz'],\
	'Left Frontal Pole'                			: ['1032', 'roi_FS_L_Frontalpole_2mm.nii.gz'],\
	'Right Frontal Pole'               			: ['2032', 'roi_FS_R_Frontalpole_2mm.nii.gz'],\
	'Left Fusiform'                    			: ['1007', 'roi_FS_L_Fusiform_2mm.nii.gz'],\
	'Right Fusiform'                   			: ['2007', 'roi_FS_R_Fusiform_2mm.nii.gz'],\
	'Left Inferior Parietal'           			: ['1008', 'roi_FS_L_Inferiorparietal_2mm.nii.gz'],\
	'Right Inferior Parietal'          			: ['2008', 'roi_FS_R_Inferiorparietal_2mm.nii.gz'],\
	'Left Inferior Temporal'           			: ['1009', 'roi_FS_L_Inferiortemporal_2mm.nii.gz'],\
	'Right Inferior Temporal'          			: ['2009', 'roi_FS_R_Inferiortemporal_2mm.nii.gz'],\
	'Left Insula'                      			: ['1035', 'roi_FS_L_Insula_2mm.nii.gz'],\
	'Right Insula'                     			: ['2035', 'roi_FS_R_Insula_2mm.nii.gz'],\
	'Left Isthmus Cingulate'           			: ['1010', 'roi_FS_L_Isthmuscingulate_2mm.nii.gz'],\
	'Right Isthmus Cingulate'          			: ['2010', 'roi_FS_R_Isthmuscingulate_2mm.nii.gz'],\
	'Left Lateral Occipital'           			: ['1011', 'roi_FS_L_Lateraloccipital_2mm.nii.gz'],\
	'Right Lateral Occipital'          			: ['2011', 'roi_FS_R_Lateraloccipital_2mm.nii.gz'],\
	'Left Lateral Orbitofronal'        			: ['1012', 'roi_FS_L_Lateralorbitofrontal_2mm.nii.gz'],\
	'Right Lateral Orbitofronal'       			: ['2012', 'roi_FS_R_Lateralorbitofrontal_2mm.nii.gz'],\
	'Left Lingual'                     			: ['1013', 'roi_FS_L_Lingual_2mm.nii.gz'],\
	'Right Lingual'                    			: ['2013', 'roi_FS_R_Lingual_2mm.nii.gz'],\
	'Left Medial Orbitofrontal'        			: ['1014', 'roi_FS_L_Medialorbitofrontal_2mm.nii.gz'],\
	'Right Medial Orbitofrontal'       			: ['2014', 'roi_FS_R_Medialorbitofrontal_2mm.nii.gz'],\
	'Left Middle Temporal'             			: ['1015', 'roi_FS_L_Middletemporal_2mm.nii.gz'],\
	'Right Middle Temporal'            			: ['2015', 'roi_FS_R_Middletemporal_2mm.nii.gz'],\
	'Left Paracentral'                 			: ['1017', 'roi_FS_L_Paracentral_2mm.nii.gz'],\
	'Right Paracentral'                			: ['2017', 'roi_FS_R_Paracentral_2mm.nii.gz'],\
	'Left Parahippocampal'             			: ['1016', 'roi_FS_L_Parahippocampal_2mm.nii.gz'],\
	'Right Parahippocampal'            			: ['2016', 'roi_FS_R_Parahippocampal_2mm.nii.gz'],\
	'Left Pars Opercularis'            			: ['1018', 'roi_FS_L_Parsopercularis_2mm.nii.gz'],\
	'Right Pars Opercularis'           			: ['2018', 'roi_FS_R_Parsopercularis_2mm.nii.gz'],\
	'Left Pars Orbitalis'              			: ['1019', 'roi_FS_L_Parsorbitalis_2mm.nii.gz'],\
	'Right Pars Orbitalis'             			: ['2019', 'roi_FS_R_Parsorbitalis_2mm.nii.gz'],\
	'Left Pars Triangularis'           			: ['1020', 'roi_FS_L_Parstriangularis_2mm.nii.gz'],\
	'Right Pars Triangularis'          			: ['2020', 'roi_FS_R_Parstriangularis_2mm.nii.gz'],\
	'Left Pericalcarine'               			: ['1021', 'roi_FS_L_Pericalcarine_2mm.nii.gz'],\
	'Right Pericalcarine'              			: ['2021', 'roi_FS_R_Pericalcarine_2mm.nii.gz'],\
	'Left Post Central'                			: ['1022', 'roi_FS_L_Postcentral_2mm.nii.gz'],\
	'Right Post Central'               			: ['2022', 'roi_FS_R_Postcentral_2mm.nii.gz'],\
	'Left Posterior Cingulate'         			: ['1023', 'roi_FS_L_Posteriorcingulate_2mm.nii.gz'],\
	'Right Posterior Cingulate'        			: ['2023', 'roi_FS_R_Posteriorcingulate_2mm.nii.gz'],\
	'Left Precentral'                  			: ['1024', 'roi_FS_L_Precentral_2mm.nii.gz'],\
	'Right Precentral'                 			: ['2024', 'roi_FS_R_Precentral_2mm.nii.gz'],\
	'Left Precuneus'                   			: ['1025', 'roi_FS_L_Precuneus_2mm.nii.gz'],\
	'Right Precuneus'                  			: ['2025', 'roi_FS_R_Precuneus_2mm.nii.gz'],\
	'Left Rostral Anterior Cingulate'  			: ['1026', 'roi_FS_L_Rostralanteriorcingulate_2mm.nii.gz'],\
	'Right Rostral Anterior Cingulate' 			: ['2026', 'roi_FS_R_Rostralanteriorcingulate_2mm.nii.gz'],\
	'Left Rostral Middle Frontal'      			: ['1027', 'roi_FS_L_Rostralmiddlefrontal_2mm.nii.gz'],\
	'Right Rostral Middle Frontal'     			: ['2027', 'roi_FS_R_Rostralmiddlefrontal_2mm.nii.gz'],\
	'Left Superior Frontal'            			: ['1028', 'roi_FS_L_Superiorfrontal_2mm.nii.gz'],\
	'Right Superior Frontal'           			: ['2028', 'roi_FS_R_Superiorfrontal_2mm.nii.gz'],\
	'Left Superior Parietal'           			: ['1029', 'roi_FS_L_Superiorparietal_2mm.nii.gz'],\
	'Right Superior Parietal'          			: ['2029', 'roi_FS_R_Superiorparietal_2mm.nii.gz'],\
	'Left Superior Temporal'           			: ['1030', 'roi_FS_L_Superiortemporal_2mm.nii.gz'],\
	'Right Superior Temporal'          			: ['2030', 'roi_FS_R_Superiortemporal_2mm.nii.gz'],\
	'Left Supramarginal'               			: ['1031', 'roi_FS_L_Supramarginal_2mm.nii.gz'],\
	'Right Supramarginal'              			: ['2031', 'roi_FS_R_Supramarginal_2mm.nii.gz'],\
	'Left Temporal Pole'               			: ['1033', 'roi_FS_L_Temporalpole_2mm.nii.gz'],\
	'Right Temporal Pole'              			: ['2033', 'roi_FS_R_Temporalpole_2mm.nii.gz'],\
	'Left Transverse Temporal'         			: ['1034', 'roi_FS_L_Transversetemporal_2mm.nii.gz'],\
	'Right Transverse Temporal'        			: ['2034', 'roi_FS_R_Transversetemporal_2mm.nii.gz']
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
	'Left Accumbens'		: ['26', 'roi_FS_L_Accumbens_2mm.nii.gz'],
	'Right Accumbens'		: ['58', 'roi_FS_R_Accumbens_2mm.nii.gz'],
	'Left Amygdala'			: ['18', 'roi_FS_L_Amygdala_2mm.nii.gz'],
	'Right Amygdala'		: ['54', 'roi_FS_R_Amygdala_2mm.nii.gz'],
	'Left Caudate'			: ['11', 'roi_FS_L_Caudate_2mm.nii.gz'],
	'Right Caudate'			: ['50', 'roi_FS_R_Caudate_2mm.nii.gz'],
	'Left Hippocampus'		: ['17', 'roi_FS_L_Hippocampus_2mm.nii.gz'],
	'Right Hippocampus'		: ['53', 'roi_FS_R_Hippocampus_2mm.nii.gz'],
	'Left Pallidum'			: ['13', 'roi_FS_L_Pallidum_2mm.nii.gz'],
	'Right Pallidum'		: ['52', 'roi_FS_R_Pallidum_2mm.nii.gz'],
	'Left Putamen'			: ['12', 'roi_FS_L_Putamen_2mm.nii.gz'],
	'Right Putamen'			: ['51', 'roi_FS_R_Putamen_2mm.nii.gz'],
	'Left Thalamus'			: ['10', 'roi_FS_L_Thalamus_2mm.nii.gz'],
	'Right Thalamus'		: ['49', 'roi_FS_R_Thalamus_2mm.nii.gz']
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
