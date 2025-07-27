#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>
#include "platform.h"
#include "vl53l7cx_api.h"
// #include "vl53l7cx_plugin_xtalk.h"

// Define the example1 function if not already defined
int example1(VL53L7CX_Configuration *p_dev);

int main()
{
    VL53L7CX_Configuration Dev;
    int status = 0;

    memset(&Dev, 0, sizeof(VL53L7CX_Configuration));

    // Open I2C communication
    status = vl53l7cx_comms_init(&Dev.platform);
    if (status != 0)
    {
        printf("Failed to initialize I2C communication\n");
        return status;
    }

    // Call example1 function
    status = example1(&Dev);
    if (status != 0)
    {
        printf("example1 failed with status %d\n", status);
    }

    // Close I2C communication
    vl53l7cx_comms_close(&Dev.platform);

    return status;
}

int example1(VL53L7CX_Configuration *p_dev)
{
    int status;
    uint8_t isAlive, isReady;
    uint32_t loop, i;
    VL53L7CX_ResultsData Results; // Results data from VL53L7CX
    // uint8_t xtalk_data[VL53L7CX_XTALK_BUFFER_SIZE]; /* Buffer containing Xtalk data */

    uint32_t integration_time_ms;

    // Arrays to store previous distances and maximum differences
    int32_t previous_distances[64] = {0};
    int32_t max_differences[64] = {0};
    int first_read = 1; // Flag to handle the first read

    // (Optional) Check if there is a VL53L7CX sensor connected
    status = vl53l7cx_is_alive(p_dev, &isAlive);
    if (!isAlive || status)
    {
        printf("VL53L7CX not detected at requested address\n");
        return status;
    }

    // (Mandatory) Init VL53L7CX sensor
    status = vl53l7cx_init(p_dev);

    if (status)
    {
        printf("VL53L7CX ULD Loading failed\n");
        return status;
    }

    printf("VL53L7CX ULD ready! (Version: %s)\n", VL53L7CX_API_REVISION);

    status = vl53l7cx_set_ranging_mode(p_dev, VL53L7CX_RANGING_MODE_CONTINUOUS);
    if (status)
    {
        printf("vl53l7cx_set_ranging_mode failed, status %u\n", status);
        return status;
    }
    // printf("Running Xtalk calibration...\n");

    // status = vl53l7cx_calibrate_xtalk(p_dev, 5, 4, 600);
    // ;
    // if (status)
    // {
    //     printf("vl53l7cx_calibrate_xtalk failed, status %u\n", status);
    //     return status;
    // }
    // else
    // {
    //     printf("Xtalk calibration done\n");

    //     /* Get Xtalk calibration data, in order to use them later */
    //     status = vl53l7cx_get_caldata_xtalk(p_dev, xtalk_data);

    //     /* Set Xtalk calibration data */
    //     status = vl53l7cx_set_caldata_xtalk(p_dev, xtalk_data);
    // }
    status = vl53l7cx_set_ranging_frequency_hz(p_dev, 10);
    if (status)
    {
        printf("vl53l7cx_set_ranging_frequency_hz failed, status %u\n", status);
        return status;
    }

    status = vl53l7cx_set_target_order(p_dev, VL53L7CX_TARGET_ORDER_CLOSEST);
    if (status)
    {
        printf("vl53l7cx_set_target_order failed, status %u\n", status);
        return status;
    }
    status = vl53l7cx_set_resolution(p_dev, VL53L7CX_RESOLUTION_8X8);
    if (status)
    {
        printf("vl53l7cx_set_resolution failed, status %u\n", status);
        return status;
    }

    status = vl53l7cx_set_integration_time_ms(p_dev, 5);
    if (status)
    {
        printf("vl53l7cx_set_integration_time_ms failed, status %u\n", status);
        return status;
    }
    /* Get current integration time */
    status = vl53l7cx_get_integration_time_ms(p_dev, &integration_time_ms);

    if (status)
    {
        printf("vl53l7cx_get_integration_time_ms failed, status %u\n", status);
        return status;
    }
    printf("Current integration time is : %d ms\n", integration_time_ms);

    // Ranging loop
    status = vl53l7cx_start_ranging(p_dev);

    loop = 0;
    while (loop < 10)
    {
        isReady = wait_for_dataready(&p_dev->platform);

        if (isReady)
        {
            vl53l7cx_get_ranging_data(p_dev, &Results);

            // Print data for each zone
            printf("Print data no: %3u\n", p_dev->streamcount);
            for (i = 0; i < 64; i++)
            {
                int32_t current_distance = Results.distance_mm[VL53L7CX_NB_TARGET_PER_ZONE * i];
                int32_t current_status = Results.target_status[VL53L7CX_NB_TARGET_PER_ZONE * i];
                if (!first_read && current_status != 255)
                {
                    int32_t difference = current_distance - previous_distances[i];

                    // Update the maximum difference if the current difference is greater
                    if (abs(difference) > max_differences[i])
                    {
                        max_differences[i] = abs(difference);
                    }
                }

                // Update the previous distance for the next iteration
                previous_distances[i] = current_distance;

                printf("Zone: %3d, Status: %3u, Distance: %4d mm, Max Difference: %4d mm\n",
                       i,
                       current_status,
                       current_distance,
                       max_differences[i]);
            }
            first_read = 0; // Clear the first read flag after the first iteration
            printf("\n");
            loop++;
        }
    }

    status = vl53l7cx_stop_ranging(p_dev);
    printf("End of ULD demo\n");

    return status;
}
