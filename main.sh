#!/bin/bash

# NPNL Lab
# Semi-automated Robust Quantification of Lesions (SRQL)Toolbox Version 2.0
# KLI kaoriito(at)usc.edu
# 20180227
#
#
#  The Semi-automated Robust Quantification of Lesions (SRQL) Toolbox is a user-friendly toolbox that uses a robust analysis pipeline for performing lesion analyses across multiple datasets.
#     Copyright (C) 2017  Kaori L Ito & Sook-Lei Liew
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
##########################################################################################

clear;

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )";


source "$DIR"/setup.sh;
source "$DIR"/wmCorr_run.sh;
source "$DIR"/wmCorrection.sh;
source "$DIR"/makeQCPage.sh;
source "$DIR"/intnormalizeT1.sh;
source "$DIR"/calcLL.sh;
source "$DIR"/calcLL_FS.sh;
source "$DIR"/reorient2rad.sh;

template_brain=`ls "$DIR"/ROIs/MNI152_T1_2mm_brain.nii*`;

####################################[ SCRIPT BEGINS ]#####################################

function pause(){
   read -p "$*"
}

function subj_set_path {
# this function sets up the paths to the file dependencies for subj $1
  SUBJECTOPDIR=$WORKINGDIR/$1;

  if [ "$RunDataReorient" == 0 ]; then
    ANATOMICAL=`ls ${SUBJECTOPDIR}/Intermediate_Files/${1}*${ANATOMICAL_ID}*_intNorm.nii.gz`;

    if [ "${LESION_MASK}" == 'WMAdjusted' ]; then
      LesionFiles=( $(ls ${SUBJECTOPDIR}/$1*${LESION_MASK}*bin.nii.gz));
    else
      LesionFiles=( $(ls ${SUBJECTOPDIR}/Intermediate_Files/$1*${LESION_MASK}*bin.nii.gz));
    fi

  else
    ANATOMICAL=${SUBJECTOPDIR}/"${SUBJ}"_"${ANATOMICAL_ID}"_rad_reorient.nii.gz;

    if [ "${RunWMCorr}" == 1 ] || [ "${RunLL}" == 1]; then
      if [ "${LESION_MASK}" == 'WMAdjusted' ]; then
        LesionFiles=( $(ls ${SUBJECTOPDIR}/$1*${LESION_MASK}*bin.nii.gz));
      else
        LesionFiles=( $(ls ${SUBJECTOPDIR}/Intermediate_Files/$1*${LESION_MASK}*rad_reorient.nii.gz));
      fi
    else
      LesionFiles=( $(ls ${SUBJECTOPDIR}/$1*${LESION_MASK}*rad_reorient.nii.gz));
    fi
  fi

  if [ "${LL_FS}" == 1 ]; then
    T1mgz=${SUBJECTOPDIR}/Intermediate_Files/Original_Files/T1.mgz;
    segfile=${SUBJECTOPDIR}/Intermediate_Files/Original_Files/aparc+aseg.mgz;
  fi


	if [ "${RunBET}" == 1 ]; then
	 	BET_Brain="${SUBJECTOPDIR}"/Intermediate_Files/"${1}"_Brain.nii.gz;
	else

      if [ "$RunDataReorient" == 0 ]; then
        BET_Brain=`ls "${SUBJECTOPDIR}"/Intermediate_Files/Original_Files/${1}*"${BET_ID}".nii.gz`;
      else
        BET_Brain="${SUBJECTOPDIR}"/Intermediate_Files/${1}_"${BET_ID}"_rad_reorient.nii.gz;
      fi

	fi

	# set WM_MASK to output of wm segmentation
  if [ "$RunWM" == 1 ]; then
    WM_MASK="${SUBJECTOPDIR}"/Intermediate_Files/"${1}"_seg_2.nii.gz;
  else
    if [ "$RunDataReorient" == 0 ]; then
      WM_MASK=$(ls ${SUBJECTOPDIR}/Intermediate_Files/Original_Files/${1}*"${WM_ID}"*.nii*);
    else
      WM_MASK="${SUBJECTOPDIR}"/Intermediate_Files/${1}_"${WM_ID}"_rad_reorient.nii.gz;
    fi
  fi
}

#declare -a roiarray;

####################################[ MAIN SCRIPT ]#######################################

setup;


cd ~ || exit;
cd $INPUTDIR || exit;
SUBJECTS=$(ls -d *);

if [ "${RunDataReorient}" == 1 ]; then

declare -a newSubjArray;

  for SUBJ in $SUBJECTS; do

    keepSUBJ='';
    reorient2rad $SUBJ $keepSUBJ;

    if [ "${keepSUBJ}" == 1 ]; then
      newSubjArray+=(${SUBJ});
    else
      printf "\nCheck orientation for $SUBJ";
    fi

  done

SUBJECTS=${newSubjArray[@]};

fi

#################################[ BRAIN EXTRACTION ]#####################################
# Brain extraction or a skull-stripped brain is necessary to run both white matter
#  correction and calculate lesion load.

if [ "${RunBET}" == 1 ]; then

	for SUBJ in $SUBJECTS; do

		cd $INPUTDIR/"$SUBJ" || exit;

    subj_set_path $SUBJ;

		# perform brain extraction on all subjects
		bet "${ANATOMICAL}" "${SUBJECTOPDIR}"/Intermediate_Files/"${SUBJ}"_Brain -R -f 0.5 -g 0;

		# use fsleyes to create pngs of the brain extractions
		fsleyes render --hideCursor -of "$WORKINGDIR"/QC_BrainExtractions/"${SUBJ}"_BET.png "$ANATOMICAL" "$BET_Brain" -cm blue -a 50;

	done

	# make QC page
	cd "$WORKINGDIR"/QC_BrainExtractions || exit;
	makeQCPage BET;

	# pause here, have user check the html output of brain extraction
  pause 'Please check your brain extractions. Press [Enter] key to continue...';
	# reset SUBJECTS to only subjects that have good brain extractions?

fi

##################################[ WM SEGMENTATION ]#####################################


if [ "$RunWM" == 1 ]; then

	printf "Performing white matter segmentation...[long process] \n";

	for SUBJ in $SUBJECTS; do
		# this assigns subject specific file paths for dependent files (e.g., BET)
		subj_set_path $SUBJ;

		# perform WM segmentation
		fast -t 1 -n 3 -H 0.1 -I 4 -l 20.0 -g --nopve -o "${SUBJECTOPDIR}"/Intermediate_Files/"${SUBJ}" "${BET_Brain}";

		# use fsleyes to create pngs of wm seg
		fsleyes render --hideCursor -of "$WORKINGDIR"/QC_WM/"${SUBJ}"_WM.png "$ANATOMICAL" "$WM_MASK" -cm blue -a 50;

	done

	# make QC page
	cd "$WORKINGDIR"/QC_WM || exit;
	makeQCPage WM;

	# pause here, have user check the html output of WM segmentation
  pause 'Please check your white matter segmentations. Press [Enter] key to continue...';

	# reset SUBJECTS to only subjects that have good WM Seg?

fi

###################################[ WM CORRECTION ]######################################
# white matter correction will take the T1 input, lesion input, brain extraction, and
#  wm seg inputs and then create a new lesion file that removes healthy white matter
#  voxels. It will also output a CSV file that contains info about the voxels removed, etc.

if [ "$RunWMCorr" == 1 ]; then

	printf "Performing white matter adjustment...\n";

	wmCorr_run $SUBJECTS;
	LESION_MASK=WMAdjusted;

	cd "$WORKINGDIR"/QC_Lesions || exit;
	makeQCPage Lesions;

	# if runLL, then pause here, have user check the html output of WM Corrected lesions
  pause 'Please check white matter corrected lesions. Press [Enter] key to continue...';
	# otherwise process is complete.

fi

####################################[ LESION LOAD ]#######################################

if [ "${RunLL}" == 1 ]; then
  cd $WORKINGDIR;

	# roiarray is an array containing the paths to each ROI
	if [[ "$LL_usrtxt" == 1 ]]; then
    space="custom";
    printf "Calculating lesion load for user defined ROIs...\n"
		calcLL $STANDARD $space;
  fi


	if [[ "$LL_default" == 1 ]]; then
    space="MNI152";
    printf "Calculating lesion load for default subcortical ROIs...\n"
		calcLL ${template_brain} $space;
  fi

  if [[ "$LL_FS" == 1 ]]; then
    printf "Calculating lesion load for Freesurfer ROIs...\n"
    # FSrois is an array with the numbers corresponding to subcortical rois the user checked off
		calcLL_FS $FSrois;
  fi

fi

####################################[ QC ONLY ]###########################################

if [ "${QConly}" == 1 ]; then

	printf "Creating QC Page...\n";

	# make pngs of lesion/T1 overlap

	# get lesion volume, output to CSV file
	cd "$WORKINGDIR"/QC_Lesions || exit;
	makeQCPage Lesions;

fi

##########################################################################################

printf "Process complete! Please be sure to QC all steps thoroughly.\n";

####################################[ END OF SCRIPT ]#####################################

exit
