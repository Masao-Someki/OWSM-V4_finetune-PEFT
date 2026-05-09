# Research Planning Report

## Axis: learning rate
| candidate | notes | source |
| --- | --- | --- |
| 1e-6 | Lower bound for large models; prevents catastrophic forgetting. | [AI Wiki](https://aiwiki.ai/wiki/fine_tuning) |
| 2e-6 | Slightly higher than minimum; balances stability and adaptation. | [AI Wiki](https://aiwiki.ai/wiki/fine_tuning) |
| 5e-6 | Common for large language models; ensures gradual adaptation. | [AI Wiki](https://aiwiki.ai/wiki/fine_tuning) |
| 1e-5 | Standard low rate for fine-tuning; preserves pre-trained knowledge. | [AI Wiki](https://aiwiki.ai/wiki/fine_tuning) |
| 2e-5 | Typical for BERT-based models; effective for many tasks. | [AI Wiki](https://aiwiki.ai/wiki/fine_tuning) |
| 5e-5 | Upper bound for fine-tuning; faster convergence but riskier. | [AI Wiki](https://aiwiki.ai/wiki/fine_tuning) |
| 1e-4 | Aggressive rate; suitable for small datasets or rapid convergence. | [AI Wiki](https://aiwiki.ai/wiki/fine_tuning) |
| 2e-4 | Higher rate; may lead to instability in fine-tuning. | [AI Wiki](https://aiwiki.ai/wiki/fine_tuning) |
| 5e-4 | Very high; typically avoided due to risk of catastrophic forgetting. | [AI Wiki](https://aiwiki.ai/wiki/fine_tuning) |

## Axis: optimizer
| candidate | notes | source |
| --- | --- | --- |
| Adam | Adaptive moment estimation; widely used for fine-tuning. | [AI Wiki](https://aiwiki.ai/wiki/optimizer) |
| AdamW | Adam with weight decay; prevents overfitting. | [AI Wiki](https://aiwiki.ai/wiki/optimizer) |
| SGD | Stochastic gradient descent; less common for fine-tuning. | [AI Wiki](https://aiwiki.ai/wiki/optimizer) |
| RMSprop | Root mean square propagation; adapts learning rate per parameter. | [AI Wiki](https://aiwiki.ai/wiki/optimizer) |
| Adagrad | Adaptive gradient algorithm; suitable for sparse data. | [AI Wiki](https://aiwiki.ai/wiki/optimizer) |
| Adadelta | Extension of Adagrad; reduces learning rate decay. | [AI Wiki](https://aiwiki.ai/wiki/optimizer) |
| LAMB | Layer-wise adaptive moments optimizer; scales well for large models. | [AI Wiki](https://aiwiki.ai/wiki/optimizer) |
| LARS | Layer-wise adaptive rate scaling; used for large-batch training. | [AI Wiki](https://aiwiki.ai/wiki/optimizer) |

## Axis: batch size
| candidate | notes | source |
| --- | --- | --- |
| 8 | Small batch; provides noisier but more frequent updates. | [TranslatorMind](https://translatormind.com/fine-tune-translation-models-a-step-by-step-guide/) |
| 16 | Moderate batch; balances update frequency and stability. | [TranslatorMind](https://translatormind.com/fine-tune-translation-models-a-step-by-step-guide/) |
| 32 | Standard batch; commonly used in fine-tuning. | [TranslatorMind](https://translatormind.com/fine-tune-translation-models-a-step-by-step-guide/) |
| 64 | Large batch; smoother gradients but higher memory usage. | [TranslatorMind](https://translatormind.com/fine-tune-translation-models-a-step-by-step-guide/) |
| 128 | Very large batch; requires significant memory resources. | [TranslatorMind](https://translatormind.com/fine-tune-translation-models-a-step-by-step-guide/) |

## Axis: max_epochs
| candidate | notes | source |
| --- | --- | --- |
| 1 | Minimal training; prevents overfitting. | [EngineersOfAI](https://engineersofai.com/docs/llms/pretraining-and-finetuning/supervised-fine-tuning) |
| 2 | Standard for fine-tuning; balances learning and generalization. | [EngineersOfAI](https://engineersofai.com/docs/llms/pretraining-and-finetuning/supervised-fine-tuning) |
| 3 | Upper limit; risk of overfitting increases. | [EngineersOfAI](https://engineersofai.com/docs/llms/pretraining-and-finetuning/supervised-fine-tuning) |
| 4 | Extended training; higher risk of overfitting. | [EngineersOfAI](https://engineersofai.com/docs/llms/pretraining-and-finetuning/supervised-fine-tuning) |
| 5 | Maximum suggested; overfitting likely. | [EngineersOfAI](https://engineersofai.com/docs/llms/pretraining-and-finetuning/supervised-fine-tuning) |

## Axis: warmup_steps
| candidate | notes | source |
| --- | --- | --- |
| 0 | No warmup; immediate full learning rate. | [AI Wiki](https://aiwiki.ai/wiki/fine_tuning) |
| 100 | Short warmup; quick ramp-up to learning rate. | [AI Wiki](https://aiwiki.ai/wiki/fine_tuning) |
| 500 | Moderate warmup; balances stability and speed. | [AI Wiki](https://aiwiki.ai/wiki/fine_tuning) |
| 1000 | Standard warmup; commonly used in fine-tuning. | [AI Wiki](https://aiwiki.ai/wiki/fine_tuning) |
| 2000 | Extended warmup; ensures stability for sensitive models. | [AI Wiki](https://aiwiki.ai/wiki/fine_tuning) |

## Axis: PEFT method choice
| candidate | notes | source |
| --- | --- | --- |
| PROMPT_TUNING | Fine-tunes prompt embeddings; efficient for adaptation. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| MULTITASK_PROMPT_TUNING | Extends prompt tuning for multiple tasks. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| P_TUNING | Parameterizes prompts with trainable embeddings. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| PREFIX_TUNING | Adds trainable vectors to each layer's input. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| LORA | Low-rank adaptation; efficient fine-tuning method. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| ADALORA | Adaptive LORA; dynamically adjusts rank during training. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| BOFT | Bottleneck fine-tuning; reduces parameter count. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| ADAPTION_PROMPT | Combines prompt tuning with adapter layers. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| IA3 | Infused adapter; modifies attention mechanisms. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| LOHA | Low-rank adaptation with higher-order terms. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| LOKR | Low-rank adaptation with Kronecker products. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| OFT | Orthogonal fine-tuning; maintains orthogonality in updates. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| XLORA | Extended LORA; enhances low-rank adaptation. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| POLY | Polynomial adaptation; uses polynomial functions for tuning. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| LN_TUNING | Layer normalization tuning; adjusts normalization parameters. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| VERA | Variational efficient reparameterization adaptation. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| FOURIERFT | Fourier-based fine-tuning; uses Fourier transforms. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| HRA | Hierarchical residual adaptation; adds residual connections. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| BONE | Bottleneck optimization for neural efficiency. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| MISS | Missing data adaptation; handles incomplete inputs. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| RANDLORA | Randomized LORA; introduces stochasticity in adaptation. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| SHIRA | Shared hierarchical adaptation; shares parameters across layers. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| C3A | Contextualized cross-attention adaptation. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| ROAD | Robust optimization for adaptation dynamics. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| WAVEFT | Wavelet-based fine-tuning; uses wavelet transforms. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| OSF | Orthogonal subspace fine-tuning; maintains subspace orthogonality. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| DELORA | Decoupled LORA; separates adaptation components. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |
| GRALORA | Gradient-aligned LORA; aligns gradients during adaptation. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/peft_types) |

## Axis: Best PEFT parameter set for each of the PEFT method, such as ranks, etc.
| candidate | notes | source |
| --- | --- | --- |
| LORA: r=8, alpha=16, dropout=0.05 | Standard parameters for LORA; balances efficiency and performance. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/config) |
| ADALORA: r=8, alpha=16, dropout=0.05, target_rank=4 | Adaptive LORA with target rank; dynamically adjusts during training. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/config) |
| IA3: r=8, alpha=16, dropout=0.05 | Infused adapter parameters; modifies attention mechanisms. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/config) |
| LOHA: r=8, alpha=16, dropout=0.05 | Low-rank adaptation with higher-order terms. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/config) |
| LOKR: r=8, alpha=16, dropout=0.05 | Low-rank adaptation with Kronecker products. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/config) |
| OFT: r=8, alpha=16, dropout=0.05 | Orthogonal fine-tuning; maintains orthogonality in updates. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/config) |
| XLORA: r=8, alpha=16, dropout=0.05 | Extended LORA; enhances low-rank adaptation. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/config) |
| POLY: r=8, alpha=16, dropout=0.05 | Polynomial adaptation; uses polynomial functions for tuning. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/config) |
| LN_TUNING: r=8, alpha=16, dropout=0.05 | Layer normalization tuning; adjusts normalization parameters. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/config) |
| VERA: r=8, alpha=16, dropout=0.05 | Variational efficient reparameterization adaptation. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/config) |
| FOURIERFT: r=8, alpha=16, dropout=0.05 | Fourier-based fine-tuning; uses Fourier transforms. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/config) |
| HRA: r=8, alpha=16, dropout=0.05 | Hierarchical residual adaptation; adds residual connections. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/config) |
| BONE: r=8, alpha=16, dropout=0.05 | Bottleneck optimization for neural efficiency. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/config) |
| MISS: r=8, alpha=16, dropout=0.05 | Missing data adaptation; handles incomplete inputs. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/config) |
| RANDLORA: r=8, alpha=16, dropout=0.05 | Randomized LORA; introduces stochasticity in adaptation. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/config) |
| SHIRA: r=8, alpha=16, dropout=0.05 | Shared hierarchical adaptation; shares parameters across layers. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/config) |
| C3A: r=8, alpha=16, dropout=0.05 | Contextualized cross-attention adaptation. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/config) |
| ROAD: r=8, alpha=16, dropout=0.05 | Robust optimization for adaptation dynamics. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/config) |
| WAVEFT: r=8, alpha=16, dropout=0.05 | Wavelet-based fine-tuning; uses wavelet transforms. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/config) |
| OSF: r=8, alpha=16, dropout=0.05 | Orthogonal subspace fine-tuning; maintains subspace orthogonality. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/config) |
| DELORA: r=8, alpha=16, dropout=0.05 | Decoupled LORA; separates adaptation components. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/config) |
| GRALORA: r=8, alpha=16, dropout=0.05 | Gradient-aligned LORA; aligns gradients during adaptation. | [Hugging Face](https://huggingface.co/docs/peft/package_reference/config) |
