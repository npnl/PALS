# Pipeline for Analyzing Lesions after Stroke (PALS)

## Contents

1. [Introduction](#intro).
2. [Expected Data Structure](#datastructure)
3. [Getting started: Installation Guide](#start)  
   3.1. [Direct use](#direct)
4. [Running PALS](#running)
5. [PALS Configuration Definition](#inputs)

## What is PALS?<a name=intro></a>

PALS is a pipeline for reliably preprocessing images of subjects with stroke lesions. The pipeline is implemented using [Nipype](https://nipype.readthedocs.io/en/latest/), with several modules:

- Reorientation to radiological convention (LAS, left is right)
- Lesion correction for healthy white matter
- Lesion load calculation by ROI

Here is a visualization of the workflow:  
![pals_workflow](img/pals_workflow.png)

For additional information about the original implementation, see the publication in [Frontier in Neuroinformatics](https://www.frontiersin.org/articles/10.3389/fninf.2018.00063/full).

## Expected Data Structure<a name=datastructure></a>

PALS expects its input data to be [BIDS-compatible](https://bids-specification.readthedocs.io/en/stable/) but does not expect any particular values for the BIDS entities. You will need to modify the [configuration file](#config) to set "LesionEntities" and "T1Entities" to match your data. Outputs are provided in BIDS derivatives.

The naming conventions of the input must be as follows:

**Main Image**:

- Unregistered: `sub-{subject}_ses-{session}_T1.nii.gz`
- Registered: `sub-{subject}_ses-{session}_space-{space}_desc_T1.nii.gz`.

**Lesion Mask**: `sub-{subject}_ses-{session}_space-{space}_label-L_desc-T1lesion_mask.nii.gz`.

**White Matter Segmentation File**: `sub-{subject}_ses-{session}_space-{space}_desc-WhiteMatter_mask.nii.gz`.

Where 'space' should be the name of the reference image or 'orig' if unregistered. For example `sub-01_ses-R001_space-orig_desc_T1.nii.gz`

## Getting Started: Installation Guide <a name=start></a>

PALS can be installed directly via the run_pals.py Python code. Additionally, you will have to install the python packages listed in [requirements.txt](https://github.com/npnl/PALS/blob/main/requirements.txt).

### Preparation for Direct Use <a name=direct></a>

A walkthrough of the PALS installation is [available on YouTube](https://youtu.be/8PN3tR34L6g). The command prompts for each step below are in gray.

1. PALS is implemented in Python 3.8.16; you will first need to [install Python](https://www.python.org/downloads/release/python-3810/).
2. We recommend that you also install the Python virtual environment [Virtualenv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).
   `python3.8 -m pip install --user virtualenv`
3. Create a virtual environment in your worksapce for PALS with `python3.8 -m venv pals_venv` and activate the environment with`source pals_venv/bin/activate`. You can deactivate the environment by typing `deactivate` in the command line when not using PALS. You will need to activate the environment every time before use.
4. Install PALS through your terminal using:
   `python3.8 -m pip install -U git+https://github.com/npnl/PALS`

5. Additionally, you will need to download the PALS code to your workspace: `git clone https://github.com/npnl/PALS`

6. You will also need to install the following software packages on your machine. This is the full list of required neuroimaging packages:
   - [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki)
     - For running FLIRT and FAST.
   - Python packages in [requirements.txt]()
     - These can be installed in your virtual environment with bash command `python3.8 -m pip install -r requirements.txt`. Run this command when you have 'cd'ed, or entered, into the cloned PALS directory on the command line: `~/PALS`. This command MUST be run when you have activated your virtual environment as in step 3.

> Note that if your intended pipeline won't use components that are dependent on a particular package, it does not need to be installed. E.g., if you plan to use FLIRT for registration, you don't need to install ANTs.

## Running PALS<a name=running></a>

Once the configuration file is set, you can run PALS from the command line:  
For direct use:  
`python3.8 run_pals.py`

PALS will prompt for required inputs throguh GUI, apply the desired pipeline, then return the output in a BIDS directory specified by info in the 'Outputs' input.
The precise output will depend on the flags you set, but here is a list of the output files you would typically expect:

- `graph.png`, `graph_detailed.png`
  - Visual representation of the pipeline used to generate the data.
- `sub-X_ses-Y_desc-LAS_T1w.nii.gz`
  - The input data reoriented to LAS. "LAS" will change to match your requested orientation.
- `sub-X_ses-Y_desc-LesionLoad.csv`
  - A .csv file containing the lesion load in each of the requested regions of interest. Units are in voxels.
  - `UncorrectedVolume` column contains the total number voxels. `CorrectedVolume` subtracts the white matter voxels (if `LesionCorrection` is set to `true` in the config file) from `UncorrectedVolume`.
- `sub-X_ses-Y_space-SPACE_desc-CorrectedLesion_mask.nii.gz`
  - The lesion mask after white matter correction; note that the quality of the mask depends on the quality of the white matter segmentation.
- `sub-X_ses-Y_space-SPACE_desc-transform.mat`
  - Affine matrix for the transformation used to register the subject images.
- `sub-X_ses-Y_space-SPACE_desc_WhiteMatter_mask.nii.gz`
  - White matter mask generated by the white matter segmentation.

Placeholder values:

- X: subject ID
- Y: session ID
- SPACE: String indicating the space the image is in (e.g. MNI152NLin2009aSym)

## Inputs Definitions <a name=inputs></a>

### Main Modules

#### Reorient to radiological convention

This module will check that all subject inputs are in the same orientation, flag subjects that have mismatched input orientations, and convert all remaining inputs to radiological convention. This is recommended for all datasets, and especially for multi-site data.

##### Orientation

Orientation to standardize to. Options: L/R (left/right), A/P (anterior/posterior), I/S (inferior/superior). Default is LAS.

#### Registration

This module will perform registration to a common template.

##### Registration method

Registration method. Example: FLIRT (default) or leave blank (no registration).

#### Brain Extraction

This module will perform brain extraction. Options: true, false.

##### Brain Extraction Method

Method to use for brain extraction. Options: BET (default) or leave blank (no brain extraction).

#### White Matter Segmentation

This module will perform white matter segmentation. Options: true, false. If false, and you want to perform LesionCorrection, LesionLoadCalculation, or Lesionheatmap, you must place file in same location as the input files in the BIDS structure.

#### Lesion Correction

This module will perform lesion correction. Options: true, false. If true, requires white matter segmentation file.

#### Lesion Load Calculation

This module will compute lesion load. Options: true, false. If true, requires white matter segmentation file.

#### LesionHeatMap

This module will combine the lesions into a heatmap. Options: true, false. If true, requires white matter segmentation file.

### Inputs 

#### BIDS Root Directory

Directory path to the BIDS root directory for the raw data.

#### Subject

ID of the subject to run. Runs all subjects if left blank. Ex: r001s001

#### Session

ID of the session to run. Runs all sessions if left blank. Ex: 1

#### Lesion Root

Path to the BIDS root directory for the lesion masks.

#### White Matter Segmentation Directory

Path to the BIDS root directory for the white matter segmentation files.

#### ROIs Directory

Path to the directory containing ROI image files.

#### Multiprocessing

Number of threads to use for multiprocessing. Has no effect unless more than 1 subject is being processed.

#### Lesion Mask Identifier

##### Space

Provide the space for your lesion file. For example, put 'MNIEx2009aEx' if your file is sub-r044s001_ses-1_space-MNIEx2009aEx_label-L_desc-T1lesion_mask.nii

##### Label

Provide the label for your lesion file. For example, put 'L' if your file is sub-r044s001_ses-1_space-MNIEx2009aEx_label-L_desc-T1lesion_mask.nii

##### Suffix

Provide the suffix for your lesion file. For example, put 'mask' if your file is sub-r044s001_ses-1_space-MNIEx2009aEx_label-L_desc-T1lesion_mask.nii

#### T1 Anatomical Image Identifier

##### Space

Provide the space for your T1 file. For example, put 'MNIEx2009aEx' if your file is sub-r044s001_ses-1_space-MNIEx2009aEx_desc-T1FinalResampledNorm.nii

##### Desc

Provide the desc for your T1 file. For example, put 'T1FinalResampledNorm' if your file is sub-r044s001_ses-1_space-MNIEx2009aEx_desc-T1FinalResampledNorm.nii

### Output

#### Root Directory

Path to directory where to place the output.

#### Start Registration Space

Value to use for 'space' entity in BIDS output filename.

#### Output Registration Space

Reserved for future use.

#### Registration Transform

Path for saving registration transform.

#### Reorient

Path for saving reoriented volume.

#### BrainExtraction

Path for saving the brain extracted volume.

#### LesionCorrected

Path for saving the white matter-corrected lesions.

### Registration

#### Cost Function

Cost function for registration

#### Reference

Path to reference file

### Lesion Correction

#### Image Norm Min

Minimum value for image.

#### Image Norm Max

Maximum value for image

#### White Matter Spread

The deviation of the white matter intensity as a fraction of the mean white matter intensity.

### Heatmap

#### Reference

Overlays the heatmap on this image and creates NIFTI file with overlay and NITFI file with the mask only. Also produces 4 PNGS: 9 slices of the lesions from sagittal, axial, and coronal orientations (3 images) and an image with a cross-section of each orientation. If your images are pre-registered, you MUST use your own reference image used for their registration.

#### Transparency

Transparency to use when mixing the reference image and the heatmap. Smaller values darker reference and lighter heatmap.

## Citing PALS<a name=citation></a>

If you use PALS for you paper, please cite the original PALS publication in [Frontier in Neuroinformatics](https://www.frontiersin.org/articles/10.3389/fninf.2018.00063/full).
