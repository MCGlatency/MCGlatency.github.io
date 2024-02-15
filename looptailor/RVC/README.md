# Remote VSync Coordinator (RVC)

With the informative help of GFI (Game Frame Interceptor), RVC aims to align the remaining 3
VSync events in the MCG interactive loop.

We have extracted relevant source codes of RVC from looper into this folder.
Hierarchical latency prediction is presented in [`hierarchical_forecasting.py`](hierarchical_forecasting.py), and synergetic VSync alignment is shown in [`synergetic_vsync_alignment.py`](synergetic_vsync_alignment.py) and [`sunshine_encoder.cpp`](sunshine_encoder.cpp).