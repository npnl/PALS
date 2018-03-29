#!/bin/bash

function reorient2rad {

  SUBJECTOPDIR=$WORKINGDIR/$1;

  # take in the original T1 and lesion mask images
  origT1=`ls ${SUBJECTOPDIR}/Intermediate_Files/${1}*${ANATOMICAL_ID}*_intNorm.nii.gz`;
  # if the T1 is already radiological, this is set here. otherwise radT1 gets updated.
  radT1=`ls ${SUBJECTOPDIR}/Intermediate_Files/${1}*${ANATOMICAL_ID}*_intNorm.nii.gz`;

  origLesionFiles=`ls ${SUBJECTOPDIR}/Intermediate_Files/Original_Files/$1*${LESION_MASK}*.nii.gz`;
  radLesions=`ls ${SUBJECTOPDIR}/Intermediate_Files/Original_Files/$1*${LESION_MASK}*.nii.gz`;

  if [ "${RunBET}" == 0 ]; then
    radBET=`ls "${SUBJECTOPDIR}"/Intermediate_Files/Original_Files/${1}*"${BET_ID}".nii.gz`;
  fi

  # get original orientation, if in neurological, change to radiological.
  origOrientation=$(fslorient $origT1 | awk '{print $1;}');

  if [ "${origOrientation}" == 'NEUROLOGICAL' ]; then
      fslswapdim $origT1 -x y z ${SUBJECTOPDIR}/Intermediate_Files/"${SUBJ}"_"${ANATOMICAL_ID}"_rad;
      fslorient -swaporient ${SUBJECTOPDIR}/Intermediate_Files/"${SUBJ}"_"${ANATOMICAL_ID}"_rad.nii.gz;
      radT1=${SUBJECTOPDIR}/Intermediate_Files/"${SUBJ}"_"${ANATOMICAL_ID}"_rad.nii.gz;

      count=1;
      for origLesion in $origLesionFiles; do

        origLesionOrientation=$(fslorient $origLesion | awk '{print $1;}');

        if [[ "${origLesionOrientation}" == 'RADIOLOGICAL'  ]]; then
          # if the lesion is in radiological, but the T1 is in neurological, return an error.
          keepSUBJ=0;
          return 0;

        else
          fslswapdim $origLesion -x y z ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_${LESION_MASK}${count}_rad;
          fslorient -swaporient ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_${LESION_MASK}${count}_rad.nii.gz;
        fi
        count=$((count+1));
      done
      radLesions=`ls ${SUBJECTOPDIR}/Intermediate_Files/${SUBJ}_${LESION_MASK}*rad.nii.gz`;

      # if user has already run BET or WMSeg, and they're in NEUROLOGICAL, then convert to RADIOLOGICAl
      if [ "${RunBET}" == 0 ]; then
        origBET=`ls "${SUBJECTOPDIR}"/Intermediate_Files/Original_Files/${1}*"${BET_ID}".nii.gz`;
        origBETOrientation=$(fslorient $origBET | awk '{print $1;}');

        if [[ "${origBETOrientation}" == 'RADIOLOGICAL'  ]]; then
            RunBET=1; # if the T1 is in NEUROLOGICAL but the Brain extraction is in radiological, rerun BET to make sure images are in same orientation.
        else
          fslswapdim $origBET -x y z "${SUBJECTOPDIR}"/Intermediate_Files/${1}_"${BET_ID}"_rad;
          radBET="${SUBJECTOPDIR}"/Intermediate_Files/${1}_"${BET_ID}"_rad.nii.gz;
          fslorient -swaporient $radBET;
        fi

      fi

      if [ "${RunWM}" == 0 ]; then
        origWM=$(ls ${SUBJECTOPDIR}/Intermediate_Files/Original_Files/${1}*"${WM_ID}"*.nii*);
        origWMOrientation=$(fslorient $origWM| awk '{print $1;}');

        if [[ "${origWMOrientation}" == 'RADIOLOGICAL'  ]]; then
            RunWM=1; # if the T1 is in NEUROLOGICAL but the WM mask is in radiological, rerun BET to make sure images are in same orientation.
        else
          fslswapdim $origWM -x y z "${SUBJECTOPDIR}"/Intermediate_Files/${1}_"${WM_ID}"_rad;
          radWM="${SUBJECTOPDIR}"/Intermediate_Files/${1}_"${WM_ID}"_rad.nii.gz;
          fslorient -swaporient $radWM;
        fi
      fi

  fi

  # reorient T1 and lesions to standard MNI and binarize lesion masks
  fslreorient2std $radT1 ${SUBJECTOPDIR}/"${1}"_"${ANATOMICAL_ID}"_rad_reorient;

  if [ "${RunBET}" == 0 ]; then
    fslreorient2std $radBET "${SUBJECTOPDIR}"/Intermediate_Files/${1}_"${BET_ID}"_rad_reorient;
  fi

  if [ "${RunWM}" == 0 ]; then
    fslreorient2std $radWM "${SUBJECTOPDIR}"/Intermediate_Files/${1}_"${WM_ID}"_rad_reorient;
  fi

  count=1;
  for Lesion in $radLesions; do
    if [ "${RunWMCorr}" == 1 ] || [ "${RunLL}" == 1 ]; then
      fslreorient2std $Lesion ${SUBJECTOPDIR}/Intermediate_Files/${1}_${LESION_MASK}${count}_rad_reorient;
    else
      fslreorient2std $Lesion ${SUBJECTOPDIR}/${1}_${LESION_MASK}${count}_rad_reorient;
    fi
    count=$((count+1));
  done
  keepSUBJ=1;
  return 1;

}
