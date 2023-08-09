import argparse
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

from .pals_workflow import pals, create_modified_config_copy, get_bounds

bids.config.set_option('extension_initial_dot', True)

class operations():
    def __init__(self, controller):
        self.controller = controller
        self.pals_config = self.build_pals_config()

    def build_pals_config(self):
        pals_config={}
        pals_config['Analysis'] = {
            'Reorient': self.controller.b_radiological_convention.get(),
            'Orientation': self.controller.sv_orientation_method.get().strip(),
            'Registration': self.controller.b_registration.get(),
            'RegistrationMethod': self.controller.sv_registration_method.get().strip(),
            'BrainExtraction': self.controller.b_brain_extraction.get(),
            'BrainExtractionMethod': self.controller.sv_brain_extraction_method.get().strip(),
            'WhiteMatterSegmentation': self.controller.b_wm_segmentation.get(),
            'LesionCorrection': self.controller.b_wm_correction.get(),
            'LesionLoadCalculation': self.controller.b_ll_calculation.get(),
            'LesionHeatMap': self.controller.b_lesion_heatmap.get()
            }
        pals_config['BrainExtraction'] = {
            'frac': float(self.controller.sv_brain_ext_frac.get().strip()),
            'mask': self.controller.b_brain_ext_mask.get()
        }
        pals_config['Registration'] = {
        'cost_func': self.controller.sv_reg_cost_func.get().strip(),
        'reference': self.controller.sv_reg_reference.get().strip()
        }
        pals_config['LesionCorrection'] = {
            'ImageNormMin': int(self.controller.sv_img_norm_min.get().strip()),
            'ImageNormMax': int(self.controller.sv_img_norm_max.get().strip()),
            'WhiteMatterSpread': float(self.controller.sv_wm_spread.get().strip())
        }
        pals_config['T1Entities'] = {
            'desc': self.controller.sv_t1_desc.get().strip(),
            'space': self.controller.sv_t1_space.get().strip()
        }
        pals_config['LesionEntities'] = {
            'suffix': self.controller.sv_lesion_mask_suffix.get().strip(),
            'space': self.controller.sv_lesion_mask_space.get().strip(),
            'label': self.controller.sv_lesion_mask_label.get().strip()
        }
        pals_config['HeatMap'] = {
            'Reference': self.controller.sv_heatmap_reference.get().strip(),
            'Transparency': float(self.controller.sv_heatmap_transparency.get().strip())
        }
        pals_config['BIDSRoot'] = self.controller.sv_input_dir.get().strip()
        pals_config['Subject'] = self.controller.sv_subject.get().strip()
        pals_config['Session'] = self.controller.sv_session.get().strip()
        pals_config['LesionRoot'] = self.controller.sv_lesion_root.get().strip()
        pals_config['WhiteMatterSegmentationRoot'] = self.controller.sv_wm_seg_root.get().strip()
        pals_config['ROIDir'] = self.controller.sv_roi_dir.get().strip()
        pals_config['ROIList'] = []
        pals_config['Multiprocessing'] = int(self.controller.sv_multiprocessing.get().strip())

        pals_config['Outputs'] = {
            'Root': self.controller.sv_output_dir.get().strip(),
            'StartRegistrationSpace': self.controller.sv_out_start_reg_space.get().strip(),
            'OutputRegistrationSpace':  self.controller.sv_output_reg_space.get().strip(),
            'RegistrationTransform':  self.controller.sv_out_reg_transform.get().strip(),
            'Reorient':  self.controller.sv_out_reorient.get().strip(),
            'BrainExtraction':  self.controller.sv_out_brain_registration.get().strip(),
            'LesionCorrected': self.controller.sv_out_lesion_corr.get().strip()
        }

        for k, v in pals_config['Outputs'].items():
            if(len(v) == 0):
                pals_config['Outputs'][k] = pals_config['Outputs']['Root']

        if not pals_config['Analysis']['Registration'] and len(pals_config['Outputs']['OutputRegistrationSpace']) == 0:
            pals_config['Outputs']['OutputRegistrationSpace'] = pals_config['Outputs']['StartRegistrationSpace']


        #print(pals_config)
        return pals_config


    def startExecution(self):
        self.controller.updateProgressBar(0)
        # If either Subject or Session is empty, assume that we'll be processing all subjects + sessions
        no_subject = len(self.pals_config['Subject']) == 0
        no_session = len(self.pals_config['Session']) == 0

        dataset_raw = bids.BIDSLayout(root=self.pals_config['BIDSRoot'],
                                    derivatives=self.pals_config['BIDSRoot'])
        deriv_list = list(dataset_raw.derivatives.keys())
        if len(deriv_list) > 0:
            derivatives_name = list(dataset_raw.derivatives.keys())[0]
            self.controller.updateMessage(f'Taking {derivatives_name} from derivatives dataset.')
            dataset = dataset_raw.derivatives[derivatives_name]
        else:
            dataset = dataset_raw

        if no_subject:
            subject_list = dataset.entities['subject'].unique()
            #print(subject_list)
        # elif pargs.subject is not None:
        #     subject_list = [pargs.subject]
        else:
            subject_list = [self.pals_config['Subject']]
        if no_session:
            session_list = dataset.entities['session'].unique()
            #print(session_list)
        # elif pargs.session is not None:
        #     session_list = [pargs.session]
        else:
            session_list = [self.pals_config['Session']]

        config_list = []
        for sub in subject_list:
            subject_session_list = util.get_subject_sessions(dataset, sub)
            session_overlap = set(subject_session_list).intersection(set(session_list))
            for ses in session_overlap:
                # Check that subject has the session
                config_list.append(create_modified_config_copy(self.pals_config,
                                                            subject=sub,
                                                            session=ses))
        num_threads = min(self.pals_config['Multiprocessing'], len(config_list))
        self.controller.updateMessage(f'Starting {num_threads} threads...')
        
        manager = multiprocessing.Manager()
        error_string = manager.Value(str, "")

        with multiprocessing.Pool(num_threads) as p:
            results = p.starmap(pals, [(config, error_string) for config in config_list])
        print(error_string.value)
        self.controller.updateMessage(error_string.value)
        # p = multiprocessing.Pool(num_threads)
        # p.map(pals, config_list)



        # Write out dataset_description.json
        util.write_dataset_description(bids_root=self.pals_config['Outputs']['Root'])

        # Gather .csv
        output_csv_path = join(self.pals_config['Outputs']['Root'], 'pals.csv')
        util.gather_csv(pals_output_dir=self.pals_config['Outputs']['Root'], output_name=output_csv_path)

        # Check if we should create heatmap
        if self.pals_config['Analysis']['LesionHeatMap']:
            # Load lesion masks, sum, then output at BIDSRoot
            heatmap_output_path = join(self.pals_config['Outputs']['Root'], 'pals_mask_heatmap.nii.gz')
            heatmap.create_mask_heatmap(mask_root=self.pals_config['LesionRoot'],
                                        mask_entities=self.pals_config['LesionEntities'],
                                        transform_derivatives_name='pals_output',
                                        output_path=join(heatmap_output_path))
            # Overlay on reference, if any
            if 'Reference' in self.pals_config['HeatMap']:
                overlay_name = join(self.pals_config['Outputs']['Root'], 'pals_mask_heatmap_overlaid.nii.gz')
                ref_image = nb.load(self.pals_config['HeatMap']['Reference'])
                ref_data = ref_image.get_fdata()
                # Normalize
                ref_data = (ref_data - np.min(ref_data)) / (
                        np.max(ref_data) - np.min(ref_data))  # is this actually normalizing??

                # Load heatmap
                heatmap_image = nb.load(heatmap_output_path)
                heatmap_data = heatmap_image.get_fdata()
                heatmap_data = (heatmap_data - np.min(heatmap_data)) / (np.max(heatmap_data) - np.min(heatmap_data))

                # Combine
                alph = self.pals_config['HeatMap']['Transparency']
                merged = alph * ref_data + (1 - alph) * heatmap_data
                merged_image = nb.Nifti1Image(merged, affine=ref_image.affine)
                nb.save(merged_image, overlay_name)

                #  check the bounds of the lesions
                x_bounds = get_bounds(heatmap_image, "x")
                y_bounds = get_bounds(heatmap_image, "y")
                z_bounds = get_bounds(heatmap_image, "z")

                # ########### PNGS WITH CROPPED RANGES ###############
                # also save as 8 equally distanced PNG files
                png_output_path = join(self.pals_config['Outputs']['Root'], 'heatmap_png')
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

                sag_fig, sag_axs = plt.subplots(nrows=fig_rows, ncols=fig_cols, squeeze=True, figsize=(10, 10))
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
                cbar.set_ticks([0, 1])
                cbar.set_ticklabels(['0', str(num_threads)])
                cbar.ax.yaxis.set_tick_params(color="white")
                cbar.ax.set_yticklabels(['0', str(num_threads)], color="white")
                cbar.ax.tick_params(axis="y", labelsize=tick_font_size)
                cbar.set_label('No. Subjects', color="white", size=tick_font_size)
                plt.savefig(
                    png_output_path + '/pals_mask_overlaid_sagittal.png')
                plt.clf()

                # #### CORONAL SLICES ###
                cor_fig, cor_axs = plt.subplots(nrows=3, ncols=3, squeeze=True, figsize=(10, 10))
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
                cbar.set_ticks([0, 1])
                cbar.set_ticklabels(['0', str(num_threads)])
                cbar.ax.yaxis.set_tick_params(color="white")
                cbar.ax.set_yticklabels(['0', str(num_threads)], color="white")
                cbar.ax.tick_params(axis="y", labelsize=tick_font_size)
                cbar.set_label('No. Subjects', color="white", size=tick_font_size)
                plt.savefig(
                    png_output_path + '/pals_mask_overlaid_coronal_slice.png')
                plt.clf()

                # #### AXIAL SLICES ###
                axial_fig, axial_axs = plt.subplots(nrows=3, ncols=3, squeeze=True, figsize=(10, 10))
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
                cbar.set_ticks([0, 1])
                cbar.set_ticklabels(['0', str(num_threads)])
                cbar.ax.yaxis.set_tick_params(color="white")
                cbar.ax.set_yticklabels(['0', str(num_threads)], color="white")
                cbar.ax.tick_params(axis="y", labelsize=tick_font_size)
                cbar.set_label('No. Subjects', color="white", size=tick_font_size)
                plt.savefig(
                    png_output_path + '/pals_mask_overlaid_axial_slice.png')
                plt.clf()

                # MAKE FIGURE WITH 3 ORIENTATIONS
                full_fig, full_axs = plt.subplots(nrows=1, ncols=3, squeeze=True, figsize=(7, 2.5),
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
                cbar.set_ticks([0, 1])
                cbar.set_ticklabels(['0', str(num_threads)])
                cbar.ax.set_yticklabels(['0', str(num_threads)], color="white")
                cbar.ax.tick_params(color='white')
                cbar.set_label('No. Subjects', color="white")
                plt.savefig(
                    png_output_path + '/pals_mask_overlaid.png')
                plt.clf()
            self.controller.updateMessage('Lesion heatmaps generated')
        self.controller.updateMessage('Operations complete. You may close the application')
        self.controller.updateProgressBar(100)
        return


    
 