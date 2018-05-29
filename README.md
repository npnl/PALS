# Pipeline for Analyzing Lesions after Stroke (PALS) #


Welcome to our github page!

This page is under construction. Please use under your own discretion.

## What is PALS?

PALS is a scalable and user-friendly toolbox designed to facilitate standardized analysis and ensure quality in stroke research using T1-weighted MRIs. The PALS toolbox offers four moduels integrated into a single pipeline, including (1) reorientation to radiological convention, (2) lesion correction for healthy white matter voxels, (3) lesion load calculation, and (4) visual quality control.

![Image of PALS Data Structure](images/pipeline.png)

## Getting Started

### Prerequisites

* Linux or Mac OS
* [Python 2.7](https://www.python.org/download/releases/2.7/)
* [pip](https://pip.pypa.io/en/stable/installing/)
* [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation)
  * If using a version of FSL older than 5.0.10, separate installion of [FSLeyes](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FSLeyes) is necessary.
* [FreeSurfer](https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall)

For first-time users, PALS might ask for the directory path to FSL binaries.

<!-- ```
Give examples
``` -->

### Install

Clone this github repository:

```
git clone https://github.com/npnl/PALS.git
```

Install `python-tk`
```
sudo apt-get install python-tk
```

Install python dependencies
```
cd PALS
pip install -r requirements.txt
```
---


## Run
Open up your terminal and navigate to the directory containing PALS source code.

```
cd /PATH/TO/PALS
python2.7 run_pals.py
```
This will open up the PALS GUI.

To use PALS, the user must first use a method of their choice to generate initial lesion masks for their dataset.

## Data Structure

![Image of PALS Data Structure](images/data_structure.jpg)

### Inputs

__Required:__  
PALS requires the user to provide an Input Directory with separate Subject Directories containing:

* Subject's T1-weighted anatomical image file (nifti)
* Subject's lesion mask file (nifti)

__Optional:__
* Subject's skull-stripped brain file (nifti)
* Subject's white matter segmentation file (nifti)
* Subject's FreeSurfer T1 file (T1.mgz)
* Subject's FreeSurfer cortical/subcortical parcellation file (aparc+aseg.mgz)

### Outputs

PALS output files and directories will vary depending on the options selected (e.g., *QC_BrainExtractions* for the brain extraction step.)

__QC Directories__  
  A new quality control directory will be created for each intermediary step taken. Each QC directory will contain screenshots for each subject, and a single HTML page for easy visual quality inspection.

__Subject Directories__  
A separate directory will be created for each subject, each of which will contain a __*Intermediate_Files*__ subdirectory.

* __*Intermediate_Files*__ will store all outputs from intermediary processing steps. __*Intermediate_Files*__ will also contain a subdirectory called __*Original_Files*__.

* __*Original_Files*__ will contain a copy of all input files for that subject.

outputs from __reorient__ module:   
>__subjX_T1_rad_reorient.nii.gz__ - subject's original T1 brain file in radiological convention  
>__subjX_lesion1_rad_reorient.nii.gz__ - subject's original lesion mask in radiological convention

outputs from __lesion correction__ module:  
>__subjX_WMAdjusted_lesion1.nii.gz__ - subject's corrected lesion mask with white matter voxels removed

outputs from __lesion load__ module:  
>__subjX_Reg_Brain_MNI.152.nii.gz__ - subject's brain registered to MNI space  
>__subjX_Reg_Brain_custom.152.nii.gz__ - subject's brain registered to user-input template space  
>__subjX_T12FS.nii.gz__ - subject's brain registered to FreeSurfer space  
>__subjX_lesion1_MNI152_bin.nii.gz__ - subject's first lesion mask registered to MNI space  
>__subjX_lesion1_custom_bin.nii.gz__ - subject's first lesion mask registered to user-input template space   
>__subjX_lesion1_FS_bin.nii.gz__ - subject's first lesion mask registered to FreeSurfer space  
>__subjX_roi_name_lesion1_overlap.nii.gz__ - subject's lesion-ROI overlap file (one for each ROI)

__Databases__:
For the lesion correction and lesion load calculation modules, separate CSV files will be created, containing information for all subjects about number of voxels removed and amount of lesion-roi overlap, respectively.



---
### Support

The best way to keep track of bugs or failures is to open a New Issue on the Github system. You can also contact the author via email: kaoriito at usc dot edu.

---

### Authors

* **Kaori Ito** - [Github](https://github.com/kaoriito)
* **Amit Kumar** - [Github](https://github.com/amitasviper)


### License

This project is licensed under the GNU General Public License - see the [LICENSE.md](LICENSE.md) file for details

<!-- ## Acknowledgments

* Hat tip to anyone who's code was used
* Inspiration
* etc -->
