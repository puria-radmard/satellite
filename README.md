# Detecting urban heat island morphology using satellite imagery

Originally built with Google Colab
Data download and pre-processing pipeline coming soon

### Running training loop

To run a training loop with set parameters, first set up your directory like this

```
satellite
├── (python files, requirements, run.sh)
├── data
│   └── [dataset name, e.g. dstl]
│       ├── images
│       │   └── (your whole dataset of images, called 0.png, 1.png ... N.png)
│       ├── labels
│       │   └── (your whole dataset of ground truth masks, called 0.png, 1.png ... N.png)
│       ├── boundaries
│       │   └── (your whole dataset of boundary masks, called 0.png, 1.png ... N.png)
│       └── mediaset
│           └── (a set of [for now exactly] 10 images that will make up your media examples in WandB)
├── saves
│   └── [model's dir_name, e.g. "TernausLoss_trial_run"]
│        └── {empty - will get populated with PyTorch saves}
└── media
    └── [model's dir_name]
        └── {empty - will get populated by example images, also on WandB}

```

Then, enter `run.sh` and change the parameters as needed. Example parameters are given, so follow the same data types for each

Finally, run:
```
./run.sh
```
from terminal