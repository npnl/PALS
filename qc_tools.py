import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
import imageio
import os
from subprocess import call

def print_msg(msg):
    """
    Prints a message to the console using the echo command.

    Args:
        msg (str): The message to be printed.
    """
    call(['echo',msg])

def get_slice_indices(shape, vals=[0.25, 0.37, 0.5, 0.63, 0.75]):
    """
    Get slice indices for given fractions of max slice along each axis.

    Args:
        shape (int): The size of the dimension to slice.
        vals (list of float): The fractions of the dimension to get slices for.

    Returns:
        list of int: The slice indices.
    """
    return [int(val * shape) for val in vals]

def generate_slices(data, slices, axis):

    """
    Generate slices along a given axis.
    
    Args:
        data (numpy.ndarray): The input data array from which slices are to be generated.
        slices (list of int): A list of indices specifying the slices to be taken along the specified axis.
        axis (int): The axis along which to take the slices. Must be 0, 1, or 2.

    Returns:
        list of numpy.ndarray: A list of slices taken from the input data array along the specified axis.
    """
    if axis == 0:
        return [data[s, :, :] for s in slices]
    elif axis == 1:
        return [data[:, s, :] for s in slices]
    elif axis == 2:
        return [data[:, :, s] for s in slices]

def plot_and_save_slices(slices_1, slices_2, slice_ixs, axis_ix, out_dir, out_base, fig1_caption, fig2_caption, gif_duration=1):
    """
    Plots and saves slices from two sets of NIfTI images, and generates a GIF comparing them.
    
    Args:
        slices_1 (list of ndarray): List of 2D arrays representing slices from the first NIfTI image.
        slices_2 (list of ndarray): List of 2D arrays representing slices from the second NIfTI image.
        slice_ixs (list of int): List of slice indices to be plotted.
        axis_ix (int): Axis index (0 for sagittal, 1 for coronal, 2 for axial).
        out_dir (str): Output directory where the images and GIF will be saved.
        out_base (str): Base name for the output GIF file.
        fig1_caption (str): Caption for the first set of slices.
        fig2_caption (str): Caption for the second set of slices.
        gif_duration (float, optional): Duration for each frame in the GIF. Default is 1 second.
    """
    
    axis_dict = {2: 'axial', 1: 'coronal', 0: 'sagittal'}
    gif_images = []

    fig1, axs1 = plt.subplots(1, 5, figsize=(20, 5))
    fig1.tight_layout()
    fig2, axs2 = plt.subplots(1, 5, figsize=(20, 5))
    fig2.tight_layout()

    for i, (slice_1, slice_2, slc) in enumerate(zip(slices_1, slices_2, slice_ixs)):
        # NIfTI 1 frame
        axs1[i].imshow(np.rot90(slice_1), cmap='gray')
        axs1[i].set_title(f'{fig1_caption} {axis_dict[axis_ix]} slice {slc}')
        axs1[i].axis('off')

        # NIfTI 2 frame
        axs2[i].imshow(np.rot90(slice_2), cmap='gray')
        axs2[i].set_title(f'{fig2_caption} {axis_dict[axis_ix]} slice {slc}')
        axs2[i].axis('off')
        
    temp_filename_1 = os.path.join(out_dir, f'temp_nifti1_{axis_ix}.png')
    fig1.savefig(temp_filename_1)
    plt.close(fig1)

    temp_filename_2 = os.path.join(out_dir, f'temp_nifti2_{axis_ix}.png')
    fig2.savefig(temp_filename_2)
    plt.close(fig2)

    # Append both images for alternating GIF cycle
    gif_images.append(imageio.imread(temp_filename_1))
    gif_images.append(imageio.imread(temp_filename_2))

    # Generate GIF
    gif_filename = os.path.join(out_dir, f'{out_base}_{axis_dict[axis_ix]}_comparison.gif')
    imageio.mimsave(gif_filename, gif_images, duration=gif_duration)
    call(['chmod','770',gif_filename])
    print_msg(f"GIF saved: {gif_filename}")

    # Cleanup temporary files
    os.remove(temp_filename_1)
    os.remove(temp_filename_2)

def compare_two_ims(out_dir, im1_path, im2_path, basename='', name_im1='', name_im2='', gif_duration=1):
    """
    Generate GIF comparing two NIfTI slices.
    
    Args:
        out_dir (str): Directory where the output GIFs will be saved.
        im1_path (str): Path to the first NIfTI image file.
        im2_path (str): Path to the second NIfTI image file.
        basename (str, optional): Base name for the output GIF files. Default is an empty string.
        name_im1 (str, optional): Name label for the first image. Default is an empty string.
        name_im2 (str, optional): Name label for the second image. Default is an empty string.
        gif_duration (int, optional): Duration of the GIF in seconds. Default is 1 second.
        
    Raises:
        ValueError: If the NIfTI files do not have the same shape.
    """
    # Load the NIfTI files
    data_1 = nib.load(im1_path).get_fdata()
    data_2 = nib.load(im2_path).get_fdata()

    # Ensure the shapes of both files match
    if data_1.shape != data_2.shape:
        raise ValueError("The NIfTI files do not have the same shape!")

    for axis in range(3):
        shape = data_1.shape[axis]
        slice_indices = get_slice_indices(shape)
        
        # Extract slices along each axis
        slices_1 = generate_slices(data_1, slice_indices, axis)
        slices_2 = generate_slices(data_2, slice_indices, axis)
        
        # Plot and save comparison GIFs with alternating NIfTI displays
        plot_and_save_slices(slices_1, slices_2, slice_indices, axis, out_dir, f'{basename}{name_im1}_to_{name_im2}', name_im1, name_im2, gif_duration=gif_duration)

def generate_mask_qc(out_dir, im_path, mask_path, basename='', caption='', binarize=False, cmap='Reds', alpha=0.3):
    """
    Generates quality control (QC) images by overlaying a mask on an image and saves the resulting images.
    
    Args:
        out_dir (str): The directory where the output images will be saved.
        im_path (str): The file path to the input NIfTI image.
        mask_path (str): The file path to the mask NIfTI image.
        basename (str, optional): The base name for the output image files. Default is an empty string.
        caption (str, optional): The caption to be added to the images. Default is an empty string.
        binarize (bool, optional): If True, binarizes the mask data. Default is False.
        cmap (str, optional): The colormap to be used for the mask overlay. Default is 'Reds'.
        alpha (float, optional): The alpha blending value for the mask overlay. Default is 0.3.
    
    Raises:
        ValueError: If the shapes of the input image and mask do not match.
    """
    axis_dict = {2: 'axial', 1: 'coronal', 0: 'sagittal'}
    im_data = nib.load(im_path).get_fdata()
    mask_data = nib.load(mask_path).get_fdata()

    if binarize:
        mask_data[mask_data>0] = 1.0
        mask_data[mask_data<=0] = 0.0

    # Ensure the shapes of both files match
    if im_data.shape != mask_data.shape:
        raise ValueError("The NIfTI files do not have the same shape!")

    for axis in range(3):
        shape = im_data.shape[axis]
        slice_indices = get_slice_indices(shape)
        
        # Extract slices along each axis
        slices_1 = generate_slices(im_data, slice_indices, axis)
        slices_2 = generate_slices(mask_data, slice_indices, axis)
        
        fig, axs = plt.subplots(1, 5, figsize=(20, 5))
        fig.tight_layout()
        
        for i, (slice_1, slice_2, slc) in enumerate(zip(slices_1, slices_2, slice_indices)):
            # NIfTI 1 frame
            axs[i].imshow(np.rot90(slice_1), cmap='gray')
            axs[i].imshow(np.rot90(slice_2), cmap=cmap, alpha=alpha)
            axs[i].set_title(f'{caption} {axis_dict[axis]} slice {slc}')
            axs[i].axis('off')

        out_im = os.path.join(out_dir, f'{basename}{axis_dict[axis]}.png')
        fig.savefig(out_im)
        plt.close(fig)
        call(['chmod','770',out_im])
        print_msg(f"PNG saved: {out_im}")

def generate_im_qc(out_dir, im_path, basename='', caption='', binarize=False):
    """
    Generate quality control images for a given NIfTI image along different anatomical planes.
    
    Args:
        out_dir (str): The directory where the output images will be saved.
        im_path (str): The file path to the input NIfTI image.
        basename (str, optional): The base name for the output image files. Default is an empty string.
        caption (str, optional): The caption to be included in the image titles. Default is an empty string.
        binarize (bool, optional): Whether to binarize the image slices. Default is False.
    """
    axis_dict = {2: 'axial', 1: 'coronal', 0: 'sagittal'}
    im_data = nib.load(im_path).get_fdata()

    for axis in range(3):
        shape = im_data.shape[axis]
        slice_indices = get_slice_indices(shape)
        
        # Extract slices along each axis
        slices_1 = generate_slices(im_data, slice_indices, axis)
        
        fig, axs = plt.subplots(1, 5, figsize=(20, 5))
        fig.tight_layout()
        
        for i, (slice_1, slc) in enumerate(zip(slices_1, slice_indices)):
            # NIfTI 1 frame
            axs[i].imshow(np.rot90(slice_1), cmap='gray')
            axs[i].set_title(f'{caption} {axis_dict[axis]} slice {slc}')
            axs[i].axis('off')

        out_im = os.path.join(out_dir, f'{basename}{axis_dict[axis]}.png')
        fig.savefig(out_im)
        plt.close(fig)
        call(['chmod','770',out_im])
        print_msg(f"PNG saved: {out_im}")


if __name__ == '__main__':
    pass