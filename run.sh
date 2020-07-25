LOSS_FUNC="ternaus_loss"
LOSS_PARAMETERS="loss_parameters/ternaus_loss.json"
TEST_METRIC="dice_coefficient"
DATASET="data/dstl"
LR="1e-4"
DIR_NAME="ternaus_loss_trial_run"
TEST_SIZE=0.25
TRAIN_SIZE=0.75
BATCH_SIZE=20
DROPOUT=0.5
SAVE_RATE=5
RANDOM_STATE=1
NUM_EPOCHS=20

python train_unet.py \
--loss_func $LOSS_FUNC \
--loss_parameters $LOSS_PARAMETERS \
--test_metric $TEST_METRIC \
--dataset $DATASET \
--lr $LR \
--dir_name $DIR_NAME \
--test_size $TEST_SIZE \
--train_size $TRAIN_SIZE \
--batch_size $BATCH_SIZE \
--dropout $DROPOUT \
--save_rate $SAVE_RATE \
--random_state $RANDOM_STATE \
--num_epochs $NUM_EPOCHS