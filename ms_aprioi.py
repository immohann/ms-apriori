# -*- coding: utf-8 -*-


import csv
import itertools
from collections import defaultdict, OrderedDict

# custom 
def read_input(inputf,paramf):
    "read inputfile"
    data = []
    param = {}
    sdc = 0

    # set file
    with open(inputf) as myfile:
      csv_records = csv.reader(myfile)
      for row in csv_records:
        new_list = [int(item) for item in row]
        data.append(new_list)
        
    # param file
    uniq_vals = set(itertools.chain.from_iterable(data))
    file_iter = open(paramf, 'r')
    for line in file_iter:
        line = line.replace(" ", "")
        line = line.strip()
        if 'MIS' in line:
            key = line[line.find("(") + 1:line.find(")")]
            val = line[line.find("=") + 1:]
            param[key] = float(val)
            
        elif 'SDC' in line:
            sdc = float(line[line.find("=") + 1:])

    # set rest value to te rest of the elements
    rest = []
    for key,vals in param.items():
      if key == "rest":
        r = vals
      else:
        rest.append(int(key))

    for i in uniq_vals:
      if i not in rest:
        param[str(i)] = r
    
    if 'rest' in param.keys():
        del param['rest']

    param = {int(k):float(v) for k,v in param.items()}
    param = OrderedDict(sorted(param.items()))

    # print(data,param,sdc)

    return data, param, sdc

# to-be modified
def l2_cgen(FF, param, sdc, it_count, max_mis, transSize):
    "generate cadidates for the 2-itemset"
    s = set(frozenset([w]) for w in FF)
    s2 = set([i.union(j) for i in s for j in s if len(i.union(j)) == 2])
    cand = []
    for e in s2:
        minSup = 1
        maxSup = 0

        for r in e:
            if it_count[r]/float(transSize) < minSup:
                minSup = it_count[r]/float(transSize)
            if it_count[r]/float(transSize) > maxSup:
                maxSup = it_count[r]/float(transSize)

        if maxSup-minSup <= sdc:
            cand.append(e)

    ## get the lowest MIS (done)
    min_mis = dict()

    for i in cand:
        min = 1
        max = 0
        maxMISItem = 0
        for j in i:
            if param[j] < min:
                min = param[j]
            if param[j] > max:
                max = param[j]
                maxMISItem = it_count[j]
        min_mis[i] = min
        max_mis[i] = maxMISItem

        # print(cand)
        # print(min_mis)

    return cand, min_mis

# to-be modified
def lk_cgen(L, param, sdc, k, it_count, max_mis):
    s2 = set([i.union(j) for i in L for j in L if len(i.union(j)) == k])
    cand = []
    for e in s2:
        minSup = 1
        maxSup = 0
        for r in e:
            if param[r] < minSup:
                minSup = param[r]
            if param[r] > maxSup:
                maxSup = param[r]
        if maxSup-minSup <= sdc:
            cand.append(e)

    ## get the lowest MIS
    min_mis = dict()
    for i in cand:
        min = 1
        max = 0
        max_mis_item = 0
        for j in i:
            if param[j] < min:
                min = param[j]
            if param[j] > max:
                max = param[j]
                max_mis_item = it_count[j]
        min_mis[i] = min
        max_mis[i] = max_mis_item

        # print(cand)
        # print(min_mis)

    return cand, min_mis
            
    
def MSA (fileData, parameters, sdc):
    "MSApriori algorithm"
    trans = []
    for tr in fileData:
        trans.append(set(tr))

    sorted_items = [(k, v) for k, v in sorted(parameters.items(), key=lambda item: item[1])]
    print(sorted_items)
    transSize = len(trans)

    ## construct the M
    M =[]
    for i in (sorted_items):
        M.append(i[0])

    # print("M",M)
    ## get the count
    
    count=defaultdict(int)
    for item in M:
        for transaction in trans:
            m={item}
            if m.issubset(transaction):
                count[item] += 1

    # print(count)
    # Initial pass
    
    L=[]
    start = 0
    pivot = 0
    for i in M:
        # print(i,count[i],parameters[i],pivot)
        if count[i]/float(len(trans)) >= parameters[i] and start == 0:
            L.append(i)
            start = 1
            pivot = parameters[i]
        elif count[i]/float(len(trans))  >= pivot and start == 1:
            L.append(i)

    # print(L)

    # select the 1-frequentset
    F = dict()
    F_local = []
    for i in L:
        if count[i] / float(len(trans))  >= parameters[i]:
            F_local.append({i})
    F[1] = F_local


    # for the rest of set-size
    k = 2
    max_mis = dict()
    while(len(F[k-1]) != 0):
        print("Working on",k,"itemset ......")
        if(k==2):
            cd, min_mis = l2_cgen(L, parameters, sdc, count, max_mis, transSize)
        else:
            cd, min_mis = lk_cgen(F[k - 1], parameters, sdc, k, count, max_mis)

        ## Get the count
        for item in cd:
            for transaction in trans:
                if item.issubset(transaction):
                    count[item] += 1
    
        ## Select the items fro the k-frequent itemset
        F_local = []
        for item in cd:
            if count[item] / float(len(trans))  >= min_mis[item]:
                F_local.append(item)
        F[k] = F_local
        k+=1

    del(F[k-1])

    return F

def save_file(outputFile, F):
    "Save output in the same format as requested"
    with open(outputFile, 'w') as f:
        k = []
        for key in F:
            k.append(key)
        k = sorted(k)
        for i in k:
            f.write("(Length-%d %d\n\n" % (i,len(F[i])))
            
            for j in F[i]:
                print("F",len(j))
                if i == 1:
                    tmp = next(iter(j))
                    f.write("\t(%s) \n" % ( tuple(list(j))))
                else:
                    s = []
                    f.write("")
                    st = ""
                    for i in set(j):
                        st+=str(i)
                        st+=" "
                    
                    f.write("\t("+st[:-1]+")\n")
            f.write(")\n")

if __name__ == "__main__":

    fileData, parameters, sdc = read_input("input-data.txt","parameter-file.txt")
    F= MSA(fileData, parameters, sdc)
    save_file("outFile.txt", F)
    print("\n DONE \n")
