#! /usr/bin/env python

from optimal_filter_lib import TreeFilter
from sys import argv
from math import sqrt
from subprocess import check_output,call
import argparse
from sys import stdout

parser = argparse.ArgumentParser()

parser.add_argument("-i","--input",required=True,help="input tree")
parser.add_argument("-o","--output",required=False,help="output tree")
parser.add_argument("-k","--k",required=False,help="number of taxon to be removed")
parser.add_argument("-r","--removal",required=False,help="list of removed taxa")
parser.add_argument("-d","--diameter",required=False,help="list of optimal diameter by level")
parser.add_argument("-g","--gradient",required=False,help="list of the gradient of the diameter by level")

args = vars(parser.parse_args())

intree = args["input"]
outtree = args["output"]

myfilter = TreeFilter(tree_file=intree)
myfilter.optFilter()

branch_list = []
for br in myfilter.ddpTree.preorder_edge_iter():
    if br.tail_node is not None:
        branch_list.append(br.length)

branch_list.sort()
if len(branch_list)%2:
    med_br = branch_list[len(branch_list)/2]
else: 
    med_br = (branch_list[len(branch_list)/2] + branch_list[len(branch_list)/2-1])/2

datafile = args["gradient"] if args["gradient"] else check_output(["mktemp"]).rstrip()
fout = open(datafile,"w")

fout1 = open(args["diameter"],"w") if args["diameter"] else None

for i in range(1,len(myfilter.min_diams)):
   fout.write(str((myfilter.min_diams[i-1]-myfilter.min_diams[i])/med_br) + "\n")
   if fout1:
       fout1.write(str(myfilter.min_diams[i-1])+"\n")

if fout1:
    fout1.write(str(myfilter.min_diams[-1]))
    fout1.close()

fout.close()

if outtree is not None:
    opt_k = min(int(args["k"]),len(myfilter.min_diams)-1) if args["k"] else int(check_output(["Rscript","/Users/uym2/my_gits/LongBranchFiltering/find_d.R",datafile,"0.05"])[4:].rstrip())

    fTree = myfilter.filterOut(d=opt_k, fout=open(args["removal"],"w") if args["removal"] else stdout)
    fTree.write_to_path(outtree,"newick")

if args["gradient"] is None:
    call(["rm",datafile])
