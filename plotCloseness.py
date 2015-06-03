## Plot the closeness of datacenters to PlanetLab users 
# plotCloseness.py
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

def get_all_pings(datafolder, pingSuffix, period):
	## Get all PING traces from all client
	ping_files = glob.glob(datafolder + "*/*" + pingSuffix)

	## Get the average mean RTTs within superbowl period and outside superbowl period
	rtts = {}

	## Iterate through all ping_files and read PINGs into dictionaries
	for pFile in ping_files:
		pPathName, pFileName = os.path.split(pFile)
		client = pPathName.split("/")[2]
		# print "Current File is for client, ", client
		ts = int(re.search(client + "_(.*?)" + pingSuffix, pFileName).group(1))
		# print "Current File is for Client, ", client, "Its Timestamp is, ", str(ts)

		## Load each client's rtt to each server
		try:
			cur_rtt = json.load(open(pFile))

			if ts >= period[0] and ts < period[1]:
				for srv in cur_rtt.keys():
					if client not in rtts.keys():
						rtts[client] = {}
					# Initialize 
					if srv not in rtts[client].keys():
						rtts[client][srv] = []

					rtts[client][srv].append(float(cur_rtt[srv]))
					# print "Current RTTs: ", str(cur_rtt[srv])
		except:
			continue
	return rtts

def get_mn_pings(rtts):
	## Get the average rtts per a client to all servers
	mn_rtts = {}
	for client in rtts.keys():
		if client not in mn_rtts.keys():
			mn_rtts[client] = {}
		for srv in rtts[client].keys():
			cur_mn_rtts = get_mn(rtts[client][srv])
			mn_rtts[client][srv] = cur_mn_rtts

	return mn_rtts

def get_min_rtts(rtts, provider):
	## Find the minimum rtts for a client to all datacenters in a specified provider.
	min_rtts = {}
	for client in rtts.keys():
		provider_rtts = []
		for srv in rtts[client].keys():
			if provider in srv:
				provider_rtts.append(rtts[client][srv])
		min_rtts[client] = min(provider_rtts)

	return min_rtts

def draw_cdf(data, ls, lg):
        sorted_data = np.sort(data)
        yvals = np.arange(len(sorted_data))/float(len(sorted_data))
        plt.plot(sorted_data, yvals, ls, label=lg, linewidth=2.0)
        # plt.show()

period = [1422850800, 1422854400]

datafolder = "./ping/"
pingSuffix = "_PING.json"
plt_styles = ['k-', 'b-.', 'r:', 'm--', 'y-s', 'k-h', 'g-^', 'b-o', 'r-*', 'm-d']

client_rtts = get_all_pings(datafolder, pingSuffix, period)
client_mn_rtts = get_mn_pings(client_rtts)

gc_min_rtts = get_min_rtts(client_mn_rtts, "gc")
az_min_rtts = get_min_rtts(client_mn_rtts, "az")
aws_min_rtts = get_min_rtts(client_mn_rtts, "aws")

## Draw the CDF of minimum RTTS in all providers
f, ax = plt.subplots()
draw_cdf(gc_min_rtts.values(), plt_styles[0], "Google")
draw_cdf(az_min_rtts.values(), plt_styles[1], "Azure")
draw_cdf(aws_min_rtts.values(), plt_styles[2], "AWS")

plt.xlabel("The CDF of Mean RTTs from all planetlab to the closest datacenter in various Cloud Providers (ms)")
plt.ylabel("The percentage of Planetlab node!")
ax.set_title("The RTTs to the closest datacenter", fontsize=15)
plt.legend(bbox_to_anchor=(1.0, 0.3))
pylab.xlim([0, 200])
plt.show()

## Save the plot
pdf = PdfPages('./imgs/ping/closest_cdf.pdf')
pdf.savefig(f)
pdf.close()

