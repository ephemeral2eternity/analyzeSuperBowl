import json
import numpy as np
import pylab
import sys
import matplotlib.pyplot as plt
import glob
import re
import datetime
from matplotlib.backends.backend_pdf import PdfPages

def plot_srvs_rtts(rtts, srv_to_plot, client, client_location, plt_styles, reg_name):
	## Find the azure anomaly period
	az_rtts = rtts['az02']
	sorted_az_ts = sorted(az_rtts.keys())
	az_anormaly_period = []
	for ts in sorted_az_ts:
		if az_rtts[ts] == 255.0:
			az_anormaly_period.append(ts)
	print az_anormaly_period
	print "Azure anomaly starts at ", az_anormaly_period[0], ' and ends at ', az_anormaly_period[-1]

	fig, ax = plt.subplots()
	srv_id = 0
	for srv in srv_to_plot.keys():
		srv_rtts = rtts[srv]
		srv_ts = srv_rtts.keys()
		sorted_rtts = []
		sorted_srv_ts = sorted(srv_ts)
		print "Selected server is:", srv
		for ts in sorted_srv_ts:
			print "Timestamp: ", ts, "Server RTT: ", srv_rtts[ts]
			sorted_rtts.append(srv_rtts[ts])

		plt.plot(sorted(srv_ts), sorted_rtts, plt_styles[srv_id], label=srv_to_plot[srv], linewidth=2.0, markersize=7.0)
		srv_id = srv_id + 1

	ts_superbowl = [int(az_anormaly_period[0]), int(az_anormaly_period[-1]), 1422833400, 1422838800, 1422840240, 1422843600]
	str_ts_superbowl = ['Azure Anormaly Starts', 'Azure Anormaly Ends', 'Superbowl Starts', 'Halftime Start', 'Halftime Ends', 'Superbowl Ends']
	plt.xticks(ts_superbowl, str_ts_superbowl, fontsize=15)
	# Make space for and rotate the x-axis tick labels
	fig.autofmt_xdate()
	print sorted_srv_ts[0], sorted_srv_ts[-1]
	pylab.xlim([1422811800, 1422865200])

	# Shrink current axis by 10%
	box = ax.get_position()
	ax.set_position([box.x0, box.y0 + 0.1, box.width, box.height * 0.9])
	#pylab.ylim([min(sorted_rtts) - 50, max(sorted_rtts) + 50])
	# Put a legend below current axis
	ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.25),
	          fancybox=True, shadow=True, ncol=5)
	ax.set_title('Ping Traces at ' + client_location, fontsize=15)

	params = {'legend.fontsize': 15,
	          'legend.linewidth': 2}
	plt.rcParams.update(params)
	plt.show()

	## Save the plot
	pdf = PdfPages('./imgs/ping/' + client + '_' + reg_name + '_PING.pdf')
	pdf.savefig(fig)
	pdf.close()

#client = "75-130-96-12.static.oxfr.ma.charter.com"
#client_location = "Worcester Polytechnic Institute, Massachusetts, US"

#client = "aguila1.lsi.upc.edu"
#client_location = "Universitat Politecnica de Catalunya, Barcelona, Spain"

#client = "planetlab-3.cmcl.cs.cmu.edu"
#client_location = "Carnegie Mellon University, Pittsburgh, US"

client = "planetlab1.ucsd.edu"
client_location = "University of California, San Diego, California, US"

datafolder = "./ping/"

pingSuffix = "_PING.json"
plt_styles = ['k-', 'b-.', 'r:', 'm--', 'y-s', 'k-h', 'g-^', 'b-o', 'r-*', 'm-d']

## Get all PING traces from client
ping_files = glob.glob(datafolder + client + "/*" + pingSuffix)

## All servers
srvs = []

rtts = {}

for pfile in ping_files:
	print pfile
	ts = re.search(datafolder + client + "/" + client + "_" + "(.*?)" + pingSuffix, pfile).group(1)
	timestamp = datetime.datetime.fromtimestamp(int(ts)).strftime('%H:%M:%S')
	print "Current timestamp:", timestamp
	cur_rtt = json.load(open(pfile))
	
	## Get the list of servers
	if not srvs:
		srvs = cur_rtt.keys()
		for srv in srvs:
			rtts[srv] = {}

	for srv in cur_rtt.keys():
		rtts[srv][ts] = cur_rtt[srv]

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

europe_srv_to_plot = { 
				"gc07" : "St Ghislain, Belgium, Google", 
				"gc09" : "Eemshaven, Netherlands, Google",
				"az06" : "Ireland, Azure",
				"az07" : "Netherlands, Azure", 
				"aws04" : "Ireland, AWS"
			}

asia_srv_to_plot = { 
				"gc03" : "Changhua County, Taiwan, Google", 
				"az08" : "Hongkong, Azure",
				"az08" : "Singapore, Azure",
				"az09" : "Osaka Prefecture, Japan, Azure",
				"aws05" : "Singapore, AWS",
				"aws06" : "Tokyo, AWS"
			}

other_srv_to_plot = {
				"aws07" : "Sydney, Australia, AWS",
				"aws08" : "Sao Paulo, Brazil, AWS"
}

plot_srvs_rtts(rtts, us_srv_to_plot, client, client_location, plt_styles, 'US')
plot_srvs_rtts(rtts, europe_srv_to_plot, client, client_location, plt_styles, 'EU')
plot_srvs_rtts(rtts, asia_srv_to_plot, client, client_location, plt_styles, 'ASIA')
plot_srvs_rtts(rtts, other_srv_to_plot, client, client_location, plt_styles, 'OTHER')


	
