#!/bin/bash

# Configuration: Add your three Stack OCIDs here
STACKS=(
    "ocid1.ormstack.oc1.us-chicago-1.amaaaaaawgku4xaahyb4ps5hgctrwiy6meix6vdy2gcf5xpavzc3c5thkz4a"
    "ocid1.ormstack.oc1.us-chicago-1.amaaaaaawgku4xaahvlwqc5zb6ne2kqkzl365jzeiof2lkrcl45w2pynrw4q"
    "ocid1.ormstack.oc1.us-chicago-1.amaaaaaawgku4xaaeaelytawv46dn5i477lq3kx3irxjhmmevlcvxjprrc6q"
)

# Timing: slower pacing reduces throttling / 429 "Too many requests"
RETRY_DELAY_MIN=180  # Min seconds between full cycles
RETRY_DELAY_MAX=300  # Max seconds; add jitter
INTER_STACK_MIN=120  # Min seconds between trying different stacks (2 min)
INTER_STACK_MAX=180  # Max seconds between stacks (3 min)
INITIAL_POLL=10      # Seconds to wait before first status check
BACKOFF_COOLDOWN=300 # Extra seconds after 3+ consecutive create failures (non-429)
BACKOFF_429=600      # Seconds to back off immediately when 429 TooManyRequests (10 min)

OCI_ERR=$(mktemp)
trap 'rm -f "$OCI_ERR"' EXIT

# Random sleep in [min, max] seconds
rand_sleep() {
    local min=$1 max=$2
    local span=$(( max - min + 1 ))
    local s=$(( min + (RANDOM % span) ))
    echo "  (sleeping ${s}s to reduce throttling risk...)"
    sleep "$s"
}

echo "Starting multi-AD sniper for Chicago (slower pacing to avoid throttling)..."

consecutive_create_failures=0

while true; do
    for i in "${!STACKS[@]}"; do
        STACK_ID="${STACKS[$i]}"
        echo "$(date): Checking AD via Stack: $STACK_ID"

        # Create the apply job — capture stderr so we can see rate limits / real errors
        JOB_ID=$(oci resource-manager job create-apply-job \
            --stack-id "$STACK_ID" \
            --execution-plan-strategy AUTO_APPROVED \
            --query "data.id" --raw-output 2>"$OCI_ERR")

        if [ -z "$JOB_ID" ]; then
            consecutive_create_failures=$(( consecutive_create_failures + 1 ))
            echo "Error initiating job for this stack. OCI output:"
            sed 's/^/  /' < "$OCI_ERR"
            echo "  (consecutive create failures: $consecutive_create_failures)"

            if grep -qE 'TooManyRequests|"status": *429' "$OCI_ERR" 2>/dev/null; then
                echo "429 TooManyRequests detected — backing off ${BACKOFF_429}s, then next cycle."
                sleep "$BACKOFF_429"
                consecutive_create_failures=0
                break
            fi

            if [ "$consecutive_create_failures" -ge 3 ]; then
                echo "Multiple failures in a row — backing off ${BACKOFF_COOLDOWN}s..."
                sleep "$BACKOFF_COOLDOWN"
                consecutive_create_failures=0
            fi
            if [ "$i" -lt $((${#STACKS[@]} - 1)) ]; then
                rand_sleep "$INTER_STACK_MIN" "$INTER_STACK_MAX"
            fi
            continue
        fi

        consecutive_create_failures=0

        # Wait for short duration to see if it moves past 'Accepted'
        sleep "$INITIAL_POLL"

        STATUS=$(oci resource-manager job get --job-id "$JOB_ID" --query "data.\"lifecycle-state\"" --raw-output 2>/dev/null)

        if [ "$STATUS" == "SUCCEEDED" ]; then
            echo "SUCCESS! Instance created in one of the ADs."
            osascript -e 'display notification "Instance Created!" with title "OCI Success"' 2>/dev/null || true
            exit 0
        elif [ "$STATUS" == "IN_PROGRESS" ]; then
            echo "Job is still running... this might be the one! Waiting..."
            STATUS=$(oci resource-manager job wait-for-state --job-id "$JOB_ID" --status SUCCEEDED --status FAILED --query "data.\"lifecycle-state\"" --raw-output 2>/dev/null)
            if [ "$STATUS" == "SUCCEEDED" ]; then
                echo "SUCCESS!"
                exit 0
            fi
        fi

        echo "AD was full. Moving to next AD..."
        if [ "$i" -lt $((${#STACKS[@]} - 1)) ]; then
            rand_sleep "$INTER_STACK_MIN" "$INTER_STACK_MAX"
        fi
    done

    cycle_sleep=$(( RETRY_DELAY_MIN + (RANDOM % (RETRY_DELAY_MAX - RETRY_DELAY_MIN + 1)) ))
    echo "All ADs full. Sleeping ${cycle_sleep}s (jitter) before next full cycle..."
    sleep "$cycle_sleep"
done

