#!/bin/bash

# this function will take a list of FS codes (corresponding to subcortical ROIS)
# then for each subject it will use its own FS segmentation and calc the lesion load in FS space
# will output a CSV file for FS subcortical ROI/lesion overlap
# each subj input file needs either an aparc+aseg.mgz or aseg.mgz file and a T1.mgz file (the T1 file in FS space)

function calcLL_FS {

	for SUBJ in $SUBJECTS; do

		declare -a LLArray;
		LLArray=($SUBJ);

		SUBJECTOPDIR=$WORKINGDIR/$SUBJ;
		cd $SUBJECTOPDIR || exit;

		subj_set_path $SUBJ;

		FST1=${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_FST1.nii.gz;
		mri_convert --in_type mgz --out_type nii --out_orientation RAS $T1mgz $FST1 >/dev/null;

		# perform registration to FS Space for each subject to get transformation matrix
		flirt -in $ANATOMICAL -ref $FST1 -omat ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_T12FS.xfm -out ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_T12FS.nii.gz;
		fsleyes render --hideCursor -of "$WORKINGDIR"/QC_Registrations/FS/"${SUBJ}"_Reg.png ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_T12FS.nii.gz;

		# invert transformation matrix
		convert_xfm -omat ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_T12FS_inv.xfm  ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_T12FS.xfm;
		count=1;

		# extract all ROIs for each subj
		for roicode in ${FSrois[@]}; do

			mri_convert --in_type mgz --out_type nii --out_orientation RAS $segfile ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_aparc+aseg.nii.gz >/dev/null;
			fslmaths ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_aparc+aseg.nii.gz -thr ${roicode} -uthr ${roicode} -bin ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_roi${roicode}.nii.gz;

			# binarize roi
			fslmaths ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_roi${roicode}.nii.gz -bin ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_roi${roicode}_bin.nii.gz

		done

		# accounts for multiple lesion masks
		for Lesion in $LesionFiles; do

			LesionFS=${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_lesion${count}_FS.nii.gz;
			LesionFS_bin=${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_lesion${count}_FS_bin.nii.gz
			# perform transformation on lesion mask, then binarize the mask
			flirt -in $Lesion -init ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_T12FS_inv.xfm -ref $FST1 -out $LesionFS -applyxfm;
			fslmaths $LesionFS -bin ${LesionFS_bin};

			FS_lesion_volume=$(fslstats ${LesionFS_bin} -V | awk '{print $2;}');
			LLArray+=(${FS_lesion_volume});

			cog=`fslstats ${LesionFS_bin} -C`;

			cog=$( printf "%.0f\n" $cog );

			for roicode in ${FSrois[@]}; do

				#add the lesion and roi masks together
				fslmaths ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_roi${roicode}_bin.nii.gz -add ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_lesion${count}_FS_bin.nii.gz ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_combined_lesion${count}_roi${roicode}.nii.gz;

				#now that two binarized masks are added, the overlapping regions will have a value of 2 so we threshold the image to remove any region that isn't overlapping
				fslmaths ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_combined_lesion${count}_roi${roicode}.nii.gz -thr 1.9 ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_roi${roicode}_lesion"$count"_overlap.nii.gz;

				lesionload=$(fslstats "${SUBJECTOPDIR}"/Intermediate_Files/${SUBJ}_roi${roicode}_lesion"$count"_overlap.nii.gz -V | awk '{print $2;}');

				ROI_volume=$(fslstats ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_roi${roicode}_bin.nii.gz -V | awk '{print $2;}');
				LLArray+=(${ROI_volume});
				LLArray+=($lesionload);

				fsleyes render -hl -vl $cog --hideCursor -of ${WORKINGDIR}/QC_LL/FS/roi$roicode/${SUBJ}_LL.png  ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_T12FS.nii.gz ${LesionFS_bin} -cm blue -a 50 ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_roi${roicode}_bin.nii.gz -cm copper -a 40;

			done

			count=$((count+1));

		done
		printf '%s,' ${LLArray[@]} >> "$WORKINGDIR"/lesion_load_data.csv;
		printf '\n' >> "$WORKINGDIR"/lesion_load_data.csv;

	done


	cd "$WORKINGDIR"/QC_Registrations/FS || exit;
	makeQCPage Registration;

	##############################[ ADD HEADER TO CSV FILE ]##################################

	cd $WORKINGDIR;
	declare -a HeaderArray;
	HeaderArray=(Subject);

	for i in $(seq 1 $maxlesions); do
		HeaderArray+=(Lesion${i}_Volume_FSSpace);
		for roi in ${FSrois[@]}; do
			HeaderArray+=(roi${roi}_Volume);
			HeaderArray+=(Lesion${i}_roi${roi}_lesionload);
		done

	done

	StringArray=$(IFS=, ; echo "${HeaderArray[*]}")

	awk -v env_var="${StringArray}" 'BEGIN{print env_var}{print}' lesion_load_data.csv > lesion_load_FS_database.csv;

	rm $WORKINGDIR/lesion_load_data.csv;

	cd $WORKINGDIR/QC_LL/FS;

	rois=`ls -d *`;

	for roi in $rois; do
			cd $roi;
			makeQCPage LL_$roi;
			cd $WORKINGDIR/QC_LL/FS/;
	done


}
