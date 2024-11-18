import os
import glob
import json
import argparse
import numpy as np
import nibabel as nib
import time
from datetime import datetime
from subprocess import call
from nibabel import processing
from qc_tools import generate_mask_qc, compare_two_ims

def PALS_version():
    return '2.0.1'

# utilities
def generate_directory(path):
    os.makedirs(path,exist_ok=True)
    return path

def binarize_im(image_path):
    mask_path = image_path.replace('.nii.gz', '_mask.nii.gz')

    img = nib.load(image_path)
    data = img.get_fdata()

    binary_data = np.where(data > 0, 1, 0)

    nib.save(nib.Nifti1Image(binary_data, img.affine, img.header), 
             mask_path)

    return mask_path

def save_outputs(dct, out_file, method='json'):
    if not os.path.exists(os.path.dirname(out_file)):
        os.makedirs(os.path.dirname(out_file))
    
    if method == 'json':
        with open(out_file+'.json','w') as f:
            json.dump(dct,f,indent=4)
        return out_file+'.json'
    else:
        with open(out_file+'.csv','w') as f:
            f.write(',' + ','.join([key for key in dct]) + '\n')
            f.write('0,' + ','.join([str(dct[key]) for key in dct]) + '\n')
        return out_file+'.csv'

def open_json(file_path, required_keys=[]):
    """
    Opens json file and returns the contents if an error is not found. 

    Inputs:
        file_path : str, file path pointing to json file of which to read contents

    Returns:
        data : dict, json contents
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            if required_keys:
                missing_keys = [key for key in required_keys if key not in data]
                if missing_keys:
                    raise ValueError(f"Error: Missing required keys in JSON file: {', '.join(missing_keys)}")
        return data
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: File '{file_path}' not found.")
    
    except json.JSONDecodeError:
        raise json.JSONDecodeError(f"Error: Unable to decode JSON from file '{file_path}'. Check if the file contains valid JSON.")

# define Workflow, a class that includes initializing PALS, setting outputs, and executing functions
class Workflow:
    def __init__(self, config_info):
        self.session_id = config_info['session_id']
        self.im_path = config_info['im_path']
        self.les_path = config_info['les_path']
        self.out_dir = self.check_valid_path(config_info['out_dir'])
        self.out_directory = generate_directory(os.path.join(self.out_dir, 'PALS', self.session_id))
        for subfolder in ['config','log','qc','results','proc']:
            generate_directory(os.path.join(self.out_directory, subfolder))

        self.log_file = os.path.join(self.out_directory, 'log', datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.txt')
        self.add_to_log('Initializing PALS workflow using config info')

        self.run = config_info['run']
        if config_info['run'] not in ['all','bet','mnireg','coreg','pals','skipdone']:
            generate_error(IOError, f'Invalid input provided for run flag, please try again using a valid flag [all,bet,halfreg,mnireg,coreg,skipdone]')
        elif config_info['run'] == 'all':
            self.script = [True, True, True, True, True, True]
        elif config_info['run'] == 'bet':
            self.script = [False, True, True, True, True, True]
        elif config_info['run'] == 'mnireg':
            self.script = [False, False, False, True, True, True]
        elif config_info['run'] == 'coreg':
            self.script = [False, False, False, False, True, True]
        elif config_info['run'] == 'pals':
            self.script = [False, False, False, False, False, True]
        else:
            self.script = [False, False, False, False, False, False]

        self.PALS_version = PALS_version()
        self.ants_path = config_info['ants_path']
        self.fsl_path = config_info['fsl_path']
        self.rois_path = self.check_valid_path(config_info['rois_path'])
        
        self.reg_method = config_info['reg_method']
        if self.reg_method not in ['fsl']:
            generate_error(IOError, f'{self.reg_method} is not in acceptable registration pipelines, please ensure it is "fsl" and try again.')
        self.reg_costfn = config_info['reg_costfn']
        self.reg_partmask = config_info['reg_partmask']
        self.reg_nomask = config_info['reg_nomask']
        self.bet_g = str(config_info['bet_g'])
        self.space = config_info['space']
        if self.space not in ['orig','mni']:
            generate_error(IOError, f'{self.space} is not in acceptable options, please ensure it is either "orig" or "mni" and try again.')
        self.out_format = config_info['out_format']
        self.gif_duration = config_info['gif_duration']

        self.template_directory = self.check_valid_path(config_info['template_directory'])
        self.mni_path = os.path.join(self.template_directory, 'mni_icbm152_t1_tal_nlin_sym_09a.nii')
        self.mni_mask = os.path.join(self.template_directory, 'mni_icbm152_t1_tal_nlin_sym_09a_brain_mask.nii.gz')
        self.mni_partmask = os.path.join(self.template_directory, 'mni_icbm152_t1_tal_nlin_sym_09a_brain_partweight_mask.nii.gz')

        self.im_std = ''
        self.les_std = ''
        self.n4_path = ''
        self.im_brain_path = ''
        self.im_skull_path = ''
        self.im_mni = ''
        self.les_mni = ''
        self.PALS_results = ''

    def check_valid_path(self, path):
        if not os.path.exists(path):
            generate_error(IOError, f'{path} was not found')
        else:
            return path

    def add_to_log(self, message):
        with open(self.log_file,'a') as f:
            time = datetime.now().strftime("%Y-%m-%d %H:%M.%S")
            f.write(f'[{time}] {message}\n')
            print(f'[{time}] {message}')

    def generate_error(self, error, message):
        add_to_log('ERROR: {error} {message}')
        exception_class = globals().get(error)    
        raise exception_class(message)
    
    def initialize(self):
        if not os.path.exists(self.im_path):
            generate_error(FileNotFoundError, f'Could not find T1 image for {self.session_id}, please ensure this path is correct')
        if not os.path.exists(self.les_path):
            generate_error(FileNotFoundError, f'Could not find lesion mask for {self.session_id}, please ensure this path is correct')

        if self.space == 'mni':
            self.im_mni = self.im_path
            self.les_mni = self.les_path

    def get_processing_directory(self, processing_folder):
        processing_order = ['fsl_reorient2std','ants_N4BiasFieldCorrection','fsl_bet','mni_registration']

        if processing_folder not in processing_order:
            generate_error(IOError, f'{processing_folder} not in acceptable folder options')

        step = processing_order.index(processing_folder) + 1
        
        folder = generate_directory(f'{self.out_directory}/proc/{step}_{processing_folder}')
        
        if processing_folder in ['mni_registration']:
            generate_directory(f'{folder}/input')
            generate_directory(f'{folder}/output')

        return folder

    def run_reorient2std(self):
        std_outdir = self.get_processing_directory('fsl_reorient2std')
    
        self.im_std = f'{std_outdir}/{self.session_id}_space-orig_desc-std_T1w.nii.gz'
        self.les_std = f'{std_outdir}/{self.session_id}_space-orig_desc-stdT1lesion_mask.nii.gz'
        
        if not os.path.exists(self.im_std) or self.script[0]:
            self.add_to_log(f'Starting reorient2std for {self.session_id}')
            if os.path.exists(self.im_std):
                self.add_to_log(f'WARNING: Found existing file, overwriting')
            cmd = [f'{self.fsl_path}/fslreorient2std',self.im_path,self.im_std]
            self.add_to_log('COMMAND: '+' '.join(cmd))
            call(cmd)
            cmd = [f'{self.fsl_path}/fslreorient2std',self.les_path,self.les_std]
            self.add_to_log('COMMAND: '+' '.join(cmd))
            call(cmd)
            cmd = [f'{self.fsl_path}/fslcpgeom',self.im_std,self.les_std]
            self.add_to_log('COMMAND: '+' '.join(cmd))
            call(cmd)
            self.add_to_log(f'Reorient to standard completed for {self.session_id}')

        else:
            self.add_to_log(f'Reorient to standard skipped for {self.session_id}')


    def run_n4(self):
        n4_outdir = self.get_processing_directory('ants_N4BiasFieldCorrection')
    
        self.n4_path = f'{n4_outdir}/{self.session_id}_space-orig_desc-N4_T1w.nii.gz'
        
        if not os.path.exists(self.n4_path) or self.script[0]:
            self.add_to_log(f'Starting N4BiasFieldCorrection for {self.session_id}')
            if os.path.exists(self.n4_path):
                self.add_to_log(f'WARNING: Found existing file, overwriting')
            cmd = [f'{self.ants_path}/N4BiasFieldCorrection','-i',self.im_std,'-o',self.n4_path]
            self.add_to_log('COMMAND: '+' '.join(cmd))
            call(cmd)
            self.add_to_log(f'N4BiasFieldCorrection completed for {self.session_id}')

        else:
            self.add_to_log(f'N4BiasFieldCorrection skipped for {self.session_id}')

    def run_bet(self):
        bet_outdir = self.get_processing_directory('fsl_bet')

        bet_output = f'{bet_outdir}/{self.session_id}_space-orig_desc-N4T1ext'
        self.im_brain_path = f'{bet_output}.nii.gz'
        self.im_skull_path = f'{bet_output}_skull.nii.gz'

        if not os.path.exists(self.im_brain_path) or self.script[1]:
            self.add_to_log(f'Starting BET for {self.session_id}')
            if os.path.exists(self.im_brain_path):
                self.add_to_log(f'WARNING: Found existing file, overwriting')
            cmd = [f'{self.fsl_path}/bet', self.n4_path, bet_output, '-s', '-g', self.bet_g, '-R']
            self.add_to_log('COMMAND: '+' '.join(cmd))
            call(cmd)
            self.add_to_log(f'BET completed for {self.session_id}')

        else:
            self.add_to_log(f'BET skipped for {self.session_id}')

    def register_to_mni(self):
        mni_outdir = self.get_processing_directory('mni_registration')

        self.im_brain_mask = binarize_im(self.im_brain_path)
        self.im_to_mni_xfm = f'{mni_outdir}/output/{self.session_id}_orig_to_MNI152NLin2009aSym.mat'
        self.im_mni = f'{mni_outdir}/output/{self.session_id}_space-MNI152NLin2009aSym_desc-N4_T1w.nii.gz'

        if not os.path.exists(self.im_to_mni_xfm) or self.script[3]:
            self.add_to_log(f'Starting registration to MNI for {self.session_id}')
            if os.path.exists(self.im_to_mni_xfm):
                self.add_to_log(f'WARNING: Found existing file, overwriting')
            flirt_cmd = [f'{self.fsl_path}/flirt','-in',self.n4_path,'-ref',self.mni_path]
            
            if self.reg_partmask:
                im_brain_partmask = f'{mni_outdir}/input/{self.session_id}_space-orig_desc-extT1partweight_mask.nii.gz'
                
                self.add_to_log(f'Generating partial weighted mask for {self.session_id}')
                cmd = [f'{self.fsl_path}/fslmaths', self.im_brain_mask, '-mul','3','-add','1','-div','4', im_brain_partmask]
                self.add_to_log('COMMAND: '+' '.join(cmd))
                call(cmd)
                self.add_to_log(f'Partial weighted mask generated for {self.session_id}')
                
                flirt_cmd += ['-inweight',im_brain_partmask, '-refweight',self.mni_partmask]
                self.add_to_log(f'Running registration using weighted mask for {self.session_id}')
            elif self.reg_nomask:
                self.add_to_log(f'Running registration using full image for {self.session_id}')
                pass
            
            else:
                flirt_cmd += ['-inweight',self.im_brain_mask, '-refweight',self.mni_mask]
                self.add_to_log(f'Running registration using brain only for {self.session_id}')

            flirt_cmd += ['-cost',self.reg_costfn,'-out',self.im_mni,'-omat',self.im_to_mni_xfm]
            self.add_to_log('COMMAND: '+' '.join(flirt_cmd))
            call(flirt_cmd)
            self.add_to_log(f'Registration from orig to MNI completed for {self.session_id}')
        else:
            self.add_to_log(f'Registration from orig to MNI skipped for {self.session_id}')

    def coregister_to_mni(self):
        mni_outdir = self.get_processing_directory('mni_registration')
        
        self.les_mni = f'{mni_outdir}/output/{self.session_id}_space-MNI152NLin2009aSym_desc-N4T1lesion_mask.nii.gz'
        
        if not os.path.exists(self.les_mni) or self.script[4]:
            self.add_to_log(f'Starting lesion co-registration to MNI for {self.session_id}')
            if os.path.exists(self.les_mni):
                self.add_to_log(f'WARNING: Found existing file, overwriting')
            cmd = [f'{self.fsl_path}/flirt','-in',self.les_std,'-ref',self.mni_path,'-applyxfm','-init',self.im_to_mni_xfm,'-interp','nearestneighbour','-out',self.les_mni]
            self.add_to_log('COMMAND: '+' '.join(cmd))
            call(cmd)
            self.add_to_log(f'Lesion co-registration to MNI completed for {self.session_id}')
        else:
            self.add_to_log(f'Lesion co-registration to MNI skipped for {self.session_id}')

    def generate_qc(self):
        self.add_to_log(f'Generating QC images for {self.session_id}')
        generate_mask_qc(out_dir=os.path.join(self.out_directory,'qc'),
                         im_path = self.im_std,
                         mask_path = self.im_brain_mask,
                         basename = f'{self.session_id}_bet-results_',
                         caption = f'{self.session_id}',
                         cmap='Greens', alpha=0.4, binarize=True)
        generate_mask_qc(out_dir=os.path.join(self.out_directory,'qc'),
                         im_path = self.im_mni,
                         mask_path = self.les_mni,
                         basename = f'{self.session_id}_lesion-coreg_',
                         caption = f'{self.session_id}')
        compare_two_ims(out_dir=os.path.join(self.out_directory,'qc'),
                        im1_path = self.im_mni,
                        im2_path = self.mni_path,
                        basename = 'reg-qual_',
                        name_im1=f'{self.session_id}',
                        name_im2=f'mni_template',
                        gif_duration=self.gif_duration)
        self.add_to_log(f'QC images generated for {self.session_id}')

    def run_lesion_overlap(self):
        self.PALS_results = os.path.join(self.out_directory, 'results', self.session_id + '_desc-lesionload_results')
    
        if not os.path.exists(f'{self.PALS_results}.{self.out_format}') or self.script[5]:
            self.add_to_log(f'Starting lesion overlap analysis for {self.session_id}')
            if os.path.exists(f'{self.PALS_results}.{self.out_format}'):
                self.add_to_log(f'WARNING: Found existing results file, overwriting')
            
            results = PALSResults()

            results.add_to_dict('SESSION_ID',self.session_id)
            results.add_to_dict('DATE_GENERATED', datetime.now().strftime('%Y-%m-%d %H:%M'))

            results.write_volume(self.les_mni, label='LesionVolume')
            results.find_overlap(self.les_mni, rois_path=self.rois_path)

            lesion_outputs = save_outputs(results.compile_attributes(),
                                          self.PALS_results,
                                          method=self.out_format)

            self.add_to_log(f'Completed lesion overlap for {self.session_id}')
        else:
            self.add_to_log(f'Skipped lesion overlap for {self.session_id}')

    def run_PALS(self):
        self.add_to_log('Starting PALS workflow')
        start_time = time.time()

        self.initialize()
        if self.space == 'orig':
            self.run_reorient2std()
            self.run_n4()
            self.run_bet()
            self.register_to_mni()
            self.coregister_to_mni()
            self.generate_qc()
        self.run_lesion_overlap()

        config_output = save_outputs(self.compile_attributes(),
                                     os.path.join(self.out_directory, 'config', self.session_id + '_date-' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '_desc-PALS_config'),
                                     method='json')

        end_time = time.time()
        elapsed_time = end_time - start_time
        elapsed_min = int(elapsed_time // 60)
        elapsed_sec = elapsed_time % 60

        self.add_to_log('Successfully completed PALS workflow')
        self.add_to_log(f"PALS execution time: {elapsed_min} mins, {elapsed_sec:.3f} secs")

    def compile_attributes(self):
        attr_dict = vars(self)
        attr_dict = {k: v for k, v in attr_dict.items() if not k.startswith('_')}
        return attr_dict

class PALSResults:
    def __init__(self):
        self.results = {}
        self.results['PALS_version'] = PALS_version()

    def add_to_dict(self, key, value):
        self.results[key] = value

    def write_volume(self, mask, label):
        mask_data = nib.load(mask).get_fdata()
        self.results[label] = np.sum(mask_data)
        mask_dims = nib.load(mask).header.get_zooms()
        self.results[label+"(mm)"] = np.sum(mask_data) * mask_dims[0] * mask_dims[1] * mask_dims[2]

    def find_overlap(self, lesion, rois_path='/ifs/loni/faculty/sliew/enigma/new/Mahir/PALS_ROIs'):
        lesion_nib = nib.load(lesion)

        rois = [roi for roi in sorted(glob.glob(rois_path+'/*.nii*'))]
        rois_nib = [nib.load(roi) for roi in rois]
        rois_label = [roi.split('/')[-1].split('.nii')[0] for roi in rois]

        #load as nib objects
        lesion_data = lesion_nib.get_fdata()
        for roi_nib, label in zip(rois_nib, rois_label):
            print ('running',label)
            roi_data = processing.resample_from_to(roi_nib, lesion_nib, order=1).get_fdata()
            overlap = np.sum((lesion_data * roi_data))
            overlap_pct = np.sum((lesion_data * roi_data))/np.sum(roi_data)*100
            self.results[label] = np.round(overlap,3)
            self.results[label+'_pct'] = np.round(overlap_pct,3)

    def compile_attributes(self):
        return self.results

def default_config(session_id, im_path, les_path, out_dir, run):
    presets = open_json('presets.json')
    config = {
        "session_id" : session_id,
        "im_path" : im_path,
        "les_path" : les_path,
        "out_dir" : out_dir,
        "run" : run,
        "space" : "orig",
        "ants_path" : presets['ants_path'],
        "fsl_path" : presets['fsl_path'],
        "rois_path" : presets['rois_path'],
        "template_directory" : presets['template_directory'],
        "out_format" : "csv",
        "reg_method" : "fsl",
        "reg_costfn" : "corratio",
        "reg_partmask" : False,
        "reg_nomask" : False,
        "bet_g" : -0.25,
        "gif_duration" : 0.5
    }
    return [config]


def cmdline_parser():
    """
    Collects arguments from command line to initialize run.
    
    Outputs:
        configs : list, file paths pointing to config files that initialize PALS run
    """
    parser = argparse.ArgumentParser(description="Run PALS on T1 and lesion mask data. Script accepts direct paths to config.json files, or text file with paths to config files on each line.")

    parser.add_argument('-c','--config', dest='config_paths', nargs='+', default=[], help='List of config files to initialize PALS.')
    parser.add_argument('-f','--file-txt', dest='file_txt', default='none.txt', help='Provide a txt file with each config to run on its own line.')

    parser.add_argument('-i','--image',default='none')
    parser.add_argument('-l','--lesion',default='none')
    parser.add_argument('-o','--outdir',default='none')
    parser.add_argument('-s','--sessionid',default='none')
    parser.add_argument('-r','--run',default='all')

    args = parser.parse_args()

    if args.file_txt != 'none.txt':
        if os.path.exists(args.file_txt):
            with open(args.file_txt, 'r') as f:
                config_paths = [val.replace('\n','') for val in f.readlines()]
                config_status = True
        else:
            raise FileNotFoundError(f'Could not find {args.file_txt}, please make sure file path is correct.')

    elif len(args.config_paths) > 0:
        config_paths = args.config_paths
        config_status = True

    else:
        print('No configs were passed into the script, attempting to look for direct input')
        config_status = False

        direct_inputs_status = [arg=='none' for arg in [args.image, args.lesion, args.outdir, args.sessionid]]
        direct_inputs = ['"-i, --image"', '"-l, --lesion"', '"-o, --outdir"', '"-s, --sessionid"']
        direct_status = True
        for direct_input, direct_input_status in zip(direct_inputs, direct_inputs_status):
            if direct_input_status:
                print (direct_input, 'was not specified')
                direct_status = False

    if config_status:
        error_configs = [config_path for config_path in config_paths if not os.path.exists(config_path)]
        
        if len(error_configs) > 0:
            raise IOError("The following config paths could not be found: " + "; ".join(error_configs))

        configs = []
        for config_path in config_paths:
            config = open_json(config_path, 
                required_keys=['session_id','im_path','les_path','out_dir','run',
                               'space','ants_path','fsl_path','rois_path','template_directory','out_format',
                               'reg_method','reg_costfn','reg_partmask','reg_nomask','bet_g'])
            configs.append(config)
        
        return configs

    elif direct_status:
        print ('Found all required direct inputs, generating config and running PALS')
        return default_config(args.sessionid, args.image, args.lesion, args.outdir, args.run)

    else:
        raise IOError("Input args were not properly specified, please review messages above traceback for details and try again")


def main():
    configs = cmdline_parser()
    for config in configs:
        Workflow(config_info=config).run_PALS()

if __name__ == '__main__':
    main()