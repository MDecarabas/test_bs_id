#!/bin/bash

# Start the bluesky queueserver.


export REDIS_ADDR=localhost
export STARTUP_DIR=$(dirname "${SHELL_SCRIPT_NAME}")
export QS_UPDATE_PLANS_DEVICES=ENVIRONMENT_OPEN
export QS_USER_GROUP_PERMISSIONS_FILE="${SCRIPT_DIR}/src/instrument/config/user_group_permissions.yaml"
export QS_USER_GROUP_PERMISSIONS_RELOAD=ON_STARTUP


# #--------------------

# Start the bluesky queueserver (QS)
start-re-manager \
    --redis-addr "${REDIS_ADDR}" \
    --startup-dir "${STARTUP_DIR}" \
    --update-existing-plans-devices "${QS_UPDATE_PLANS_DEVICES}" \
    --user-group-permissions "${QS_USER_GROUP_PERMISSIONS_FILE}" \
    --user-group-permissions-reload "${QS_USER_GROUP_PERMISSIONS_RELOAD}" \
    --zmq-publish-console ON \
    --keep-re
