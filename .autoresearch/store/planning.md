# Research Planning Report

## Axis: learning rate
| candidate | notes | source |
| --- | --- | --- |
| 1e-5 | Common lower bound for fine-tuning large models | General practice |
| 3e-5 | Intermediate value | General practice |
| 1e-4 | Default value in base template | conf/base_recipe_template.yaml |
| 3e-4 | Higher value for faster convergence | General practice |
| 1e-3 | Upper bound; may cause instability | General practice |

## Axis: optimizer
| candidate | notes | source |
| --- | --- | --- |
| AdamW | Default optimizer in base template | conf/base_recipe_template.yaml |
| SGD | Stochastic Gradient Descent | General practice |
| RMSprop | Root Mean Square Propagation | General practice |
| Adagrad | Adaptive Gradient Algorithm | General practice |
| Adadelta | Adaptive Delta | General practice |
| Adam | Adaptive Moment Estimation | General practice |
| Nadam | Adam with Nesterov momentum | General practice |

## Axis: batch size
| candidate | notes | source |
| --- | --- | --- |
| 2 | Default value in base template | conf/base_recipe_template.yaml |
| 4 | Small batch size | General practice |
| 8 | Moderate batch size | General practice |
| 16 | Larger batch size; requires more memory | General practice |
| 32 | Even larger batch size; may improve stability | General practice |

## Axis: max_epochs
| candidate | notes | source |
| --- | --- | --- |
| 1 | Default value in base template | conf/base_recipe_template.yaml |
| 3 | Common choice for fine-tuning | General practice |
| 5 | Allows more training; risk of overfitting | General practice |
| 10 | Extended training; higher risk of overfitting | General practice |

## Axis: warmup_steps
| candidate | notes | source |
| --- | --- | --- |
| 0 | Default value in base template | conf/base_recipe_template.yaml |
| 100 | Small warmup period | General practice |
| 500 | Moderate warmup period | General practice |
| 1000 | Longer warmup period | General practice |

## Axis: PEFT method choice
| candidate | notes | source |
| --- | --- | --- |
| PROMPT_TUNING | Prompt tuning method | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| MULTITASK_PROMPT_TUNING | Multitask prompt tuning | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| P_TUNING | P-tuning method | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| PREFIX_TUNING | Prefix tuning method | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| LORA | Low-Rank Adaptation | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| ADALORA | Adaptive LoRA | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| BOFT | Bottleneck Fine-Tuning | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| ADAPTION_PROMPT | Adaption prompt method | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| IA3 | Infused Adapter by Inhibiting and Amplifying Inner Activations | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| LOHA | Low-Rank Adaptation with High-rank Updates | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| LOKR | Low-Rank Adaptation with Kronecker Product | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| OFT | Orthogonal Fine-Tuning | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| XLORA | Extended LoRA | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| POLY | Polynomial Fine-Tuning | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| LN_TUNING | LayerNorm Tuning | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| VERA | Variational Efficient Rank Adaptation | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| FOURIERFT | Fourier Fine-Tuning | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| HRA | High-Rank Adaptation | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| BONE | Bone Fine-Tuning | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| MISS | Missing Data Adaptation | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| RANDLORA | Randomized LoRA | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| SHIRA | Shared Infused Adapter | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| C3A | Cross-layer Cross-attention Adapter | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| ROAD | Robust Optimization-based Adapter | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| WAVEFT | Wavelet Fine-Tuning | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| OSF | Orthogonal Subspace Fine-Tuning | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| DELORA | Decoupled LoRA | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| GRALORA | Gradient-based LoRA | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| ADAMSS | Adaptive Model Selection Strategy | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |

## Axis: Best PEFT parameter set for each of the PEFT method, such as ranks, etc.
| candidate | notes | source |
| --- | --- | --- |
| LORA: r=8, alpha=16, dropout=0.05 | Default parameters in base template | conf/base_recipe_template.yaml |
| LORA: r=4, alpha=8, dropout=0.1 | Alternative configuration | General practice |
| LORA: r=16, alpha=32, dropout=0.01 | Higher rank and alpha values | General practice |
| ADALORA: r=8, alpha=16, dropout=0.05 | Default parameters for AdaLoRA | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| IA3: lambda=0.1 | Default parameter for IA3 | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| PROMPT_TUNING: num_virtual_tokens=20 | Default number of virtual tokens | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| PREFIX_TUNING: num_virtual_tokens=20, prefix_projection=False | Default parameters for prefix tuning | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| P_TUNING: num_virtual_tokens=20, encoder_hidden_size=1280 | Default parameters for p-tuning | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| LOHA: r=8, alpha=16, dropout=0.05 | Default parameters for LoHa | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| LOKR: r=8, alpha=16, dropout=0.05 | Default parameters for LoKr | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| OFT: r=8, alpha=16, dropout=0.05 | Default parameters for OFT | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| XLORA: r=8, alpha=16, dropout=0.05 | Default parameters for XLORA | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| POLY: degree=3, alpha=0.1 | Default parameters for POLY | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| LN_TUNING: num_layers=2, alpha=0.1 | Default parameters for LN_TUNING | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| VERA: r=8, alpha=16, dropout=0.05 | Default parameters for VERA | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| FOURIERFT: r=8, alpha=16, dropout=0.05 | Default parameters for FOURIERFT | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| HRA: r=8, alpha=16, dropout=0.05 | Default parameters for HRA | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| BONE: r=8, alpha=16, dropout=0.05 | Default parameters for BONE | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| MISS: r=8, alpha=16, dropout=0.05 | Default parameters for MISS | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| RANDLORA: r=8, alpha=16, dropout=0.05 | Default parameters for RANDLORA | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| SHIRA: r=8, alpha=16, dropout=0.05 | Default parameters for SHIRA | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| C3A: r=8, alpha=16, dropout=0.05 | Default parameters for C3A | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| ROAD: r=8, alpha=16, dropout=0.05 | Default parameters for ROAD | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| WAVEFT: r=8, alpha=16, dropout=0.05 | Default parameters for WAVEFT | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| OSF: r=8, alpha=16, dropout=0.05 | Default parameters for OSF | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| DELORA: r=8, alpha=16, dropout=0.05 | Default parameters for DELORA | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| GRALORA: r=8, alpha=16, dropout=0.05 | Default parameters for GRALORA | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
| ADAMSS: r=8, alpha=16, dropout=0.05 | Default parameters for ADAMSS | [PEFT types](https://huggingface.co/docs/peft/en/package_reference/peft_types) |
