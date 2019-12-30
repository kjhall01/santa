import numpy as np
import copy
#*README
#***schedule 5000x2 numpy array - [:,0] is family ids, [:,1] is day assigned
#***fams is dict - keys are family ids values are dicts- keys are:
#                   - 'n_members' for number of members
#                   - 'prefs' for 1x10 numpy array of prefferred days


ndays, min_occ, max_occ = 100, 125, 300
days = np.arange(1,ndays+1)
pen_const = [0,50,50,100,200,200,300,300,400,500,500]
pen_term1 = [0,0,9,9,9,18,18,36,36,235,434]

def fam_info(file):
    fam = {}
    data = np.genfromtxt(file, delimiter=',', dtype=int, skip_header=1)
    for i in range(data.shape[0]):
        if data[i,0] not in fam.keys():
            fam[data[i,0]] = {}
        fam[data[i,0]]['n_members'] = data[i,-1]
        fam[data[i,0]]['prefs'] = data[i,1:-1]
    return fam

def occupancy(schedule, fams):
    occ = {k: 0 for k in days}
    for i in range(schedule.shape[0]):
        occ[schedule[i,1]] += fams[schedule[i,0]]['n_members']
    return occ

def cost(schedule, fams):
    t_cost, by_day, by_fam = 0, {k:0 for k in days}, {k:0 for k in fams.keys()}
    for i in range(len(schedule)):
        pref = np.where(fams[schedule[i,0]]['prefs'] == schedule[i,1])
        pref = 10 if len(pref[0]) == 0 else pref[0][0]
        pen = pen_const[pref] + fams[schedule[i,0]]['n_members']*pen_term1[pref]
        t_cost += pen
        by_fam[schedule[i,0]] += pen

    occ = occupancy(schedule, fams)
    for day in occ.keys():
        if occ[day] > max_occ or occ[day] < min_occ:
            t_cost += 1000000
            by_day[day] += 1000000

    accounting_cost = (occ[ndays] - min_occ) / 400.0 * occ[ndays]**0.5
    accounting_cost = max(0, accounting_cost)
    by_day[ndays] += accounting_cost
    for day in occ.keys():
        if day < ndays:
            if occ[day] < occ[day+1]:
                diff = occ[day+1] - occ[day]
            else:
                diff = occ[day] - occ[day+1]
            accounting_cost += max(0, (occ[day] - min_occ) / 400.0 * occ[day]**(0.5 + diff / 50.0))
            by_day[day] += max(0, (occ[day] - min_occ) / 400.0 * occ[day]**(0.5 + diff / 50.0) )
    t_cost += accounting_cost
    return t_cost, by_day, by_fam

def fam_optim(sc, fam_data):
    tc, bd, bf = cost(sc, fam_data)
    print(tc)
    blah = 0
    for fam in fam_data.keys():
        blah += 1
        print(blah)
        #sc2 = np.asarray([[j, np.random.randint(1,100)] for j in range(5000)])
        sc2 = sc.copy()
        for i in range(len(fam_data[fam]['prefs'])):
            sc2[sc2[:,0] == fam, 1] = fam_data[fam]['prefs'][i]
            tc2, bd2, bf2 = cost(sc2, fam_data)
            if tc2 < tc:
                print(tc2)
                tc, bd, bf = tc2, bd2, bf2
                sc = sc2
                break
    return sc

def day_optim(sc, fam_data):
    tc, bd, bf = cost(sc, fam_data)
    print(tc)
    occ = occupancy(sc, fam_data)
    for day in bd.keys():
        print(day)
        temp = sc.copy()
        i, lst_i = 0, 0
        while occ[day] > 125 and i < 5000:
            if temp[i,1] == day:
                lst_i = i
                lst_fam = temp[i,0]
                found = 0
                for oc_day in occ.keys():
                    if found == 0 and occ[oc_day] <= max_occ - fam_data[temp[i,0]]['n_members']:
                        found = 1
                        temp[i,1] = oc_day
                        occ = occupancy(temp, fam_data)
            i += 1
        temp[lst_i, 1] = day
        occ = occupancy(temp, fam_data)

        tc2, bd2, bf2 = cost(temp, fam_data)
        occ2 = occupancy(temp, fam_data)
        if tc2 < tc:
            print(tc2)
            tc, bd, bf, occ = tc2, bd2, bf2, occ2
            sc = temp
    return sc

def fam_day_optim(sc, fam_data, day):
    tc, bd, bf = cost(sc, fam_data)
    occ = occupancy(sc, fam_data)
    #print(day)
    temp = sc.copy()
    b = np.arange(5000)
    np.random.shuffle(b)
    for k in range(temp.shape[0]):
        temp = sc.copy()
        j = b[k]
        if temp[j,1] == day and occ[day] - fam_data[temp[j,0]]['n_members'] >= min_occ:
            #for k in range(len(fam_data[temp[j,0]]['prefs']) - 1, -1, -1):
                #if found==0 and occ[fam_data[temp[j,0]]['prefs'][k]] < max_occ - fam_data[temp[j,0]]['n_members']:
            temp[j,1] = fam_data[temp[j,0]]['prefs'][np.random.randint(10)]
            #occ = occupancy(temp, fam_data)

            tc2, bd2, bf2 = cost(temp, fam_data)
            if tc2 < tc:
                tc, bd, bf = tc2, bd2, bf2
                print(tc)

                #occ = occupancy(temp, fam_data)
                sc = copy.deepcopy(temp)
                temp = sc.copy()

    return sc

fam_data = fam_info('family_data.csv')
#sc = np.asarray([[j, np.random.randint(1,101)] for j in range(5000)])
sc = np.genfromtxt('./sub1.csv', delimiter=',', dtype=int, skip_header=1)

def cool_optim(sc, fam_data):
    buf = 3
    last_mx = [x+1 for x in range(buf)]
    for i in range(400):
        print('{}----------------'.format(i))
        tc, bd, bf = cost(sc, fam_data)

        mx = last_mx


        for key in bd.keys():
            for ndx in range(len(mx)):
                if bd[key] > bd[mx[ndx]]:
                    if key not in mx:
                        for j in range(len(mx)-1, ndx -1, -1):
                            mx[j] = mx[j-1]
                        mx[ndx] = key

        if last_mx == mx and len(last_mx) <100:
            mx.append(1)

        for x in range(len(mx)):
            print('{} - {}'.format(mx[x], bd[mx[x]]))
            sc = fam_day_optim(sc, fam_data, mx[x])

        last_mx = mx
    return sc

    #sc = fam_optim(sc, fam_data)



sc = day_optim(sc, fam_data)


occ = occupancy(sc, fam_data)
for key in occ.keys():
    if occ[key] > max_occ or occ[key] < min_occ:
        print('invalid day: {} - {}'.format(key, occ[key]))

f = open('sub2.csv', 'w')
f.write('family_id,assigned_day\n')
for i in range(sc.shape[0]):
    f.write('{},{}\n'.format(int(sc[i][0]), int(sc[i][1])))
f.close()
