## Introduction

Binary Delay Equations (BDEs) can be used to model a variety of problems.  ```pybde``` allows
to you write binary delay equations models in Python and simulate them.

## Install pybde

```pybde``` requires Python 3.5 or above.  

You can install `pybde` using `pip`:

```
pip install pybde
```

## Writing and simulating a model

The first model we will simulate has a single variable and a single delay.  The single equation 
for the model is:

x(t) = NOT x(t-τ)

where x is the model variable, t is time, and τ is the time delay.  In our example τ = 1.

To implement this model we must write a function that when given the state of the model's
variables at each of the time delays returns the state of the model's variables at the current time.
The argument to this function is a list of lists.  If the argument is called `z` then `z[i][j]` contains
the state of the _j_ th variable at the _i_ th delay (note that indexing starts from 0).

So in this case we can write our model in the following function:

```
def my_model(z):
   return [ not z[0][0] ]
```

To simulate this model we must provide:
* the state of the variables at time t=0 and at any other switch points before the start of the simulation,
* the time delays,
* the start time for the simulation, and
* the end time for the simulation.

Our model has only one variable and we will specify its value only at t=0 so the input states and input
times will be:

```
input_states = [ [True] ]
input_times = [ 0 ]
```

We only have a single delay parameter in this model and its value is 1 so the delay_parameters list is:
```
delay_parameters = [ 1 ]
```

The start time of our simulation will be t=1 and the end time will be t=5:
```
start_time = 1
end_time = 5
```

Note that the start time must be greater than or equal to the maximum delay parameter.

Putting this altogether gives:

```
from pybde import BDESolver

def my_model(z):
    return [ not z[0][0] ]

def main():
    input_states = [ [True] ]
    input_times = [ 0 ]
    delay_parameters = [ 1 ]
    start_time = 1
    end_time = 5

    my_bde_solver = BDESolver(my_model, input_times, input_states, delay_parameters)
    my_bde_solver.solve(start_time, end_time)
    my_bde_solver.show_result()

if __name__ == "__main__":
    main()

```

This will display the following plot showing the state of the variable
over the duration of the simulation.

![One variable one delay output](https://github.com/EPCCed/pybde/wiki/images/one_variable_one_delay_output.png)

## Multiple variables and delays

In this example our model will contain two variable and two delays.  The model
equations are:

x1(t) = x2(t-τ1)

x2(t) = NOT x1(t-τ2)

where x1 and x2 are the model variables, t is time, and τ1 and τ2 are the time delays.
In this example example τ1 = 1 and τ2 = 0.5.

We implement this model with the following function.  Note that the first index 
specifies the delay and the second index specifies the variable.  Here we have
explicitly named index variables so the code looks more like the equations
expressed above.

```
def my_two_variable_model(z):
    x1 = 0
    x2 = 1
    tau1 = 0
    tau2 = 1
    return [z[tau1][x2], not z[tau2][x1]]
```

We wish to start the simulation at t=2 with input states until this point as shown below:

[[images/two_variables_input.png]]

So we specify the input times and states as:

```
input_times = [0, 1, 1.5]
input_states = [ [True, True], [True, False], [False, False] ]
```

So the full simulation is run with the following code:

```
from pybde import BDESolver

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
    my_bde_solver.solve(start_time, end_time)
    my_bde_solver.show_result(variable_names=['x1','x2'])

if __name__ == "__main__":
    main()

```

This will display the following plot showing the state of the variables
over the duration of the simulation.  Note how the optional argument
`variable_names` has been passed to the `show_plot` function to specify
the labels for the variables.

[[images/two_variables_output.png]]

## Forcing inputs

Forcing inputs are input variables that must be specified for the whole duration of
the simulation.  These variables' state are not determined by model equations but
can be used within model equations to determine the state of other variables.

As an example of forced inputs consider the following model equations:

x1(t) = 1 if t mod 1 >= 0.5, 0 otherwise   

x2(t) = x1(t-τ)                        

where x1 and x2 are model state variables, t is the time and τ is the delay.
In this case τ is 0.3.

Here we can model x1 as a forcing input as we can define the value of x1 for
the whole duration of the simulation. To specify x1 we must define the
starting state and switch points for the whole simulation.  

For a three second simulation this can be defined as:

```
forcing_times = [ 0, 0.5, 1, 1.5, 2, 2.5, 3 ]
forcing_states = [[False], [True], [False], [True], [False], [True], [False]
```

Given that x1 is a forcing variable the only normal variable will be
x2.  The following code initialised it to `True`:

```
input_times = [0]
input_states = [ [True] ]
```

The inputs to the simulation are shown in the following plot:

[[images/inputs_plot.png]]

When using forcing inputs the state of forcing inputs are the various
time delays is passed to the model function as a second 
argument.  The model function is therefore:

```
def my_forced_input_model(z, forced_inputs):
    tau = 0
    x1 = 0
    return [ forced_inputs[tau][x1] ]
```

To run the simulation is very similar to before except the forcing inputs
must be passed when constructing the ```BDESolver``` object:

```
my_bde_solver = BDESolver(my_forced_input_model, delay_parameters,  
                          input_times, input_states, 
                          forcing_times, forcing_states)
```

The whole code is:

```
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
```


Running this simulation produces the following plots:

[[images/forcing_inputs_output.png]]


## Obtaining the result data

The `solve` method of `BDESolver` returns two lists which contain the switch points 
and variable states.  The fist list contains the times of all switch points (including
the input switch points and also the final time of the simulation).  The second list
contains lists of variable states for each switch time point.

For example, for the two variables and two delays example show above we can obtain
and print the results with code such as:

```
result_t, result_y = my_bde_solver.solve(start_time, end_time)

print("result_t: {}".format(result_t))
print("result_y = {}".format(result_y))
```

This would output:

```
result_t: [0, 1, 1.5, 2, 3, 3.5, 4.5, 5.0, 6.0]
result_y = [[True, True], [True, False], [False, False], [False, True], [True, True], [True, False], [False, False], [False, True], [True, True]]
```

Which corresponds to the following plot:

[[images/two_variables_output.png]]

Another way to print out the result is to use the `print_result` method which will print the
result over multiple lines in a format that may be easier to read.  The following code
does this:

```
    0.00 ->     1.00 : T T 
    1.00 ->     1.50 : T F 
    1.50 ->     2.00 : F F 
    2.00 ->     3.00 : F T 
    3.00 ->     3.50 : T T 
    3.50 ->     4.50 : T F 
    4.50 ->     5.00 : F F 
    5.00 ->     6.00 : F T 
    6.00 ->     6.00 : T T 
```

and produces output like:

```
my_bde_solver.solve(start_time, end_time)
my_bde_solver.print_result()
```

## Plotting results

As show in the above examples the result of a simulation can be plotted using
[`matplotlib`](https://matplotlib.org/) by calling `BSESolver`'s `show_result`
method.

### Plotting the inputs

To show a plot of only the inputs to a simulation so they can be visually
verified before running the simulation call the `show_inputs` method of
the `BDESolver` class:

```
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

    my_bde_solver.show_inputs()

if __name__ == "__main__":
    main()
```

### Saving plots to file

To construct not show the `matplotlib` object you can use the `plot_result` method. This would
allow you to save the plot to file, for example:

```
import matplotlib.pyplot as plt

...

my_bde_solver.solve(start_time, end_time)
my_bde_solver.plot_result()
plt.savefig('my_fig.png')
```


## Convenience functions

`BDESolver` provides a number of convenience functions the may be useful
to users.  These are discussed here.

### `to_plots`

The static `to_plots` method converts switch point data into data suitable
for plotting on graphs. It is used inside the `show_result` and `plot_result`
methods but can also be useful to users who wish to plot results using a
different plotting package or wish to have more control over the configuration
of their plots.  The method takes a list of switch time points and a 
list of lists of variable states at these time points and returns an list
of time values to plot and list of lists with the variable states at these
time points. Essentially, the function just replicates each value in the
lists so as to produce the sharp edge plots required.

For example, using the two variables and two delays example:

```
    my_bde_solver = BDESolver(my_two_variable_model, delay_parameters,
                              input_times, input_states)

    result_t, result_y = my_bde_solver.solve(start_time, end_time)

    print("result_t: {}".format(result_t))
    print("result_y = {}".format(result_y))

    t_plot_data, y_plot_data = BDESolver.to_plot(result_t, result_y)

    print("t_plot_data = {}".format(t_plot_data))
    print("y_plot_data = {}".format(y_plot_data))
```

produces

```
result_t: [0, 1, 1.5, 2, 3, 3.5, 4.5, 5.0, 6.0]
result_y = [[True, True], [True, False], [False, False], [False, True], [True, True], [True, False], [False, False], [False, True], [True, True]]

t_plot_data = [0, 1, 1, 1.5, 1.5, 2, 2, 3, 3, 3.5, 3.5, 4.5, 4.5, 5.0, 5.0, 6.0, 6.0]
y_plot_data = [[True, True], [True, True], [True, False], [True, False], [False, False], [False, False], [False, True], [False, True], [True, True], [True, True], [True, False], [True, False], [False, False], [False, False], [False, True], [False, True], [True, True]]
```

### `to_logical`

The static `to_logical` method can be used to convert a list of 1s and 0s into the
list of `True` and `False`.  When specifying longer input sequences it is often
more readable to use 1s and 0s. For example:

```
input_states = [ [True, True], [True, False], [False, False] ]
```

Can be replaced with

```
input_states = BDESolver.to_logical([[1, 1], [1, 0], [0, 0]]
```

## Logging

`pybde` using Python's [logging library](https://docs.python.org/3/library/logging.html) to provide
some debug logging. For example, the following line can be used to turn own debug logging:

```
import logging

logging.basicConfig(level=logging.DEBUG)
```

## Numerical accuracy

The implementation of `pydbe` has to compare possible switch times generated in 
different ways to see if they are the same time.  For example, is t1+τ2 the timepoint
as t2+τ1. To perform comparisons of floating point numbers `pydbe` uses [`math.isclose`](https://docs.python.org/3.5/library/math.html#math.isclose) function.  This function
defines the acceptable accuracy using the `rel_tol` and `abs_tol` arguments. To specify
non-default values for these arguments you can specify `rel_tol` and `abs_tol` arguments
when constructing the `BDESolver` object.
