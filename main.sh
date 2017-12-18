#!/bin/bash

# NPNL Lab
# Semi-automated Robust Quantification of Lesions (SRQL)Toolbox Version 2.0
# KLI kaoriito(at)usc.edu 
# 20171012
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
source "$DIR"/wmCorrection.sh;
source "$DIR"/makeQCPage.sh;
source "$DIR"/intnormalizeT1.sh;

####################################[ SCRIPT BEGINS ]#####################################

# INPUTDIR=/Users/lilyito/Documents/Projects/SRQL/TEST_INPUT;
# WORKINGDIR=/Users/lilyito/Documents/Projects/SRQL/TEST_OUTPUT;
# ANATOMICAL_ID=T1;
# LesionMask='LesionSmooth';
# RunWM=0;


####################################[ MAIN SCRIPT ]#######################################

setup;

cd ~ || exit;
cd $INPUTDIR || exit; 
pwd;

maxlesions=1;

for SUBJ in $SUBJECTS; do

	cd "$SUBJ" || exit;
	
	ANATOMICAL=$(ls "${SUBJ}"*"${ANATOMICAL_ID}".nii*);
	SUBJECTOPDIR=$WORKINGDIR/$SUBJ;
	
	#normalize T1 intensity for the subject T1
 	intnormalizeT1 "$ANATOMICAL" "${SUBJ}"_"${ANATOMICAL_ID}" "$SUBJECTOPDIR"/Intermediate_Files; 
	
	# set bet and wm 
	if [ "${RunBET}" == 1 ]; then
			bet "${ANATOMICAL}" "${SUBJECTOPDIR}"/Intermediate_Files/"${SUBJ}"_Brain -R -f 0.5 -g 0;
			BET_Brain="${SUBJECTOPDIR}"/Intermediate_Files/"${SUBJ}"_Brain.nii.gz;
			fsleyes render --hideCursor -of "$WORKINGDIR"/QC_BrainExtractions/"${SUBJ}"_BET.png "$ANATOMICAL" "$BET_Brain" -cm blue -a 50;
	
	else

			BET_Brain=$(ls "${SUBJ}"*"${BET_ID}".nii*);
	fi
	
		
	if [ "$RunWM" == 1 ]; then
		
		# perform WM segmentation 
		fast -t 1 -n 3 -H 0.1 -I 4 -l 20.0 -g --nopve -o "${SUBJECTOPDIR}"/Intermediate_Files/"${SUBJ}" "${BET_Brain}";
		WM_MASK="${SUBJECTOPDIR}"/Intermediate_Files/"${SUBJ}"_seg_2.nii.gz;
		fsleyes render --hideCursor -of "$WORKINGDIR"/QC_WM/"${SUBJ}"_WM.png "$ANATOMICAL" "$WM_MASK" -cm blue -a 50;
		
	else
		
		WM_MASK=$(ls ./*"${WM_ID}"*.nii*);
	fi
	
	fslmaths "${SUBJ}"*"${LESION_MASK}".nii* -bin "$SUBJECTOPDIR"/Intermediate_Files/"${SUBJ}"_LesionMask1_bin;	
	
	
	if $(fslmaths "${WM_MASK}" -sub "${SUBJECTOPDIR}"/Intermediate_Files/"${SUBJ}"_LesionMask1_bin.nii.gz "${SUBJECTOPDIR}"/Intermediate_Files/"${SUBJ}"_corrWM); then
		:
	else
		echo "
			Check Image Orientations for T1 and Lesion Mask. Skipping Subject: ${SUBJ}.";
		printf "${SUBJ} Skipped" >> "$WORKINGDIR"/lesion_data.csv;
		printf '\n' >> "$WORKINGDIR"/lesion_data.csv;
		cd "$INPUTDIR" || exit;
		continue;
	fi
	
	
	corrWM=$SUBJECTOPDIR/Intermediate_Files/"${SUBJ}"_corrWM.nii.gz;
	
	
	# set values for healthy WM removal
	# multiply WM mask by intensity normalized T1
	fslmaths "$SUBJECTOPDIR"/Intermediate_Files/"${SUBJ}"_"${ANATOMICAL_ID}"_int_scaled -mul "${corrWM}" "$SUBJECTOPDIR"/Intermediate_Files/"${SUBJ}"_NormRangeWM;
	
	WM_Mean=$(fslstats "$SUBJECTOPDIR"/Intermediate_Files/"${SUBJ}"_NormRangeWM -M);

	# updating number of max lesions	
	NumLesionFiles=$(find -d "${SUBJ}"*"${LESION_MASK}"*.nii* | wc -l);
	
	if (( maxlesions < NumLesionFiles )); then
		maxlesions=$NumLesionFiles;
			
		echo "updated num of max lesions: " "$maxlesions";
	fi
	
	LesionFiles=$(ls -d "${SUBJ}"*"${LESION_MASK}"*.nii*);
	
	counter=1;
	
	#create subject info array
	
	declare -a SubjInfoArray;
	
	TotalNativeBrainVol=$(fslstats "${BET_Brain}" -V | awk '{print $2;}');
	
	SubjInfoArray=($SUBJ $TotalNativeBrainVol ${WM_Mean});
	
 	for Lesion in $LesionFiles; do
	
		if [ "$counter" -gt 1 ]; then
			# binarize lesion mask
			fslmaths "$Lesion" -bin "$SUBJECTOPDIR"/Intermediate_Files/"${SUBJ}"_LesionMask"${counter}"_bin;	
		
		fi
		
		#calculate original and white matter adjusted lesion volumes
		OrigLesionVol=$(fslstats "$Lesion" -V | awk '{print $2;}');
		
		CorrLesionVol=$( wmCorrection );
		
		VolRemoved=$(awk "BEGIN {printf \"%.9f\",${OrigLesionVol}-${CorrLesionVol}}");
		
		PercentRemoved=$(awk "BEGIN {printf \"%.9f\",${VolRemoved}/${TotalNativeBrainVol}}");
		
		#determine side of lesion
		#this gets the center of gravity of the lesion using the mni coord and then extracts the first char of the X coordinate
		LesionCOG=$(fslstats ${Lesion} -c | awk '{print substr($0,0,1)}'); 
		
		if [ $LesionCOG == '-' ]; then
			LesionSide='L';
		else
			LesionSide='R';
		fi
		
		#concatenate onto array with all lesion volumes and percentage:
		SubjInfoArray+=(${LesionSide});
		SubjInfoArray+=(${OrigLesionVol});
		SubjInfoArray+=(${CorrLesionVol});
		SubjInfoArray+=(${VolRemoved});
		SubjInfoArray+=(${PercentRemoved});
			
		
		if [ "$RunQC" == 1 ]; then
			
			COG=$(fslstats $Lesion -C);
			COG=$( printf "%.0f\n" $COG ); 
			
			fsleyes render -vl $COG --hideCursor -of "$WORKINGDIR"/QC_Lesions/"${SUBJ}"_Lesion"${counter}".png "$ANATOMICAL" "$INPUTDIR"/"$SUBJ"/"$Lesion" -a 40 "$SUBJECTOPDIR"/"${SUBJ}"_WMAdjusted_Lesion"${counter}"_bin -cm blue -a 50;
		
		fi
		
		counter=$((counter+1)); 
	
	done
	
	printf '%s,' ${SubjInfoArray[@]} >> "$WORKINGDIR"/lesion_data.csv;
	printf '\n' >> "$WORKINGDIR"/lesion_data.csv;
	
	cd "$INPUTDIR" || exit;
	
done


################################# ADD HEADER TO DATAFILE #################################

cd $WORKINGDIR;
declare -a HeaderArray;
HeaderArray=(Subject "Total_Native_Brain_Volume" "Mean_White_Matter_Intensity");

for i in $(seq 1 $maxlesions); do 
	HeaderArray+=(Lesion${i}_Hemisphere);
	HeaderArray+=(Lesion${i}_Original_Lesion_Volume); 
	HeaderArray+=(Lesion${i}_Corrected_Lesion_Volume);
	HeaderArray+=(Lesion${i}_Volume_Removed);
	HeaderArray+=(Lesion${i}_Percent_Removed);	
done

StringArray=$(IFS=, ; echo "${HeaderArray[*]}")

awk -v env_var="${StringArray}" 'BEGIN{print env_var "\n"}{print}' lesion_data.csv > lesion_database.csv;

rm $WORKINGDIR/lesion_data.csv;


if [ "$RunQC" == 1 ]; then
	cd "$WORKINGDIR"/QC_Lesions || exit;
	makeQCPage Lesions;
fi

if [ "$RunBET" == 1 ]; then
	cd "$WORKINGDIR"/QC_BrainExtractions || exit;
	makeQCPage BET;
fi

if [ "$RunWM" == 1 ]; then
	cd "$WORKINGDIR"/QC_WM || exit;
	makeQCPage WM;
fi



####################################[ END OF SCRIPT ]#####################################

exit