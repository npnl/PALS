#!/bin/bash

function setup {
############################# READ INPUTS & SET OPTIONS #################################

echo "    SRQL (circle) Toolbox 2.0 Copyright (C) 2017  Kaori L Ito & Sook-Lei Liew

    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it under certain conditions; 
    please visit <https://www.gnu.org/licenses/gpl.html> for details.
  
    "

#Identify location of input directory. 
echo "Specify the location of your input directory. (e.g., /Users/Lily/ProjectX/Input_Data)";
read INPUTDIR;

#Identify location of output directory. 
echo "
Specify the location of your desired output directory. (e.g., /Users/Lily/ProjectX/Outputs)";
read WORKINGDIR;

echo "
Specify your anatomical image identifier/wildcard. (e.g., T1 if Subj01_T1 or F013_T1 is your anatomical image.)"
read ANATOMICAL_ID;

echo "Specify your lesion mask identifier/wildcard (e.g., lesion_mask if subj01_lesion_mask or F013_lesion_mask is your identifier)";
read LESION_MASK;

#########################################################################################
echo "Have you performed skull stripping on your anatomical images? ('y'/'n')"
read -r BET_STATUS;

	if [ "${BET_STATUS}" == 'y' ] || [ "${BET_STATUS}" == 'yes' ]; then 
		RunBET=0; 
		echo "Please specify skull stripped brain identifier (e.g., brain)";
		read -r BET_ID;
		
	elif [ "${BET_STATUS}" == 'n' ] || [ "${BET_STATUS}" == 'no' ]; then
		RunBET=1;	
		
	else
		echo "Cannot process response. Exiting script." || exit;
	fi

echo "Have you performed white matter segmentation on your subjects? ('y'/'n')";
read -r WM_STATUS;

	if [ "${WM_STATUS}" == 'y' ] || [ "${WM_STATUS}" == 'yes' ]; then 
		echo "Please specify identifier for white matter mask (e.g., c1)";
		read -r WM_ID;
		RunWM=0;
		
	elif [ "${WM_STATUS}" == 'n' ] || [ "${WM_STATUS}" == 'no' ]; then 
		RunWM=1;
		
		if [ "$RunBET" == 1 ]; then
			echo "SRQL will run brain extraction and white matter segmentation";
		fi
		
	else
		echo "Cannot process response. Exiting script." || exit;
	fi

echo "
Indicate the percentage of intensity values you would like to have removed from your mask. 
	 Note: 0% indicates no white matter correction will be made (default: 5%)";
read -r RMPERCENT_INTENSITY;

	re='^[0-9]+$';
	if ! [[ "${RMPERCENT_INTENSITY}" =~ $re ]] ; then
	   echo "error: Not a number" >&2; exit 1;
	fi

RMPercentage=$(echo "scale=2; ${RMPERCENT_INTENSITY}/100" | bc -l);
VoxelRange=$(echo "scale=0; $RMPercentage * 255 / 2" | bc -l);

echo " $VoxelRange voxels will be removed above and below the white matter mean intensity.";

echo "
Create a quality control page? ('y'/'n')
	Note: This requires pre-installation of fsleyes";
read -r QC_STATUS;
	
	if [ "${QC_STATUS}" == 'y' ] || [ "${QC_STATUS}" == 'yes' ]; then 
		RunQC=1;
	elif [ "${QC_STATUS}" == 'n' ] || [ "${QC_STATUS}" == 'no' ]; then
		RunQC=0;
	else
		echo "Cannot process response. Exiting script."  || exit ;
	fi


############################## CREATE OUTPUT DIRECTORIES #################################


cd "$INPUTDIR" || exit;

SUBJECTS=$(ls -d *);

cd $WORKINGDIR || exit;


if [ "$RunQC" == 1 ]; then
	mkdir QC_Lesions;
fi

if [ "$RunBET" == 1 ]; then
	mkdir QC_BrainExtractions;
fi

if [ "$RunWM" == 1 ]; then
	mkdir QC_WM;
fi


for SUBJ in $SUBJECTS; do
	mkdir "$SUBJ";
	cd "$SUBJ" || exit;
	mkdir Intermediate_Files;
	cd "$WORKINGDIR" || exit;
done

}