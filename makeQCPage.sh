#!/bin/bash

function makeQCPage {

	echo "<html>" >  "$1"_QC.html
	echo "<head>" >> "$1"_QC.html
	echo "<style type=\"text/css\">" >> "$1"_QC.html
	echo "*" >> "$1"_QC.html
	echo "{" >> "$1"_QC.html
	echo "margin: 0px;" >> "$1"_QC.html
	echo "padding: 0px;" >> "$1"_QC.html
	echo "}" >> "$1"_QC.html
	echo "html, body" >> "$1"_QC.html
	echo "{" >> "$1"_QC.html
	echo "height: 100%;" >> "$1"_QC.html
	echo "}" >> "$1"_QC.html

	echo ".container { " >> "$1"_QC.html
	echo "height: 240px;" >> "$1"_QC.html 
	echo "overflow: hidden;" >> "$1"_QC.html 
	echo "}" >> "$1"_QC.html

	echo ".container img { " >> "$1"_QC.html
	echo " margin-top: -200px;" >> "$1"_QC.html
	echo "}" >> "$1"_QC.html
	echo "</style>" >> "$1"_QC.html
	echo "</head>" >> "$1"_QC.html
	echo "<body>" >> "$1"_QC.html

	
	IMAGEFILES=`ls *.png`;
	for IMAGE in $IMAGEFILES; do
	
	filename=$(basename "$IMAGE");
	extension="${filename##*.}";
	filename="${filename%.*}";
	
	subjName=$(echo $filename | cut -d '_' -f 1);
	
	if [ "$1" = "Lesions" ]; then 
		lesionNum=$(echo $filename | cut -d '_' -f 2);
	fi
	
		echo "<table cellspacing=\"1\" style=\"width:100%;background-color:#000;\">" >> "$1"_QC.html
		echo "<tr>"	>> "$1"_QC.html
		echo "<td> <FONT COLOR=WHITE FACE=\"Geneva, Arial\" SIZE=5> $subjName </FONT> </td>" >> "$1"_QC.html
		echo "</tr>" >> "$1"_QC.html
		
	if [ "$1" = "Lesions" ]; then 
		echo "<tr>" >> "$1"_QC.html
		echo "<td><FONT COLOR=WHITE FACE=\"Geneva, Arial\" SIZE=3> $lesionNum </FONT><div class=\"container\"><a href=\"file:"$IMAGE"\"><img src=\""$IMAGE"\" height=\"600\" ></a></div></td>" >> "$1"_QC.html
	else 
		echo "<tr>" >> "$1"_QC.html
		echo "<td><div class=\"container\"><a href=\"file:"$IMAGE"\"><img src=\""$IMAGE"\" height=\"600\" ></a></div></td>" >> "$1"_QC.html
	fi
	
	
		echo "</table>" >> "$1"_QC.html
	
 	done;


	echo "</body>" >> "$1"_QC.html

	echo "</html>" >> "$1"_QC.html

}
