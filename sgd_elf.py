import numpy as np
import pandas as pd
import random as rd
import copy
import matplotlib.pyplot as plt
import sys

fam = np.asarray(pd.read_csv('family_data.csv').values)

n_days = 100
max_occupancy = 300
min_occupancy = 125
days = np.arange(n_days) + 1
penalty_const = [0,50,50,100,200,200,300,300,400,500,500]
penalty_term1 = [0,0,9,9,9,18,18,36,36,235,434]

def cost(schedule):
    penalty, occupancy, day_cost = 0, {k: 0 for k in days}, {k: 0 for k in days}
    fam_prefs = {}
    fam_costs = []

    for assignment in schedule:
        family, day = assignment[0], assignment[1]

        choices = fam[fam[:,0] == family][0]
        choices2, n_members = choices[1:-1], choices[-1]
        if family not in fam_prefs.keys():
            fam_prefs[family] = {'n_members': n_members, 'choices': choices2}
        pref = np.where(choices2 == day)
        pref = 10 if len(pref[0]) == 0 else pref[0][0]
        penalty = penalty + penalty_const[pref] + n_members*penalty_term1[pref]
        occupancy[day] += n_members
        day_cost[day] += penalty_const[pref] + n_members*penalty_term1[pref]
        fam_costs.append((family, penalty))

    for i in days:
        if occupancy[i] > max_occupancy or (occupancy[i] < min_occupancy):
            penalty += 10000000000000

    accounting_cost = (occupancy[n_days] - min_occupancy) / 400.0 * occupancy[n_days]**0.5
    day_cost[n_days] += (occupancy[n_days] - min_occupancy) / 400.0 * occupancy[n_days]**0.5
    accounting_cost = max(0, accounting_cost)
    for i in range(len(days) - 1, -1):
        accounting_cost += (occupancy[i] - min_occupancy) / 400.0 * occupancy[i]**(0.5 + np.sqrt( (occupancy[i] - occupancy[i+1])**2))
        day_cost[i] += (occupancy[i] - min_occupancy) / 400.0 * occupancy[i]**(0.5 + np.sqrt( (occupancy[i] - occupancy[i+1])**2))

    penalty += accounting_cost
    return penalty, np.asarray(fam_costs), occupancy, fam_prefs, day_cost

def make_guess(schedule, fc):
    fam_day_costs = np.hstack((schedule, fc[:,1:]))
    fam_day_costs.view('i8,i8,i8').sort(order=['f2'], axis=0)
    return fam_day_costs[::-1]

def make_sched():
    bymems = []
    for i in fam_prefs.keys():
        cv = [i]
        cv.append(fam_prefs[i]['n_members'])
        bymems.append(cv)
    bymems = np.array(bymems)
    bymems.view('i8,i8').sort(order=['f1','f0'], axis=0)
    bymems = bymems[::-1]

    occ = {k:0 for k in days}

    sched = []
    not_scheduled = []
    for i in range(bymems.shape[0]):
        found = 0
        for j in range(len(fam_prefs[bymems[i][0]]['choices'])):
            if (occ[fam_prefs[bymems[i][0]]['choices'][j]] < max_occupancy - bymems[i][1]) and found == 0:
                sched.append([bymems[i][0], fam_prefs[bymems[i][0]]['choices'][j]])
                found = 1
                occ[fam_prefs[bymems[i][0]]['choices'][j]] += bymems[i][1]
        if found == 0:
            not_scheduled.append(i)

    for i in not_scheduled:
        scheduled = 0
        for key in occ.keys():
            if occ[key] < max_occupancy - bymems[i][1] and occ[key] + bymems[i][1] >= min_occupancy and scheduled == 0:
                sched.append([bymems[i][0], key])
                occ[key] += bymems[i][1]
                scheduled = 1
    return np.asarray(sched)

init = [[j, rd.randint(1,n_days)] for j in range(len(fam))]
total_cost, fam_costs, occ, fam_prefs, day_costs = cost(init)
#start = make_sched()
start = np.asarray(init)
total_cost, fam_costs, occ, fam_prefs, day_costs = cost(start)
day_costs = np.asarray([[m,day_costs[m]] for m in day_costs.keys()])
day_costs.view('i8,i8').sort(order=['f1'], axis=0)
day_costs = day_costs[::-1]

print(total_cost)
total_cost2 = 100000000000000000
for i in range(100):
    not_scheduled = []
    temp = start.copy()


    for j in range(10):
        occ[day_costs[j,0]] = 0
        occ[day_costs[j,0]] = 0
        occ[day_costs[j,0]] = 0
    for j in range(10):
        fams_toberescheduled = temp[temp[:,1] == day_costs[j,0]][:,0]
        for k in range(fams_toberescheduled.shape[0]):
            found = 0
            try:
                fam_prefs[fams_toberescheduled[k]]['choices'].remove(day_costs[j,0])
            except:
                pass
            for l in range(len(fam_prefs[fams_toberescheduled[k]]['choices'])):
                if found == 0 and (occ[fam_prefs[fams_toberescheduled[k]]['choices'][l]] < max_occupancy - fam_prefs[fams_toberescheduled[k]]['n_members']) and (occ[fam_prefs[fams_toberescheduled[k]]['choices'][l]] > min_occupancy) and (fam_prefs[fams_toberescheduled[k]]['choices'][l] != day_costs[j,0]):
                    found = 1
                    temp[temp[:,0] == fams_toberescheduled[k]][0] = fam_prefs[fams_toberescheduled[k]]['choices'][l]
                    occ[fam_prefs[fams_toberescheduled[k]]['choices'][l]] += fam_prefs[fams_toberescheduled[k]]['n_members']
            if found == 0:
                not_scheduled.append(fams_toberescheduled[k])
    for familia in not_scheduled:
        found= 0
        for dia in occ.keys():
            if dia != day_costs[j,0] and found ==0 and occ[dia] > min_occupancy and occ[dia] < max_occupancy - fam_prefs[familia]['n_members']:
                occ[dia] += fam_prefs[familia]['n_members']
                found = 1
                temp[temp[:,0] == fams_toberescheduled[k]][0] = dia
        if found == 0:
            for dia in occ.keys():
                if dia != day_costs[j,0] and found ==0 and occ[dia] < max_occupancy - fam_prefs[familia]['n_members']:
                    occ[dia] += fam_prefs[familia]['n_members']
                    found = 1
                    temp[temp[:,0] == fams_toberescheduled[k]][0] = dia
    total_cost2, fam_costs2, occ2, fam_prefs2, day_cost2 = cost(temp)
    print(total_cost2)
    if total_cost <= total_cost2:
        total_cost = total_cost2
        occ = occ2
        fam_costs = fam_costs2
        #fam_prefs = fam_prefs2
        day_costs = day_cost2
        day_costs = np.asarray([[m,day_costs[m]] for m in day_costs.keys()])
        day_costs.view('i8,i8').sort(order=['f1'], axis=0)
        day_costs = day_costs[::-1]
        start=temp
    print(sum(start - temp))


sched = np.asarray(start, dtype=int)
f = open('sub.csv', 'w')
f.write('family_id,assigned_day\n')
for i in range(len(sched)):
    f.write('{},{}\n'.format(int(sched[i][0]), int(sched[i][1])))
f.close()
