import math

def flow_rate_from_beta(beta, D, deltaP, rho, C_eff, epsilon):
    """
    Calcula a vazão volumétrica Q (m³/s) para um dado beta,
    onde d = beta * D e A = π*(d)²/4.
    """
    d = beta * D
    A = math.pi * d**2 / 4.0
    # Cuidado: 1 - beta^4 não pode ser zero; beta está em (0,1)
    Q = C_eff * epsilon * A * math.sqrt(2 * deltaP / (rho * (1 - beta**4)))
    return Q

def find_beta(Q_desired, D, deltaP, rho, C_eff, epsilon, tol=1e-6, max_iter=100):
    """
    Resolve a equação f(beta) = Q(beta) - Q_desired = 0 por bisseção para beta.
    Considera beta no intervalo [0.25, 0.72], faixa típica para dimensionamento.
    """
    beta_min = 0.25
    beta_max = 0.72
    
    f_min = flow_rate_from_beta(beta_min, D, deltaP, rho, C_eff, epsilon) - Q_desired
    f_max = flow_rate_from_beta(beta_max, D, deltaP, rho, C_eff, epsilon) - Q_desired
    
    # Verifica se há mudança de sinal; se não, o Q_desired pode estar fora do alcance
    if f_min * f_max > 0:
        raise ValueError("A vazão desejada não está no intervalo possível para beta entre 0.25 e 0.72.")

    for _ in range(max_iter):
        beta_mid = (beta_min + beta_max) / 2.0
        f_mid = flow_rate_from_beta(beta_mid, D, deltaP, rho, C_eff, epsilon) - Q_desired
        if abs(f_mid) < tol:
            return beta_mid
        if f_min * f_mid < 0:
            beta_max = beta_mid
            f_max = f_mid
        else:
            beta_min = beta_mid
            f_min = f_mid

    return (beta_min + beta_max) / 2.0