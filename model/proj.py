from neuromancer.modules.solvers import GradientProjection

if __name__ == "__main__":

    import numpy as np
    import torch
    from torch import nn
    import neuromancer as nm

    from problem.solver import exactQuadratic
    from model import roundModel, roundGumbelModel
    from utlis import test

    # random seed
    np.random.seed(42)
    torch.manual_seed(42)

    # init
    num_data = 5000   # number of data
    num_vars = 10     # number of decision variables
    num_ints = 5      # number of integer decision variables
    test_size = 1000  # number of test size
    val_size = 1000   # number of validation size

    # exact optimization model
    model = exactQuadratic(n_vars=num_vars, n_integers=num_ints)

    # get datasets
    from data import getDatasetQradratic
    data_train, data_test, data_dev = getDatasetQradratic(num_data=num_data, num_vars=num_vars,
                                                          test_size=test_size, val_size=val_size)

    # torch dataloaders
    from torch.utils.data import DataLoader
    loader_train = DataLoader(data_train, batch_size=32, num_workers=0, collate_fn=data_train.collate_fn, shuffle=True)
    loader_test = DataLoader(data_test, batch_size=32, num_workers=0, collate_fn=data_test.collate_fn, shuffle=True)
    loader_dev = DataLoader(data_dev, batch_size=32, num_workers=0, collate_fn=data_dev.collate_fn, shuffle=True)

    # parameters
    p = nm.constraint.variable("p")
    # variables
    x_bar = nm.constraint.variable("x_bar")
    x_rnd = nm.constraint.variable("x_rnd")
    # model
    from problem.neural import probQuadratic
    obj_bar, constrs_bar = probQuadratic(x_bar, p, num_vars=10, alpha=100)
    obj_rnd, constrs_rnd = probQuadratic(x_rnd, p, num_vars=10, alpha=100)

    # define neural architecture for the solution mapping
    func = nm.modules.blocks.MLP(insize=num_vars, outsize=num_vars, bias=True,
                                 linear_map=nm.slim.maps["linear"], nonlin=nn.ReLU, hsizes=[80]*4)
    # solution map from model parameters: sol_map(p) -> x
    sol_map = nm.system.Node(func, ["p"], ["x_bar"], name="smap")

    # round x
    #round_func = roundModel(param_key="p", var_key="x_bar", output_keys="x_rnd",
    #                        int_ind=model.intInd, input_dim=num_vars*2, hidden_dims=[80]*2, output_dim=num_vars,
    #                        name="round")
    round_func = roundGumbelModel(param_key="p", var_key="x_bar", output_keys="x_rnd",
                                  int_ind=model.intInd, input_dim=num_vars*2, hidden_dims=[80]*2, output_dim=num_vars,
                                  name="round")

    # proj x to feasible region
    num_steps = 5
    step_size = 0.1
    decay = 0.1
    proj = GradientProjection(constraints=constrs_bar,  # inequality constraints to be corrected
                              input_keys=["x_bar"],  # primal variables to be updated
                              #output_keys = ["x_bar"], # updated primal variables
                              num_steps=num_steps,  # number of rollout steps of the solver method
                              step_size=step_size,  # step size of the solver method
                              decay=decay,  # decay factor of the step size
                              name="proj")

    # trainable components
    components = [sol_map, proj, round_func]

    # penalty loss
    #loss = nm.loss.PenaltyLoss(obj_bar, constrs_bar) + 0.5 * nm.loss.PenaltyLoss(obj_rnd, constrs_rnd)
    loss = nm.loss.PenaltyLoss(obj_rnd, constrs_rnd)
    problem = nm.problem.Problem(components, loss, grad_inference=True)

    # training
    lr = 0.001    # step size for gradient descent
    epochs = 400  # number of training epochs
    warmup = 50   # number of epochs to wait before enacting early stopping policy
    patience = 50 # number of epochs with no improvement in eval metric to allow before early stopping
    # set adamW as optimizer
    optimizer = torch.optim.AdamW(problem.parameters(), lr=lr)
    # define trainer
    trainer = nm.trainer.Trainer(problem, loader_train, loader_dev, loader_test,
                                 optimizer, epochs=epochs, patience=patience, warmup=warmup)
    best_model = trainer.train()
    print()

    # params
    p = np.random.uniform(1, 11, (3, num_vars))
    print("Parameters p:", list(p[0]))
    print()


    # get solution from neuroMANCER
    print("neuroMANCER:")
    datapoints = {"p": torch.tensor(p, dtype=torch.float32),
                  "name": "test"}
    test.nmTest(problem, datapoints, model, x_name="test_x_rnd")

    # get solution from Ipopt
    print("SCIP:")
    model.setParamValue(*p[0])
    test.solverTest(model, solver="scip")