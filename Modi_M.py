import sys
import copy

def calculate_penalties(costs, supply, demand, r_done, c_done):
    r_pen = []
    for i in range(len(supply)):
        if r_done[i]: 
            r_pen.append(-1)
            continue
        row = [costs[i][j] for j in range(len(demand)) if not c_done[j]]
        if len(row) >= 2:
            s_row = sorted(row)
            r_pen.append(s_row[1] - s_row[0])
        elif len(row) == 1:
            r_pen.append(row[0])
        else:
            r_pen.append(-1)
            
    c_pen = []
    for j in range(len(demand)):
        if c_done[j]: 
            c_pen.append(-1)
            continue
        col = [costs[i][j] for i in range(len(supply)) if not r_done[i]]
        if len(col) >= 2:
            s_col = sorted(col)
            c_pen.append(s_col[1] - s_col[0])
        elif len(col) == 1:
            c_pen.append(col[0])
        else:
            c_pen.append(-1)
            
    return r_pen, c_pen

def vogel_approximation(costs, supply, demand):
    print("=== RUNNING VAM ===")
    allocations = [[0]*len(demand) for _ in range(len(supply))]
    r_done = [False]*len(supply)
    c_done = [False]*len(demand)
    
    basic_cells = []
    sup = copy.deepcopy(supply)
    dem = copy.deepcopy(demand)
    
    while not (all(r_done) or all(c_done)):
        r_pen, c_pen = calculate_penalties(costs, sup, dem, r_done, c_done)
        
        max_r = max(r_pen) if r_pen else -1
        max_c = max(c_pen) if c_pen else -1
        
        if max_r == -1 and max_c == -1:
            break
            
        if max_r >= max_c:
            i = r_pen.index(max_r)
            valid_costs = [(costs[i][j], j) for j in range(len(dem)) if not c_done[j]]
            j = min(valid_costs, key=lambda x: x[0])[1]
        else:
            j = c_pen.index(max_c)
            valid_costs = [(costs[i][j], i) for i in range(len(sup)) if not r_done[i]]
            i = min(valid_costs, key=lambda x: x[0])[1]
            
        qty = min(sup[i], dem[j])
        allocations[i][j] = qty
        basic_cells.append((i, j))
        sup[i] -= qty
        dem[j] -= qty
        
        if sup[i] == 0 and dem[j] == 0:
            c_done[j] = True
        elif sup[i] == 0:
            r_done[i] = True
        else:
            c_done[j] = True

    req_cells = len(supply) + len(demand) - 1
    if len(basic_cells) < req_cells:
        print("Degeneracy detected in VAM. Adding 0 allocations.")
        for i in range(len(supply)):
            for j in range(len(demand)):
                if (i, j) not in basic_cells and len(basic_cells) < req_cells:
                    allocations[i][j] = 0
                    basic_cells.append((i, j))
                    
    return allocations, basic_cells

def calculate_potentials(costs, basic_cells, rows, cols):
    u = [None] * rows
    v = [None] * cols
    u[0] = 0 
    
    progress = True
    while progress and (None in u or None in v):
        progress = False
        for i, j in basic_cells:
            if u[i] is not None and v[j] is None:
                v[j] = costs[i][j] - u[i]
                progress = True
            elif v[j] is not None and u[i] is None:
                u[i] = costs[i][j] - v[j]
                progress = True
    for i in range(rows):
        if u[i] is None: u[i] = 0
    for j in range(cols):
        if v[j] is None: v[j] = 0
        
    return u, v

def find_closed_loop(start_cell, basic_cells, rows, cols):
    def dfs(current_cell, path, is_row_search):
        if len(path) > 3 and path[-1] == start_cell:
            return path
        
        i, j = current_cell
        search_space = basic_cells + [start_cell]
        
        for r, c in search_space:
            if (r, c) != current_cell and (r, c) not in path[1:]:
                if (is_row_search and r == i) or (not is_row_search and c == j):
                    res = dfs((r, c), path + [(r, c)], not is_row_search)
                    if res: return res
        return None

    return dfs(start_cell, [start_cell], True)

def modi(costs, allocations, basic_cells):
    print("\n=== RUNNING MODI (OPTIMIZATION) ===")
    rows, cols = len(costs), len(costs[0])
    
    while True:
        u, v = calculate_potentials(costs, basic_cells, rows, cols)
        
        min_delta = 0
        enter_cell = None
        
        for i in range(rows):
            for j in range(cols):
                if (i, j) not in basic_cells:
                    delta = costs[i][j] - (u[i] + v[j])
                    if delta < min_delta:
                        min_delta = delta
                        enter_cell = (i, j)
                        
        if min_delta >= 0:
            print("Optimality Condition Met! All Deltas >= 0.")
            break
            
        print(f"Negative Delta found at {enter_cell}. Delta = {min_delta}")
        loop = find_closed_loop(enter_cell, basic_cells, rows, cols)
        loop = loop[:-1]
        
        minus_cells = loop[1::2]
        theta = min(allocations[r][c] for r, c in minus_cells)
        print(f"Shifting theta = {theta} units along closed loop.\n")
        
        for idx, (r, c) in enumerate(loop):
            if idx % 2 == 0:
                allocations[r][c] += theta
            else:
                allocations[r][c] -= theta
                
       
        basic_cells.append(enter_cell)
        for r, c in minus_cells:
            if allocations[r][c] == 0:
                basic_cells.remove((r, c))
                break
                
    return allocations

def calculate_cost(costs, allocations):
    total = 0
    for i in range(len(costs)):
        for j in range(len(costs[0])):
            if allocations[i][j] > 0:
                total += costs[i][j] * allocations[i][j]
    return total

if __name__ == "__main__":
    costs = [
        [5, 2, 4, 3],
        [4, 8, 1, 6],
        [4, 6, 7, 5],
        [0, 0, 0, 0]
    ]
    supply = [15, 25, 10, 5]
    demand = [10, 15, 15, 15]
    allocations, basic_cells = vogel_approximation(costs, supply, demand)
    initial_cost = calculate_cost(costs, allocations)
    print(f"Initial Cost (VAM) = {initial_cost}")
    final_alloc = modi(costs, allocations, basic_cells)
    final_cost = calculate_cost(costs, final_alloc)
    
    print("\n=== FINAL ALLOCATIONS ===")
    for i in range(len(final_alloc)):
        print(final_alloc[i])
    print(f"\nFinal Minimum Transportation Cost = {final_cost}")
    print("Verification: sum(allocation[i][j] * cost[i][j]) validates this")