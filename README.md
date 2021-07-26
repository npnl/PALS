# Pipeline for Analyzing Lesions after Stroke (PALS)

## What is PALS?

[PALS](https://www.frontiersin.org/articles/10.3389/fninf.2018.00063/full) is a scalable and user-friendly toolbox designed to facilitate standardized analysis and ensure quality in stroke research using T1-weighted MRIs. The PALS toolbox offers four moduels integrated into a single pipeline, including (1) reorientation to radiological convention, (2) lesion correction for healthy white matter voxels, (3) lesion load calculation, and (4) visual quality control. To learn more, please refer to our [paper in Frontiers](https://www.frontiersin.org/articles/10.3389/fninf.2018.00063/full). 

![Image of PALS Data Structure](images/pipeline.png)

## Getting Started

There are two ways to use PALS:
1. Via a [Singularity container](#singularity)
2. Using your local environment.

The Singularity container is recommended since the environment is self-contained, easy to reproduce, and is typically supported by HPC clusters. You can also set up your local environment with PALS's requirements and run it outside of a container.

<a id='singularity'></a>
### Singularity

Singularity first needs to be installed (see [Singularity documentation](https://sylabs.io/docs/). The latest version is recommended. 

#### Local build
The definition file, `pals_singularity.def` can be used to build the image locally:
```
sudo singularity build pals.sif pals_singularity.def
```
The output image, `pals.sif` will be output in the current directory. Note that since this is run with elevated privileges, you should check for `%pre` and `%setup` sections of the definition file before building the image; these sections are run on the host machine and are potential security risks. These sections are not used for PALS.  

### Data Structure
PALS expects one of two formats for your data: [BIDS](https://bids.neuroimaging.io/), or the legacy custom PALS structure. In either case, each subject requires a **structural T1w image** and a **mask covering the lesions**.

#### BIDS
If your data is BIDS-compatible, you only need to set the input path to the BIDS root directory. Since lesion masks are derivatives, you can specify the pipeline name using the `lesion_mask_id` parameter of the config file. PALS expects the data to be of the form `BIDS_ROOT/derivatives/[lesion_mask_id]/sub-123/ses-1/sub-123_[...]_desc-[lesion_mask_id]`.

#### Legacy
Note that this structure is slated for deprecation; future versions of PALS may not support 
1. Gather all subjects on which you want to perform PALS operations into a single data directory. This directory should contain sub-directories with subject ID's for each subject (see [Data Structure](#data_structure)). For example, here we will call this directory `/subjects`.
2. Create another directory which would contain the result files after running PALS on the input subjects. We will call this directory  `/results` in our example.
3. Go to [PALS Config Generator](https://npnl.github.io/ConfigGenerator/), select all the options that apply and download the config file. This step will download a file named `config.json`. __Do not rename this file.__
4. Store the config file in a separate directory. Here, we have moved our config file to our `/settings` directory

### Running PALS
PALS uses a configuration file to control its behaviour; you can use the [PALS config generator](https://npnl.github.io/ConfigGenerator/) to create one. It is then passed to PALS using the `--config` flag.

#### Singularity
Running the Singularity container is done using the `singularity run` command. The `run` command accepts arguments and passes them directly to PALS. You'll need to specify the path to the config file, and set the `-b` flag if you're dealing with a BIDS directory:  
```
singularity run pals.sif --config config.json -b
```

If your data directories are not visible to your container, you may need to use a bind mount using the `-B` flag.
```
singularity run -B data_directory:/data_directory pals.sif --config config.json -b
```

Similarly for the output directory:
```
singularity run -B data_directory:/data_directory pals.sif -B output_directory:/output_directory/ --config config.json -b
```

#### Local
The run method is run through Python; otherwise, the syntax is identical to the previous section:  
```
python3.8 run_pals.py --config config.son -b
```


### Requirements
Singularity version >3.5  
  
**or**  
  
Python version >3.8
	See `requirements.txt` for packages.
[FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation)
[FreeSurfer](https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall)

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

The best way to keep track of bugs or failures is to open a [New Issue](https://github.com/npnl/PALS/issues/new) on the Github system. You can also contact the author via email: kaoriito at usc dot edu.

---

### Referencing

Please reference our overview paper when using PALS:

*Ito, K. L., Kumar, A., Zavaliangos-Petropulu, A., Cramer, S. C., & Liew, S. L. (2018). Pipeline for Analyzing Lesions After Stroke (PALS). Frontiers in neuroinformatics, 12, 63.*

### Authors

* **Kaori Ito** - [Github](https://github.com/kaoriito)
* **Amit Kumar** - [Github](https://github.com/amitasviper)


### License

This project is licensed under the GNU General Public License - see the [LICENSE.md](LICENSE.md) file for details

<!-- ## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc -->
