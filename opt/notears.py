import numpy as np
from scipy.linalg import expm
from scipy.optimize import minimize


def h(w):

    return np.trace(expm(w**2)) - w.shape[0]


def f(w, x):
    n, d = x.shape

    w = w.reshape(d, d)
    return 1 / (2 * n) * np.linalg.norm(x - x @ w) ** 2


def augmented_lagrangian(w, x, alpha, rho):
    d = x.shape[1]
    w = w.reshape(d, d)
    return f(w, x) + rho / 2 * h(w) ** 2 + alpha * h(w)


def find_minimum(w_init, x, alpha, rho):
    d = w_init.shape[0]
    w_init = w_init.flatten()
    result = minimize(
        augmented_lagrangian, w_init, args=(x, alpha, rho), method="BFGS"
    )
    # reshape the result to a matrix
    w = result.x.reshape(d, d)

    return w


def optimize(x):
    beta, tol = 10, 1e-6
    d = x.shape[1]
    w = np.zeros((d, d))

    rho, alpha, k = 1, 0, 0
    max_iter = 100
    rho_max = 1e10
    h_w = np.inf

    for i in range(max_iter):
        # solve unconstrained optimization problem
        w = find_minimum(w, x, alpha, rho)
        # update alpha
        alpha = alpha + rho * h(w)
        new_h_w = h(w)
        if new_h_w > h_w / 2:
            rho = beta * rho

        h_w = new_h_w
        # update rho
        print("Iteration:", i, "alpha:", alpha, "rho:", rho)
        # check convergence
        if np.linalg.norm(new_h_w) < tol or rho > rho_max:
            break

    return w


def solve():
    # read data from ata/X.csv
    X = np.loadtxt("data/X.csv", delimiter=",")
    print("X shape:", X.shape)
    W = optimize(X)
    print("W:", W)
    return W


if __name__ == "__main__":
    W1 = np.array(
        [[0, -2, 0.5, 0], [0, 0, 1.5, 0.8], [0, 0, 0, 0], [0, 0, 0, 0]]
    )

    W2 = np.array([[0, 1, 0], [0, 0, 1.5], [0.5, 0, 0]])
    print("h(w1) =", h(W1))
    print("h(w2) =", h(W2))
    testW = np.eye(4)
    print(np.linalg.norm(testW))
    solve()
