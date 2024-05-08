<!-- # Dissecting and Streamlining the Interactive Loop of Mobile Cloud Gaming -->

![license](https://img.shields.io/badge/Platform-Android-green "Android")
![license](https://img.shields.io/badge/Licence-Apache%202.0-blue.svg "Apache")

## Table of Contents
- [Introduction](#introduction)
- [Measurement Results in the Wild](#measurement-results-in-the-wild)
- [Frame Trace of MCG-X](#frame-trace-of-mcg-x)
- [LoopTailor](#looptailor)
    - [Game Frame Interceptor (GFI)](#game-frame-interceptor-gfi)
    - [Remote VSync Coordinator (RVC)](#remote-vsync-coordinator-rvc)

## Introduction

With cloud-side computing and rendering,
    mobile cloud gaming (MCG) is expected to deliver high-quality gaming experiences to budget mobile devices.
However, our measurement on mainstream MCG platforms reveals that even under good network conditions,
    all platforms exhibit high interactive latency of 112-403 ms, from a user-input action to its display response,
    that critically affects users' quality of experience.
Moreover, jitters in network latency often lead to significant fluctuations in interactive latency.

In this work,
    we collaborate with a commercial MCG platform to conduct the first in-depth analysis on the interactive latency of cloud gaming.
We identify VSync, the synchronization primitive of Android graphics pipeline,
    to be a key contributor to the excessive interactive latency;
    as many as five VSync events are intricately invoked,
    which serialize the complex graphics processing logic on both the client and cloud sides.
To address this,
    we design an end-to-end VSync regulator, dubbed LoopTailor,
    which minimizes VSync events by decoupling game rendering from the lengthy cloud-side graphics pipeline and
    coordinating cloud game rendering directly with the client.
We implement LoopTailor on the collaborated platform and commodity Android devices,
    reducing the interactive latency (by ~34%) to stably below 100 ms.

## Measurement Results in the Wild

We have released a portion of our measurement results of the interactive latency of eight mainstream cloud gaming platforms [here](https://github.com/MCGlatency/MCGlatency.github.io/tree/main/data).

### Data Format

The data file is organized in `.csv` format. 

Each row represents the latency from a single user input action, with detailed information described in the table below.


| Column | Description |
| ------ | ----------- |
| interactive latency | The interactive latency (i.e., the delay between a user input action and when the game’s response to that action manifests at the client). |
| network latency | The real-time network latency. |
| non-network latency | The latency with the network latency excluded. |
| network type | The type of radio access technologies (RATs). |
| test time | The time at which the measurement was performed. |
| platform name | The name of the platform, where the '-MCG' suffix represents the MCG part of the platform, while the '-CCG' suffix represents the CCG part of that platform.|
| platform type | The type of the platform, where 'mcg' stands for mobile cloud gaming platform and 'ccg' stands for console cloud gaming platform. |

## Frame Trace of MCG-X

We have released the code for game frame tracing of MCG-X in our [repo](https://github.com/MCGlatency/MCGlatency.github.io/tree/main/frame_trace).
Key instrumentations in `AOSP` involve game rendering in [`eglApi.cpp`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/frame_trace/eglApi.cpp), layer composition in [`SurfaceFlinger.cpp`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/frame_trace/SurfaceFlinger.cpp).

| File | Instrumented Symbols | Purpose | Location in `AOSP` |
| ---- | ---- | ---- | ---- |
|   [`InputDispatcher.cpp`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/frame_trace/InputDispatcher.cpp)   |   `dispatchOnceInnerLocked`   |   Monitor input injection  | `frameworks/native/services/inputflinger/dispatcher/InputDispatcher.cpp` |
|   [`eglApi.cpp`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/frame_trace/eglApi.cpp)   |   `eglSwapBuffers`   |   Monitor buffer swaps in game rendering  | `frameworks/native/opengl/libs/EGL/eglApi.cpp` |
|   [`egl_platform_entries.cpp`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/frame_trace/egl_platform_entries.cpp)   |   `eglSwapBuffersWithDamageKHRImpl`  |  Monitor buffer swaps in game rendering  | `frameworks/native/opengl/libs/EGL/egl_platform_entries.cpp` |
|   [`MessageQueue.cpp`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/frame_trace/MessageQueue.cpp)   |   `vsyncCallback`, `invalidate`   |   Monitor VSync2  | `frameworks/native/services/surfaceflinger/Scheduler/MessageQueue.cpp` |
|   [`BufferStateLayer.cpp`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/frame_trace/BufferStateLayer.cpp)   |   `setBuffer`, `onLayerDisplayed`   |   Monitor layer creation and display | `frameworks/native/services/surfaceflinger/BufferStateLayer.cpp` |
|   [`SurfaceFlinger.cpp`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/frame_trace/SurfaceFlinger.cpp)   |   `onMessageInvalidate`,`onMessageRefresh`   |   Monitor layer composition  | `frameworks/native/services/surfaceflinger/SurfaceFlinger.cpp` |
|   [`HWC2.cpp`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/frame_trace/HWC2.cpp)   |   `present`   |   Monitor hardware display  | `frameworks/native/services/surfaceflinger/DisplayHardware/HWC2.cpp` |

We also instrument `Sunshine/Moonlight` to monitor frame encoding and decoding.

| File | Instrumented Symbols | Purpose | Location in `Sunshine/Moonlight` |
| ---- | ---- | ---- | ---- |
|   [`video.cpp`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/frame_trace/video.cpp)   |   `encode_avcodec`   |   Monitor frame encoding | `Sunshine/src/video.cpp` |
|   [`MediaCodecDecoderRenderer.java`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/frame_trace/MediaCodecDecoderRenderer.java)   |   `startRendererThread`   |   Monitor frame decoding | `moonlight-android/app/src/main/java/com/limelight/binding/video/MediaCodecDecoderRenderer.java` |

## LoopTailor

### Game Frame Interceptor (GFI)

GFI aims to capture raw frames from game rendering ahead
of time, before any form of layer composition.
GFI is implemented by modifying the [`Trinity`](https://github.com/TrinityEmulator/TrinityEmulator) emulator as well as several guest modules. 

We have provided our modifications to `Trinity`.
Key changes to the emulator involve the ability to associate OpenGL contexts with game-issued render instructions in [`egl_context.c`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/looptailor/GFI/egl_context.c), and in-place game frame capture in [`egl_surface.c`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/looptailor/GFI/egl_surface.c).

| File | Added/Changed Symbols | Purpose | Location in `Trinity` |
| ---- | ---- | ---- | ---- |
|   [`egl_context.c`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/looptailor/GFI/egl_context.c)   |   `d_eglSetProcName` (added)   |   Provide frame correlations across the virtualization boundary  | `hw/express-gpu/egl_context.c` |
|   [`egl_context.h`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/looptailor/GFI/egl_context.h)   |   `FUNID_eglSetProcName`, `PARA_NUM_MIN_eglSetProcName`, `d_eglSetProcName` (added)   |   Function and variable declarations  | `include/express-gpu/egl_context.h` |
|   [`egl_surface.c`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/looptailor/GFI/egl_surface.c)   |   `egl_surface_swap_buffer` (changed)  |   Forward frames to encoder in-place  | `hw/express-gpu/egl_surface.c` |
|   [`egl_trans.c`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/looptailor/GFI/egl_trans.c)   |   `egl_decode_invoke` (changed)   |   Provide support for frame correlations  | `hw/express-gpu/egl_trans.c` |
|   [`offscreen_render_thread.c`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/looptailor/GFI/offscreen_render_thread.c)   |   `get_render_thread_context`, `render_context_destroy` (changed)   |   Variable initialization and de-initialization | `hw/express-gpu/offscreen_render_thread.c` |
|   [`offscreen_render_thread.h`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/looptailor/GFI/offscreen_render_thread.h)   |   `struct Process_Context` (changed)   |   Variable Declarations  | `include/express-gpu/offscreen_render_thread.h` |

### Remote VSync Coordinator (RVC)

With the informative help of GFI (Game Frame Interceptor), RVC aims to align the remaining 3
VSync events in the MCG interactive loop.

We have extracted relevant source codes of RVC from looper.
Hierarchical latency prediction is presented in [`hierarchical_forecasting.py`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/looptailor/RVC/hierarchical_forecasting.py), and synergetic VSync alignment is shown in [`synergetic_vsync_alignment.py`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/looptailor/RVC/synergetic_vsync_alignment.py) and [`sunshine_encoder.cpp`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/looptailor/RVC/sunshine_encoder.cpp).
