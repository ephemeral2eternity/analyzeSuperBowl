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

def read_period_pings(datafolder, pingSuffix, period):
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
					# Initialize 
					if srv not in rtts.keys():
						rtts[srv] = {}

					if client not in rtts[srv].keys():
						rtts[srv][client] = []

					rtts[srv][client].append(float(cur_rtt[srv]))
					# print "Current RTTs: ", str(cur_rtt[srv])
		except:
			continue

	return rtts

def add_period_pings(rtts, datafolder, pingSuffix, period):
	## Get all PING traces from all client
	ping_files = glob.glob(datafolder + "*/*" + pingSuffix)

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
					# Initialize 
					if srv not in rtts.keys():
						rtts[srv] = {}

					if client not in rtts[srv].keys():
						rtts[srv][client] = []

					rtts[srv][client].append(float(cur_rtt[srv]))
					# print "Current RTTs: ", str(cur_rtt[srv])
		except:
			continue

	return rtts

def get_ave_rtts(rtts):
	mn_rtts = {}
	## Compare RTTS for all servers in and out of superbowl period
	for srv in rtts.keys():
		# Initialize 
		if srv not in mn_rtts.keys():
			mn_rtts[srv] = {}
		for client in rtts[srv].keys():
			# print "All RTTs for client ", client, " to server ", srv, " is: ", rtts[srv][client]
			client_mn_rtt = get_mn(rtts[srv][client])
			mn_rtts[srv][client] = client_mn_rtt
	return mn_rtts

def get_std_rtts(rtts):
	std_rtts = {}
	## Compare RTTS for all servers in and out of superbowl period
	for srv in rtts.keys():
		# Initialize 
		if srv not in std_rtts.keys():
			std_rtts[srv] = {}
		for client in rtts[srv].keys():
			# print "All RTTs for client ", client, " to server ", srv, " is: ", rtts[srv][client]
			client_std_rtt = get_std(rtts[srv][client])
			std_rtts[srv][client] = client_std_rtt
	return std_rtts

def draw_cdf(data, ls, lg):
        sorted_data = np.sort(data)
        yvals = np.arange(len(sorted_data))/float(len(sorted_data))
        plt.plot(sorted_data, yvals, ls, label=lg, linewidth=2.0)
        # plt.show()

before_period = [1422822600, 1422833400]
superbowl_period_first = [1422833400, 1422838800]
superbowl_period_second = [1422854400, 1422843600]
halftime_period = [1422838800, 1422840240]
after_period = [1422843600, 1422854400]

datafolder = "./ping/"
pingSuffix = "_PING.json"
plt_styles = ['k-', 'b-.', 'r:', 'm--', 'y-s', 'k-h', 'g-^', 'b-o', 'r-*', 'm-d']

before_rtts = read_period_pings(datafolder, pingSuffix, before_period)
mn_before_rtts = get_ave_rtts(before_rtts)
std_before_rtts = get_std_rtts(before_rtts)

rtts = read_period_pings(datafolder, pingSuffix, superbowl_period_first)
sb_rtts = add_period_pings(rtts, datafolder, pingSuffix, superbowl_period_second)
mn_sb_rtts = get_ave_rtts(sb_rtts)
std_sb_rtts = get_std_rtts(sb_rtts)

half_rtts = read_period_pings(datafolder, pingSuffix, halftime_period)
mn_half_rtts = get_ave_rtts(half_rtts)
std_half_rtts = get_std_rtts(half_rtts)

after_rtts = read_period_pings(datafolder, pingSuffix, after_period)
mn_after_rtts = get_ave_rtts(after_rtts)
std_after_rtts = get_std_rtts(after_rtts)

## Compare two US data centers during and after superbowl period 
us_srv_to_plot = { 
				"gc11" : "Council Bluffs, Iowa, Google", 
				"gc13" : "Mayes county, Okalahoma, Google",
				"az01" : "Virginia, Azure",
				"az02" : "Iowa, Azure", 
				"az04" : "Texas, Azure",
				"az05" : "California, Azure",
				"aws01" : "North Virginia, AWS",
				"aws02" : "Oregon, AWS",
				"aws03" : "California, AWS"
			}

for srv in us_srv_to_plot.keys():
	## Draw the CDF of mean RTTS
	f, ax = plt.subplots()
	if "az" not in srv:
		mn_before_srv = []
		for client in mn_before_rtts[srv].keys():
			# print "The mean Superbowl period rtts for server ", srv, " at client ", client, " is: ", str(mn_sb_rtts[srv][client])
			mn_before_srv.append(mn_before_rtts[srv][client])
		draw_cdf(mn_before_srv, plt_styles[2], "Before Super Bowl")
	mn_half_srv = []
	for client in mn_half_rtts[srv].keys():
		# print "The mean Superbowl period rtts for server ", srv, " at client ", client, " is: ", str(mn_sb_rtts[srv][client])
		mn_half_srv.append(mn_half_rtts[srv][client])
	draw_cdf(mn_half_srv, plt_styles[3], "Half Time")
	mn_sb_srv = []
	for client in mn_sb_rtts[srv].keys():
		# print "The mean Superbowl period rtts for server ", srv, " at client ", client, " is: ", str(mn_sb_rtts[srv][client])
		mn_sb_srv.append(mn_sb_rtts[srv][client])
	draw_cdf(mn_sb_srv, plt_styles[0], "Super Bowl")
	mn_after_srv = []
	for client in mn_after_rtts[srv].keys():
		mn_after_srv.append(mn_after_rtts[srv][client])
	draw_cdf(mn_after_srv, plt_styles[1], "After Super Bowl")
	ax.set_title("Mean RTTs CDF for datacenter at " + us_srv_to_plot[srv], fontsize=15)
	plt.xlabel("Mean(RTTs) from one Planetlab node to a datacenter (ms)")
	plt.ylabel("The percentage of Planetlab node!")
	plt.legend(bbox_to_anchor=(1.0, 0.8))
	pylab.xlim([0, 500])
	plt.show()

	## Save the plot
	pdf = PdfPages('./imgs/ping/' + srv + '_mnrtts_cdf.pdf')
	pdf.savefig(f)
	pdf.close()

	## Draw the CDF of std of RTTs
	f, ax = plt.subplots()
	if "az" not in srv:
		std_before_srv = []
		for client in std_before_rtts[srv].keys():
			std_before_srv.append(std_before_rtts[srv][client])
		draw_cdf(std_before_srv, plt_styles[2], "Before Super Bowl")
	std_half_srv = []
	for client in std_half_rtts[srv].keys():
		std_half_srv.append(std_half_rtts[srv][client])
	draw_cdf(std_half_srv, plt_styles[3], "Half Time")
	std_sb_srv = []
	for client in std_sb_rtts[srv].keys():
		std_sb_srv.append(std_sb_rtts[srv][client])
	draw_cdf(std_sb_srv, plt_styles[0], "Super Bowl")
	std_after_srv = []
	for client in std_after_rtts[srv].keys():
		std_after_srv.append(std_after_rtts[srv][client])
	draw_cdf(std_after_srv, plt_styles[1], "After Super Bowl")
	ax.set_title("STD of RTTs CDF for datacenter at " + us_srv_to_plot[srv], fontsize=15)
	plt.legend(bbox_to_anchor=(1.0, 0.3))
	if "gc" in srv:
		pylab.xlim([0, 100])
	else:
		pylab.xlim([0, 50])

	plt.xlabel("Std(RTTs) from one Planetlab node to a datacenter (ms)")
	plt.ylabel("The percentage of Planetlab node!")
	plt.show()

	## Save the plot
	pdf = PdfPages('./imgs/ping/' + srv + '_stdrtts_cdf.pdf')
	pdf.savefig(f)
	pdf.close()








