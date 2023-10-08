#! /bin/bash
VARIANCE_THRESHOLD=0.05
CLASSES=10
PARAM_PATH=./datasets/MVFractalDB/3DIFS_params/MVFractalDB-${CLASSES}
MODEL_SAVE_PATH=./datasets/MVFractalDB/3D-model/MVFractalDB-${CLASSES}
SAVE_ROOT=./datasets/MVFractalDB/images/MVFractalDB-${CLASSES}

cd ./exfractaldb_render

# Parameter search
python 3dfractal_render/category_search.py --variance ${VARIANCE_THRESHOLD} --numof_classes ${CLASSES} --save_root ../${PARAM_PATH}

# Generate 3D fractal model
python 3dfractal_render/instance.py --load_root ../${PARAM_PATH} --save_root ../${MODEL_SAVE_PATH} --classes ${CLASSES}

# Multi-view images render
python image_render/render.py --load_root ../${MODEL_SAVE_PATH} --save_root ../${SAVE_ROOT}

cd ../

# MV-FractalDB Pre-training

# model size
MODEL=tiny
# initial learning rate
LR=1.0e-3
# name of dataset
DATA_NAME=ExFractalDB
# num of epochs
EPOCHS=2
# path to train dataset
SOURCE_DATASET=${SAVE_ROOT}
# output dir path
OUT_DIR=./cheak_points/${MODEL}/${CLASSES}/pretrain
# num of GPUs
NGPUS=4
# num of processes per node
NPERNODE=4
# local mini-batch size (global mini-batch size = NGPUS × LOCAL_BS)
LOCAL_BS=64

# environment variable which is the IP address of the machine in rank 0 (need only for multiple nodes)
# MASTER_ADDR="192.168.1.1"

mpirun -npernode ${NPERNODE} -np ${NGPUS} \
python pretrain.py ${SOURCE_DATASET} \
    --model deit_${MODEL}_patch16_224 --experiment pretrain_deit_${MODEL}_${DATA_NAME}${CLASSES}_${LR} \
    --input-size 3 224 224 \
    --sched cosine_iter --epochs ${EPOCHS} --lr ${LR} --weight-decay 0.05 \
    --batch-size ${LOCAL_BS} --opt adamw --num-classes ${CLASSES} \
    --warmup-epochs 5 --cooldown-epochs 0 \
    --smoothing 0.1 --drop-path 0.1 --aa rand-m9-mstd0.5-inc1 \
    --repeated-aug --mixup 0.8 --cutmix 1.0 --reprob 0.25 \
    --remode pixel --interpolation bicubic --hflip 0.0 \
    -j 16 --eval-metric loss \
    --interval-saved-epochs 10 --output ${OUT_DIR}
    # --log-wandb

# MV-FractalDB Fine-training

# ======== parameter for pre-trained model ========
# initial learning rate for pre-train
PRE_LR=1.0e-3
# name of dataset for pre-train
PRE_DATA_NAME=ExFractalDB
# num of classes for pre-train
PRE_CLASSES=10
# path to checkpoint of pre-trained model
CP_PATH=${OUT_DIR}/pretrain_deit_${MODEL}_${PRE_DATA_NAME}${PRE_CLASSES}_${PRE_LR}/model_best.pth.tar

# ======== parameter for fine-tuning ========
# output dir path
OUT_DIR=./cheak_points/${MODEL}/${CLASSES}/finetune
# path to fine-tune dataset
SOURCE_DATASET_DIR=/groups/gcd50691/datasets/cifar10
# name of dataset
DATA_NAME=CIFAR10
# initial learning rate
LR=1.0e-3
# num of classes
CLASSES=10
# num of epochs
EPOCHS=2
# num of GPUs
NGPUS=4
# num of processes per node
NPERNODE=4
# local mini-batch size (global mini-batch size = NGPUS × LOCAL_BS)
LOCAL_BS=64

mpirun -npernode ${NPERNODE} -np ${NGPUS} \
python finetune.py ${SOURCE_DATASET_DIR} \
    --model deit_${MODEL}_patch16_224 --experiment finetune_deit_${MODEL}_${DATA_NAME}_from_${PRE_DATA_NAME}${PRE_CLASSES}_${PRE_LR} \
    --input-size 3 224 224 --num-classes ${CLASSES} \
    --sched cosine_iter --epochs ${EPOCHS} --lr ${LR} --weight-decay 0.05 \
    --batch-size ${LOCAL_BS} --opt adamw \
    --warmup-epochs 5 --cooldown-epochs 0 \
    --smoothing 0.1 --aa rand-m9-mstd0.5-inc1 \
    --repeated-aug --mixup 0.8 --cutmix 1.0 \
    -j 16 \
    --output ${OUT_DIR} \
    --pretrained-path ${CP_PATH}
