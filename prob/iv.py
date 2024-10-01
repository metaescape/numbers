"""
instrumental variable estimation
 
Model:
U = εu; εu ~ N (0, 1)
W = εw; εw ~ N (0, 1)
A = 10U + βwaW + εa; εa ~ N (0, 1)
Y = 2.5U + 7.5A + εy; εy ~ N (0, 1)
"""

import numpy as np
from sklearn.linear_model import LinearRegression

print(f"βwa\t beta_aw \t beta_yw \t beta_yw/beta_aw")
for x in [0.05, 0.5, 5]:
    data = np.genfromtxt(
        f"instrumental_data/samples_{x}.csv", delimiter=" ", skip_header=0
    )

    # print(data.shape)
    # W,A,Y in first,sencond,third column

    # regression of A on W
    reg = LinearRegression().fit(data[:, 0].reshape(-1, 1), data[:, 1])
    beta_aw = reg.coef_

    # regression of Y on W
    reg = LinearRegression().fit(data[:, 0].reshape(-1, 1), data[:, 2])
    beta_yw = reg.coef_

    print(f"{x}\t {beta_aw} \t {beta_yw} \t {beta_yw/beta_aw}")
