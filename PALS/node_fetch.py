from nipype.interfaces import fsl
from nipype.pipeline import Node, MapNode
from nipype.interfaces import Function


def infile_to_outfile(**kwargs):
    print(f"returning {kwargs['in_file']}")
    return kwargs['in_file']


def extraction_node(config: dict, **kwargs):
    '''
    Parses config file to return desired brain extraction method.
    Parameters
    ----------
    config : dict
        PALS config file
    kwargs
        Keyword arguments to send to brain extraction method.

    Returns
    -------
    MapNode
    '''
    # Get extraction type
    extract_type = config['Analysis']['BrainExtractionMethod']
    if(not config['Analysis']['BrainExtraction']):
        # No brain extraction; in-> out
        n = MapNode(Function(function=infile_to_outfile, input_names='in_file', output_names='out_file'),
                    name='extract_skip', iterfield='in_file')
        return n
    elif(extract_type.lower() == 'bet'):
        n = MapNode(fsl.BET(**kwargs), name='extraction_bet', iterfield='in_file')
        return n
    else:
        raise(NotImplementedError(f'Extraction method {extract_type} not implemented.'))


def registration_node(config: dict, **kwargs):
    '''
    Parses config file to return desired registration method.
    Parameters
    ----------
    config : dict
        PALS config file
    kwargs
        Keyword arguments to send to registration method.

    Returns
    -------
    MapNode
    '''
    # Get registration method
    reg_method = config['Analysis']['RegistrationMethod']
    if(not config['Analysis']['Registration']):
        # No registration; in -> out
        n = MapNode(Function(function=reg_no_reg,
                             input_names=['in_file'],
                             output_names=['out_file', 'out_matrix_file']),
                    name='registration_identity', iterfield='in_file')
    elif(reg_method.lower() == 'flirt'):
        # Use FLIRT
        n = MapNode(fsl.FLIRT(), name='registration_flirt', iterfield='in_file')
        for k, v in kwargs.items():
            setattr(n.inputs, k, v)
    else:
        raise(NotImplementedError(f'Registration method {reg_method} not implemented.'))
    return n


def apply_xfm_node(config: dict, **kwargs):
    '''
    Parses config file to return desired apply_xfm node.
    Parameters
    ----------
    config : dict
        PALS config file
    kwargs
        Keyword arguments to send to registration method.

    Returns
    -------
    MapNode
    '''

    if(not config['Analysis']['Registration']):
        # No registration; no xfm to apply.
        n = MapNode(Function(function=infile_to_outfile,
                             input_names=['in_file', 'in_matrix_file'],
                             output_names='out_file'),
                    name='transformation_skip', iterfield=['in_file', 'in_matrix_file'])
    else:
        n = MapNode(fsl.FLIRT(apply_xfm=True, reference=config['Registration']['reference']),
                    name='transformation_flirt', iterfield=['in_file', 'in_matrix_file'])
    return n


def reg_no_reg(in_file):
    '''
    Returns the input file and an identity transform.
    Parameters
    ----------
    in_file
        Input file, as with fsl.FLIRT()
    reference
        Ignored; present for compatibility.
    Returns
    -------
    tuple
        Returns input file + path to identity transform
    '''
    import numpy as np
    import tempfile
    ident_transf = np.eye(4)
    ident_transf[-1,-1] = 0
    ident_path = tempfile.mktemp()
    np.savetxt(ident_path, ident_transf, fmt='%.1f')
    return in_file, ident_path