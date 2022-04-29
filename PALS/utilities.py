import pandas as pd
import glob, json
from os.path import join, sep, basename
import nibabel as nb, nibabel.processing
import numpy as np
import bids
from bids import BIDSLayout
import PALS

def gather_csv(pals_output_dir: str,
               output_name: str = 'pals.csv'):
    '''
    Gathers the subject-specific .csv produced by the PALS workflow for each subject and places them into a single
    .csv at the top level of the output.
    Parameters
    ----------
    pals_output_dir : str
        Path to the top-level directory where the subject directories are output.
    output_name : str
        Optional. Name for the .csv containing all the gathered info. If there is no directory separator in the output
         name, the file will be saved in the pals_output_dir. Default: 'pals.csv'
    numerical_noise_thresh : float
        Optional. Minimum value for values to not be considered numerical noise.
    Returns
    -------
    None
    '''

    glob_path = join(pals_output_dir, '*', '*', '*', '*.csv')
    csv_list = glob.glob(glob_path)

    csv_output = pd.read_csv(csv_list[0])
    for csv in csv_list[1:]:
        csv_output = csv_output.append(pd.read_csv(csv))
    csv_output.set_index('subject', inplace=True)
    csv_output.sort_index(inplace=True)
    if(sep in output_name):
        csv_output.to_csv(output_name, index='subject')
    else:
        csv_output.to_csv(join(pals_output_dir, output_name), index='subject')
    return

def apply_numerical_thresh(pals_csv: str,
                           output_csv: str,
                           numerical_thresh: float = 1e-8):
    '''
    Applies a threshold to values in a .csv; values below this value are set to 0. This is intended to correct for
    numerical noise introduced by interpolation.
    Parameters
    ----------
    pals_csv : str
        Path to the .csv file to process.
    output_csv : str
        Filepath to save the processed .csv. If None, will overwrite the input.
    numerical_thresh : float
        Optional. Value to use for the threshold. Default: 1e-8

    Returns
    -------
    None
    '''
    if(output_csv is None):
        output_csv = pals_csv
    data = pd.read_csv(pals_csv, index_col='subject')
    for col in data.columns:
        if(data[col].dtype != 'object'):
            data[col][data[col] < numerical_thresh] = 0
    data.to_csv(output_csv)
    return


def compute_roi_lesion_pct(pals_csv: str,
                           roi_dir: str,
                           reference: str,
                           output_csv: str,
                           roi_list: list = None):
    '''
    Computes the percentage of each ROI's volume which is covered by a lesion, then saves the result in the specified
    PALS csv.
    Parameters
    ----------
    pals_csv : str
        Path to the PALS .csv containing the ROI overlap results.
    roi_dir : str
        Path to the directory containing ROIs.
    reference : str
        Path to the reference image used for registration (e.g. MNI152)
    output_csv : str
        Path to the file in which to save the output CSV. If None, overwrites input.
    roi_list : list
        List of paths to ROIs not covered in roi_dir

    Returns
    -------
    None
    '''

    if(output_csv is None):
        output_csv = pals_csv

    # Generate list of ROI files
    rois_to_check = glob.glob(f'{roi_dir}{sep}*nii*')
    if(roi_list is not None):
        rois_to_check += roi_list

    # Generate ROI csv names (remove .nii, .nii.gz)
    roi_names = {}
    roi_names_pct = {}
    for roi in rois_to_check:
        name = roi
        if(name.endswith('.gz')):
            name = name[:-len('.gz')]
        if(name.endswith('.nii')):
            name = name[:-len('.nii')]
        roi_names[roi] = basename(name)
        roi_names_pct[roi] = f'{basename(name)}_pct'

    data = pd.read_csv(pals_csv, index_col='subject')
    # Compute roi pct:
    ref_img = nb.load(reference)
    for roi_path in rois_to_check:
        roi_name = roi_names[roi_path]
        roi_image = nb.load(roi_path)
        roi_resampled = nb.processing.resample_from_to(roi_image, ref_img, order=1)
        roi_resampled_data = roi_resampled.get_fdata()
        roi_volume = np.sum(roi_resampled_data[:])

        data[roi_names_pct[roi_path]] = 100*data[roi_name] / roi_volume
    data.to_csv(output_csv)
    return


def write_dataset_description(bids_root: str,
                              bids_name: str = 'pals_output',
                              bids_version: str = '1.6.0',
                              authors: list = None
                              ):
    '''
    Writes a dataset_description.json file in the `bids_root` directory.
    Parameters
    ----------
    bids_root : str
        Path to the BIDS root directory where the dataset_description.json file should be written.

    Returns
    -------
    None
    '''

    if(authors is None):
        authors = []

    dset_desc = {}
    dset_desc['Name'] = bids_name
    dset_desc['BIDSVersion'] = bids_version
    dset_desc['Authors'] = authors
    dset_desc['PipelineDescription'] = {'Name': 'pals_output'}
    dset_desc['GeneratedBy'] = [{'Name': 'pals', 'Version': PALS.__version__}]
    dset_desc['SourceDatasets'] = [{}]

    f = open(join(bids_root, 'dataset_description.json'), 'w')
    json.dump(dset_desc, f)
    f.close()
    return


def get_subject_sessions(bids_set: BIDSLayout,
                         subject: str):
    '''
    Returns the list of sessions in a BIDS directory for a given subject.
    Parameters
    ----------
    bids_set : BIDSLayout
        BIDS dataset to check
    subject : str
        Subject ID to fetch sessions froms

    Returns
    -------
    list [str]
        List of sessions that a particular subject has.
    '''
    file_list = bids_set.get(subject=subject)
    session_list = set()
    for f in file_list:
        ents = f.entities
        if('session' in ents):
            sess = f.entities['session']
            session_list.add(sess)
    return list(session_list)


