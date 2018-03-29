#!/bin/bash

function calcLL () {
	# first input must be the template brain (either MNI or user provided)
	# second input is the $space variable, whether it is user-defined ("custom")
	# or "MNI152" for the default rois.

	if [ $2 == "custom" ]; then
		roilist=${binROIs};
	elif [ $2 == "MNI152" ]; then
		roilist=${defaultrois};
	fi

	for SUBJ in $SUBJECTS; do
		declare -a LLArray;
		LLArray=($SUBJ);

		SUBJECTOPDIR=$WORKINGDIR/$SUBJ;
		cd $SUBJECTOPDIR || exit;

		subj_set_path $SUBJ;

		printf "Performing registration...\n";

		RegBrain="$SUBJECTOPDIR"/Intermediate_Files/"${SUBJ}"_Reg_brain_$2;
		RegFile="$SUBJECTOPDIR"/Intermediate_Files/"${SUBJ}"_Reg_$2.mat;

		flirt -in "$BET_Brain" -ref $1 -out $RegBrain -omat $RegFile -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12  -interp trilinear;

		fsleyes render --hideCursor -of "$WORKINGDIR"/QC_Registrations/$2/"${SUBJ}"_Reg.png "$RegBrain".nii.gz;

		# updating number of max lesions
		lesfiles=($LesionFiles);
		NumLesionFiles=${#lesfiles[@]};

		if (( maxlesions < NumLesionFiles )); then
					maxlesions=$NumLesionFiles;
		fi

		count=1;

		cd $SUBJECTOPDIR || exit;

		for Lesion in $LesionFiles; do

			lesionName=$(basename "$Lesion")
			lesionName="${lesionName%%.*}";

			printf "Registering lesion to template space...\n";
			Lesion_SS="$SUBJECTOPDIR"/"${lesionName}"_"$2"_SS.nii.gz;
			flirt -in "$Lesion" -applyxfm -init $RegFile -out "${Lesion_SS}" -paddingsize 0.0 -interp trilinear -ref $RegBrain

			SS_lesion_volume=$(fslstats $Lesion -V | awk '{print $2;}')
			LLArray+=(${SS_lesion_volume});

			fslmaths "$Lesion_SS" -bin "$SUBJECTOPDIR"/"${lesionName}"_SS.nii.gz;
			LesionBin="$SUBJECTOPDIR"/"${lesionName}"_"$2"_SS.nii.gz;

			cog=`fslstats "$Lesion_SS" -C`;

			cog=$( printf "%.0f\n" $cog );

			for roifile in ${roilist[@]}; do

				roiname=$(basename "$roifile")
				roiname="${roiname%%.*}";

				ROI_volume=$(fslstats $roifile -V | awk '{print $2;}');

				#add the two binarized masks together
				fslmaths $roifile -add "${LesionBin}" "${SUBJECTOPDIR}"/Intermediate_Files/${SUBJ}_combined_${roiname}_lesion${count}_"$2".nii.gz;

				#now that two binarized masks are added, the overlapping regions will have a value of 2 so we threshold the image to remove any region that isn't overlapping
				fslmaths "${SUBJECTOPDIR}"/Intermediate_Files/${SUBJ}_combined_${roiname}_lesion"${count}"_"$2".nii.gz -thr 2 "${SUBJECTOPDIR}"/Intermediate_Files/${SUBJ}_${roiname}_lesion"$count"_overlap_"$2".nii.gz

				lesionload=$(fslstats "${SUBJECTOPDIR}"/Intermediate_Files/${SUBJ}_${roiname}_lesion"$count"_overlap_"$2".nii.gz -V | awk '{print $2;}')

				fsleyes render -hl -vl $cog --hideCursor -of ${WORKINGDIR}/QC_LL/$2/$roiname/${SUBJ}_LL.png "$RegBrain".nii.gz $LesionBin -cm blue -a 50 $roifile -cm copper -a 40;

				LLArray+=(${ROI_volume});
				LLArray+=(${lesionload});

			done

			count=$((count+1));

		done

		printf '%s,' ${LLArray[@]} >> "$WORKINGDIR"/lesion_load_data.csv;
		printf '\n' >> "$WORKINGDIR"/lesion_load_data.csv;
	done


cd "$WORKINGDIR"/QC_Registrations/"$2" || exit;
makeQCPage Registration;

##############################[ ADD HEADER TO CSV FILE ]##################################

cd $WORKINGDIR;
declare -a HeaderArray;
HeaderArray=(Subject);

for i in $(seq 1 $maxlesions); do
	HeaderArray+=(Lesion${i}_Volume_StandardSpace);
	for roifile in ${roilist[@]}; do

		roiname=$(basename "$roifile")
		roiname="${roiname%%.*}";

		HeaderArray+=(Lesion${i}_${roiname}_Volume);
		HeaderArray+=(Lesion${i}_${roiname}_lesionload);
	done

done

StringArray=$(IFS=, ; echo "${HeaderArray[*]}")

awk -v env_var="${StringArray}" 'BEGIN{print env_var}{print}' lesion_load_data.csv > lesion_load_${2}_database.csv;

rm $WORKINGDIR/lesion_load_data.csv;

cd $WORKINGDIR/QC_LL/${2};

rois=`ls -d *`;

for roi in $rois; do
		cd $roi;
		makeQCPage LL_$roi;
		cd $WORKINGDIR/QC_LL/$2/;
done


}
