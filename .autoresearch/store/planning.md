# Research Planning Report

## Axis: learning rate
| candidate | notes | source |
| --- | --- | --- |
| 1e-5 | Commonly used for fine-tuning transformer models | |
| 2e-5 | Standard learning rate for many NLP tasks | |
| 3e-5 | Often used in ASR tasks for balanced convergence | |
| 5e-5 | Suitable for larger batch sizes | |
| 1e-4 | Higher learning rate for faster convergence; may require careful tuning | |
| 2e-4 | Used in some ASR models for rapid training | |
| 5e-4 | Aggressive learning rate; risk of instability | |
| 1e-3 | High learning rate; typically used with caution | |

## Axis: optimizer
| candidate | notes | source |
| --- | --- | --- |
| AdamW | Standard optimizer with weight decay fix | [Hugging Face Transformers Documentation](https://huggingface.co/docs/transformers/optimizers) |
| AdaFactor | Memory-efficient optimizer suitable for large models | [Hugging Face Transformers Documentation](https://huggingface.co/docs/transformers/optimizers) |
| SGD | Stochastic Gradient Descent; requires careful tuning | [PyTorch Documentation](https://pytorch.org/docs/stable/optim.html) |
| RMSprop | Adaptive learning rate method; often used in RNNs | [PyTorch Documentation](https://pytorch.org/docs/stable/optim.html) |
| Adagrad | Adaptive learning rate method; suitable for sparse data | [PyTorch Documentation](https://pytorch.org/docs/stable/optim.html) |
| APOLLO | Memory-efficient optimizer for full-parameter learning | [Hugging Face Transformers Documentation](https://huggingface.co/docs/transformers/optimizers) |
| GrokAdamW | Optimizer designed for models benefiting from grokking | [Hugging Face Transformers Documentation](https://huggingface.co/docs/transformers/optimizers) |
| LOMO | Low-Memory Optimization for full-parameter fine-tuning | [Hugging Face Transformers Documentation](https://huggingface.co/docs/transformers/optimizers) |
| Schedule Free | Eliminates the need for learning rate annealing | [Hugging Face Transformers Documentation](https://huggingface.co/docs/transformers/optimizers) |
| StableAdamW | Hybrid between AdamW and AdaFactor; removes need for gradient clipping | [Hugging Face Transformers Documentation](https://huggingface.co/docs/transformers/optimizers) |

## Axis: batch size
| candidate | notes | source |
| --- | --- | --- |
| 2 | Suitable for memory-constrained environments | |
| 4 | Commonly used in ASR tasks | |
| 8 | Balances memory usage and training speed | |
| 16 | Requires more memory; faster training | |
| 32 | High batch size; may improve convergence stability | |
| 64 | Large batch size; suitable for powerful hardware | |
| 128 | Very large batch size; may require gradient accumulation | |

## Axis: max_epochs
| candidate | notes | source |
| --- | --- | --- |
| 1 | Useful for quick testing and debugging | |
| 3 | Commonly used for initial training phases | |
| 5 | Balances training time and performance | |
| 10 | Standard for many ASR training routines | |
| 20 | Extended training; may lead to better performance | |
| 50 | Long training; suitable for large datasets | |
| 100 | Very long training; risk of overfitting | |

## Axis: warmup_steps
| candidate | notes | source |
| --- | --- | --- |
| 0 | No warmup; immediate full learning rate | |
| 500 | Short warmup period | |
| 1000 | Commonly used in ASR tasks | |
| 2000 | Extended warmup; stabilizes training | |
| 5000 | Long warmup; suitable for large models | |
| 10000 | Very long warmup; may be excessive | |

## Axis: PEFT method choice
| candidate | notes | source |
| --- | --- | --- |
| LoraConfig | Low-Rank Adaptation | [Hugging Face PEFT Documentation](https://huggingface.co/docs/peft/package_reference/lora) |
| AdaLoraConfig | Adaptive Low-Rank Adaptation | [Hugging Face PEFT Documentation](https://huggingface.co/docs/peft/package_reference/adalora) |
| PrefixTuningConfig | Prefix Tuning | [Hugging Face PEFT Documentation](https://huggingface.co/docs/peft/package_reference/prefix_tuning) |
| PromptTuningConfig | Prompt Tuning | [Hugging Face PEFT Documentation](https://huggingface.co/docs/peft/package_reference/prompt_tuning) |
| PeftType.LORA | Enum for LORA method | [Hugging Face PEFT Documentation](https://huggingface.co/docs/peft/package_reference/peft_types) |
| PeftType.ADALORA | Enum for ADALORA method | [Hugging Face PEFT Documentation](https://huggingface.co/docs/peft/package_reference/peft_types) |
| PeftType.PREFIX_TUNING | Enum for PREFIX_TUNING method | [Hugging Face PEFT Documentation](https://huggingface.co/docs/peft/package_reference/peft_types) |
| PeftType.PROMPT_TUNING | Enum for PROMPT_TUNING method | [Hugging Face PEFT Documentation](https://huggingface.co/docs/peft/package_reference/peft_types) |

## Axis: Best PEFT parameter set for each of the PEFT method, such as ranks, etc.
| candidate | notes | source |
| --- | --- | --- |
| LoraConfig: r=8, alpha=16, dropout=0.05 | Standard configuration for LORA | [Hugging Face PEFT Documentation](https://huggingface.co/docs/peft/package_reference/lora) |
| AdaLoraConfig: r=8, alpha=16, dropout=0.05, target_r=4, init_r=12, beta1=0.85, beta2=0.85, tinit=200, tfinal=1000, deltaT=10 | Standard configuration for ADALORA | [Hugging Face PEFT Documentation](https://huggingface.co/docs/peft/package_reference/adalora) |
| PrefixTuningConfig: num_virtual_tokens=20, encoder_hidden_size=768 | Standard configuration for Prefix Tuning | [Hugging Face PEFT Documentation](https://huggingface.co/docs/peft/package_reference/prefix_tuning) |
| PromptTuningConfig: num_virtual_tokens=20, encoder_hidden_size=768 | Standard configuration for Prompt Tuning | [Hugging Face PEFT Documentation](https://huggingface.co/docs/peft/package_reference/prompt_tuning) |
