#!/bin/bash

function setup {
############################### READ INPUTS ####################################

printf "    SRQL (circle) Toolbox  Copyright (C) 2017  Kaori L Ito & Sook-Lei Liew

    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it under certain conditions;
    please visit <https://www.gnu.org/licenses/gpl.html> for details."

#Identify location of input directory.
printf "\nSpecify the location of your input directory. (e.g., /Users/Lily/ProjectX/Input_Data)\n";
read INPUTDIR;

#Identify location of output directory.
printf "\nSpecify the location of your desired output directory. (e.g., /Users/Lily/ProjectX/Outputs)\n";
read WORKINGDIR;

printf "\nSpecify your anatomical image identifier/wildcard. (e.g., T1 if Subj01_T1 or F013_T1 is your anatomical image.)\n"
read ANATOMICAL_ID;

printf "\nSpecify your lesion mask identifier/wildcard (e.g., lesion_mask if subj01_lesion_mask or F013_lesion_mask is your identifier)\n";
read LESION_MASK;

# this really doesn't matter as long as both of them are in the same space...
printf "\nAre your T1 and lesion masks both registered to stereotaxic space? ('y'/'n')\n";
read -r NORMALIZED;

# INPUTDIR=/Users/npnlusc/Documents/SRQL/TESTFILES/INPUTS_FS;
# WORKINGDIR=/Users/npnlusc/Documents/SRQL/TESTFILES/OUTPUT_FILES;
# ANATOMICAL_ID=T1;
# LESION_MASK=LesionSmooth;


################################ SET OPTIONS ####################################
printf "\nScrub Data? ('y'/'n')\n";
read -r DATASCRUB;

	if [ "${DATASCRUB}" == 'y' ] || [ "${DATASCRUB}" == 'yes' ]; then
		RunDataScrub=1;
  elif [ "${DATASCRUB}" == 'n' ] || [ "${DATASCRUB}" == 'no' ];  then
    RunDataScrub=0;
  fi

printf "\nRun white matter intensity correction on manual lesions? ('y'/'n')\n";
read -r WM_INT_CORR;

	if [ "${WM_INT_CORR}" == 'y' ] || [ "${WM_INT_CORR}" == 'yes' ]; then
		RunWMCorr=1;

		printf "\nIndicate the percentage of intensity values you would like to have removed from your mask. \nNote: 0%% indicates no white matter correction will be made (default: 5%%)\n";
		read -r RMPERCENT_INTENSITY;

		re='^[0-9]+$';
		if ! [[ "${RMPERCENT_INTENSITY}" =~ $re ]] ; then
		   echo "error: Not a number" >&2; exit 1;
		fi

		RMPercentage=$(echo "scale=2; ${RMPERCENT_INTENSITY}/100" | bc -l);
		VoxelRange=$(echo "scale=0; $RMPercentage * 255 / 2" | bc -l);

		printf "\n$VoxelRange voxels will be removed above and below the white matter mean intensity.\n";

	elif [ "${WM_INT_CORR}" == 'n' ] || [ "${WM_INT_CORR}" == 'no' ]; then
		RunWMCorr=0;
	fi

printf "\nCalculate lesion load? ('y'/'n')\n";
read -r CALC_LESIONLOAD;

	if [ "${CALC_LESIONLOAD}" == 'y' ] || [ "${CALC_LESIONLOAD}" == 'yes' ]; then
		RunLL=1;

      printf "\nCalculate lesion load for default subcortical ROIs (Harvard Oxford Atlas). (y/n)\n";
      # This should be a checkbox!
      read -r LL_response_default;

      if [ "${LL_response_default}" == 'y' ]; then
        LL_default=1;
        defaultrois=`ls "$DIR"/ROIs/*roi*.nii*`;
      else
        LL_default=0;
      fi

      printf "\nProvide my own list of ROIs. (y/n)\n";
      read -r LL_response_usrtxt;

      if [ "${LL_response_usrtxt}" == 'y' ]; then
        LL_usrtxt=1;

    		## Change this part out as we talked about so the user directly puts the directory here and we get a list!
    		printf "Please provide a txt file with location of all ROIs. ROIs should be in stereotaxic space.\n";
    		read -r ROI_DIR_TXTFILE;

    		let i=0

    		while IFS=$'\n' read -r line_data; do
    		   roiarray[i]="${line_data}"
    			((++i))
    		done < "${ROI_DIR_TXTFILE}"

      	printf "Please specify the full path to a standard/reference brain (e.g., /Users/Lily/ProjectX/Standard/MNI_152T1_brain.nii)\n";
      	read STANDARD;

      else

        LL_usrtxt=0;

      fi

      printf "\nUse subject specific Freesurfer ROIs (y/n)\n(*note Freesurfer should already have been run, and each subject directory should contain a T1.mgz and aparc+aseg.mgz file. )\n";
      read -r LL_response_FS;

      if [ "${LL_response_FS}" == 'y' ]; then
        LL_FS=1;
        # have user select the ROIs from a list -> put response into list FSrois.
        FSrois=( 11 10 50 ); # reset this list to the user response.
      else
        LL_FS=0;
      fi

	elif [ "${CALC_LESIONLOAD}" == 'n' ] || [ "${CALC_LESIONLOAD}" == 'no' ]; then
		RunLL=0;
	else
		printf "Cannot process response. Exiting script.\n"  || exit ;
	fi

## This option should only be allowed if neither of the two above are selected.
if [ "$RunLL" -eq 0 ] && [ "$RunWMCorr" -eq 0 ]; then

  printf "\nOnly create QC page to visualize lesions?\n";
  read -r QC_STATUS;

  	if [ "${QC_STATUS}" == 'y' ] || [ "${QC_STATUS}" == 'yes' ]; then
  		QCOnly=1;
  	elif [ "${QC_STATUS}" == 'n' ] || [ "${QC_STATUS}" == 'no' ]; then
  		QCOnly=0;
  	else
  		printf "Cannot process response. Exiting script.\n"  || exit ;
  	fi
fi

#########################################################################################
if [[ $RunWMCorr -eq 1 ||  $RunLL -eq 1 ]]; then
  printf "\nHave you performed skull stripping on your anatomical images? ('y'/'n')\n";
  read -r BET_STATUS;

  	if [ "${BET_STATUS}" == 'y' ] || [ "${BET_STATUS}" == 'yes' ]; then
  		RunBET=0;
  		printf "Please specify skull stripped brain identifier (e.g., brain)\n";
  		read -r BET_ID;

  	elif [ "${BET_STATUS}" == 'n' ] || [ "${BET_STATUS}" == 'no' ]; then
  		RunBET=1;

  	else
  		printf "Cannot process response. Exiting script." || exit;
  	fi
fi

if [ "$RunWMCorr" == 1 ]; then
  printf "\nHave you performed white matter segmentation on your subjects? ('y'/'n')\n"
  read -r WM_STATUS;

  	if [ "${WM_STATUS}" == 'y' ] || [ "${WM_STATUS}" == 'yes' ]; then
  		printf "Please specify identifier for white matter mask (e.g., c1)\n";
  		read -r WM_ID;
  		RunWM=0;

  	elif [ "${WM_STATUS}" == 'n' ] || [ "${WM_STATUS}" == 'no' ]; then
  		RunWM=1;

  		if [ "$RunBET" == 1 ]; then
  			printf "SRQL will run brain extraction and white matter segmentation\n";
  		fi

  	else
  		printf "Cannot process response. Exiting script." || exit;
  	fi
fi

if [ "$RunWMCorr" == 1 ] || [ "$RunLL" == 1 ]; then
printf "\nSRQL will pause to allow for visual QC after brain extraction and/or segmentation. Press 1 to opt out of pausing, 0 otherwise...\n";
read -r NO_PAUSE_RESPONSE;
	if [ "${NO_PAUSE_RESPONSE}" == 1 ]; then
		NoPause=1;
	else
		NoPause=0;
    # pop up window with warning: "Warning: QC is highly recommended. Please be sure to thoroughly check the quality of all lesions.""
	fi
fi

############################## CREATE OUTPUT DIRECTORIES #################################


cd "$INPUTDIR" || exit;

SUBJECTS=$(ls -d *);

cd $WORKINGDIR || exit;

if [ "$RunWMCorr" == 1 ]; then
	mkdir QC_Lesions;
fi

if [ "$RunBET" == 1 ]; then
	mkdir QC_BrainExtractions;
fi

if [ "$RunWM" == 1 ]; then
	mkdir QC_WM;
fi

if [[ "$RunLL" == 1 ]]; then
	mkdir QC_LL QC_Registrations;
	cd QC_LL;

  if [[ "$LL_usrtxt" == 1 ]]; then
    mkdir custom;
    cd $WORKINGDIR;
    mkdir ROI_binarized;
    cd $WORKINGDIR/QC_LL/custom;

  	for roi in ${roiarray[@]}; do
  		roiname=$(basename "$roi");
  		roiname="${roiname%.*}";
      fslmaths "$roi" -bin $WORKINGDIR/ROI_binarized/${roiname}_bin;
  	done

    binROIs=`ls $WORKINGDIR/ROI_binarized/*_bin.nii.gz`;

    #create new directory for each roi
    for roi in ${binROIs}; do
      roiname=$(basename "$roi")
      roiname="${roiname%%.*}";
      mkdir $roiname;
    done

    cd $WORKINGDIR/QC_Registrations;
    mkdir custom;

    cd $WORKINGDIR/QC_LL;
  fi

  if [[ "$LL_default" == 1 ]]; then
    mkdir MNI152;
    cd MNI152;
    for roi in ${defaultrois}; do
      roiname=$(basename "$roi")
      roiname="${roiname%%.*}";
      mkdir $roiname;
    done
    cd $WORKINGDIR/QC_Registrations;
    mkdir MNI152;
    cd $WORKINGDIR/QC_LL;
  fi

  if [[ "$LL_FS" == 1 ]]; then
    mkdir FS;
    cd FS;
    for roi in ${FSrois[@]}; do
      mkdir roi$roi;
    done
    cd $WORKINGDIR/QC_Registrations;
    mkdir FS;
    cd $WORKINGDIR/QC_LL;
  fi

  cd "$WORKINGDIR";

fi

for SUBJ in $SUBJECTS; do
	mkdir "$SUBJ";
	cd "$SUBJ" || exit;
	mkdir Intermediate_Files;
  cd Intermediate_Files;
  mkdir Original_Files;
  # copy all files from subj dir to working directory.
  cp $INPUTDIR/$SUBJ/* $WORKINGDIR/$SUBJ/Intermediate_Files/Original_Files;

  gzip $WORKINGDIR/$SUBJ/Intermediate_Files/Original_Files/*.nii > /dev/null 2>&1;

  SUBJECTOPDIR=$WORKINGDIR/$SUBJ;
  # normalize T1 intensity for the subject T1
  intnormalizeT1 ${SUBJECTOPDIR}/Intermediate_Files/Original_Files/"${SUBJ}"*"${ANATOMICAL_ID}"*.nii.gz "${SUBJ}"_"${ANATOMICAL_ID}" "$SUBJECTOPDIR"/Intermediate_Files;

  LesionFiles=`ls ${SUBJECTOPDIR}/Intermediate_Files/Original_Files/$1*${LESION_MASK}*.nii.gz`;

  count=1;
  for lesion in $LesionFiles; do
      fslmaths $lesion -bin ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_${LESION_MASK}${count}_bin.nii.gz;
      count=$((count+1));
  done

	cd "$WORKINGDIR" || exit;
done

}
