# Differentiable Mixed-Integer Programming Layers

![Framework](img/pipeline.png)

This project is an implementation of Differentiable Mixed-Integer Programming Layers based on the [NeuroMANCER library](https://github.com/pnnl/neuromancer). It introduces learnable differentiable correction layers for rounding and projection, enabling efficient integer solution acquisition for parametric nonlinear mixed-integer problems through neural networks, thus eliminating the need for traditional mathematical programming solvers.

While inherently heuristic and not guaranteed to find the optimal or even a feasible solution, the framework often provides high-quality feasible solutions that are extremely useful either as alternatives to optimal solutions or as initial solutions for traditional solvers. This capability makes them invaluable tools in complex optimization scenarios where exact methods might struggle or be too slow.

## Features

- **Efficient Solution Acquisition**: The entire solution process relies entirely on neural networks without the need for mathematical programming solvers.

- **Integer Solution Guarantee**: Integrates learnable rounding directly into the network architecture, ensuring that solutions adhere strictly to integer constraints.

## Problem Definition

A generic formulation of a multiparametric mix-integer nonlinear program (pMINLP) is given in the form:

$$
\begin{aligned}
  \underset{\boldsymbol{\Theta}}{\min} \quad & \frac{1}{m} \sum_{i=1}^m f(\mathbf{x}^i_R, \mathbf{x}^i_Z, \boldsymbol{\xi}^i) \\ 
  s.t. \quad & \mathbf{g} (\mathbf{x}^i_R, \mathbf{x}^i_Z, \boldsymbol{\xi}^i) \leq \mathbf{0} \quad \forall i \\ 
  & \mathbf{h} (\mathbf{x}^i_R, \mathbf{x}^i_Z, \boldsymbol{\xi}^i) = \mathbf{0} \quad \forall i \\ 
  & \mathbf{x}^i_R \in \mathbb{R}^{n_r} \quad \forall i \\ 
  & \mathbf{x}^i_Z \in \mathbb{Z}^{n_i} \quad \forall i \\ 
  & [\mathbf{x}^i_R, \mathbf{x}^i_Z] = \boldsymbol{\pi}_{\boldsymbol{\Theta}} (\boldsymbol{\xi}^i) \quad \forall i \\ 
  & \boldsymbol{\xi}^i \in \boldsymbol{\Xi} \subset \mathbb{R}^s \quad \forall i 
\end{aligned}
$$

where $\boldsymbol{\Xi}$ represents the sampled dataset and $\boldsymbol{\xi}^i$ denotes the $i$-th sample. The vector $\mathbf{x}^i_R$ represents the continuous variables, and $\mathbf{x}^i_Z$ represents the integer variables, both of which are involved in minimizing the objective function $f(\cdot)$ while satisfying a set of inequality and equality constraints $\mathbf{g}(\cdot) \leq 0$ and $\mathbf{h}(\cdot) = 0$. The mapping $\boldsymbol{\pi}_{\boldsymbol{\Theta}}(\boldsymbol{\xi}^i)$, given by a deep neural network parametrized by $\Theta$, represents the solution to the optimization problem.


