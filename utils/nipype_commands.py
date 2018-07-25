import os
from os.path import abspath
from nipype import Workflow, Node, MapNode, Function
from nipype.interfaces.fsl import BET, ApplyMask, BinaryMaths,
