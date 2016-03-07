import json
import numpy as np
import pylab
import sys
import matplotlib.pyplot as plt
import glob
import re
import datetime
from matplotlib.backends.backend_pdf import PdfPages

client = "aguila1.lsi.upc.edu"
client_location = "Universitat Politecnica de Catalunya"

datafolder = "../superbowl_data/log/"

pingSuffix = "_BBB.json"
plt_styles = ['k-', 'b-.', 'r:', 'm--', 'y-s', 'k-h', 'g-^', 'b-o', 'r-*', 'm-d']

## Get all PING traces from client
ping_files = glob.glob(datafolder + client + "/" + client + "_" + "[0-9]+" + pingSuffix)