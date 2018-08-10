from nilearn import plotting
from nilearn import image
import nibabel as nb
import matplotlib.pyplot as plt

def generateImage(subject_id,filename_1,filename_2,label):

    img_base = nb.load(filename_1)
    img_overlay = nb.load(filename_2)

    display = plotting.plot_anat(img_base,
                             title=None,
                             dim=-1,
                             display_mode='x',
                             cut_coords=7)

    display.add_edges(img_overlay)
    display.savefig('%s_%s.png'%sub_id,label)
