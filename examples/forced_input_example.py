from pybde import BDESolver

def my_forced_input_model(z, forced_inputs):
    tau = 0
    x1 = 0
    return [ forced_inputs[tau][x1] ]

def main():
    input_times = [0]
    input_states = [[True]]
    delay_parameters = [ 0.3 ]
    start_time = 0.5
    end_time = 3

    forcing_times = [0, 0.5, 1, 1.5, 2, 2.5, 3]
    forcing_states = [[False], [True], [False], [True], [False], [True], [False]]

    my_bde_solver = BDESolver(my_forced_input_model, delay_parameters,
                              input_times, input_states,
                              forcing_times, forcing_states)
    my_bde_solver.solve(start_time, end_time)

    my_bde_solver.show_result(variable_names=['x2'], forcing_variable_names=['x1'])

if __name__ == "__main__":
    main()
