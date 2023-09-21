import argparse
from multiprocessing.managers import ValueProxy
import bids
import os
import multiprocessing
from nipype.pipeline import Node, MapNode, Workflow
from nipype.interfaces.utility import Function
from nipype.interfaces.io import BIDSDataGrabber, DataSink, SQLiteSink
from nipype.interfaces.image import Reorient
from nipype.interfaces.fsl import FAST
import pathlib
from copy import deepcopy
from os.path import join
from . import node_fetch
from .config_parse import PALSConfig
import warnings
from . import utilities as util
from . import heatmap
import nibabel as nb
import numpy as np
from matplotlib import pyplot as plt
import scipy.ndimage as ndi

bids.config.set_option('extension_initial_dot', True)


def pals(pals_config: dict, progress_string: ValueProxy):
    # Get config file defining workflow
    # configs = json.load(open(config_file, 'r'))
    print('Starting: initializing workflow.')
    progress_string.value = str(progress_string.value) + 'Starting: pals workflow for subject: {0}, session: {1}\n'.format(pals_config['Subject'], pals_config['Session'])
    # Build pipeline
    wf = Workflow(name='PALS')

    # bidsLayout = bids.BIDSLayout(config['BIDSRoot'])
    # Get data
    loader = BIDSDataGrabber(index_derivatives=False)
    loader.inputs.base_dir = pals_config['BIDSRoot']
    loader.inputs.subject = pals_config['Subject']
    if pals_config['Session'] is not None:
        loader.inputs.session = pals_config['Session']
    loader.inputs.output_query = {'t1w': dict(**pals_config['T1Entities'], invalid_filters='allow')}
    loader.inputs.extra_derivatives = [pals_config['BIDSRoot']]
    loader = Node(loader, name='BIDSgrabber')

    entities = {'subject': pals_config['Subject'], 'session': pals_config['Session'], 'suffix': 'T1w', 'extension': '.nii.gz'}

    # Reorient to radiological
    if pals_config['Analysis']['Reorient']:
        radio = MapNode(Reorient(orientation=pals_config['Analysis']['Orientation']), name="reorientation",
                        iterfield='in_file')
        if 'Reorient' in pals_config['Outputs'].keys():
            reorient_sink = MapNode(Function(function=copyfile, input_names=['src', 'dst']),
                                    name='reorient_copy', iterfield='src')
            path_pattern = 'sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_desc-' + pals_config['Analysis'][
                'Orientation'] + '_{suffix}{extension}'
            reorient_filename = join(pals_config['Outputs']['Reorient'], path_pattern.format(**entities))
            pathlib.Path(os.path.dirname(reorient_filename)).mkdir(parents=True, exist_ok=True)
            reorient_sink.inputs.dst = reorient_filename
            wf.connect([(radio, reorient_sink, [('out_file', 'src')])])
            
    else:
        radio = MapNode(Function(function=infile_to_outfile, input_names='in_file', output_names='out_file'),
                        name='identity', iterfield='in_file')

    # Brain extraction
    bet = node_fetch.extraction_node(pals_config, **pals_config['BrainExtraction'])
    if 'BrainExtraction' in pals_config['Outputs'].keys():
        path_pattern = 'sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_space-' + \
                       pals_config['Outputs']['StartRegistrationSpace'] + '_desc-brain_mask{extension}'
        brain_mask_sink = MapNode(Function(function=copyfile, input_names=['src', 'dst']),
                                  name='brain_mask_sink', iterfield='src')
        brain_mask_out = join(pals_config['Outputs']['BrainExtraction'], path_pattern.format(**entities))
        pathlib.Path(os.path.dirname(brain_mask_out)).mkdir(parents=True, exist_ok=True)
        brain_mask_sink.inputs.dst = brain_mask_out

    ## Lesion load calculation
    # Registration
    reg = node_fetch.registration_node(pals_config, **pals_config['Registration'])
    if 'RegistrationTransform' in pals_config['Outputs'].keys():
        path_pattern = 'sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_space-' + \
                       pals_config['Outputs']['StartRegistrationSpace'] + '_desc-transform.mat'
        path_pattern_nifti = 'sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_space-' + \
                       pals_config['Outputs']['StartRegistrationSpace'] + '_desc-transform.nii.gz'
        registration_transform_filename = join(pals_config['Outputs']['RegistrationTransform'],
                                               path_pattern.format(**entities))
        registration_nifti_filename = join(pals_config['Outputs']['RegistrationTransform'],
                                               path_pattern_nifti.format(**entities))
        registration_transform_sink = MapNode(Function(function=copyfile, input_names=['src', 'dst']),
                                              name='registration_transf_sink', iterfield='src')
        registration_nifti_sink = MapNode(Function(function=copyfile, input_names=['src', 'dst']),
                                              name='registration_nifti_sink', iterfield='src')
        pathlib.Path(os.path.dirname(registration_transform_filename)).mkdir(parents=True, exist_ok=True)
        registration_transform_sink.inputs.dst = registration_transform_filename
        registration_nifti_sink.inputs.dst = registration_nifti_filename
        wf.connect([(reg, registration_transform_sink, [('out_matrix_file', 'src')]), 
                    (reg, registration_nifti_sink, [('out_file', 'src')])])

    # Get mask
    mask_path_fetcher = Node(BIDSDataGrabber(base_dir=pals_config['LesionRoot'],
                                             subject=pals_config['Subject'],
                                             index_derivatives=False,
                                             output_query={'mask': dict(**pals_config['LesionEntities'],
                                                                        invalid_filters='allow')},
                                             extra_derivatives=[pals_config['LesionRoot']]
                                             ), name='mask_grabber')
    if pals_config['Session'] is not None:
        mask_path_fetcher.inputs.session = pals_config['Session']

    # Apply reg file to lesion mask
    apply_xfm = node_fetch.apply_xfm_node(pals_config)

    # Lesion load calculation
    if pals_config['Analysis']['LesionLoadCalculation']:
        lesion_load = MapNode(Function(function=overlap, input_names=['ref_mask', 'roi_list'], output_names='out_list'),
                              name='overlap_calc', iterfield=['ref_mask'])
        roi_list = []
        if os.path.exists(pals_config['ROIDir']):
            buf = os.listdir(pals_config['ROIDir'])
            roi_list = [os.path.abspath(os.path.join(pals_config['ROIDir'], b)) for b in buf]
        else:
            warnings.warn(f"ROIDir ({pals_config['ROIDir']}) doesn't exist.")
        buf = pals_config['ROIList']
        roi_list += [os.path.abspath(b) for b in buf]
        roi_list.sort(reverse=True)
        lesion_load.inputs.roi_list = roi_list

        # CSV output
        csv_output = MapNode(Function(function=csv_writer, input_names=['filename', 'data_dict', 'subject', 'session']),
                             name='csv_output', iterfield=['data_dict'])
        csv_output.inputs.subject = pals_config['Subject']
        csv_output.inputs.session = pals_config['Session']
        path_pattern = 'sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_desc-LesionLoad.csv'
        csv_out_filename = join(pals_config['Outputs']['RegistrationTransform'], path_pattern.format(**entities))
        csv_output.inputs.filename = csv_out_filename

        wf.connect([(apply_xfm, lesion_load, [('out_file', 'ref_mask')]),
                    (lesion_load, csv_output, [('out_list', 'data_dict')])])

    # #Lesion correction
    if pals_config['Analysis']['LesionCorrection']:
        # White matter removal node. Does the white matter correction; has multiple inputs that need to be supplied.
        wm_removal = MapNode(Function(function=white_matter_correction, input_names=['image', 'wm_mask', 'lesion_mask',
                                                                                     'max_difference_fraction'],
                                      output_names=['out_data', 'corrected_volume']),
                             name='wm_removal', iterfield=['image', 'wm_mask', 'lesion_mask'])
        wm_removal.inputs.max_difference_fraction = pals_config['LesionCorrection']['WhiteMatterSpread']

        # #File loaders
        # Loads the subject image, passes it to wm_removal node
        subject_image_loader = MapNode(
            Function(function=image_load, input_names=['in_filename'], output_names='out_image'),
            name='file_load0', iterfield='in_filename')
        wf.connect([(radio, subject_image_loader, [('out_file', 'in_filename')]),
                    (subject_image_loader, wm_removal, [('out_image', 'image')])])

        # Loads the mask image, passes it to wm_removal node
        mask_image_loader = MapNode(
            Function(function=image_load, input_names=['in_filename'], output_names='out_image'),
            name='file_load2', iterfield='in_filename')
        wf.connect([(mask_path_fetcher, mask_image_loader, [('mask', 'in_filename')]),
                    (mask_image_loader, wm_removal, [('out_image', 'lesion_mask')])])

        # Save lesion mask with white matter voxels removed
        output_image = MapNode(Function(function=image_write, input_names=['image', 'reference', 'file_name']),
                               name='image_writer0', iterfield=['image', 'reference'])
        path_pattern = 'sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_space-' + \
                       pals_config['Outputs']['StartRegistrationSpace'] + '_desc-CorrectedLesion_mask{extension}'
        lesion_corrected_filename = join(pals_config['Outputs']['LesionCorrected'], path_pattern.format(**entities))
        output_image.inputs.file_name = lesion_corrected_filename
        wf.connect([(wm_removal, output_image, [('out_data', 'image')]),
                    (mask_path_fetcher, output_image, [('mask', 'reference')])])

        # CSV output
        csv_output_corr = MapNode(
            Function(function=csv_writer, input_names=['filename', 'subject', 'session', 'data', 'data_name']),
            name='csv_output_corr', iterfield=['data'])
        csv_output_corr.inputs.subject = pals_config['Subject']
        csv_output_corr.inputs.session = pals_config['Session']
        csv_output_corr.inputs.data_name = 'CorrectedVolume'

        path_pattern = 'sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_desc-LesionLoad.csv'
        csv_out_filename = join(pals_config['Outputs']['RegistrationTransform'], path_pattern.format(**entities))
        csv_output_corr.inputs.filename = csv_out_filename

        wf.connect([(wm_removal, csv_output_corr, [('corrected_volume', 'data')])])

        # White matter segmentation; either do segmentation or load the file
        if pals_config['Analysis']['WhiteMatterSegmentation']:
            # Config is set to do white matter segmentation
            # T1 intensity normalization
            t1_norm = MapNode(
                Function(function=rescale_image, input_names=['image', 'range_min', 'range_max', 'save_image'],
                         output_names='out_file'), name='normalization', iterfield=['image'])
            t1_norm.inputs.range_min = pals_config['LesionCorrection']['ImageNormMin']
            t1_norm.inputs.range_max = pals_config['LesionCorrection']['ImageNormMax']
            t1_norm.inputs.save_image = True
            wf.connect([(bet, t1_norm, [('out_file', 'image')])])

            # White matter segmentation
            wm_seg = MapNode(FAST(), name="wm_seg", iterfield='in_files')
            wm_seg.inputs.out_basename = "segmentation"
            wm_seg.inputs.img_type = 1
            wm_seg.inputs.number_classes = 3
            wm_seg.inputs.hyper = 0.1
            wm_seg.inputs.iters_afterbias = 4
            wm_seg.inputs.bias_lowpass = 20
            wm_seg.inputs.segments = True
            wm_seg.inputs.no_pve = True
            ex_last = MapNode(Function(function=extract_last, input_names=['in_list'], output_names='out_entry'),
                              name='ex_last', iterfield='in_list')

            file_load1 = MapNode(Function(function=image_load, input_names=['in_filename'], output_names='out_image'),
                                 name='file_load1', iterfield='in_filename')
            # White matter output; only necessary if white matter is segmented
            wm_map = MapNode(Function(function=image_write, input_names=['image', 'reference', 'file_name']),
                             name='image_writer1', iterfield=['image', 'reference'])
            path_pattern = 'sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_space-' + \
                           pals_config['Outputs']['StartRegistrationSpace'] + '_desc-WhiteMatter_mask{extension}'
            wm_map_filename = join(pals_config['Outputs']['LesionCorrected'], path_pattern.format(**entities))
            wm_map.inputs.file_name = wm_map_filename
            wf.connect([(file_load1, wm_map, [('out_image', 'image')]),
                        (mask_path_fetcher, wm_map, [('mask', 'reference')])])
            # Connect nodes in workflow
            wf.connect([(wm_seg, ex_last, [('tissue_class_files', 'in_list')]),
                        (t1_norm, wm_seg, [('out_file', 'in_files')]),
                        # (ex_last, wm_map, [('out_entry', 'image')]),
                        (ex_last, file_load1, [('out_entry', 'in_filename')]),
                        (file_load1, wm_removal, [('out_image', 'wm_mask')])])

        elif pals_config['Analysis']['LesionCorrection']:
            # No white matter segmentation should be done, but lesion correction is expected.
            # White matter segmentation must be supplied
            wm_seg_path = pals_config['WhiteMatterSegmentationRoot']

            # White matter input; files should be in derivative folders
            wm_map = MapNode(Function(function=image_write, input_names=['image', 'reference', 'file_name']),
                             name='image_writer1', iterfield=['image', 'reference'])
            path_pattern = 'sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_space-' + \
                           pals_config['Outputs']['StartRegistrationSpace'] + '_desc-WhiteMatter_mask{extension}'
            wm_seg_path = join(wm_seg_path, path_pattern.format(**entities))

            if os.path.exists(wm_seg_path):
                # keep file the same
                wm_seg_path = wm_seg_path
            elif len(wm_seg_path) == 0 or not os.path.exists(wm_seg_path):
                # Check if file exists at output
                path_pattern = 'sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_space-' + \
                               pals_config['Outputs']['StartRegistrationSpace'] + '_desc-WhiteMatter_mask{extension}'

                wm_map_filename = join(pals_config['Outputs']['LesionCorrected'], path_pattern.format(**entities))
                if os.path.exists(wm_map_filename):
                    wm_seg_path = wm_map_filename

            else:
                raise ValueError('Config file is inconsistent; if WhiteMatterSegmentation is false but LesionCorrection'
                                 ' is true, then WhiteMatterSegmentationRoot must be defined and must exist.')
            file_load1 = MapNode(Function(function=image_load, input_names=['in_filename'], output_names='out_image'),
                                 name='file_load1', iterfield='in_filename')
            file_load1.inputs.in_filename = wm_seg_path

            # Connect nodes in workflow
            wf.connect([(file_load1, wm_removal, [('out_image', 'wm_mask')])])

    # Connecting workflow.
    wf.connect([
        # Starter
        (loader, radio, [('t1w', 'in_file')]),
        (radio, bet, [('out_file', 'in_file')]),
        (bet, reg, [('out_file', 'in_file')]),
        (reg, apply_xfm, [('out_matrix_file', 'in_matrix_file')]),
        (mask_path_fetcher, apply_xfm, [('mask', 'in_file')]),
    ])

    try:
        graph_out = pals_config['Outputs']['LesionCorrected'] + '/sub-{subject}/ses-{session}/anat/'.format(**entities)
        wf.write_graph(graph2use='orig', dotfilename=join(graph_out, 'graph.dot'), format='png')
        os.remove(graph_out + 'graph.dot')
        os.remove(graph_out + 'graph_detailed.dot')
    except OSError:
        warnings.warn("graphviz not installed; can't produce graph. See http://www.graphviz.org/download/ for "
                      "installation instructions.")
    wf.run()
    progress_string.value = str(progress_string.value) + 'Completed: pals workflow for subject: {0}, session: {1}\n'.format(pals_config['Subject'], pals_config['Session'])
    return wf


def copyfile(src, dst):
    import shutil
    shutil.copyfile(src, dst)
    return


def infile_to_outfile(**kwargs):
    return kwargs['in_file']


def extract_last(in_list: list):
    '''
    Returns the last entry
    Parameters
    ----------
    in_list : list

    Returns
    -------

    '''
    return in_list[-1]


def image_load(in_filename: str):
    import nibabel as nb
    return nb.load(in_filename)


def image_write(image, file_name, reference=None):
    '''
    Save image.
    Parameters
    ----------
    image : Nitfti1Image
        Image to save.
    file_name : str
        Path to save the image as.
    reference : Nifti1Image
        Optional. Reference image to save; uses its header to define image atttributes.

    Returns
    -------

    '''
    import nibabel as nb
    if type(image) is not nb.Nifti1Image:
        image = nb.load(image)
    if reference is not None:
        # try to load
        if type(reference) is not nb.Nifti1Image:
            print(f'Warning: {reference} should be Nifti1Image, not {type(reference)}')
            ref = nb.load(reference)
        else:
            ref = reference
        hdr = ref.header
        hdr.set_slope_inter(ref.dataobj.slope, ref.dataobj.inter)  # need to patch since nb doesn't play nice
        new_img = nb.Nifti1Image(image.dataobj, affine=ref.affine, header=hdr)
    else:
        new_img = image
    nb.save(new_img, filename=file_name)
    return


def rescale_image(image, range_min: float = 0, range_max: float = 255, save_image: bool = False):
    '''
    Rescales the image values to be within the specified range.
    Parameters
    ----------
    image : Nifti1Image
        Nibabel image file pointer.
    range_min : float
        Optional. Minimum value for the new image. Default: 0.
    range_max : float
        Optional. Maximum value for the new image. Default: 255.
    save_image : bool
        Optional. If True, will save the rescaled image and return the path.

    Returns
    -------
    Nifti1Image
        Rescaled image.
    '''
    import nibabel as nb
    import numpy as np
    import os
    # Get data
    if type(image) is str:
        image = nb.load(image)

    data = image.get_fdata()
    data_min = np.min(data)
    data_max = np.max(data)
    # Normalize data
    data = (data - data_min) / (data_max - data_min) * (range_max + range_min) - range_min
    rescaled = nb.Nifti1Image(data, affine=image.affine)
    if save_image:
        nb.save(rescaled, 'rescaled_image.nii.gz')
        return os.path.abspath('rescaled_image.nii.gz')
    else:
        return rescaled


def white_matter_correction(image,
                            wm_mask,
                            lesion_mask,
                            max_difference_fraction: float = 0.05):
    '''
    Removes white matter intensities from the lesion mask.
    Parameters
    ----------
    image : Nifti1Image
        Base image to correct.
    wm_mask : Nifti1Image
        White matter mask.
    lesion_mask : Nifti1Image
        Lesion mask.
    max_difference_fraction : float
        Optional. Indicates the fraction of the max value that white matter might deviate from its mean. Higher values
        remove more voxels. Default: 0.05.

    Returns
    -------
    corrected_lesion : Nifti1Image
        Lesion mask with extra white matter voxels removed.
    corrected_lesion_volume : float
        Corrected lesion volume.
    '''
    import numpy as np
    import nibabel as nb

    # Load images
    lesion_mask_data = lesion_mask.get_fdata()
    wm_mask_data = wm_mask.get_fdata()
    image_data = image.get_fdata()

    # Extract white matter that doesn't have lesion to get mean value of white matter
    not_lesion = lesion_mask_data == 0
    wm_mask_sans_lesions = wm_mask_data * not_lesion
    wm_sans_lesions = wm_mask_sans_lesions * image_data

    # Get expected range
    mean_wm = np.mean(wm_sans_lesions[wm_sans_lesions != 0])
    mean_dist = np.max(image_data) * max_difference_fraction / 2
    lower_thresh = mean_wm - mean_dist
    upper_thresh = mean_wm + mean_dist

    lesion_data = image_data * lesion_mask_data
    corrected_lesion_data = lesion_mask_data * ((lesion_data < lower_thresh) + (lesion_data >= upper_thresh))
    corrected_lesion = nb.Nifti1Image(np.array(corrected_lesion_data, dtype=float),
                                      affine=lesion_mask.affine, header=lesion_mask.header)

    return corrected_lesion, np.sum(corrected_lesion_data)


def overlap(ref_mask: str, roi_list: list) -> str:
    '''
    Computes the overlap between the input binary mask file and each of the masks in the list.
    Parameters
    ----------
    ref_mask : str
        Path to binary mask to evaluate.
    roi_list : list
        List of paths to binary masks to compare against the reference mask.

    Returns
    -------
    str
        Path to list of floats indicating the amount of overlap between the reference mask and each ROI in the list.
    '''
    import nibabel as nb
    import nibabel.processing as nbp
    import numpy as np
    import os

    # Initialize; get reference data
    overlap_list = []
    overlap_dict = {}
    ref_image = nb.load(ref_mask)
    ref_dat = nb.load(ref_mask).get_fdata()
    overlap_dict['UncorrectedVolume'] = np.sum(ref_dat)

    # alphabetize ROI list
    roi_list.sort()
    # Compute overlap for each mask
    for roi_file in roi_list:
        roi_image = nb.load(roi_file)
        roi = nb.processing.resample_from_to(roi_image, ref_image, order=1).get_fdata()
        # roi = nb.load(roi_file).get_fdata()
        overlap_val = np.sum(ref_dat * roi)
        overlap_list.append(overlap_val)
        base_roi = os.path.basename(roi_file)
        if base_roi.endswith('.nii.gz'):
            base_roi = base_roi[:-len('.nii.gz')]
        if base_roi.endswith('.nii'):
            base_roi = base_roi[:-len('.nii')]
        overlap_dict[base_roi] = overlap_val
    filename = 'overlap_list'
    f = open(filename, 'w')
    for roi_val in overlap_list:
        f.write(str(roi_val) + '\n')
    f.close()
    return overlap_dict


def csv_writer(filename: str, subject: str, session: str, data_dict: dict = None, data=None, data_name: str = None):
    '''
    Writes dictionary to CSV file.
    Parameters
    ----------
    filename : str
        Output filename.
    subject : str
        Subject ID.
    session : str
        Session ID.
    data_dict : dict
        Dictionary to write to CSV.
    data
        Single data point to write.
    data_name : str
        Name of column.

    Returns
    -------
    None
    '''
    import pandas as pd
    import os

    if data_dict is None:
        data_dict = {data_name: data}
    if os.path.exists(filename):
        pdat = pd.read_csv(filename)
        pdat_cols = pdat.columns
        for col in data_dict.keys():
            if col not in pdat_cols:
                pdat.insert(len(pdat), col, data_dict[col])
    else:
        pdat = pd.DataFrame(data_dict, [0])
    if 'session' not in pdat.columns:
        pdat.insert(0, 'session', session)
    if 'subject' not in pdat.columns:
        pdat.insert(0, 'subject', subject)
    pdat.to_csv(filename, index=False)
    return


def sql_writer(database: str, subject: str, session: str, data_dict: dict = None, table_name='LESION', data=None,
               data_name: str = None):
    '''
    Writes dictioanry to SQL database
    Parameters
    ----------
    database : str
        Path to SQL database. If it doesn't exist, it will be created.
    subject : str
        Subject ID.
    session : str
        Session ID.
    data_dict : dict
        Dictioanry to write to database.
    data : str,float
        Ignored if data_dict is defined. Used to store single-values.
    data_name : str
        Ignored if data_dict is defined. Required with "data". Used to name the single values
    Returns
    -------
    None
    '''
    # Need to import within function due to nipype's dispatching
    import sqlite3
    import os

    # Create data_dict if not defined
    if data_dict is None:
        data_dict = {data_name: data}

    create = False
    if not os.path.exists(database):
        create = True
    else:
        com = sqlite3.connect(database)
        cursor = com.cursor()
        tables = list(cursor.execute("SELECT name FROM sqlite_master WHERE type='table';"))
        com.close()
        if len(tables) == 0:
            create = True
        elif tables[0][0] != table_name:
            create = True
    if create:
        com = sqlite3.connect(database)
        s = f'CREATE TABLE {table_name} ('
        s += 'subject TEXT NOT NULL,'
        s += 'session TEXT NOT NULL,'
        for k in data_dict.keys():
            s += f'{k} FLOAT,'
        # s += 'CONSTRAINT PK_lesion PRIMARY KEY (subject,session));'
        s = s[:-1]
        s += ');'
        print(f'executing: {s}')
        com.execute(s)
        com.close()
    # Check if column needs to be added
    if data_name is not None:
        com = sqlite3.connect(database)
        cursor = com.cursor()
        all = cursor.execute(f'select * from {table_name}')
        col_names = [d[0] for d in all.description]
        if data_name not in col_names:
            # Add column
            cursor = com.cursor()
            cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN {data_name}')
            com.commit()
            com.close()
    keys = tuple(['subject', 'session'] + list(data_dict.keys()))
    data = tuple([subject, session] + list(data_dict.values()))
    print('connecting to db')
    com = sqlite3.connect(database)

    try:
        print('inserting')
        print(f'values: {data}')
        print()
        com.execute(f'INSERT INTO {table_name} {keys} values{data}')
        com.commit()
    except sqlite3.IntegrityError:
        print('updating')
        s = 'UPDATE LESION SET'
        for k, v in data_dict.items():
            s += f' {k}={v} WHERE subject="{subject}" AND session="{session}"'
        com.execute(f'UPDATE {table_name} SET')
        com.commit()
    com.close()
    return


def extract_first(in_list: list) -> str:
    '''
    Returns the first entity of the input list.
    Parameters
    ----------
    in_list : list
        List of strings.

    Returns
    -------
    var
        First element of input
    '''
    return in_list[0]


def create_modified_config_copy(config: dict,
                                subject: str = None,
                                session: str = None) -> dict:
    '''
    Sets the subject and session using a function for parallelization.
    Parameters
    ----------
    config : dict
     Config dict object
    subject : str
        BIDS subject ID
    session : str
        BIDS session ID

    Returns
    -------
    dict
        Config with updated values
    '''
    new_config = deepcopy(config)
    if subject is not None:
        new_config['Subject'] = subject
    if session is not None:
        new_config['Session'] = session
    return new_config


def get_bounds(image, dimension):
    '''
    Locates the edges of the lesions in the lesion mask in the x, y, and z directions.
    Parameters
    ----------
    image
        nb.load MRI image object of the heatmap lesion mask.
    dimension
        "x", "y", or "z"

    Returns
    -------
    bounds
        A 2 element list of the start and stop edge slice indices of the lesions.

    '''
    x_dim = image.shape[0]
    y_dim = image.shape[1]
    z_dim = image.shape[2]
    bounds = [None] * 2  # create list to hold bound

    if dimension == "x":
        # loop through slices in order to get first bound
        for i in range(x_dim):
            if np.average(image.slicer[i:i + 1, ...].get_fdata()) > 0 and bounds[0] is None:
                bounds[0] = i
                break
        # loop through slices in reverse to get second bound
        for j in reversed(range(x_dim)):
            if j == 0:
                break
            if np.average(image.slicer[j - 1:j, ...].get_fdata()) > 0 and bounds[1] is None:
                bounds[1] = j
                break
        return bounds

    elif dimension == "y":
        # loop through slices in order to get first bound
        for i in range(y_dim):
            if np.average(image.slicer[:, i:i + 1, :].get_fdata()) > 0 and bounds[0] is None:
                bounds[0] = i
                break
        # loop through slices in reverse to get second bound
        for j in reversed(range(y_dim)):
            if j == 0:
                break
            if np.average(image.slicer[:, j - 1:j, :].get_fdata()) > 0 and bounds[1] is None:
                bounds[1] = j
                break
        return bounds

    elif dimension == "z":
        # loop through slices in order to get first bound
        for i in range(z_dim):
            if np.average(image.slicer[:, :, i:i + 1].get_fdata()) > 0 and bounds[0] is None:
                bounds[0] = i
                break
        # loop through slices in reverse to get second bound
        for j in reversed(range(z_dim)):
            if j == 0:
                break
            if np.average(image.slicer[:, :, j - 1:j].get_fdata()) > 0 and bounds[1] is None:
                bounds[1] = j
                break
        return bounds


def main():
    parser = argparse.ArgumentParser(description='Pipeline for Analyzing Lesions after Stroke. Runs the PALS processing'
                                                 ' pipeline on a BIDS dataset. Preprocessing includes reorientation '
                                                 'to a common direction, registration, brain extraction, white matter '
                                                 'segmentation, lesion correction, and lesion load calculation. Most '
                                                 'options are controlled via the configuration file.')
    parser.add_argument('--root_dir', type=str, help='BIDS root directory containing the data. If set, overrides the'
                                                     ' value in the config file.', default=None, required=False)
    parser.add_argument('--subject', type=str, help='Subject ID; value of the label associated with the "subject" BIDS'
                                                    ' entity. If set, overrides the value in the config file.',
                        default=None, required=False)
    parser.add_argument('--session', type=str, help='Session ID; value of the label associated with the "session" BIDS'
                                                    ' entity. If set, overrides the value in the config file.',
                        default=None)
    parser.add_argument('--lesion_root', type=str, help='Root directory for the BIDS directory containing the lesion '
                                                        'masks. If set, overrides the value in the config file.',
                        default=None)
    parser.add_argument('--config', type=str, help='Path to the configuration file.', required=True)

    pargs = parser.parse_args()
    pals_config = PALSConfig(pargs.config)

    # config = json.load(open(pargs.config, 'r'))
    if pargs.root_dir is not None:
        pals_config['BIDSRoot'] = pargs.root_dir
    if pargs.subject is not None:
        pals_config['Subject'] = pargs.subject
    if pargs.session is not None:
        pals_config['Session'] = pargs.session
    if pargs.lesion_root is not None:
        pals_config['LesionRoot'] = pargs.lesion_root

    # If either Subject or Session is empty, assume that we'll be processing all subjects + sessions
    no_subject = len(pals_config['Subject']) == 0
    no_session = len(pals_config['Session']) == 0

    dataset_raw = bids.BIDSLayout(root=pals_config['BIDSRoot'],
                                  derivatives=pals_config['BIDSRoot'])
    deriv_list = list(dataset_raw.derivatives.keys())
    if len(deriv_list) > 0:
        derivatives_name = list(dataset_raw.derivatives.keys())[0]
        print(f'Taking {derivatives_name} from derivatives dataset.')
        dataset = dataset_raw.derivatives[derivatives_name]
    else:
        dataset = dataset_raw

    if no_subject:
        subject_list = dataset.entities['subject'].unique()
        print(subject_list)
    elif pargs.subject is not None:
        subject_list = [pargs.subject]
    else:
        subject_list = [pals_config['Subject']]
    if no_session:
        session_list = dataset.entities['session'].unique()
        print(session_list)
    elif pargs.session is not None:
        session_list = [pargs.session]
    else:
        session_list = [pals_config['Session']]

    config_list = []
    for sub in subject_list:
        subject_session_list = util.get_subject_sessions(dataset, sub)
        session_overlap = set(subject_session_list).intersection(set(session_list))
        for ses in session_overlap:
            # Check that subject has the session
            config_list.append(create_modified_config_copy(pals_config,
                                                           subject=sub,
                                                           session=ses))
    num_threads = min(pals_config['Multiprocessing'], len(config_list))
    print(f"Starting {num_threads} threads...")
    p = multiprocessing.Pool(num_threads)
    p.map(pals, config_list)

    # Write out dataset_description.json
    util.write_dataset_description(bids_root=pals_config['Outputs']['Root'])

    # Gather .csv
    output_csv_path = join(pals_config['Outputs']['Root'], 'pals.csv')
    util.gather_csv(pals_output_dir=pals_config['Outputs']['Root'], output_name=output_csv_path)

    # Check if we should create heatmap
    if pals_config['Analysis']['LesionHeatMap']:
        # Load lesion masks, sum, then output at BIDSRoot
        heatmap_output_path = join(pals_config['Outputs']['Root'], 'pals_mask_heatmap.nii.gz')
        heatmap.create_mask_heatmap(mask_root=pals_config['LesionRoot'],
                                    mask_entities=pals_config['LesionEntities'],
                                    transform_derivatives_name='pals_output',
                                    output_path=join(heatmap_output_path))
        # Overlay on reference, if any
        if 'Reference' in pals_config['HeatMap']:
            overlay_name = join(pals_config['Outputs']['Root'], 'pals_mask_heatmap_overlaid.nii.gz')
            ref_image = nb.load(pals_config['HeatMap']['Reference'])
            ref_data = ref_image.get_fdata()
            # Normalize
            ref_data = (ref_data - np.min(ref_data)) / (
                    np.max(ref_data) - np.min(ref_data))  # is this actually normalizing??

            # Load heatmap
            heatmap_image = nb.load(heatmap_output_path)
            heatmap_data = heatmap_image.get_fdata()
            heatmap_data = (heatmap_data - np.min(heatmap_data)) / (np.max(heatmap_data) - np.min(heatmap_data))

            # Combine
            alph = pals_config['HeatMap']['Transparency']
            merged = alph * ref_data + (1 - alph) * heatmap_data
            merged_image = nb.Nifti1Image(merged, affine=ref_image.affine)
            nb.save(merged_image, overlay_name)

            #  check the bounds of the lesions
            x_bounds = get_bounds(heatmap_image, "x")
            y_bounds = get_bounds(heatmap_image, "y")
            z_bounds = get_bounds(heatmap_image, "z")

            # ########### PNGS WITH CROPPED RANGES ###############
            # also save as 8 equally distanced PNG files
            png_output_path = join(pals_config['Outputs']['Root'], 'heatmap_png')
            pathlib.Path(os.path.dirname(png_output_path)).mkdir(parents=True, exist_ok=True)
            if not os.path.exists(png_output_path):
                os.mkdir(png_output_path)

            sag_slices = []
            coronal_slices = []
            axial_slices = []

            # #### SAGITTAL SLICES ###
            fig_rows = 3
            fig_cols = 3
            cbar_loc = [0.9, 0.15, 0.03, 0.65]
            tick_font_size = 16

            sag_fig, sag_axs = plt.subplots(nrows=fig_rows, ncols=fig_cols, layout="compressed", figsize=(10, 10))
            sag_fig.patch.set_facecolor('black')
            x_step = round((x_bounds[1] - x_bounds[0]) // 8) - 1

            for idx, x_slice in enumerate(range(x_bounds[0], x_bounds[1], x_step)):
                ref_png_slice = ref_data[x_slice, :, :]
                mask_png_slice = heatmap_data[x_slice, :, :]
                sag_slices.append([ref_png_slice, mask_png_slice])
                sag_axs.flat[idx].imshow(ndi.rotate(ref_png_slice, 90), cmap='bone')
                im = sag_axs.flat[idx].imshow(ndi.rotate(mask_png_slice, 90), cmap='inferno', alpha=0.5)
                im.set_clim(0, 1)
                sag_axs.flat[idx].axis('off')

            sag_fig.tight_layout()
            plt.subplots_adjust(bottom=0.05, right=0.89, top=0.95)
            cax = plt.axes(cbar_loc)
            cbar = plt.colorbar(im, ax=sag_axs.ravel().tolist(), cax=cax)
            cbar.set_ticks([0, 1], labels=['0', str(num_threads)], color="white")
            cbar.ax.set_yticklabels(['0', str(num_threads)], color="white")
            cbar.ax.tick_params(axis="y", labelsize=tick_font_size)
            cbar.set_label('No. Subjects', color="white", size=tick_font_size)
            plt.savefig(
                png_output_path + '/pals_mask_overlaid_sagittal.png')
            plt.clf()

            # #### CORONAL SLICES ###
            cor_fig, cor_axs = plt.subplots(nrows=3, ncols=3, layout="compressed", figsize=(10, 10))
            cor_fig.patch.set_facecolor('black')
            y_step = round((y_bounds[1] - y_bounds[0]) // 8)

            for idx, y_slice in enumerate(range(y_bounds[0], y_bounds[1], y_step)):
                ref_png_slice = ref_data[:, y_slice, :]
                mask_png_slice = heatmap_data[:, y_slice, :]
                coronal_slices.append([ref_png_slice, mask_png_slice])
                cor_axs.flat[idx].imshow(ndi.rotate(ref_png_slice, 90), cmap='bone')
                im = cor_axs.flat[idx].imshow(ndi.rotate(mask_png_slice, 90), cmap='inferno', alpha=0.5)
                im.set_clim(0, 1)
                cor_axs.flat[idx].axis('off')

            cor_fig.tight_layout()
            plt.subplots_adjust(bottom=0.05, right=0.89, top=0.95)
            cax = plt.axes(cbar_loc)
            cbar = plt.colorbar(im, ax=cor_axs.ravel().tolist(), cax=cax)
            cbar.set_ticks([0, 1], labels=['0', str(num_threads)], color="white")
            cbar.ax.set_yticklabels(['0', str(num_threads)], color="white")
            cbar.ax.tick_params(axis="y", labelsize=tick_font_size)
            cbar.set_label('No. Subjects', color="white", size=tick_font_size)
            plt.savefig(
                png_output_path + '/pals_mask_overlaid_coronal_slice.png')
            plt.clf()

            # #### AXIAL SLICES ###
            axial_fig, axial_axs = plt.subplots(nrows=3, ncols=3, layout="compressed", figsize=(10, 10))
            axial_fig.patch.set_facecolor('black')
            z_step = round((z_bounds[1] - z_bounds[0]) // 8)

            for idx, z_slice in enumerate(range(z_bounds[0], z_bounds[1], z_step)):
                ref_png_slice = ref_data[:, :, z_slice]
                mask_png_slice = heatmap_data[:, :, z_slice]
                axial_slices.append([ref_png_slice, mask_png_slice])
                axial_axs.flat[idx].imshow(ndi.rotate(ref_png_slice, 90), cmap='bone')
                im = axial_axs.flat[idx].imshow(ndi.rotate(mask_png_slice, 90), cmap='inferno', alpha=0.5)
                im.set_clim(0, 1)
                axial_axs.flat[idx].axis('off')

            axial_fig.tight_layout()
            plt.subplots_adjust(bottom=0.05, right=0.89, top=0.95)
            cax = plt.axes(cbar_loc)
            cbar = plt.colorbar(im, ax=axial_axs.ravel().tolist(), cax=cax)
            cbar.set_ticks([0, 1], labels=['0', str(num_threads)], color="white")
            cbar.ax.set_yticklabels(['0', str(num_threads)], color="white")
            cbar.ax.tick_params(axis="y", labelsize=tick_font_size)
            cbar.set_label('No. Subjects', color="white", size=tick_font_size)
            plt.savefig(
                png_output_path + '/pals_mask_overlaid_axial_slice.png')
            plt.clf()

            # MAKE FIGURE WITH 3 ORIENTATIONS
            full_fig, full_axs = plt.subplots(nrows=1, ncols=3, layout="compressed", figsize=(7, 2.5),
                                              gridspec_kw={'width_ratios': [5, 4.25, 3.75]})
            full_fig.patch.set_facecolor('black')
            full_slices = [sag_slices[4], coronal_slices[4], axial_slices[4]]
            for idx, f_slice in enumerate(full_slices):
                full_axs.flat[idx].imshow(ndi.rotate(f_slice[0], 90), cmap='bone')
                im = full_axs.flat[idx].imshow(ndi.rotate(f_slice[1], 90), cmap='inferno', alpha=0.5)
                im.set_clim(0, 1)
                full_axs.flat[idx].axis('off')

            full_fig.tight_layout()
            plt.subplots_adjust(bottom=0.05, right=0.9, top=0.9)
            f_cbar_loc = [0.91, 0.1, 0.03, 0.75]
            cax = plt.axes(f_cbar_loc)
            cbar = plt.colorbar(im, ax=axial_axs.ravel().tolist(), cax=cax)
            cbar.set_ticks([0, 1], labels=['0', str(num_threads)])
            cbar.ax.set_yticklabels(['0', str(num_threads)], color="white")
            cbar.ax.tick_params(color='white')
            cbar.set_label('No. Subjects', color="white")
            plt.savefig(
                png_output_path + '/pals_mask_overlaid.png')
            plt.clf()

    return


if __name__ == "__main__":
    main()
