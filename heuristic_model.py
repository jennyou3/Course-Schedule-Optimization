import pandas as pd
import numpy as np

# read in data
sched = pd.read_csv("PD_Schedule.csv")
units = pd.read_csv("PD_Units.csv")
prereq = pd.read_csv("PD_PR.csv")
groups = pd.read_csv("PD_Groups.csv")
req = pd.read_csv("PD_Req.csv")

needed_prereq = {}
prereq_for = {}

# for each class, adds in prereqs needed
for i in prereq.index:
    curr_class_i = prereq.loc[i]['Num']
    classes_needed_for_i = [col for col in prereq.columns if prereq.at[i, col] == 1]
    needed_prereq[curr_class_i] = classes_needed_for_i

prereq_classes = [('OR_PR', 21292), ('DTF_PR', 21370), ('MF_PR', 21270), ('DE_PR', 21260), ('Py_PR', 15112), ('D_PR', 21228), ('Con_PR', 21128), ('Cal_PR', 21268), ('M_Pr', 21241), ('Al_PR', 21373), ('An_PR', 21355), ('P_PR', 21325), ('MI_PR', 73102), ('MA_PR', 73103), ('OM_PR', 70371), ('S_PR', 36226), ('MR_PR', 36401)]

# for each class, adds in what classes require it as a prereq
for c in prereq_classes:
    curr_prereq = c[0]
    filtered_classes = prereq[prereq[curr_prereq] == 1]
    curr_num = c[1]
    prereq_for[curr_num] = filtered_classes['Num'].tolist()

technicals = [21228, 21236, 21238, 21241, 21254, 21256, 21259, 21260, 21261, 21266, 21268, 21269, 21270, 21292, 21301, 21325, 21329, 21341, 21355, 21356, 21366, 21369, 21373, 21374, 21378, 21380, 21420, 21441, 21484, 15110, 15112, 15122, 15150, 15210, 21128, 21237, 21240, 21242, 21300, 21370, 21371, 21393, 21469, 21360]

# classes that satisfy each of these requirements
depth_req = (req[req['Depth Electives'] == 1])['Num'].tolist()
d_req = (req[req['D_R'] == 1])['Num'].tolist()
m_req = (req[req['M_R'] == 1])['Num'].tolist()
cal_req = (req[req['Cal_R'] == 1])['Num'].tolist()
de_req = (req[req['DE_R'] == 1])['Num'].tolist()
p_req = (req[req['P_R'] == 1])['Num'].tolist()
e_req = (req[req['E_R'] == 1])['Num'].tolist()
bs_req = (req[req['BS_R'] == 1])['Num'].tolist()
ps_req = (req[req['PS_R'] == 1])['Num'].tolist()

# checks if requirements have been satisfied
depth_req_sat = False
d_req_sat = False
m_req_sat = False
cal_req_sat = False
de_req_sat = False
p_req_sat = False
e_req_sat = False
bs_req_sat = False
ps_req_sat = False
total_req_sat = False

all_available_classes = sched['Num'].tolist()
taken_classes = []

# initializes number of units and semesters, minimum number of depth and total units
num_sem = 8
depth_req_units = 45
total_req_units = 360
max_num_tech = 3
max_num_non = 2

curr_depth_units = 0
curr_total_units = 0

final_schedule = {}

for s in range(1, num_sem + 1):
    curr_num_tech = 0
    curr_num_non = 0
    considered_classes = []
    curr_schedule = [0] * 130
    
    # initializes semesters with assumptions
    if s == 1:
        curr_sem_classes = [21128, 38101, 76101]
        max_num_classes = 5
        curr_num_tech = 1
        curr_num_non = 2
    elif s == 3:
        curr_sem_classes = [21201]
        max_num_classes = 6
    elif s == 4:
        curr_sem_classes = [38230]
        max_num_classes = 6
    elif s == 5:
        curr_sem_classes = [38330]
        max_num_classes = 6
    elif s == 6:
        curr_sem_classes = [38304]
        max_num_classes = 6
    elif s == 7:
        curr_sem_classes = [38110, 38220, 38430]
        max_num_classes = 8
    else:
        curr_sem_classes = []
        max_num_classes = 5
    
    curr_num_classes = len(curr_sem_classes)
    
    while curr_num_classes < max_num_classes:
        prereq_sat = False
        schedule_conflict = True
        not_taken = False
        not_considered = False
        offered_in_sem = False
        
        # gets set of classes that have not been taken yet or attempted to have been taken
        filtered_dict = {key: value for key, value in prereq_for.items() if (key not in considered_classes) and (key not in taken_classes)}
        if not filtered_dict:
            print("The dictionary is empty.")
            break
        
        # finds class that the most number of classes require it
        max_prereq_class = max(filtered_dict, key=lambda k: len(filtered_dict[k]))
        
        # checks if all prereqs for chosen class have been taken
        if all(c in taken_classes for c in needed_prereq[str(max_prereq_class)]):
            prereq_sat = True
        
        # finds what semester it is offered
        index = sched.index[sched['Num'] == str(max_prereq_class)].tolist()[0]
        print(index)
        print(sched)
        print(sched['Sem'])
        curr_offered_sem = sched['Sem'][index]
        
        # if the current semester matches the semester when the course is offered
        if (((s % 2) == 0) and curr_offered_sem == 'S') or (((s % 2) == 1) and curr_offered_sem == 'F'):
            offered_in_sem = True
        
        # check scheduling conflict
        curr_offered_sem = sched['Sem'][index]
        max_prereq_class_sched = sched.loc[index, sched.columns.difference(['Num', 'Sem'])]
        
        # check if there is an avaialble time in current schedule for when the class is offered
        result = [(a + b) % 2 for a, b in zip(curr_schedule, max_prereq_class_sched)]
        
        chosen_time = []
        chosen_yet = False
        
        for i in range(len(curr_schedule) - 1):
            if not chosen_yet:
                if result[i] == 1 and result[i + 1] == 1:
                    schedule_conflict = False
                    chosen_yet = True
                    chosen_time.append(i)
                    chosen_time.append(i + 1)
                    if i != (len(curr_schedule) - 2):
                        if result[i + 2] == 1:
                            chosen_time.append(i + 2)
        
        # checks if class has been considered or taken yet
        if max_prereq_class not in considered_classes:
            not_considered = True
        
        if max_prereq_class in all_available_classes:
            not_taken = True
        
        # increments either nontechnical or technical count by 1
        if max_prereq_class in technicals:
            curr_num_tech += 1
        else:
            curr_num_non += 1
        
        # checks if all constraints satisfied
        if prereq_sat and (not schedule_conflict) and not_taken and (curr_num_tech <= max_num_tech) and (curr_num_non <= max_num_non) and not_considered and offered_in_sem:
            print(f"adding {max_prereq_class}")
            curr_sem_classes.append(max_prereq_class)
            all_available_classes.remove(max_prereq_class)
            taken_classes.append(max_prereq_class)
            prereq_for.pop(max_prereq_class)
            
            index = units.index[units['Num'] == max_prereq_class].tolist()[0]
            curr_total_units += units[index]['Units']
            
            for t in range(len(chosen_time)):
                curr_schedule[chosen_time[t]] == 1
            
            considered_classes.append(max_prereq_class)
            
            # count as grad req
            if curr_total_units == total_req_units:
                total_req_sat = True
            
            if max_prereq_class in depth_req:
                index = units.index[units['Num'] == max_prereq_class].tolist()[0]
                curr_depth_units += units[index]['Units']
            
            if curr_depth_units == depth_req_units:
                depth_req_sat = True
            
            if max_prereq_class in d_req:
                d_req_sat = True
            if max_prereq_class in m_req:
                m_req_sat = True
            if max_prereq_class in cal_req:
                cal_req_sat = True
            if max_prereq_class in de_req:
                de_req_sat = True
            if max_prereq_class in p_req:
                p_req_sat = True
            if max_prereq_class in e_req:
                e_req_sat = True
            if max_prereq_class in bs_req:
                bs_req_sat = True
            if max_prereq_class in ps_req:
                ps_req_sat = True
    
    final_schedule[s] = (curr_sem_classes, curr_schedule)
    print(final_schedule)
