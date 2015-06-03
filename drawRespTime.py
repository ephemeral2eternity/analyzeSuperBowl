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
from matplotlib.backends.backend_pdf import PdfPages

def plot_srv_resp_times(resp_times, client, client_location, plt_sty, srv):
	sorted_ts = sorted(resp_times.keys())
	sorted_resp_times = []
	for ts in sorted_ts:
		sorted_resp_times.append(resp_times[ts])

	plt.plot(sorted_ts, sorted_resp_times, plt_sty, label=srv, linewidth=2.0, markersize=3.0)


def plot_all_resp_times(all_resp_times, client, client_location, plt_styles):
	fig, ax = plt.subplots()
	srv_id = 0
	for srv in all_resp_times.keys():
		resp_times = all_resp_times[srv]
		plot_srv_resp_times(resp_times, client, client_location, plt_styles[srv_id], srv)
		srv_id = srv_id + 1

	## Label figure axis
	ts_superbowl = [1422833400, 1422838800, 1422840240, 1422843600]
	str_ts_superbowl = ['Superbowl Starts', 'Halftime Start', 'Halftime Ends', 'Superbowl Ends']
	plt.xticks(ts_superbowl, str_ts_superbowl, fontsize=15)
	# Make space for and rotate the x-axis tick labels
	fig.autofmt_xdate()
	pylab.xlim([1422820000, 1422855000])
	pylab.ylim([0, 50])
	ax.set_title('Chunks\' Response Time for client ' + client + ' at ' + client_location, fontsize=15)
	# Shrink current axis by 10%
	box = ax.get_position()
	ax.set_position([box.x0, box.y0 + 0.1, box.width, box.height * 0.9])
	## Set up legends
	ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.25),
	          fancybox=True, shadow=True, ncol=3)
	plt.show()

	## Save the plot
	pdf = PdfPages('./imgs/resptime/' + client + '.pdf')
	pdf.savefig(fig)
	pdf.close()


def find_dash_srv(client, ts):
	## Get all PING traces from client
	pingFolder = "./ping/"
	pingSuffix = "_PING.json"
	ping_files = glob.glob(pingFolder + client + "/*" + pingSuffix)

	less_than_ts = []
	## Extract all TS from all available PING files
	for p_file in ping_files:
		cur_ts = re.search(pingFolder + client + "/" + client + "_" + "(.*?)" + pingSuffix, p_file).group(1)
		if int(cur_ts) < ts:
			less_than_ts.append(int(cur_ts))

	max_less_than_ts = max(less_than_ts)
	ping_file_used = pingFolder + client + "/" + client + "_" + str(max_less_than_ts) + pingSuffix
	srv_rtts = json.load(open(ping_file_used))
	gc_srv_rtts = {}
	for srv in srv_rtts.keys():
		if "gc" in srv:
			gc_srv = srv.replace("gc", "cache-")
			gc_srv_rtts[gc_srv] = srv_rtts[srv]
	sorted_srv_rtts = sorted(gc_srv_rtts.items(), key=operator.itemgetter(1))
	srv = sorted_srv_rtts[0][0]
	return srv

def read_all_resptime(client, datafolder, file_suffix):
	## Get all DASH chunk traces from client
	chunk_files = glob.glob(datafolder + client + "/" + client + "_*" + file_suffix)
	# print "Files: ", chunk_files

	### Initialize resp_times
	resp_times = {}

	### Read all chunk QoE files
	for cfile in chunk_files:
		print cfile
		dash_file = re.compile(datafolder + client + "/" + client + "_([0-9]+)" + file_suffix)
		cur_video = json.load(open(cfile))
		if dash_file.match(cfile):
			print cfile, " is a DASH file"
			ts = re.search(datafolder + client + "/" + client + "_" + "(.*?)" + file_suffix, cfile).group(1)
			## Find server of the DASH streaming
			srv = find_dash_srv(client, int(ts))
			if srv not in resp_times.keys():
				resp_times[srv] = {}

			for chunk_id in sorted(cur_video.keys()):
				cur_chunk_info = cur_video[chunk_id]
				chunk_ts = int(cur_chunk_info["TS"])
				chunk_resp_time = math.fabs(float(cur_chunk_info["Response"]))
				resp_times[srv][chunk_ts] = chunk_resp_time
		else:
			print cfile, " is not a DASH file."

			for chunk_id in sorted(cur_video.keys()):
				cur_chunk_info = cur_video[chunk_id]
				chunk_ts = int(cur_chunk_info["TS"])
				if "Response" in cur_chunk_info.keys():
					chunk_resp_time = math.fabs(float(cur_chunk_info["Response"]))
				else:
					chunk_resp_time = math.fabs(float(cur_chunk_info["Reponse"]))
				chunk_srv = cur_chunk_info["Server"]

				if chunk_srv not in resp_times.keys():
					resp_times[chunk_srv] = {}

				resp_times[chunk_srv][chunk_ts] = chunk_resp_time

	return resp_times


#client = "75-130-96-12.static.oxfr.ma.charter.com"
#client_location = "Worcester Polytechnic Institute, Massachusetts, US"

#client = "planetlab-1.tagus.ist.utl.pt"
#client_location = "Instituto Superior Tecnico, Lisboa, Portugal"

client = "planetlab-3.cmcl.cs.cmu.edu"
client_location = "Carnegie Mellon University, Pittsburgh, US"

datafolder = "./data/"

file_suffix = "_BBB.json"

plt_styles = ['bs', 'kd', 'r*', 'g+', 'mo', 'y^', 'ch', 'k^', 'ro', 'g*', 'md']
all_resp_times = read_all_resptime(client, datafolder, file_suffix)
plot_all_resp_times(all_resp_times, client, client_location, plt_styles)
