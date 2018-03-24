import numpy as np
from timeit import default_timer as timer

filenames = ['1', '2', '3', '4']

# ====================
# === INPUT PARSER ===
# ====================
for filename in filenames:
    start = timer()
    services, countries, tabella, progetti = [[], [], [], []]
    with open("in/{}.in".format(filename)) as f:
        # V = providers, S = services, C = countries, P = projects
        V, S, C, P = map(int, f.readline().split())
        services = f.readline().split()
        countries = f.readline().split()
        # Read providers
        for i in range(V):
            name, number = f.readline().split()
            for j in range(int(number)):
                f.readline()
                mID = int("{}{}".format(i, j))
                tabella.append([mID] + list(map(lambda x: float(x), f.readline().split())) + list(map(lambda x: float(x), f.readline().split())))
        # Read projects
        idProg = 0
        for p in range(P):
            l = list(f.readline().split())
            l[0] = int(l[0])
            l[1] = countries.index(l[1])
            l[2:] = [int(el) for el in l[2:]]
            progetti.append([idProg] + l)
            idProg += 1
    tabella = np.asarray(tabella)
    progetti = np.asarray(progetti)


    # ===================
    # === CALCULATION ===
    # ===================
    output = []
    tBackup = tabella.copy()
    for p in progetti:
        units_needed = p[3:]          # Units needed for project p
        units_allocated = np.zeros(S) # Units allocated to project p
        tempOUT = []
        
        loop = True
        if tabella.size == 0: loop = False
        
        while loop:
            loop = False
            for indexU, u in enumerate(units_needed):
                # If a unit is already satisfied go to the next one
                if u <= units_allocated[indexU] or tabella.size == 0: continue 
            
                col = tabella[:, 3+indexU]
                indexMax = np.argmax(col)
                
                if tabella[indexMax, 1] > 0:
                    tempOUT.append(tabella[indexMax, 0])
                    # Assign the units to the project
                    units_allocated +=  tabella[indexMax, 3:3+S]
                    # Decrease the number of packages available for the provider
                    tabella[indexMax, 1] -= 1
                else:
                    tabella = np.delete(tabella, indexMax, 0)
                    
            # If there is at least one unit not satisfied reloop
            if any(units_allocated < units_needed): loop = True
            # If the table is empty, exit
            if tabella.size == 0: loop = False

        output.append(tempOUT)
        del tempOUT

    output = [sorted(o) for o in output]


    # ==============
    # === OUTPUT ===
    # ==============
    with open("out/{}.out".format(filename), 'w') as f:
        for o1 in output:
            checked = []
            for o2 in o1:
                if o2 not in checked:
                    tot = o1.count(o2)
                    checked.append(o2)
                    if o2 < 10:  
                        f.write("{} {} {} ".format(0, int(o2), tot))
                    else:  
                        f.write("{} {} {} ".format(str(int(o2))[0], str(int(o2))[1], tot))
            f.write("\n")
    print("End file {} in {}".format(filename, timer()-start))