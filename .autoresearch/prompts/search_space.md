# Search Space Checklist

- [ ] Ensure all search space axes match `prompt.txt`.
- [ ] Enumerate explicit candidate values for each axis.

## Candidate Values

### Learning Rates (lr)
- [x] 5e-5 (exploitation)
- [x] 3e-5 (exploration)
- [x] 2e-5 (exploration)

### Method Parameters
- param_a
  - [x] 8 (exploitation)
  - [x] 10 (exploration)
  - [x] 12 (exploration)

- param_b
  - [x] 0.05 (exploitation)
  - [x] 0.1 (exploration)
  - [x] 0.15 (exploration)

## Trial Order
1. Config 0 (exploitation)
2. Config 1 (exploration)
3. Config 2 (exploration)

Links to refer for parameter adjustments:
- Learning rate insights from [Best Practices in Hyperparameter Tuning](https://machinelearningmastery.com/grid-search-hyperparameters-deep-learning-models-python-keras/).
- Insights on adapter-like methods can be found in [Understanding Adaptation in Transfer Learning](https://arxiv.org/pdf/2004.05295.pdf).
