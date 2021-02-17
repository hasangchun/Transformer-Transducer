# Copyright (c) 2021, Sangchun Ha. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Tuple
from torch import Tensor
from transformer_transducer.mask import get_attn_pad_mask
from transformer_transducer.module import PositionalEncoding
from transformer_transducer.layer import EncoderLayer
import torch
import torch.nn as nn


class AudioEncoder(nn.Module):
    def __init__(
            self,
            device: torch.device,
            input_size: int = 80,
            model_dim: int = 512,
            ff_dim: int = 2048,
            num_layers: int = 18,
            num_heads: int = 8,
            dropout: float = 0.1,
            max_len: int = 5000,
    ) -> None:
        super(AudioEncoder, self).__init__()
        self.device = device
        self.input_size = input_size
        self.model_dim = model_dim
        self.ff_dim = ff_dim
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.input_dropout = nn.Dropout(p=dropout)
        self.layer_norm = nn.LayerNorm(model_dim)
        self.positional_encoding = PositionalEncoding(model_dim, max_len)
        self.input_fc = nn.Linear(input_size, model_dim)
        self.encoder_layers = nn.ModuleList(
            [EncoderLayer(model_dim, ff_dim, num_heads, dropout) for _ in range(num_layers)]
        )

    def forward(
            self,
            inputs: Tensor,
            inputs_lens: Tensor,
    ) -> Tuple[Tensor, Tensor]:
        inputs = inputs.transpose(1, 2)
        seq_len = inputs.size(1)

        self_attn_mask = get_attn_pad_mask(inputs, inputs_lens, seq_len)

        inputs = self.input_fc(inputs) + self.positional_encoding(seq_len)
        outputs = self.input_dropout(inputs)

        for encoder_layer in self.encoder_layers:
            outputs, _ = encoder_layer(outputs, self_attn_mask)

        return outputs, inputs_lens



