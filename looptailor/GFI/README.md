# Game Frame Interceptor (GFI)

GFI aims to capture raw frames from game rendering ahead
of time, before any form of layer composition.
GFI is implemented by modifying the [`Trinity`](https://github.com/TrinityEmulator/TrinityEmulator) emulator as well as several guest modules. 

We have provided our modifications to `Trinity` in this folder.
Key changes to the emulator involve the ability to associate OpenGL contexts with game-issued render instructions in [`egl_context.c`](egl_context.c), and in-place game frame capture in [`egl_surface.c`](egl_surface.c).

| File | Added/Changed Symbols | Purpose | Location in `Trinity` |
| ---- | ---- | ---- | ---- |
|   [`egl_context.c`](egl_context.c)   |   `d_eglSetProcName` (added)   |   Provide frame correlations across the virtualization boundary  | `hw/express-gpu/egl_context.c` |
|   [`egl_context.h`](egl_context.h)   |   `FUNID_eglSetProcName`, `PARA_NUM_MIN_eglSetProcName`, `d_eglSetProcName` (added)   |   Function and variable declarations  | `include/express-gpu/egl_context.h` |
|   [`egl_surface.c`](egl_surface.c)   |   `egl_surface_swap_buffer` (changed)  |   Forward frames to encoder in-place  | `hw/express-gpu/egl_surface.c` |
|   [`egl_trans.c`](egl_trans.c)   |   `egl_decode_invoke` (changed)   |   Provide support for frame correlations  | `hw/express-gpu/egl_trans.c` |
|   [`offscreen_render_thread.c`](offscreen_render_thread.c)   |   `get_render_thread_context`, `render_context_destroy` (changed)   |   Variable initialization and de-initialization | `hw/express-gpu/offscreen_render_thread.c` |
|   [`offscreen_render_thread.h`](offscreen_render_thread.h)   |   `struct Process_Context` (changed)   |   Variable Declarations  | `include/express-gpu/offscreen_render_thread.h` |
