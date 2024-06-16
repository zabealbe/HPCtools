#!/bin/bash

PROJECT_NAME=None
EXPERIMENT_NAME=test-hpctools-as-package
SUBEXPERIMENT_NAME=None

CONFIG_NAMES=(
)



for i in "${!CONFIG_NAMES[@]}"; do
    echo "$i: ${CONFIG_NAMES[$i]}"

    CONFIG_NAME=${CONFIG_NAMES[$i]}

    logdir=runs/None/$CONFIG_NAME

    if [ -d "$logdir" ]; then
        suffix=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 5 | head -n 1)
        logdir=$logdir-$suffix
    fi

    mkdir -p $logdir

    logfile=$logdir/out.log

    

    

    export WANDB_NAME=${CONFIG_NAMES[$SLURM_ARRAY_TASK_ID]}
    echo "WANDB_NAME: $WANDB_NAME" >> $logfile

    CONFIGS=(
    )
    COMMAND=" ${CONFIGS[$SLURM_ARRAY_TASK_ID]}"

    echo "Running $COMMAND" >> $logfile

    eval $COMMAND &>> $logfile

    
done

