import torch
from torch import nn
from torch.nn.utils.parametrizations import spectral_norm

from src.utils import init_weights

class CDModel(nn.Module):
    def __init__(self, in_features: int, label_num: int):
        super().__init__()
        self.main_model = nn.Sequential(
            # 3 * 32 * 32
            spectral_norm(nn.Conv2d(1, 16, 4, 2, 1)),
            nn.LeakyReLU(0.2),
            # 16 * 16 * 16
            #spectral_norm(nn.Conv2d(16, 32, 4, 2, 1)),
            #nn.LeakyReLU(0.2),
            # 32 * 8 * 8r
            spectral_norm(nn.Conv2d(16, 32, 4, 2, 1)),
            nn.LeakyReLU(0.2),
            # 64 * 4 * 4
            spectral_norm(nn.Conv2d(32, 64, 4, 1, 0)),
            # 128 * 1 * 1
            nn.LeakyReLU(0.2),
        )
        self.hidden_status: torch.Tensor = None
        self.c_last_layer = nn.Sequential(
            nn.Linear(64, label_num),
            #nn.Softmax(dim=1),
        )
        self.d_last_layer = nn.Sequential(
            spectral_norm(nn.Linear(64, 1)),
        )
        self.apply(init_weights)

    def forward(self, x: torch.Tensor):
    #-> tuple[torch.Tensor, torch.Tensor]:
        x = self.main_model(x)
        self.hidden_status = x
        x = x.squeeze()
    
        d_last_layer = self.d_last_layer(x)
        c_last_layer = self.c_last_layer(x)
        return d_last_layer, c_last_layer
