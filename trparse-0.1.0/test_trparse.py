import trparse

trFile = './sample_tr.log'

trFileHdl = open(trFile, 'r')
trString = trFileHdl.read()
trFileHdl.close()

# Parse the traceroute output
traceroute = trparse.loads(trString)
# You can print the result
print traceroute
# Save it as string
tr_str = str(traceroute) 
# Or travel the tree
hop = traceroute.hops[0]
probe = hop.probes[0]
# And print the IP address
print probe.ip