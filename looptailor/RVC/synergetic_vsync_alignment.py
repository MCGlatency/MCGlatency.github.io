import numpy as np
import math

# Parameters
n = 60 # Forecast horizon
G_REFRESH_RATE = 60 # Refresh rate
I_c = 1000 / G_REFRESH_RATE # VSync5 interval
SAMPLE_PACE = 0.1 # ms

# Synergetic VSync Alignment for VSync1
# V_c: the timestamp of the most recent VSync5 event in the client
# cv: cloud-side VSync1 timing
# x: predicted timestamps when the client finishes frame decoding
def postpone_vsync1(V_c, cv, x):

    # Calculating client-side VSync5 timestamps
    v = []
    for i in range(n):
        vi = V_c + (1 + math.floor((x[i] - V_c) / I_c))
        v.append(vi)
    v = np.asarray(v)

    def ts_to_interval(t: float, time_base=I_c):
        while t < 0:
            t += time_base
        while t >= time_base:
            t -= time_base
        return t

    # Main loop
    for i in range(n):

        # Calculate expectation
        preds_rel = [ts_to_interval(v[i] - x[i]) for i in range(n)]  # time that a frame needs to wait
        preds_rel_sum = sum(preds_rel)
        best_delta = 0  # Best choice of rendering delay
        best_error = 0  # The smaller the better. if < 0, best_delta is feasible
        # Monte Carlo sampling
        for delta in np.arange(0, I_c, SAMPLE_PACE):
            error = sum([ts_to_interval(p - delta) for p in preds_rel]) - preds_rel_sum
            if error < best_error:
                best_delta = delta
                best_error = error

        if best_error < 0:
            cv += max(0, best_delta)

            if best_delta > 0:
                return best_delta

        else:
            print(f"warning! prediction failed at frame {i} in current iteration!")

    return 0
