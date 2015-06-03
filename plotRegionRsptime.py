## Draw response time per server during a period
# plotRegionRsptime.py
import json
import numpy as np
import pylab
import sys
import matplotlib.pyplot as plt
import glob
import re
import datetime
import operator
import math
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


def read_srv_resptime(datafolder, file_suffix, period):
	## Get all DASH chunk traces from client
	dash_files = glob.glob(datafolder + "*/*" + file_suffix)

	### Initialize resp_times
	resp_times = {}

	### Read all chunk QoE files
	for cfile in dash_files:
		# print cfile
		pPathName, pFileName = os.path.split(cfile)
		client = pPathName.split("/")[2]
		# print "Current File is for client, ", client
		try:
			ts = int(re.search('[0-9]{10}', pFileName).group())
			if ts >= period[0] and ts < period[1]:
				# print "Loading file: ", cfile
				cur_video = json.load(open(cfile))

				for chunk_id in sorted(cur_video.keys()):
					cur_chunk_info = cur_video[chunk_id]
					chunk_srv = cur_chunk_info["Server"]
					if chunk_srv not in resp_times.keys():
						resp_times[chunk_srv] = {}

					if "Response" in cur_chunk_info.keys():
						chunk_resp_time = math.fabs(float(cur_chunk_info["Response"]))
					else:
						chunk_resp_time = math.fabs(float(cur_chunk_info["Reponse"]))

					if client not in resp_times[chunk_srv].keys():
						resp_times[chunk_srv][client] = []
					resp_times[chunk_srv][client].append(chunk_resp_time)
		except:
			continue

	return resp_times

def get_mn_resptime(resp_times):
	mn_resptime = {}
	for srv in resp_times.keys():
		if srv not in mn_resptime.keys():
			mn_resptime[srv] = []
		for client in resp_times[srv].keys():
			cur_mn_rsptime = get_mn(resp_times[srv][client])
			mn_resptime[srv].append(cur_mn_rsptime)
			print "Mean Response Time for client", client, " to server ", srv, " is ", str(cur_mn_rsptime)
	return mn_resptime

def get_std_resptime(resp_times):
	std_resptime = {}
	for srv in resp_times.keys():
		if srv not in std_resptime.keys():
			std_resptime[srv] = []
		for client in resp_times[srv].keys():
			std_resptime[srv].append(get_std(resp_times[srv][client]))
	return std_resptime


def draw_cdf(data, ls, lg):
        sorted_data = np.sort(data)
        yvals = np.arange(len(sorted_data))/float(len(sorted_data))
        plt.plot(sorted_data, yvals, ls, label=lg, linewidth=2.0)
        # plt.show()

datafolder = "./data/"
file_suffix = "QAS_BBB.json"
plt_styles = ['k-', 'b-.', 'r:', 'm--', 'y-s', 'k-h', 'g-^', 'b-o', 'r-*', 'm-d']

## Draw period chunk response time for Google Datacenters in US
before_period = [1422822600, 1422833400]
superbowl_period = [1422833400, 1422843600]
after_period = [1422843600, 1422854400]

before_rsptimes = read_srv_resptime(datafolder, file_suffix, before_period)
mn_before_rsptime = get_mn_resptime(before_rsptimes)
std_before_rsptime = get_std_resptime(before_rsptimes)

sb_rsptimes = read_srv_resptime(datafolder, file_suffix, superbowl_period)
mn_sb_rsptime = get_mn_resptime(sb_rsptimes)
std_sb_rsptime = get_std_resptime(sb_rsptimes)

after_rsptimes = read_srv_resptime(datafolder, file_suffix, after_period)
mn_after_rsptime = get_mn_resptime(after_rsptimes)
std_after_rsptime = get_std_resptime(after_rsptimes)

us_srv_to_plot = { 
				"cache-11" : "Council Bluffs, Iowa, Google", 
				"cache-13" : "Mayes county, Okalahoma, Google",
			}

for srv in us_srv_to_plot.keys():
	f, ax = plt.subplots()
	draw_cdf(mn_before_rsptime[srv], plt_styles[2], "Before Super Bowl")
	draw_cdf(mn_sb_rsptime[srv], plt_styles[0], "Super Bowl")
	draw_cdf(mn_after_rsptime[srv], plt_styles[1], "After Super Bowl")
	plt.xlabel("Mean Chunk Response Time From One Client (Second)")
	plt.ylabel("The percentage of planetlab users connecting to the Server")
	plt.legend(bbox_to_anchor=(0.8, 0.25))
	pylab.xlim([0, 10])
	ax.set_title("Study for server in Google Datacenter at " + us_srv_to_plot[srv], fontsize=15)

	plt.show()

	## Save the plot
	pdf = PdfPages('./imgs/resptime/' + srv + '_mn_rsptime_cdf.pdf')
	pdf.savefig(f)
	pdf.close()

	f, ax = plt.subplots()
	draw_cdf(std_before_rsptime[srv], plt_styles[2], "Before Super Bowl")
	draw_cdf(std_sb_rsptime[srv], plt_styles[0], "Super Bowl")
	draw_cdf(std_after_rsptime[srv], plt_styles[1], "After Super Bowl")
	plt.xlabel("Std of Chunk Response Time From One Client (Second)")
	plt.ylabel("The percentage of planetlab users connecting to the Server")
	plt.legend(bbox_to_anchor=(0.8, 0.25))
	pylab.xlim([0, 10])
	ax.set_title("Study for server in Google Datacenter at " + us_srv_to_plot[srv], fontsize=15)

	plt.show()

	## Save the plot
	pdf = PdfPages('./imgs/resptime/' + srv + '_std_rsptime_cdf.pdf')
	pdf.savefig(f)
	pdf.close()

regions = {
		"us" : ["cache-11", "cache-13"],
		"eu" : ["cache-07", "cache-09"],
		"asia" : ["cache-01", "cache-03"],
}

reg_id = 0
f, ax = plt.subplots()
for reg in regions.keys():
	cur_reg_rsptime = []
	for srv in regions[reg]:
		cur_reg_rsptime = sum([cur_reg_rsptime, mn_after_rsptime[srv]], [])
	draw_cdf(cur_reg_rsptime, plt_styles[reg_id], reg)
	reg_id = reg_id + 1

plt.xlabel("Server Response Time (Second)")
plt.ylabel("The percentage of planetlab users in the same region")
plt.legend(bbox_to_anchor=(0.9, 0.25))
pylab.xlim([0, 10])
ax.set_title("Response time for servers in various Regions of Google Datacenters", fontsize=15)

plt.show()

## Save the plot
pdf = PdfPages('./imgs/resptime/region_rsptime_cdf.pdf')
pdf.savefig(f)
pdf.close()

