// Copyright (c) Acconeer AB, 2019-2021
// All rights reserved
// This file is subject to the terms and conditions defined in the file
// 'LICENSES/license_acconeer.txt', (BSD 3-Clause License) which is part
// of this source code package.

#include <stdbool.h>
#include <stdio.h>

//csv and socket
#include <time.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/time.h>

#include "acc_definitions_common.h"
#include "acc_detector_presence.h"
#include "acc_hal_definitions.h"
#include "acc_hal_integration.h"
#include "acc_integration.h"
#include "acc_rss.h"
#include "acc_version.h"

/** \example example_detector_presence.c
 * @brief This is an example on how the presence detector can be used
 * @n
 * The example executes as follows:
 *   - Activate Radar System Software (RSS)
 *   - Create a presence detector configuration
 *   - Create a presence detector using the previously created configuration
 *   - Destroy the presence detector configuration
 *   - Activate the presence detector
 *   - Get the result and print it 1000 times
 *   - Deactivate and destroy the presence detector
 *   - Deactivate Radar System Software (RSS)
 */

#define DEFAULT_START_M (0.1f)
#define DEFAULT_LENGTH_M (0.7f)
#define DEFAULT_UPDATE_RATE (10)
#define DEFAULT_POWER_SAVE_MODE ACC_POWER_SAVE_MODE_SLEEP
#define DEFAULT_DETECTION_THRESHOLD (2.0f)
#define DEFAULT_NBR_REMOVED_PC (1)
#define DEFAULT_PROFILE (1)
#define DEFAULT_RECEIVER_GAIN (0.5) //default 0.7
#define DEFAULT_HWAAS (5) // Hardware accelerated average samples bigger numbers reduce SNR default is 10

#define PORT 9090

static void update_configuration(acc_detector_presence_configuration_t presence_configuration);

static void print_result(acc_detector_presence_result_t result);

void trigger_camera(void);


int main(int argc, char *argv[]);
void delete_csv(void); // Declare delete_csv with no parameters
bool do_loop(acc_detector_presence_handle_t handle); // Declare do_loop with its parameter


void delete_csv(void) {
    if (remove("output.csv") == 0) {
        printf("File deleted successfully\n");
    } else {
        perror("Failed to delete the file");
    }
}

bool do_loop(acc_detector_presence_handle_t handle){
    bool success = true;
    const int iterations = 100;
    acc_detector_presence_result_t result;
    int i;
    do {
        for (i = 0; i < iterations; i++)
        {
            success = acc_detector_presence_get_next(handle, &result);
            if (!success)
            {
                printf("acc_detector_presence_get_next() failed\n");
                break;
            }

            print_result(result);
            
            acc_integration_sleep_ms(1000 / DEFAULT_UPDATE_RATE);
        }
        if (i == iterations) {
            // This block only executes if the loop completes all iterations without breaking
            delete_csv();
            printf("Restarting the process...\n");
            do_loop(handle);
            // Call main again to restart the process
        }

    }while (i == iterations);
    return success;
}

int main(int argc, char *argv[])
{
    (void)argc;
    (void)argv;
    printf("Acconeer software version %s\n", acc_version_get());

    const acc_hal_t *hal = acc_hal_integration_get_implementation();

    if (!acc_rss_activate(hal))
    {
        printf("Failed to activate RSS\n");
        return EXIT_FAILURE;
    }

    acc_detector_presence_configuration_t presence_configuration = acc_detector_presence_configuration_create();
    if (presence_configuration == NULL)
    {
        printf("Failed to create configuration\n");
        acc_rss_deactivate();
        return EXIT_FAILURE;
    }

    update_configuration(presence_configuration);

    acc_detector_presence_handle_t handle = acc_detector_presence_create(presence_configuration);
    if (handle == NULL)
    {
        printf("Failed to create detector\n");
        acc_detector_presence_configuration_destroy(&presence_configuration);
        acc_rss_deactivate();
        return EXIT_FAILURE;
    }

    acc_detector_presence_configuration_destroy(&presence_configuration);

    if (!acc_detector_presence_activate(handle))
    {
        printf("Failed to activate detector\n");
        acc_detector_presence_destroy(&handle);
        acc_rss_deactivate();
        return EXIT_FAILURE;
    }

    bool success = do_loop(handle);

    

    bool deactivated = acc_detector_presence_deactivate(handle);

    acc_detector_presence_destroy(&handle);

    acc_rss_deactivate();

    if (deactivated && success)
    {
        printf("Application finished OK\n");
        return EXIT_SUCCESS;
    }

    return EXIT_FAILURE;
}

void update_configuration(acc_detector_presence_configuration_t presence_configuration)
{
    acc_detector_presence_configuration_update_rate_set(presence_configuration, DEFAULT_UPDATE_RATE);
    acc_detector_presence_configuration_service_profile_set(presence_configuration, DEFAULT_PROFILE);
    acc_detector_presence_configuration_detection_threshold_set(presence_configuration, DEFAULT_DETECTION_THRESHOLD);
    acc_detector_presence_configuration_start_set(presence_configuration, DEFAULT_START_M);
    acc_detector_presence_configuration_length_set(presence_configuration, DEFAULT_LENGTH_M);
    acc_detector_presence_configuration_power_save_mode_set(presence_configuration, DEFAULT_POWER_SAVE_MODE);
    acc_detector_presence_configuration_nbr_removed_pc_set(presence_configuration, DEFAULT_NBR_REMOVED_PC);
    acc_detector_presence_configuration_receiver_gain_set(presence_configuration, DEFAULT_RECEIVER_GAIN);
    acc_detector_presence_configuration_hw_accelerated_average_samples_set(presence_configuration, DEFAULT_HWAAS);
}

void print_result(acc_detector_presence_result_t result) {
    // Get current time including microseconds
    struct timeval tv;
    gettimeofday(&tv, NULL);
    long long microseconds = ((long long)tv.tv_sec) * 1000000LL + (long long)tv.tv_usec;
    //distance greater than 0; maybe change to or presence score>1100?
    if (result.presence_distance > 0) {
    // if (rand() % 10 < 3) { // uncoment to debug socket
        trigger_camera();
    }

    // Open the file for appending
    FILE *csv_file = fopen("output.csv", "a");
    if (csv_file == NULL) {
        perror("Error opening file");
        return;
    }

    // Print headers if the file is empty
    long file_size;
    fseek(csv_file, 0, SEEK_END);
    file_size = ftell(csv_file);
    if (file_size == 0) {
        fprintf(csv_file, "Presence Score,Presence Distance,Time (Microseconds)\n");
    }

    // Write the presence score, presence distance, and current time to the CSV file in three columns
    fprintf(csv_file, "%d,%d,%lld\n", (int)(result.presence_score * 1000.0f), (int)(result.presence_distance * 1000.0f), microseconds);

    // Close the file
    fclose(csv_file);

    // Print to console for demonstration
    if (result.presence_detected) {
        printf("Motion\n");
    } else {
        printf("No motion\n");
    }

    printf("Presence score: %d, Distance: %d, Time (Microseconds): %lld\n", (int)(result.presence_score * 1000.0f), (int)(result.presence_distance * 1000.0f), microseconds);
}

void trigger_camera(void) {
    int sockfd = 0, valread;
    struct sockaddr_in servaddr;
    printf("sending trigger message");
    // Create socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd == -1) {
        perror("Socket creation failed");
        return;
    }

    // Configure server address
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_LOOPBACK); // Assuming the server is running on localhost
    servaddr.sin_port = htons(PORT); 

    // Connect to server
    if (connect(sockfd, (struct sockaddr *)&servaddr, sizeof(servaddr)) != 0) {
        perror("Socket connection failed");
        close(sockfd);
        return;
    }
    char buffer[1024] = {0};
    // Connection successful, send trigger message to server
    const char *trigger_msg = "trigger_camera";
    if (send(sockfd, trigger_msg, strlen(trigger_msg), 0) == -1) {
        perror("Error sending trigger message");
    }
    valread = read(sockfd, buffer, 1024);
    if (valread == 0) {
        printf("No data received from the server.\n");
    }
    printf("%s\n", buffer);
    // Close socket
    close(sockfd);
}
