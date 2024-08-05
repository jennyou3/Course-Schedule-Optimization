from gurobipy import *

#------------------Defining the model---------------------------
# Initialization. The name is arbitrary
model = Model('take3')

#-----------------Importing Data-----------------------------
import pandas as pd
import numpy as np
sched = pd.read_csv("PD_Schedule.csv")
units = pd.read_csv("PD_Units.csv")
PR = pd.read_csv("PD_PR.csv")
groups = pd.read_csv("PD_Groups.csv")
req = pd.read_csv("PD_Req.csv")
semCount = 8 # semCount is the number of semesters
courseCount = len(units) # courseCount is the number of courses

# Schedule Matrix
fall = sched[sched.Sem == "F"]
fall = fall.drop("Sem", axis = 1)
fall = fall.drop("Num", axis = 1)
spr = sched[sched.Sem == "S"]
spr = spr.drop("Sem", axis = 1)
spr = spr.drop("Num", axis = 1)
timeVec = list(np.stack((fall, spr), axis = 1))
#timeVec_i,s,g is if course i is offered in timeslot g in season s (fall or spring)
timeCount = len(timeVec[0][0])
print(timeCount)

# FCE Vector
fceVec = list(units["FCE"]) # f_i is the FCE of course i

# Units Vec
unitVec = list(units["Units"]) # unitVec_i is the units of course i

# Group Vec
groups = groups.drop("Num", axis = 1)
groupVec = groups.values.tolist()
groupCount = len(groupVec[0])

# PR Vec
PR = PR.drop("Num", axis = 1)
prereqVec = PR.values.tolist()
prereqCount = len(prereqVec[0])

# Requirements Vector
req = req.drop("Num", axis = 1)
depthVec = req["Depth Electives"]
depthReqUnits = 45
req = req.drop("Depth Electives", axis = 1)
reqVec = req.values.tolist()
reqCount = len(reqVec[0])

#-----------------Creating decision variables---------------------
# Define binary variables x_i,j
x=[([0]*semCount) for i in range(courseCount)];
for i in range(courseCount):
    for j in range(semCount):
        x[i][j] = model.addVar(vtype=GRB.BINARY, name="x_({},{})".format(i+1, j+1))

a = model.addVar(vtype=GRB.CONTINUOUS, name = "semester_max")

# Pushing created variables to the model
model.update()

# Each class is taken once
for i in range(courseCount):
    model.addConstr(sum(x[i][j] for j in range(semCount)) <= 1, name='Class {} taken once'.format(i+1))

# Don't overload in any semester
for j in range(semCount):
    model.addConstr(sum(unitVec[i]*x[i][j] for i in range(courseCount)) <= 54, name="Don't overload in sem {}".format(j+1))

# Loop through courses
# Loop through groups
# If group is prereq for that course
# loop through group, add constr
for i in range(courseCount):
    for g in range(groupCount):
        if (prereqVec[i][g] == 1):
            # If course i requires group g as a prereq
            for j in range(semCount):
                # Then if course i is taken in semester j, at least one class (c)
                # from group g must be taken in a semester (k) lower than j
                model.addConstr(sum(sum(groupVec[c][g] * x[c][k] for k in range(j))
                                    for c in range(courseCount)) >= x[i][j],
                                name="Group {} prereq for {} in sem {}".format(g+1,i+1,j+1))

# Each graduation requirement must be satisfied
for r in range(reqCount):
    model.addConstr(sum(sum(reqVec[i][r] * x[i][j] for i in range(courseCount))
                        for j in range(semCount)) >= 1,
                    name="Satisfy requirement {}".format(r+1))

# Need at least 45 units of depth electives
model.addConstr(sum(sum(depthVec[i]*x[i][j]*unitVec[i] for i in range(courseCount))
                    for j in range(semCount)) >= depthReqUnits,
                name = "Satisfy depth requirements")

# One class per time slot per semester
for g in range(timeCount):
    for j in range(semCount):
        model.addConstr(sum(x[i][j]*timeVec[i][j%2][g]
                            for i in range(courseCount)) <= 1,
                        name="One class in slot {} for sem {}".format(g+1,j+1))

# Courses only taken in seasons they are offered in
for i in range(courseCount):
    model.addConstr(sum(x[i][2*j] for j in range(4)) <= sum(timeVec[i][0][g] for g in range(timeCount)),
                    name="Course {} not taken in fall if spring only".format(i+1))
    model.addConstr(sum(x[i][2*j+1] for j in range(4)) <= sum(timeVec[i][1][g] for g in range(timeCount)),
                    name="Course {} not taken in spring if fall only".format(i+1))

# 360 units in total needed to graduate
model.addConstr(sum(sum(x[i][j] * unitVec[i] for j in range(semCount))
                    for i in range(courseCount)) >= 360,
                name = "Total courses needed to graduate")

# Hardcoding to make schedule more reliable
x[44][0] = 1; # concepts in sem 1
x[72][0] = 1 # eureka in sem 1
x[75][3] = 1; # engageInwards in sem 4
x[76][4] = 1; # engageOutwards in sem 5
x[77][6] = 1; # engageForwards in sem 7
x[73][6] = 1; # enagageService in sem 7
x[74][6] = 1; # engageArts in sem 7
x[71][2] = 1 # underGradColloq in sem 3
model.addConstr(sum(x[65][j]+x[67][j]+x[68][j]+x[69][j] for j in range(2,8)) <=0, name="No first year writing after first year")

# To minimize the max FCE among semesters (but keep this linear), we create
# variable a which is at least the FCE for each semester and minimize that
model.setObjective(a, GRB.MINIMIZE)
for j in range(semCount):
    model.addConstr(a >= sum(fceVec[i] * x[i][j] for i in range(courseCount)),
                    name = "Max FCE >= sem {} FCE".format(j+1))

# Printing the model in a separate file for easier look
model.write('take3.lp')

#-------------------- Solving the LP -------------------------------------
model.optimize()

#------------------ Outputting the solution ----------------------------
# Prints the non-zero variables and its values in a table format
model.printAttr('X')
