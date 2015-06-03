import json
import numpy as np
import pylab
import sys
import matplotlib.pyplot as plt
import glob
import re
import datetime
from matplotlib.backends.backend_pdf import PdfPages

def plot_chunk_QoEs(QoEs, client, client_location, plt_sty, method):
	sorted_ts = sorted(QoEs.keys())
	sorted_qoe = []
	for ts in sorted_ts:
		# print "Timestamp: ", ts, "Chunk QoE: ", QoEs[ts]
		sorted_qoe.append(QoEs[ts])

	plt.plot(sorted_ts, sorted_qoe, plt_sty, label=method, linewidth=2.0, markersize=7.0)


def plot_all_QoEs(all_qoes, client, client_location, plt_styles):
	fig, ax = plt.subplots()
	method_id = 0
	for method in all_qoes.keys():
		cur_qoe = all_qoes[method]
		plot_chunk_QoEs(cur_qoe, client, client_location, plt_styles[method_id], method)
		method_id = method_id + 1

	## Label figure axis
	ts_superbowl = [1422833400, 1422838800, 1422840240, 1422843600]
	str_ts_superbowl = ['Superbowl Starts', 'Halftime Start', 'Halftime Ends', 'Superbowl Ends']
	plt.xticks(ts_superbowl, str_ts_superbowl, fontsize=15)
	# Make space for and rotate the x-axis tick labels
	fig.autofmt_xdate()
	pylab.xlim([1422833000, 1422844000])
	pylab.ylim([0, 5])
	ax.set_title('DASH Chunks\' QoE for client ' + client + ' at ' + client_location, fontsize=15)
	# Shrink current axis by 10%
	box = ax.get_position()
	ax.set_position([box.x0, box.y0 + 0.1, box.width, box.height * 0.9])
	## Set up legends
	ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.25),
	          fancybox=True, shadow=True, ncol=3)
	plt.show()

	## Save the plot
	pdf = PdfPages('./imgs/qoe/' + client + '.pdf')
	pdf.savefig(fig)
	pdf.close()

def readChunkQoE(client, datafolder, suffix):
	## Get all DASH chunk traces from client
	qoe_files = glob.glob(datafolder + client + "/" + client + "_" + ('[0-9]' * 10) + suffix)
	print "Files: ", qoe_files

	### Initialize QoEs
	qoes = {}

	### Read all chunk QoE files
	for qfile in qoe_files:
		print qfile
		cur_qoe = json.load(open(qfile))
		for chunk_id in sorted(cur_qoe.keys()):
			cur_chunk = cur_qoe[chunk_id]
			chunk_ts = int(cur_chunk["TS"])
			qoes[chunk_ts] = cur_chunk["QoE"]

	return qoes

def readAllQoEs(client, datafolder, methods):
	all_qoes = {}
	for key in methods:
		suffix = methods[key]
		curQoE = readChunkQoE(client, datafolder, suffix)
		all_qoes[key] = curQoE
	return all_qoes

client = "75-130-96-12.static.oxfr.ma.charter.com"
client_location = "Worcester Polytechnic Institute, Massachusetts, US"

#client = "planetlab-1.tagus.ist.utl.pt"
#client_location = "Instituto Superior Tecnico, Lisboa, Portugal"

datafolder = "./data/"

methods = {
			"DASH" : "_BBB.json",
			"Intra Zone QAS-DASH" : "_intra_QAS_BBB.json",
			"Inter Zone QAS-DASH" : "_inter_QAS_BBB.json",
			"Intra Zone CQAS-DASH" : "_intra_CQAS_BBB.json",
			"Inter Zone CQAS-DASH" : "_inter_CQAS_BBB.json"
		}

plt_styles = ['bs', 'kd', 'b*', 'r+', 'mo', 'y^', 'k-h', 'g-^', 'b-o', 'r-*', 'm-d']

## Read all streaming files for this client
qoes = readAllQoEs(client, datafolder, methods)

## Plot All QoEs
plot_all_QoEs(qoes, client, client_location, plt_styles)

