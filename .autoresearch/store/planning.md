# Research Planning Report

## Axis: learning rate
| candidate | notes | source |
| --- | --- | --- |
| 1e-5 | Commonly used for fine-tuning large models | |
| 3e-5 | Often used in NLP tasks | |
| 5e-5 | Standard for many transformer models | |
| 1e-4 | Default in many configurations | |
| 3e-4 | Used in some ASR tasks | |
| 5e-4 | Higher learning rate for faster convergence | |
| 1e-3 | Suitable for smaller models or initial training | |

## Axis: optimizer
| candidate | notes | source |
| --- | --- | --- |
| SGD | Stochastic Gradient Descent | [PyTorch Optimizers](https://docs.pytorch.org/stable/optim.html) |
| Adam | Adaptive Moment Estimation | [PyTorch Optimizers](https://docs.pytorch.org/stable/optim.html) |
| AdamW | Adam with weight decay correction | [PyTorch Optimizers](https://docs.pytorch.org/stable/optim.html) |
| RMSprop | Root Mean Square Propagation | [PyTorch Optimizers](https://docs.pytorch.org/stable/optim.html) |
| Adagrad | Adaptive Gradient Algorithm | [PyTorch Optimizers](https://docs.pytorch.org/stable/optim.html) |
| Adadelta | Extension of Adagrad to reduce learning rate decay | [PyTorch Optimizers](https://docs.pytorch.org/stable/optim.html) |
| Adamax | Variant of Adam based on infinity norm | [PyTorch Optimizers](https://docs.pytorch.org/stable/optim.html) |
| ASGD | Averaged Stochastic Gradient Descent | [PyTorch Optimizers](https://docs.pytorch.org/stable/optim.html) |
| LBFGS | Limited-memory Broyden–Fletcher–Goldfarb–Shanno algorithm | [PyTorch Optimizers](https://docs.pytorch.org/stable/optim.html) |
| NAdam | Adam with Nesterov momentum | [PyTorch Optimizers](https://docs.pytorch.org/stable/optim.html) |
| RAdam | Rectified Adam | [PyTorch Optimizers](https://docs.pytorch.org/stable/optim.html) |
| Rprop | Resilient backpropagation | [PyTorch Optimizers](https://docs.pytorch.org/stable/optim.html) |

## Axis: batch size
| candidate | notes | source |
| --- | --- | --- |
| 16 | Common for ASR tasks | |
| 32 | Standard in many training setups | |
| 64 | Larger batch size for faster training | |
| 128 | Requires more memory, faster convergence | |
| 256 | High batch size, suitable for large datasets | |

## Axis: max_epochs
| candidate | notes | source |
| --- | --- | --- |
| 10 | Standard for many tasks | |
| 20 | Allows more training for convergence | |
| 30 | Extended training for complex models | |
| 50 | Long training for thorough learning | |
| 100 | Very long training, risk of overfitting | |

## Axis: warmup_steps
| candidate | notes | source |
| --- | --- | --- |
| 0 | No warmup | |
| 500 | Gradual increase in learning rate | |
| 1000 | Common in transformer training | |
| 2000 | Longer warmup for stability | |
| 5000 | Extended warmup for large models | |

## Axis: PEFT method choice
| candidate | notes | source |
| --- | --- | --- |
| PROMPT_TUNING | Fine-tuning by adding prompt vectors | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| MULTITASK_PROMPT_TUNING | Prompt tuning for multiple tasks | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| P_TUNING | Parameter-efficient tuning method | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| PREFIX_TUNING | Adding prefix parameters to model inputs | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| LORA | Low-Rank Adaptation | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| ADALORA | Adaptive LORA | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| BOFT | Bottleneck Fine-Tuning | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| ADAPTION_PROMPT | Adaptation through prompt tuning | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| IA3 | Infused Adapter by Inhibiting and Amplifying Inner Activations | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| LOHA | Low-Rank Orthogonal Adaptation | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| LOKR | Low-Rank Kronecker Adaptation | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| OFT | Orthogonal Fine-Tuning | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| XLORA | Extended LORA | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| POLY | Polynomial Adaptation | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| LN_TUNING | LayerNorm Tuning | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| VERA | Variational Efficient Rank Adaptation | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| FOURIERFT | Fourier Fine-Tuning | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| HRA | Hierarchical Rank Adaptation | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| BONE | Bottleneck Neural Adaptation | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| MISS | Minimalist Subspace Adaptation | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| RANDLORA | Randomized LORA | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| SHIRA | Shared Hierarchical Adaptation | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| C3A | Compact Contextualized Cross-layer Adaptation | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| ROAD | Robust Optimization-based Adaptation | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| WAVEFT | Wavelet-based Fine-Tuning | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| OSF | Orthogonal Subspace Fine-Tuning | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| DELORA | Decoupled LORA | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| GRALORA | Gradient-based LORA | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| ADAMSS | Adaptive Moment Subspace Scaling | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |

## Axis: Best PEFT parameter set for each of the PEFT method
| candidate | notes | source |
| --- | --- | --- |
| PROMPT_TUNING: prompt_length | Length of the prompt vectors | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| MULTITASK_PROMPT_TUNING: prompt_length | Length of the prompt vectors for multitask | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| P_TUNING: prompt_length | Length of the prompt vectors | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| PREFIX_TUNING: prefix_length | Length of the prefix parameters | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| LORA: r, alpha, dropout | Rank, scaling factor, dropout rate | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| ADALORA: r, alpha, dropout | Rank, scaling factor, dropout rate | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| BOFT: bottleneck_size | Size of the bottleneck layer | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| ADAPTION_PROMPT: prompt_length | Length of the adaptation prompt | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| IA3: adapter_dim | Dimension of the adapter | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| LOHA: r, alpha | Rank, scaling factor | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| LOKR: r, alpha | Rank, scaling factor | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| OFT: r, alpha | Rank, scaling factor | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| XLORA: r, alpha, dropout | Rank, scaling factor, dropout rate | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| POLY: degree | Degree of the polynomial | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| LN_TUNING: layer_norm_eps | Epsilon for layer normalization | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| VERA: r, alpha | Rank, scaling factor | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| FOURIERFT: frequency | Frequency parameter | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| HRA: r, alpha | Rank, scaling factor | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| BONE: bottleneck_size | Size of the bottleneck layer | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| MISS: subspace_dim | Dimension of the subspace | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| RANDLORA: r, alpha | Rank, scaling factor | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| SHIRA: r, alpha | Rank, scaling factor | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| C3A: r, alpha | Rank, scaling factor | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| ROAD: r, alpha | Rank, scaling factor | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| WAVEFT: wavelet_level | Level of wavelet decomposition | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| OSF: subspace_dim | Dimension of the subspace | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| DELORA: r, alpha | Rank, scaling factor | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| GRALORA: r, alpha | Rank, scaling factor | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| ADAMSS: r, alpha | Rank, scaling factor | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
