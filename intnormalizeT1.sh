#!/bin/bash

# $1 is the T1 file to be normalized
# $2 is the output file name
# $3 is location of output file

function intnormalizeT1 {

	min=`fslstats $1 -R | awk '{ print $1 }'`;
	max=`fslstats $1 -R | awk '{ print $2 }'`;

	scaling=`echo "scale=5; 255.0 / ( $max - $min )" | bc`;

	fslmaths $1 -sub $min -mul $scaling ${3}/${2}_scaled;
	fslmaths ${3}/${2}_scaled ${3}/${2}_int_scaled;

}
