# this code was written by Petter Holme spring / summer 2017
# it calculates the outbreak size of the SIR model given sets of seed nodes (i.e. influence maximization)
# it could be ran as
#   python infmax.py [# links] [links] <seeds>
# where [links] list the pairs of nodes connected in the network
# so for a triangle, and one seed node, one can run it as:
#   python infmax.py 3 0 1 1 2 2 0 0

import networkx as nx
from sys import argv
from sympy.abc import x
from sympy import Poly
from copy import deepcopy

# from gc import collect

#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
# get the nodes that could be infected, or recovered

def get_infect_reco ():
	global G

	r = []
	for u,v in G.edges_iter():
		if G.node[u]['state'] == 'S' and G.node[v]['state'] == 'I':
			r.append(u)
		elif G.node[u]['state'] == 'I' and G.node[v]['state'] == 'S':
			r.append(v)
	
	infect = {}
	for rr in r:
		if rr in infect:
			infect[rr] += 1
		else:
			infect[rr] = 1

	recoverables = [v for v in G.nodes() if G.node[v]['state'] == 'I']
	return infect, recoverables


#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

def obsize (G):
	n = 0
	for v in G.nodes():
		if G.node[v]['state'] == 'S':
			n += 1
		
	return G.number_of_nodes() - n

#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
# stepping down in the tree of states, the path to the root is an infection chain

def stepdown (wnum0,wden0): # num means numerator, den denominator
	global G, onum, oden

	wnum = wnum0.mul_ground(1)
	wden = wden0.mul_ground(1)

	infectables, recoverables = get_infect_reco()
	si = sum(infectables.values())

	if si == 0: # if there are no nodes that can be infected, we can exit
		# this calculates onum/oden += wnum/wden * obsize(G)
		a = onum.mul(wden)
		b = wnum.mul(oden).mul_ground(obsize(G))
		c = oden.mul(wden)
		d = a.add(b)
		
		a = d.gcd(c)
		onum,no = d.div(a)
		oden,no = c.div(a)
		# collect() # if program takes too much memory 

		return

	sr = len(recoverables)
	# calculating the denominator for calculations below
	den = Poly(si * x + sr, x)

	for you, num in sorted(infectables.iteritems()):
		G.node[you]['state'] = 'I'
		# stepdown with a weight: num * x * [wnum/wden] / den
		
		stepdown(wnum.mul(Poly(num * x,x)),wden.mul(den))
		
		G.node[you]['state'] = 'S'
	for you in sorted(recoverables):
		G.node[you]['state'] = 'R'
		# stepdown with a weight: [wnum/wden] / den
		
		stepdown(wnum,wden.mul(den))
		
		G.node[you]['state'] = 'I'
	# collect() # if program takes too much memory

#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

if __name__ == "__main__":
	global G, onum, oden

	if len(argv) < 2:
		print 'usage python infmax.py [# links] [links] <seeds>'
		exit()

	G0 = nx.Graph()

	nl = int(argv[1])

	for i in range(nl):
		G0.add_edge(argv[2 + 2 * i], argv[3 + 2 * i])

	for v in G0.nodes():
		G0.node[v]['state'] = 'S'

	s = ''
	for i in range(2 + 2 * nl,len(argv)):
		me = argv[i]
		s += me + ' '
		if me not in G0.nodes():
			print me, 'not in G'
			exit()
		G0.node[me]['state'] = 'I'

	#G = nx.convert_node_labels_to_integers(G0,label_attribute='id')
	G = deepcopy(G0)

	onum = Poly(0,x)
	oden = Poly(1,x)
	stepdown(Poly(1,x),Poly(1,x))
	
	a = onum.gcd(oden)
	onum, no = onum.div(a)
	oden, no = oden.div(a)

	# the output format is: [active nodes (separated by blanks)], [solution polynomial]
	print s.strip() + ', (' + str(onum.as_expr()) + ')/(' + str(oden.as_expr()) + ')'

#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
