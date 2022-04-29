from bids import BIDSLayout
import nibabel as nb
import nibabel.processing
import bidsio
import numpy as np
import bids
import scipy.ndimage

def create_mask_heatmap(mask_root: str,
                          transform_root: str = None,
                          mask_entities: dict = None,
                          transform_entities: dict = None,
                          mask_derivatives_name: str = None,
                          transform_derivatives_name: str = None,
                          output_path: str = 'pals_mask_heatmap.nii.gz'):
    """
    Creates a heatmap from the mask data.
    Parameters
    ----------
    mask_root : str
        Path to the BIDS dataset containing the mask masks.
    transform_root : str
        Path to the BIDS dataset containing the registration transformations for the masks.
    mask_entities : dict
        BIDS entities that identify the mask files. Default: {'subject': '', 'session':'', 'suffix': 'mask'}
    transform_entities : dict
        BIDS entities that identify the transformation files. Default: {'desc': 'transform', 'extension': 'mat'}
    mask_derivatives_name : str
        Optional. Specifies the name of the derivative BIDS directory for the mask data. Default: None
    transform_derivatives_name : str
        Optional. Specifies the name of the derivative BIDS directory for the transformations. Default: None
    output_path : str
        Output path of the heatmap.
    Returns
    -------
    None
    """
    if(mask_entities is None):
        mask_entities = {'subject': '',
                         'session': '',
                         'suffix': 'mask'}
    if(transform_entities is None):
        transform_entities = {'desc': 'transform',
                              'extension': 'mat'}

    # Get matching data.
    loader_args = {'data_root': [mask_root],
                   'data_entities': [mask_entities],
                   'target_root': [],
                   'target_entities': []}
    if(transform_root is not None):
        loader_args['target_root'] = [transform_root]
        loader_args['target_entities'] = [transform_entities]
    if(mask_derivatives_name is not None):
        loader_args['data_derivatives_names'] = [mask_derivatives_name]
    if(transform_derivatives_name is not None):
        loader_args['target_derivatives_names'] = [transform_derivatives_name]
    loader = bidsio.BIDSLoader(**loader_args)
    mask_images = loader.data_list
    transforms = loader.target_list

    heatdata = compute_heatmap(mask_images, transforms, transform_loader=None)
    heat_img = nb.Nifti1Image(heatdata, np.eye(4))
    nb.save(heat_img, output_path)

    return


def compute_heatmap(masks: list,
                    transforms: list = None,
                    transform_loader: callable = None) -> np.array:
    """
    Computes the heatmap of the input masks. If supplied, this function applies the specified transformation
    Parameters
    ----------
    masks : list [BIDSImageFile]
        Masks to use for computing the heatmap; expects a list of BIDSImage files.
    transforms : list [BIDSFile]
        Optional. List of transforms to apply to the masks before computing the heatmap. Assumes that the order is
        the same as the masks. Default: None
    transform_loader : callable
        Function to use for loading the transform file. Signature is 'aff = transform_loader(BIDSFile)'
        Default: np.loadtxt

    Returns
    -------
    np.array
        Heatmap computed from the supplied list of masks.
    """
    heatmap = np.zeros(masks[0][0].get_image().shape, dtype=np.float32)

    if(transforms is not None and transform_loader is None):
        transform_loader = np.loadtxt

    # Decide whether to iterate over transforms or just use identity
    if(transforms is not None):
        mask_zip = zip(masks, _none_generator())
    else:
        mask_zip = zip(masks, transforms)

    for mask_tuple, transf_tuple in mask_zip:
        mask = mask_tuple[0]
        if(transf_tuple is not None):
            transf = transf_tuple[0]
            transf_data = transform_loader(transf)
            image_data = get_transformed_image(mask, transf_data)
        else:
            image_data = mask.get_image().get_fdata()
        heatmap += np.clip(image_data, 0, 1)
    return heatmap


def _none_generator() -> np.array:
    """Generates None forever."""
    while True:
        yield None
    return

def get_transformed_image(image: bids.layout.BIDSImageFile,
                          affine_transf: np.array) -> np.array:
    """
    Loads an image, applies the specified transform, and returns the result.
    Parameters
    ----------
    image : bids.layout.BIDSImageFile
        BIDSImageFile to load
    affine_transf : np.array
        4x4 affine transformation to apply to image.

    Returns
    -------
    np.array
        Transformed image.
    """
    # Load data
    data = image.get_image()
    # data = image.get_image().get_fdata()
    # Apply transformation and return
    return nb.processing.resample_from_to(data, (data.shape, affine_transf @ data.affine), order=1)
