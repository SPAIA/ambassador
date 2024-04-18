// Copyright (c) Acconeer AB, 2024
// All rights reserved
// This file is subject to the terms and conditions defined in the file
// 'LICENSES/license_acconeer.txt', (BSD 3-Clause License) which is part
// of this source code package.

/**
 * Wrapper module that implements "acc_time.h" with "acc_integration.h"
 */

#include <stdint.h>

#include "acc_integration.h"
#include "acc_time.h"


uint32_t acc_time_get(void)
{
	return acc_integration_get_time();
}
