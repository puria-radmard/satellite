from losses import TernausLossFunc
from torch.nn import BCELoss

from perf_metrics import dice_coef

loss_dict = {"BCELoss": BCELoss, "TernausLoss": TernausLossFunc}

test_metric_dict = {"DiceCoefficient": dice_coef}


def isColab():
    try:
        import google.colab

        return True
    except ModuleNotFoundError:
        return False
