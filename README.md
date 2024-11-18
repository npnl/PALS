# Pipeline for Analyzing Lesions after Stroke (PALS)

**Current Version:** 2.0.1 (Last updated 11/18/2024)

## Contents

1. [What is PALS?](#intro)
    1. [Pipeline Overview](#pipeline-overview)
2. [Installation](#installation)
    1. [Dependencies](#dependencies)
    2. [PALS Installation](#pals-installation)
3. [Expected Data Structure](#datastructure)
4. [Usage](#usage)  
    1. [Before First Use](#before-first-use)
    2. [Running Using Command Line Inputs](#cli-inputs)
    3. [Running Using Configuration File](#config-inputs)
    4. [Running Multiple Configurations Files](#multiple-configs)
5. [Configuration Options](#config)
6. [Outputs](#outputs)
7. [Quality Checking Data](#qc)
7. [Planned Developments](#planned-developments)
8. [Citing PALS](#citation)

## What is PALS?<a name=intro></a>

PALS is a flexible, scalable toolbox to facilitate image processing and analysis for subjects with stroke lesions. The pipeline requires two inputs: a T1-weighted MRI image and a stroke segmentation mask. 

For additional information about the original implementation, please see the publication in [Frontier in Neuroinformatics](https://www.frontiersin.org/articles/10.3389/fninf.2018.00063/full).

### Pipeline Overview

The PALS pipeline consists of six modules.

1. Reorientation to MNI Standard (via FSL fslreorient2std)
2. Intensity Inhomogeneity Correction (via ANTs N4BiasFieldCorrection)
3. Brain Extraction (via FSL BET)
4. Registration to MNI Template (via FSL FLIRT)
5. Lesion load calculation
6. Quality check of processing outputs

## Installation

Installing the PALS code requires roughly 23.4 MB of space, exclusive of dependencies. 

### Dependencies

PALS requires the ANTs and FSL neuroimaging packages to run in entirety. If not already installed, please follow the links below to find instructions to install each package:

- [ANTs](https://github.com/ANTsX/ANTs)
- [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki)

Be sure to add each to your PATH variable in the command line. 

PALS also uses Python to run the pipeline. PALS was developed and tested on Python 3.8 and 3.10, but should be compatible with any Python version after 3.8. If you do not already have Python installed, we link to the official distribution to [install Python](https://www.python.org/downloads).

We recommend that you also install the Python virtual environment manager [Virtualenv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).

### PALS Installation

1. <a name=venv></a>Create a virtual environment in your workspace for PALS with `python -m venv pals_venv` and activate the environment with `source pals_venv/bin/activate`. You can deactivate the environment by typing `deactivate` in the command line when not using PALS. You will need to activate the environment every time before use.

2. Navigate to a folder of your choice on your computer, then clone the PALS repository to your computer:
    `git clone https://github.com/npnl/PALS`

3. Navigate into the `PALS` folder:
    `cd PALS`

4. Install the Python package dependencies:
    `python -m pip install -r requirements.txt`

## Expected Data Structure<a name=datastructure></a>

PALS is designed to have outputs saved to a BIDS derivatives folder. While PALS generates outputs in [BIDS-compatible](https://bids-specification.readthedocs.io/en/stable/) format, it does not require inputs to be in BIDS-compatible structure. 

However, we do recommend adhering to the BIDS structure as much as possible by specifying `SESSION_ID` to the BIDS format of `sub-[SUBJECT]_ses-[SESSION]`.

## Usage

PALS is currently developed to run only in the command line. There are two ways to run PALS: (1) using command line inputs, or (2) using a config (short for *configuration*) JSON file. 

Please note that a full run of the PALS pipeline requires at least 2GB of RAM (ideal is 8GB of RAM), and roughly 65 MB of storage.

The following sections describe how to run PALS using each method.

### Before First Use

1. Navigate to the PALS repository, and open the `presets.json` in a text editor.

2. The JSON file should look like this initially:

```{json}
{
    "ants_path" : "",
    "fsl_path" : "",
    "rois_path" : "",
    "template_directory" : ""
}
```

For each key, be sure to fill the value according to the following instructions:

- `ants_path` : This variable sets the path to your ANTs binaries. In your terminal, type `which N4BiasFieldCorrection` and copy the path to this key's value. Remove "/N4BiasFieldCorrection" to ensure the path is set to the ANTs binaries folder.
- `fsl_path` : This variable sets the path to your FSL binaries. In your terminal, type `which flirt` and copy the path to this key's value. Remove "/flirt" to ensure the path is set to the FSL binaries folder.
- `rois_path` : This variable sets the path to the ROIs used to determine lesion load. The PALS repository includes a standard set for your convenience. This key's value should be `[path/to/PALS]/ROIs`.
- `template_directory` : This variable sets the path to the MNI templates used to register the T1 images. The PALS repository includes this for your convenience. This key's value should be `[path/to/PALS]/templates`.

3. Save the `presets.json` file with the filled values. 

### Running Using Command Line Inputs<a name=cli-inputs></a>

Running PALS using the command line inputs is the simplest way to run the pipeline on a single scan. Running PALS this way will use the default configuration.

The required inputs are: (1) the scan identifier (we refer to this as `SESSION_ID`); (2) the path to the T1 image; (3) the path to the lesion mask; and (4) the output directory to save the results. 

1. Activate the [PALS virtual environment](#venv). Navigate to the PALS repository. To run PALS, type the following (replacing the values in square brackets with your actual values):

    `python run_pals.py -s [SESSION_ID] -i [PATH_TO_IMAGE] -l [PATH_TO_LESIONMASK] -o [OUTPUT_DIRECTORY]`

2. Once PALS is run, the outputs will be saved. Information about the outputs can be found in the [outputs section](#outputs).

### Running Using Configuration File<a name=config-inputs></a>

Running PALS with a config (short for *configuration*) JSON file offers greater flexibility in processing data. It allows you to customize the pipeline to suit your preferences and enables programmatic generation of JSON files, reducing the need for manual input.

1. Using a text editor or other means, generate a config file and save as a json file. A sample is provided in the PALS repository (called config.json) and below for your reference, with default values prefilled. Information about the config options can be found in the [config section](#config).

```{json}
{
    "session_id" : "",
    "im_path" : "",
    "les_path" : "",
    "out_dir" : "",
    "run" : "all",
    "space" : "orig",
    "ants_path" : "",
    "fsl_path" : "",
    "rois_path" : "",
    "template_directory" : "",
    "out_format" : "csv",
    "reg_method" : "fsl",
    "reg_costfn" : "corratio",
    "reg_partmask" : false,
    "reg_nomask" : false,
    "bet_g" : -0.25,
    "gif_duration" : 0.5
}
```

2. Activate the [PALS virtual environment](#venv). Navigate to the PALS repository. To run PALS, type the following (replacing the values in square brackets with your actual values):

    `python run_pals.py -c [PATH_TO_CONFIG]`

3. Once PALS is run, the outputs will be saved. Information about the outputs can be found in the [outputs section](#outputs).

### Running Multiple Configuration Files<a name=multiple-configs></a>

The PALS script can be set to run multiple config files in serial. There are two ways to do this: 

1. Input multiple config file paths after the `-c` flag. The command would then be:

    `python run_pals.py -c [PATH_TO_CONFIG_1] [PATH_TO_CONFIG_2] ... [PATH_TO_CONFIG_N]`

2. Input the path to a text file that has each config path on its own line. The command would then be:

    `python run_pals.py -f [PATH_TO_TXT_FILE]`

## Configuration Options<a name=config></a>

PALS offers flexibility to run the pipeline to your specification using the config (short for *configuration*) file. The config options are described below:

- `session_id`: The identifier for the scan. We recommend following the BIDS format of `sub-[SUBJECT]_ses-[SESSION]`.
- `im_path`: The path to the image file corresponding to the T1 weighted MRI. Note that it must be in nifti format.
- `les_path`: The path to the lesion segmentation mask file. Note that it must be in nifti format.
- `out_dir`: The path to the output directory to save the PALS outputs. Note that a folder called `PALS` will be generated within this output directory. See the [output section](#output) for more details.
- `run`: Specifies which processing steps to execute. QC images are generated in all cases. For options other than `all`, the process will skip any steps that have already been completed, and begin at the specified step.
    - `all`: Runs all steps, overwriting any previous outputs and results.
    - `bet`: Starts from the brain extraction step, overwriting all subsequent outputs and results.
    - `mnireg`: Starts from the registration to the MNI template step, overwriting all subsequent outputs and results.
    - `coreg`: Starts from the lesion coregistration step, overwriting all subsequent outputs and results.
    - `pals`: Starts from the lesion load calculation step, overwriting all subsequent outputs and results.
    - `skipdone`: Starts from the first step that has not yet been completed, skipping any steps that are already finished.
- `space`: The space the image and mask are in. Default should be `orig` for images that are unprocessed and/or are in native space. If images are already registered to MNI template, `mni` is an acceptable option to skip all image processing steps and only obtain PALS output. 
- `ants_path`: The path to the ANTs binaries folder. See [Before First Use](#before-first-use) section for more information.
- `fsl_path` : The path to the FSL binaries folder. See [Before First Use](#before-first-use) section for more information.
- `rois_path` : The path to the ROIs folder to obtain lesion loads. See [Before First Use](#before-first-use) section for more information.
- `template_directory`: The path to the MNI template directory. See [Before First Use](#before-first-use) section for more information.
- `out_format`: The format to save the lesion load information. Default is `csv` although `json` is another acceptable option.
- `reg_method`: The registration method. Currently PALS only supports FSL's flirt, although future development may include other options. Thus the default option is `fsl`.
- `reg_costfn`: The cost function to register the T1 image to MNI template. The default option is `corratio`. Other flirt cost function ratios may be used as long as they are valid option (for more information, please see the [FLIRT User Guide](https://web.mit.edu/fsl_v5.0.10/fsl/doc/wiki/FLIRT(2f)UserGuide.html))
- `reg_partmask`: Flag to use a partial weighting mask to register the images. This should be used as the first backup if registration QC fails. By default, PALS uses the brain only to register the image to the MNI template. This allows non-brain features to exert a minor influence the registration, in hopes of finding a better registration.
- `reg_nomask`: Flag to use a no weighting mask (i.e. full scan information) to register the images. This should be used as the second backup if registration QC fails. By default, PALS uses the brain only to register the image to the MNI template. This allows non-brain features to exert the influence as brain features on the registration, in hopes of finding a better registration.
- `bet_g`: Flag to specify the brain extraction vertical gradient. If the brain extraction QC fails, this value can be changed to influence the starting seed for brain extraction. Through trial and error, we have found a `g` value of `-0.25` to be most robust for MPRAGE images given how much neck and spinal cord is included in the field of view. However, this value can differ for every acquisition. For more information, please see the [BET User Guide](https://web.mit.edu/fsl_v5.0.10/fsl/doc/wiki/BET(2f)UserGuide.html)
- `gif_duration`: Flag to specify the number of seconds between each picture in a GIF. By default, we use `0.5` seconds. However, this can be altered to your preference.

## Outputs<a name=outputs></a>

The PALS output directory looks as follows:

```{text}
[OUTPUT_DIRECTORY]/
└── PALS/
    └── [SESSION_ID]/
        ├── results/
        ├── config/
        ├── log/
        ├── qc/
        └── proc/
            ├── 1_fsl_reorient2std/
            ├── 2_ants_N4BiasFieldCorrection/
            ├── 3_fsl_bet/
            └── 4_mni_registration/

```

- The `PALS/` directory is generated inside the specified `out_dir` file in your config or command line input.
- Within the `PALS/` directory a separate folder for each `SESSION_ID` is generated. 
- Within the `SESSION_ID/` directory, the following folders are generated:
    - `results/` : The PALS lesion load analysis files are saved here.
    - `config/` : For each PALS run, a JSON file is generated with the date/time of when the pipeline was run with all the input paths, input options, and output paths saved. If desired, these config files can be used to re-run PALS with the same options.
    - `log/` : For each PALS run, a log TXT file is generated with date/times of each step of the pipeline.
    - `qc/` : PALS generates QC images for key steps of the pipeline. More information can be found in the [QC section](#qc)
    - `proc/` : All PALS intermediary processing files are saved here.

The lesion load analysis, which can be saved as either a CSV or a JSON file, includes the following information:

- `SESSION_ID`: The scan identifier as specified in the config
- `DATE_GENERATED`: The date/time when this PALS output was generated
- `LesionVolume`: The lesion volume as calculated in MNI template space
- `roi_[ROI_NAME]`: The volume overlap between the lesion and each ROI. The ROI_NAME is derived from the nifti file within the ROI folder.
- `roi_[ROI_NAME]_pct`: The percent overlap between the lesion and each ROI. The ROI_NAME is derived from the nifti file within the ROI folder. Percent overlap is calculated as Volume(Overlap) / Volume(ROI). 

Additional outputs of interest are the following (labeled according to the output config json):

- `im_std`: `../proc/1_fsl_reorient2std/[SESSION_ID]_space-orig_desc-std_T1w.nii.gz`
    - The T1 image in standard orientation. This ensures the image and lesion mask are aligned (as sometimes lesion tracing software can alter this).
- `les_std`: `../proc/1_fsl_reorient2std/[SESSION_ID]_space-orig_desc-stdT1lesion_mask.nii.gz`
    - The lesion image in standard orientation. This ensures the image and lesion mask are aligned (as sometimes lesion tracing software can alter this).
- `n4_path`: `../proc/2_ants_N4BiasFieldCorrection/[SESSION_ID]_space-orig_desc-N4_T1w.nii.gz`
    - The T1 image after intensity inhomogeneity correction.
- `im_brain_path`: `../proc/3_fsl_bet/[SESSION_ID]_space-orig_desc-N4T1ext.nii.gz`
    - The brain-extracted T1 image. This zeros out any non-brain structures following BET.
- `im_skull_path`: `../proc/3_fsl_bet/[SESSION_ID]_space-orig_desc-N4T1ext_skull.nii.gz`
    - The skull mask produced by BET.
- `im_brain_mask`: `../proc/3_fsl_bet/[SESSION_ID]_space-orig_desc-N4T1ext_mask.nii.gz`
    - The brain mask produced by BET.
- `im_mni`: `../proc/4_mni_registration/output/[SESSION_ID]_space-MNI152NLin2009aSym_desc-N4_T1w.nii.gz`
    - The T1 image in MNI template space.
- `les_mni`: `../proc/4_mni_registration/output/[SESSION_ID]_space-MNI152NLin2009aSym_desc-N4T1lesion_mask.nii.gz`
    - The lesion mask in MNI template space.
- `im_to_mni_xfm`: `../proc/4_mni_registration/output/[SESSION_ID]_orig_to_MNI152NLin2009aSym.mat`
    - The registration transformation matrix moving from T1 native space to MNI template space.
- `PALS_results`: `../results/[SESSION_ID]_desc-lesionload_results.csv`
    - The lesion load analysis file

## Quality Checking Data<a name=qc></a>

*This section will be written soon*

## Planned Developments

- Updating [QC](#qc) section with examples
- Previously, PALS had a feature to correct lesion masks using the white matter segmentation. Due to development challenges, we have temporarily removed this function from PALS, but hope to include it in future versions. 
- Previously, PALS had a GUI to run PALS. Due to development challenges, we have temporarily removed this function from PALS, but hope to include it in future versions.
- Previously, PALS had a heatmap feature to create a heatmap image of all lesions in a directory. We hope to reincorporate this in future versions.

## Citing PALS<a name=citation></a>

If you use PALS for you paper, please cite the original PALS publication in [Frontier in Neuroinformatics](https://www.frontiersin.org/articles/10.3389/fninf.2018.00063/full).
