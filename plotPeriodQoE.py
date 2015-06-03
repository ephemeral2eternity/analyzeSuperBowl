## Plot std and mean of all rtts from all planetlab to all us servers in CDF
# plotPeriod.py
import json
import numpy as np
import pylab
import sys
import matplotlib.pyplot as plt
import glob
import re
import datetime
import os
from matplotlib.backends.backend_pdf import PdfPages

## Get the statistics from a client trace file
def get_mn(data):
        mn = sum(data) / float(len(data))
        return mn

def get_std(data):
        mn = get_mn(data)
        ss = sum((x - mn)**2 for x in data)
        pvar = ss / float(len(data))
        std = pvar**0.5
        return std

def get_session_qoe(dash_file):
	qoes = []
	cur_qoe = json.load(open(dash_file))
	for chunk_id in sorted(cur_qoe.keys()):
		cur_chunk = cur_qoe[chunk_id]
		qoes.append(cur_chunk["QoE"])
	session_qoe = get_mn(qoes)

	return session_qoe

def read_period_mn_qoes(datafolder, suffix, period):
	## Get all DASH chunk traces from client
	qoe_files = glob.glob(datafolder + "*/*_" + ('[0-9]' * 10) + suffix)
	# print "Files: ", qoe_files

	## Get the average mean RTTs within superbowl period and outside superbowl period
	qoes = []

	## Iterate through all ping_files and read PINGs into dictionaries
	for pFile in qoe_files:
		pPathName, pFileName = os.path.split(pFile)
		client = pPathName.split("/")[2]
		# print "Current File is for client, ", client
		ts = int(re.search(client + "_(.*?)" + suffix, pFileName).group(1))
		print "Current File is for Client, ", client, "Its Timestamp is, ", str(ts)

		## Load each client's rtt to each server

		if ts >= period[0] and ts < period[1]:
			try:
				cur_session_qoe = get_session_qoe(pFile)
				print "Current session is for client ", client, " at Timestamp, ", str(ts), " with Session QoE, ", str(cur_session_qoe)
				qoes.append(cur_session_qoe)
			except:
				continue

	return qoes

def draw_cdf(data, ls, lg):
        sorted_data = np.sort(data)
        yvals = np.arange(len(sorted_data))/float(len(sorted_data))
        plt.plot(sorted_data, yvals, ls, label=lg, linewidth=2.0)
        # plt.show()

before_period = [1422822600, 1422833400]
superbowl_period = [1422833400, 1422843600]
after_period = [1422843600, 1422854400]

datafolder = "./data/"
Suffix = "_BBB.json"
plt_styles = ['k-', 'b-.', 'r:', 'm--', 'y-s', 'k-h', 'g-^', 'b-o', 'r-*', 'm-d']

before_qoes = read_period_mn_qoes(datafolder, Suffix, before_period)
sb_qoes = read_period_mn_qoes(datafolder, Suffix, superbowl_period)
after_qoes = read_period_mn_qoes(datafolder, Suffix, after_period)

## Draw the CDF of all users' QoE during superbowl period
f, ax = plt.subplots()
draw_cdf(before_qoes, plt_styles[2], "Before Super Bowl")
draw_cdf(sb_qoes, plt_styles[0], "Super Bowl")
draw_cdf(after_qoes, plt_styles[1], "After Super Bowl")

ax.set_title("CDF of user QoE for  at DASH streaming from the closest Google Datacenter", fontsize=15)
plt.xlabel("User Session QoE (0 - 5)")
plt.ylabel("The percentage of users.")
plt.legend(bbox_to_anchor=(0.45, 0.9))
pylab.xlim([3, 5])
plt.show()

## Save the plot
pdf = PdfPages('./imgs/qoe/dash_period_qoe_cdf.pdf')
pdf.savefig(f)
pdf.close()








