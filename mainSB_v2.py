import numpy as np
from timeit import default_timer as timer

filenames = ['1', '2', '3', '4']
LOOPS = 5000

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
                tabella.append([i] + [j] + list(map(lambda x: float(x), f.readline().split())) + list(map(lambda x: float(x), f.readline().split())))
        # Read projects
        idProg = 0
        for p in range(P):
            line = list(f.readline().split())
            line[0] = int(line[0])
            line[1] = countries.index(line[1])
            line[2:] = [int(l) for l in line[2:]]
            progetti.append([idProg] + line)
            idProg += 1
    tabella = np.asarray(tabella)
    progetti = np.asarray(progetti)
    
    
    # ===================
    # === CALCULATION ===
    # ===================
    output = []
    for p in progetti:
        units_needed = p[3:]          # Units needed for project p
        units_allocated = np.zeros(S) # Units allocated to project p
        tempOUT = []
        
        loop = True
        tBackup = tabella.copy()
        count = 0 # number of times looped
        
        while loop and count < LOOPS and tabella.size > 0:
            loop = False
            
            diff = units_needed - units_allocated
            if any(diff > 0):
                indexU = np.argmax(diff)
                
                col = tabella[:, 4+indexU]
                indexMax = np.argmax(col) 
                
                tempOUT.append("{} {}".format(int(tabella[indexMax, 0]), int(tabella[indexMax, 1])))
                # Assign the units to the project
                units_allocated += tabella[indexMax, 4:4+S]
                # Decrease the number of packages available for the provider
                tabella[indexMax, 2] -= 1
                
                if tabella[indexMax, 2] == 0: tabella = np.delete(tabella, indexMax, 0)
                if tabella.size == 0: break
                    
            # If there is at least one unit not satisfied reloop
            if any(units_allocated < units_needed): 
                loop = True
                count += 1
    
        output.append(tempOUT)
        del tempOUT
    
    output = [sorted(o) for o in output]
    print("Calc for {} done.".format(filename))
    
    
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
                    f.write("{} {} ".format(o2, tot))
            f.write("\n")
    print("End file {} in {}".format(filename, timer()-start))
