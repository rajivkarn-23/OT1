def print_tableau(tableau, basic_vars, variables):
    header = f"{'Basic':<8}" + "".join([f"{v:<8}" for v in variables]) + f"{'RHS':<8}"
    print("-" * len(header))
    print(header)
    print("-" * len(header))
    for i in range(len(basic_vars)):
        row_str = f"{variables[basic_vars[i]]:<8}"
        row_str += "".join([f"{val:<8.2f}" for val in tableau[i][:-1]])
        row_str += f"{tableau[i][-1]:<8.2f}"
        print(row_str)
    
    z_row = f"{'Z-Row':<8}"
    z_row += "".join([f"{val:<8.2f}" for val in tableau[-1][:-1]])
    z_row += f"{tableau[-1][-1]:<8.2f}"
    print(z_row)
    print("-" * len(header) + "\n")

def big_m_simplex():
    print("=== BIG-M SIMPLEX METHOD ===")
    variables = ['x1', 'x2', 's1', 's2', 'A1']
    M = 10000.0
    tableau = [
        [1.0, 1.0, -1.0, 0.0, 1.0, 10.0],
        [2.0, 1.0,  0.0, 1.0, 0.0, 16.0],
        [4.0 - M, 8.0 - M, M, 0.0, 0.0, -10.0 * M]
    ]
    basic_vars = [4, 3]
    iteration = 0
    while True:
        print(f"Iteration {iteration}:")
        print_tableau(tableau, basic_vars, variables)
        
        z_row = tableau[-1][:-1]
        
        if all(coeff >= -1e-5 for coeff in z_row):
            print("Optimality reached! All Z-row coefficients are >= 0.\n")
            break
            
        enter_idx = z_row.index(min(z_row))
        print(f"Entering Variable: {variables[enter_idx]}")
        
        ratios = []
        for i in range(len(basic_vars)):
            if tableau[i][enter_idx] > 0:
                ratios.append(tableau[i][-1] / tableau[i][enter_idx])
            else:
                ratios.append(float('inf'))
                
        if all(r == float('inf') for r in ratios):
            print("Problem is unbounded.")
            return
            
        leave_idx = ratios.index(min(ratios))
        print(f"Leaving Variable: {variables[basic_vars[leave_idx]]}")
        
        pivot = tableau[leave_idx][enter_idx]
        print(f"Pivot Element: {pivot:.2f}\n")
        
        basic_vars[leave_idx] = enter_idx
        
        tableau[leave_idx] = [val / pivot for val in tableau[leave_idx]]
        
        for i in range(len(tableau)):
            if i != leave_idx:
                factor = tableau[i][enter_idx]
                tableau[i] = [tableau[i][j] - factor * tableau[leave_idx][j] for j in range(len(tableau[i]))]
                
        iteration += 1

    print("=== FINAL SOLUTION ===")
    solution = {var: 0 for var in variables}
    for i, b_var in enumerate(basic_vars):
        solution[variables[b_var]] = tableau[i][-1]
        
    for var, val in solution.items():
        print(f"{var} = {val:.2f}")
        
    optimal_z_prime = tableau[-1][-1]
    optimal_cost = -optimal_z_prime 
    print(f"\nMinimum Optimal Cost = {optimal_cost:.2f}")

if __name__ == "__main__":
    big_m_simplex()