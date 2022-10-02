# READ INPUTS 
import csv
import itertools
from collections import defaultdict, OrderedDict

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
    # print("reading set")
        
    # param file
    uniq_vals = set(itertools.chain.from_iterable(data))
    file_iter = open(paramf, 'r')
    for line in file_iter:
        line = line.replace(" ", "").replace("{","").replace("}","")
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
    # param = OrderedDict(sorted(param.items()))

    # print(data,param,sdc
    return data, param, sdc

def init_pass(item_list,item_count,file_data,parameters):
  L = []
  F = []
  for i in range(len(item_list)):
    if i != 0:
        if ((item_count.get(item_list[i]) / len(file_data)) >= parameters.get(item_list[0])):
            L.append(item_list[i])
    else:
        L.append(item_list[0])
  return L

def level2_gen(L, cand_list, sdc, item_count, inp_data, parameters):
    for item_in_L in range(0, len(L)):
        if (item_count[L[item_in_L]] / len(inp_data)) >= parameters[L[item_in_L]]:
            for data in range(item_in_L + 1, len(L)):
                if (abs((item_count[L[data]] / len(inp_data)) - (item_count[L[item_in_L]] / len(inp_data))) <= sdc) and (item_count[L[data]] / len(inp_data)) >= parameters[L[item_in_L]]:
                    cand_list[2].append([])
                    cand_list[2][len(cand_list[2]) - 1].append(L[item_in_L])
                    cand_list[2][len(cand_list[2]) - 1].append(L[data])
    cand_list[2].sort(key=lambda row: row[1])
    return(cand_list)

def level_n_gen(num,sotred_items,freq_items,cand_list,inp_data,sdc,item_count ):
    element = 0
    freq_level = num - 1
    for i in range(0, len(freq_items[freq_level])):
        for j in range(0, len(freq_items[freq_level])):
            while (element < freq_level - 1) and (freq_items[freq_level][i][element] == freq_items[freq_level][j][element]):
                element += 1

            if element == freq_level - 1:
                if ((sotred_items[freq_items[freq_level][i][element]] < sotred_items[freq_items[freq_level][j][element]]) and (
                        abs((item_count[freq_items[freq_level][i][element]] / len(inp_data)) - (item_count[freq_items[freq_level][j][element]] / len(inp_data))) <= sdc)):
                    cand_list[freq_level + 1].append(list(freq_items[freq_level][i]))
                    cand_list[freq_level + 1][len(cand_list[freq_level + 1]) - 1].append(freq_items[freq_level][j][element])

            element = 0

def MSA (file_data, parameters, sdc):
    "MSApriori algorithm"
    item_count ={}
    item_list = []
    freq_items = list([] for _ in range(10))

    # item_count
    unique_items = sorted(parameters, key=parameters.__getitem__)
    
    for item in unique_items:
        item_list.append(int(item))
        item_count[int(item)] = 0
    # print("Item_List",item_list)
    
    for i in file_data:
      for j in i:
          if j not in item_count.keys():
              item_count[j] = 0
          else:
              item_count[j] = item_count[j] + 1
    # print("Item_Count",item_count)

    # init-pass
    L = init_pass(item_list,item_count,file_data,parameters)

    sotred_items = {} 
    for i in range(len(L)):
        sotred_items[L[i]] = i

    # print(sotred_items)

    # Adding 1-Itemsets to the freq_items
    if freq_items[1] is not None:
        for i in range(len(L)):
            if (item_count.get(L[i]) / len(file_data)) >= parameters.get(L[i]):
                freq_items[1].append([L[i]])
        # print("freq_items after", freq_items)



    level = 2
    cand_dict = {}
    cand_list = list([] for _ in range(10))
    
    while 1:
        if not freq_items[level - 1]:
            break

        if level == 2:
            Candidate_L = level2_gen(L, cand_list, sdc, item_count, data, parameters)
        else:
            Candidate_L = level_n_gen(level,sotred_items,freq_items,cand_list,data,sdc,item_count)

        for transac in data:
            for cand in cand_list[level]:
                if set(cand).issubset(set(transac)):
                    if cand_dict.get(tuple(cand)) != None:
                        cand_dict[tuple(cand)] += 1
                    else:
                        cand_dict[tuple(cand)] = 1

        for cand in cand_list[level]:
            if cand_dict.get(tuple(cand)) != None:
                if cand_dict.get(tuple(cand)) / len(data) >= parameters[cand[0]]:
                    freq_items[level].append(cand[:])
        level += 1
    # print(cand_dict)
    # print(cand_list)
    print("freq_items:",freq_items)
    freq_items = [x for x in freq_items if x != []]
    return freq_items




data, parameters, sdc = read_input("data-2.txt","para-2.txt")
F= MSA(data, parameters, sdc)

result_path = "results_1.txt"
output_file = open(result_path, "w")

count = 0
for _ in F[0]:
    count += 1


output_file.write("(Length-1 " + str(count) + "\n")
if F != []:
    for t in F[0]:
        count += 1

        output_file.write("\t" + "(" + str(t[0]) + ")\n")
        # print("count2:",str(t[0]))

output_file.write(")\n")

for i in range(1, len(F)):
    total_count = 0
    for _ in F[i]:
        total_count += 1
    output_file.write("\n(Length-"+ str(i + 1) + " "+str(total_count)+"\n")
    count = 0
    for t in F[i]:
        total_cnt = 0
        for j in range(len(data)):
            if set(data[j]) >= set(t):
                total_cnt = total_cnt + 1
        count += 1
        output_file.write("\t" + "(" + str(t).replace("[", "").replace("]", "").replace(",", "") + ")\n")
    output_file.write(")\n")

