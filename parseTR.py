import json
import numpy as np
import pylab
import sys
import matplotlib.pyplot as plt
import glob
import re
import datetime
from matplotlib.backends.backend_pdf import PdfPages

def plot_chunk_QoEs(QoEs, client, client_location, plt_styles, reg_name):


client = "75-130-96-12.static.oxfr.ma.charter.com"
client_location = "Worcester Polytechnic Institute, Massachusetts, US"

datafolder = "./data/"

pingSuffix = "_BBB.json"
plt_styles = ['k-', 'b-.', 'r:', 'm--', 'y-s', 'k-h', 'g-^', 'b-o', 'r-*', 'm-d']

## Get all PING traces from client
ping_files = glob.glob(datafolder + client + "/" + client + "_" + "[0-9]+" + pingSuffix)