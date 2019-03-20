import nipype
from os.path import join as opj
from nipype.interfaces.io import SelectFiles, DataSink
from nipype import IdentityInterface
from nipype import Node, Workflow
from nipype.interfaces.fsl import BET

def runNipypeBet(controller, subject_list, anatomical_id, proj_directory):

    infosource = Node(IdentityInterface(fields=['subject_id']),
                  name="infosource")
    infosource.iterables = [('subject_id', subject_list)]

    #anat_file = opj('{subject_id}','{subject_id}_{anatomical_id}.nii')
    seperator=''
    concat_words=('{subject_id}_', anatomical_id ,'.nii.gz')
    anat_file_name=seperator.join(concat_words)

    if controller.b_radiological_convention.get() == True:
      anat_file = opj('{subject_id}', anat_file_name)
    else:
      anat_file = opj('{subject_id}', 'Intermediate_Files', 'Original_Files',anat_file_name)

    templates = {'anat': anat_file}

    selectfiles = Node(SelectFiles(templates,
                               base_directory=proj_directory),
                   name="selectfiles")

    skullstrip = Node(BET(robust=True,
                          frac=0.5,
                          vertical_gradient=0,
                          output_type='NIFTI_GZ'),
                      name="skullstrip")

    # Datasink - creates output folder for important outputs
    datasink = Node(DataSink(base_directory=proj_directory),
                    name="datasink")

    wf_sub = Workflow(name="wf_sub")
    wf_sub.base_dir=proj_directory
    wf_sub.connect(infosource, "subject_id", selectfiles, "subject_id")
    wf_sub.connect(selectfiles, "anat", skullstrip, "in_file")
    wf_sub.connect(skullstrip,"out_file", datasink, "bet.@out_file")


    substitutions = [('%s_brain'%(anatomical_id), 'brain')]
    # Feed the substitution strings to the DataSink node
    datasink.inputs.substitutions = substitutions
    # Run the workflow again with the substitutions in place
    wf_sub.run(plugin='MultiProc')

    return 'brain'
