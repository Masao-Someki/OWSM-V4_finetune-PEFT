# Research Planning Report

## Axis: learning rate
| candidate | notes | source |
| --- | --- | --- |
| Constant | Fixed learning rate throughout training. | [IBM](https://www.ibm.com/think/topics/learning-rate) |
| Time-based decay | Learning rate decreases over time, typically inversely proportional to epoch number. | [IBM](https://www.ibm.com/think/topics/learning-rate) |
| Step decay | Learning rate reduces by a factor every N epochs. | [IBM](https://www.ibm.com/think/topics/learning-rate) |
| Exponential decay | Learning rate decreases exponentially after a set number of epochs. | [IBM](https://www.ibm.com/think/topics/learning-rate) |
| Polynomial decay | Learning rate decay determined by a polynomial function of the current epoch. | [IBM](https://www.ibm.com/think/topics/learning-rate) |
| Cosine annealing | Learning rate follows a cosine curve to near-zero. | [Deep Learning Wizard](https://www.deeplearningwizard.com/deep_learning/boosting_models_pytorch/lr_scheduling/) |
| Warmup + decay | Learning rate ramps up for initial steps, then decays. | [Deep Learning Wizard](https://www.deeplearningwizard.com/deep_learning/boosting_models_pytorch/lr_scheduling/) |
| One-cycle | Learning rate increases to a maximum, then decreases, often with momentum cycling. | [Deep Learning Wizard](https://www.deeplearningwizard.com/deep_learning/boosting_models_pytorch/lr_scheduling/) |
| Cyclical learning rate | Learning rate oscillates between a minimum and maximum value. | [IBM](https://www.ibm.com/think/topics/learning-rate) |
| Adaptive learning rate | Learning rate adjusts dynamically based on training progress. | [IBM](https://www.ibm.com/think/topics/learning-rate) |

## Axis: optimizer
| candidate | notes | source |
| --- | --- | --- |
| SGD (Stochastic Gradient Descent) | Basic optimizer updating weights using the gradient of the loss function. | [AI Wiki](https://aiwiki.ai/wiki/optimizer) |
| SGD with momentum | Enhances SGD by adding a fraction of the previous update vector to the current update. | [AI Wiki](https://aiwiki.ai/wiki/optimizer) |
| Nesterov Accelerated Gradient (NAG) | Variant of momentum that adjusts the gradient calculation to anticipate the next position. | [AI Wiki](https://aiwiki.ai/wiki/optimizer) |
| AdaGrad | Adapts learning rates for each parameter, performing larger updates for infrequent parameters. | [AI Wiki](https://aiwiki.ai/wiki/optimizer) |
| RMSProp | Modifies AdaGrad to reduce aggressive, monotonically decreasing learning rates. | [AI Wiki](https://aiwiki.ai/wiki/optimizer) |
| Adadelta | Further refines RMSProp by reducing the need to manually set a learning rate. | [AI Wiki](https://aiwiki.ai/wiki/optimizer) |
| Adam | Combines momentum and RMSProp, adapting learning rates for each parameter. | [AI Wiki](https://aiwiki.ai/wiki/optimizer) |
| AdamW | Variant of Adam that decouples weight decay from the gradient-based update. | [AI Wiki](https://aiwiki.ai/wiki/optimizer) |
| NAdam | Combines Adam and Nesterov momentum. | [AI Wiki](https://aiwiki.ai/wiki/optimizer) |
| RAdam | Rectified Adam, designed to rectify the variance of adaptive learning rate methods. | [AI Wiki](https://aiwiki.ai/wiki/optimizer) |
| Adafactor | Memory-efficient variant of Adam, suitable for large-scale models. | [AI Wiki](https://aiwiki.ai/wiki/optimizer) |

## Axis: batch size
| candidate | notes | source |
| --- | --- | --- |
| Small batch sizes (e.g., 16, 32) | More frequent updates, can lead to noisier gradients but faster convergence. | [Deep Learning Wizard](https://www.deeplearningwizard.com/deep_learning/boosting_models_pytorch/lr_scheduling/) |
| Medium batch sizes (e.g., 64, 128) | Balance between update frequency and gradient stability. | [Deep Learning Wizard](https://www.deeplearningwizard.com/deep_learning/boosting_models_pytorch/lr_scheduling/) |
| Large batch sizes (e.g., 256, 512) | Less frequent updates, more stable gradients, but may require more memory. | [Deep Learning Wizard](https://www.deeplearningwizard.com/deep_learning/boosting_models_pytorch/lr_scheduling/) |

## Axis: max_epochs
| candidate | notes | source |
| --- | --- | --- |
| Fixed number (e.g., 10, 50, 100) | Predefined number of epochs for training. | [Deep Learning Wizard](https://www.deeplearningwizard.com/deep_learning/boosting_models_pytorch/lr_scheduling/) |
| Early stopping | Stop training when validation performance stops improving. | [Deep Learning Wizard](https://www.deeplearningwizard.com/deep_learning/boosting_models_pytorch/lr_scheduling/) |

## Axis: warmup_steps
| candidate | notes | source |
| --- | --- | --- |
| No warmup | Start training with the initial learning rate. | [Deep Learning Wizard](https://www.deeplearningwizard.com/deep_learning/boosting_models_pytorch/lr_scheduling/) |
| Linear warmup | Gradually increase the learning rate linearly over a number of steps. | [Deep Learning Wizard](https://www.deeplearningwizard.com/deep_learning/boosting_models_pytorch/lr_scheduling/) |
| Exponential warmup | Increase the learning rate exponentially over a number of steps. | [Deep Learning Wizard](https://www.deeplearningwizard.com/deep_learning/boosting_models_pytorch/lr_scheduling/) |

## Axis: PEFT method choice
| candidate | notes | source |
| --- | --- | --- |
| LoRA (Low-Rank Adaptation) | Reduces the number of trainable parameters by decomposing weight matrices into low-rank factors. | [Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/index) |
| Prefix Tuning | Adds trainable prefix tokens to the input sequence to adapt the model. | [Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/index) |
| P-Tuning | Similar to prefix tuning but uses continuous embeddings as prompts. | [Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/index) |
| Prompt Tuning | Optimizes soft prompts to guide the model's behavior. | [Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/index) |
| Adapter | Introduces small bottleneck layers into each transformer layer to adapt the model. | [Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/index) |
| BitFit | Fine-tunes only the bias terms of the model. | [Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/index) |

## Axis: Best PEFT parameter set for each PEFT method
| candidate | notes | source |
| --- | --- | --- |
| LoRA: rank | Determines the rank of the low-rank decomposition. | [Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/index) |
| LoRA: alpha | Scaling factor for the low-rank matrices. | [Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/index) |
| LoRA: dropout | Dropout rate applied to the low-rank matrices. | [Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/index) |
| Prefix Tuning: prefix length | Number of prefix tokens added to the input. | [Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/index) |
| P-Tuning: prompt length | Length of the continuous prompt embeddings. | [Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/index) |
| Prompt Tuning: prompt length | Length of the soft prompts. | [Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/index) |
| Adapter: bottleneck size | Size of the bottleneck layer in the adapter. | [Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/index) |
| Adapter: non-linearity | Activation function used in the adapter. | [Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/index) |
| BitFit: bias terms | Selection of bias terms to fine-tune. | [Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/index) |
