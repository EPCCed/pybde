from pybde import BDESolver
from pybde import SwitchPoints
from numpy import genfromtxt
import matplotlib.pyplot as plt

def neurospora_eqns(z, forced_inputs):
    m = 0
    ft = 1
    tau1 = 0
    tau2 = 1
    tau3 = 2

    return [ (not z[tau2][ft]) or forced_inputs[tau3][0], z[tau1][m] ]

# Read in the experiment data from CSV - first column is a, second column is b, third column is time
# Data goes to t=118 hours.
experiment_data = genfromtxt('neur_circ_data_gillespie.csv', delimiter=',')

num_plots = 3

# Plot the data so we can see it
plt.subplot(num_plots,1,1)
plt.plot(experiment_data[:,2], experiment_data[:,0], 'r-', label="a", )
plt.plot(experiment_data[:,2], experiment_data[:,1], 'b-', label="b")
plt.legend()
plt.title("Experiment data")

a_switch_points = SwitchPoints.relative_threshold(experiment_data[:,2], experiment_data[:,0], 0.3)
b_switch_points = SwitchPoints.relative_threshold(experiment_data[:,2], experiment_data[:,1], 0.3)
a_switch_points.label = "a"
b_switch_points.label = "b"
a_switch_points.style = "r-"
b_switch_points.style = "b-"

# Now we need to run a simulation...  Let's take the input up to 24 hours

hist_a = a_switch_points.cut(0, 24)
hist_b = b_switch_points.cut(0, 24)

# Build up forced input

forcing_x = [0, 6] + list(range(18,120,12))
forcing_y = []
for x in forcing_x:
    forcing_y.append(6 <= x % 24 < 18)
light_switch_points = SwitchPoints(forcing_x, forcing_y, 118)
light_switch_points.label = "light"
light_switch_points.style = "-g"

plt.subplot(num_plots,1,2)
plt.title("Simulation input")
SwitchPoints.plot_many([hist_a, hist_b, light_switch_points])
plt.legend()


# Run the simulation
tau1 = 5.0752
tau2 = 6.0211
tau3 = 14.5586
delays = [tau1, tau2, tau3]

solver = BDESolver(neurospora_eqns, delays, [hist_a, hist_b], [light_switch_points])
outputs = solver.solve(118)

# Plot the simulation
plt.subplot(num_plots, 1, 3)
plt.title("Simulation output")
SwitchPoints.plot_many(outputs + [light_switch_points])
plt.xlabel("Time (hours)")
plt.show()

# Calculate hamming distance between simulation and discrete experiment data


print("a.t = {} a.end = {}".format(a_switch_points.t, a_switch_points.end))
print("out0.t = {} out0.end = {}".format(outputs[0].t, outputs[0].end))

num_plots = 2
print("Hamming distance of a : {}".format(a_switch_points.hamming_distance(outputs[0])))
print("Hamming distance of b : {}".format(b_switch_points.hamming_distance(outputs[1])))

# Plot a and sim_a
plt.subplot(num_plots, 1, 1)
plt.title("a and simulation of a")
outputs[0].style = '-c'
outputs[0].label = "sim a"
SwitchPoints.plot_many([a_switch_points, outputs[0]])
plt.legend()

# Plot b and sim_b
plt.subplot(num_plots, 1, 2)
plt.title("b and simulation of b")
outputs[1].style = '-c'
outputs[1].label = "sim b"
SwitchPoints.plot_many([b_switch_points, outputs[1]])
plt.legend()
plt.show()

