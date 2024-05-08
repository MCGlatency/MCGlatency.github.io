# Frame Trace of MCG-X

We have provided our instrumentation to `AOSP` and `Sunshine/Moonlight` in this folder.

## Instrumentation to `AOSP`
Key instrumentations involve game rendering in [`eglApi.cpp`](eglApi.cpp), and layer composition in [`SurfaceFlinger.cpp`](SurfaceFlinger.cpp).

| File | Instrumented Symbols | Purpose | Location in `AOSP` |
| ---- | ---- | ---- | ---- |
|   [`InputDispatcher.cpp`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/frame_trace/InputDispatcher.cpp)   |   `dispatchOnceInnerLocked`   |   Monitor input injection  | `frameworks/native/services/inputflinger/dispatcher/InputDispatcher.cpp` |
|   [`eglApi.cpp`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/frame_trace/eglApi.cpp)   |   `eglSwapBuffers`   |   Monitor buffer swaps in game rendering  | `frameworks/native/opengl/libs/EGL/eglApi.cpp` |
|   [`egl_platform_entries.cpp`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/frame_trace/egl_platform_entries.cpp)   |   `eglSwapBuffersWithDamageKHRImpl`  |  Monitor buffer swaps in game rendering  | `frameworks/native/opengl/libs/EGL/egl_platform_entries.cpp` |
|   [`MessageQueue.cpp`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/frame_trace/MessageQueue.cpp)   |   `vsyncCallback`, `invalidate`   |   Monitor VSync2  | `frameworks/native/services/surfaceflinger/Scheduler/MessageQueue.cpp` |
|   [`BufferStateLayer.cpp`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/frame_trace/BufferStateLayer.cpp)   |   `setBuffer`, `onLayerDisplayed`   |   Monitor layer creation and display | `frameworks/native/services/surfaceflinger/BufferStateLayer.cpp` |
|   [`sunshine-encode.cpp`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/frame_trace/sunshine-encode.cpp)   |   `encode_avcodec`   |   Monitor frame encodeing | - |
|   [`moonlight-decode.java`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/frame_trace/moonlight-decode.java)   |   `startRendererThread`   |   Monitor frame decoding | - |
|   [`SurfaceFlinger.cpp`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/frame_trace/SurfaceFlinger.cpp)   |   `onMessageInvalidate`,`onMessageRefresh`   |   Monitor layer composition  | `frameworks/native/services/surfaceflinger/SurfaceFlinger.cpp` |
|   [`HWC2.cpp`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/frame_trace/HWC2.cpp)   |   `present`   |   Monitor hardware display  | `frameworks/native/services/surfaceflinger/DisplayHardware/HWC2.cpp` |

## Instrumentation to `Sunshine/Moonlight`
We instrument `Sunshine/Moonlight` to monitor frame encoding and decoding.
| File | Instrumented Symbols | Purpose | Location in `Sunshine/Moonlight` |
| ---- | ---- | ---- | ---- |
|   [`video.cpp`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/frame_trace/video.cpp)   |   `encode_avcodec`   |   Monitor frame encodeing | `Sunshine/src/video.cpp` |
|   [`MediaCodecDecoderRenderer.java`](https://github.com/MCGlatency/MCGlatency.github.io/blob/main/frame_trace/MediaCodecDecoderRenderer.java)   |   `startRendererThread`   |   Monitor frame decoding | `moonlight-android/app/src/main/java/com/limelight/binding/video/MediaCodecDecoderRenderer.java` |