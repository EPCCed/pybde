from pybde import BDESolver
import matplotlib.pyplot as plt

def my_two_variable_model(z):
    x1 = 0
    x2 = 1
    tau1 = 0
    tau2 = 1
    return [z[tau1][x2], not z[tau2][x1]]

def main():
    input_times = [0, 1, 1.5]
    input_states = [ [True, True], [True, False], [False, False] ]
    delay_parameters = [ 1, 0.5 ]
    start_time = 2
    end_time = 6

    my_bde_solver = BDESolver(my_two_variable_model, delay_parameters,
                              input_times, input_states)

    result_t, result_y = my_bde_solver.solve(start_time, end_time)

    print("result_t: {}".format(result_t))
    print("result_y = {}".format(result_y))

    my_bde_solver.print_result()

    t_plot_data, y_plot_data = BDESolver.to_plot(result_t, result_y)

    print("t_plot_data = {}".format(t_plot_data))
    print("y_plot_data = {}".format(y_plot_data))

    my_bde_solver.plot_result(variable_names=['x1','x2'])
    plt.show()



if __name__ == "__main__":
    main()
