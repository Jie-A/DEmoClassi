import torch
import torch.nn.functional as F
import torch.optim as optim


class SeparableConv(torch.nn.Module):
    """Depthwise separable convolution layer implementation."""

    def __init__(self, nin, nout, kernel_size=3):
        super(SeparableConv, self).__init__()
        self.depthwise = torch.nn.Conv2d(nin, nin, kernel_size=kernel_size, groups=nin)
        self.pointwise = torch.nn.Conv2d(nin, nout, kernel_size=1)

    def forward(self, x):
        x = self.depthwise(x)
        x = self.pointwise(x)
        return x


class SepConvModel(torch.nn.Module):

    def __init__(self, dropout=0.7, n_class=7, n_filters=[64, 128, 256, 512]):
        super(SepConvModel, self).__init__()

        self.dropout = dropout
        self.n_class = n_class
        self.n_filters = n_filters

        # 1st block
        self.conv1 = SeparableConv(1, self.n_filters[0])
        self.batchnorm1 = torch.nn.BatchNorm2d(self.n_filters[0])
        self.conv2 = SeparableConv(self.n_filters[0], self.n_filters[0])
        self.batchnorm2 = torch.nn.BatchNorm2d(self.n_filters[0])

        # 2nd block
        self.conv3 = SeparableConv(self.n_filters[0], self.n_filters[1])
        self.batchnorm3 = torch.nn.BatchNorm2d(self.n_filters[1])
        self.conv4 = SeparableConv(self.n_filters[1], self.n_filters[1])
        self.batchnorm4 = torch.nn.BatchNorm2d(self.n_filters[1])

        # 3rd block
        self.conv5 = SeparableConv(self.n_filters[1], self.n_filters[2])
        self.batchnorm5 = torch.nn.BatchNorm2d(self.n_filters[2])
        self.conv6 = SeparableConv(self.n_filters[2], self.n_filters[2])
        self.batchnorm6 = torch.nn.BatchNorm2d(self.n_filters[2])

        # 4th block
        self.conv7 = SeparableConv(self.n_filters[2], self.n_filters[3])
        self.batchnorm7 = torch.nn.BatchNorm2d(self.n_filters[3])
        self.conv8 = SeparableConv(self.n_filters[3], self.n_filters[3])
        self.batchnorm8 = torch.nn.BatchNorm2d(self.n_filters[3])

        self.avg_pool = torch.nn.AdaptiveAvgPool2d((1, 1))

        # 1st fc block
        self.fc1 = torch.nn.Linear(self.n_filters[3], 256)
        self.batchnorm9 = torch.nn.BatchNorm1d(256)

        # # 2nd fc block
        self.fc2 = torch.nn.Linear(256, 128)
        self.batchnorm10 = torch.nn.BatchNorm1d(128)

        # output block
        self.fc3 = torch.nn.Linear(128, self.n_class)

    def forward(self, x):
        # 1st block
        x = self.conv1(x)
        x = self.batchnorm1(F.relu(x))
        x = self.conv2(x)
        x = self.batchnorm2(F.relu(x))
        x = F.max_pool2d(x, 2)

        # 2nd block
        x = self.conv3(x)
        x = self.batchnorm3(F.relu(x))
        x = self.conv4(x)
        x = self.batchnorm4(F.relu(x))
        x = F.max_pool2d(x, 2)

        x = F.dropout(x, self.dropout)

        # 3rd block
        x = self.conv5(x)
        x = self.batchnorm5(F.relu(x))
        x = self.conv6(x)
        x = self.batchnorm6(F.relu(x))

        # 4th block
        x = self.conv7(x)
        x = self.batchnorm7(F.relu(x))
        x = self.conv8(x)
        x = self.batchnorm8(F.relu(x))

        x = self.avg_pool(x)
        x = F.dropout(x.view(-1, x.size()[1]), self.dropout)

        x = self.batchnorm9(F.relu(self.fc1(x)))
        x = F.dropout(x, self.dropout)

        x = self.batchnorm10(F.relu(self.fc2(x)))
        x = F.dropout(x, self.dropout)
        #
        x = self.fc3(x)
        #
        return x


# Define the model
my_model = SepConvModel()

# Define the optimizer
optimizer = optim.Adam(my_model.parameters(), lr=1e-3)
