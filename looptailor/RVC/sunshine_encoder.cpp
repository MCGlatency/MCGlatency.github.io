#include "express-gpu/egl_surface.h"
#include "express-gpu/egl_display.h"

#include "express-gpu/express_gpu_render.h"
#include "express-enc/sunshine_encoder.h"

#define G_REFRESH_RATE 60.0 // Refresh rate
#define I_c (1000 / G_REFRESH_RATE) // VSync5 interval

/**
 * Synergetic VSync Alignment for VSync4
 * context: the rendering context for the frame
 * frame: the arrival frame
 * cloud_fr: cloud-side frame rate
 * client_fr: client-side frame rate
 * vsync4_t: the next VSync4 timestamp
 * last_enc_t: the timestamp of the last encoded frame
 * arrival_t: the timestamp of the arrival frame
 * next_arrival_t: the timestamp of the next arrival frame, given by the latency prediction 
*/
bool adaptive_frame_encoding(const Opengl_Context *context, const Graphic_Buffer *frame, const float cloud_fr, const float client_fr, const float vsync4_t, const float last_enc_t, const float arrival_t, const float next_arrival_t) {
    if (cloud_fr <= client_fr) {
        return do_encode_frame(frame);
    }
    else {
        if ((arrival_t - last_enc_t >= I_c) || abs(next_arrival_t - vsync4_t) >= abs(arrival_t - vsync4_t)) {
            do_encode_frame(frame)
        }
    }
    return false;
}
