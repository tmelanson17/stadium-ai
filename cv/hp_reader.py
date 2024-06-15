import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import transforms
import numpy as np
import cv2

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1) 
        self.conv2 = nn.Conv2d(32, 64, 3, 1) # -2x-2
        self.dropout1 = nn.Dropout(0.25)
        self.dropout2 = nn.Dropout(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2) 
        x = self.dropout1(x)
        x = torch.flatten(x, 1) 
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        output = F.log_softmax(x, dim=1)
        return output

    def fix_conv_layers(self):
        for param in self.conv1.parameters():
            param.requires_grad_(False)
        for param in self.conv2.parameters():
            param.requires_grad_(False)



class HPReader:
    def __init__(self, dataset="cv/mnist_cnn.pt"):
        self.net = Net()
        self.net.load_state_dict(torch.load(dataset))
        self.net.eval()
        scale_size = (28, 28)
        self.transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize(scale_size, interpolation=3),
        transforms.Normalize((0.1307,), (0.3081,)),
        ])
        self.min_white_fraction = 0.1

    def single_infer(self, img):
        if np.average(img) < self.min_white_fraction:
            return 0
        tensor = self.transform(img).float()
        cv2.imshow("input", tensor.detach().numpy()[0])
        cv2.waitKey(0)
        softmax = self.net(tensor.unsqueeze(0))
        result = softmax.detach().numpy()
        print(result)
        return np.argmax(result)

def retrain():
    from numbers_dataset import HPNumbersDataset, SaltPepperNoise, RandomPadding
    device = torch.device("cpu")
    reader = Net().to(device)
    reader.load_state_dict(torch.load("cv/mnist_cnn.pt"))
    scale_size=(28,28)
    transform = transforms.Compose([
        RandomPadding(pad_amount=10),
        transforms.Resize(scale_size, interpolation=3),
        SaltPepperNoise(0.01, 0.01),
        transforms.Normalize((0.1307,), (0.3081,)),
    ])
    dataset = HPNumbersDataset("data/numbers", transform=transform)
    train_loader = torch.utils.data.DataLoader(dataset,batch_size=4, shuffle=True)
    optimizer = optim.Adadelta(reader.parameters(), lr=0.5)

    reader.train()
    reader.fix_conv_layers()
    for epoch in range(300):
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            #cv2.imshow("data", data.detach().numpy()[0][0])
            #cv2.waitKey(0)
            optimizer.zero_grad()
            output = reader(data)
            loss = F.nll_loss(output, target)
            loss.backward()
            optimizer.step()
            if batch_idx % 3 == 0:
                print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                    epoch, batch_idx * len(data), len(train_loader.dataset),
                    100. * batch_idx / len(train_loader), loss.item()))
    torch.save(reader.state_dict(), "cv/hp_cnn.pt")


        
if __name__ == "__main__":
    retrain()
    import cv2
    reader = HPReader("cv/hp_cnn.pt")
    for i in range(7):
        if i == 3:
            continue
        img = cv2.imread(f"box_number_{i}.png", cv2.IMREAD_GRAYSCALE)
        hp = reader.single_infer(img)
        print(hp)
    img = cv2.imread("mnist.png", cv2.IMREAD_GRAYSCALE)
    hp = reader.single_infer(img)
    print(hp)
#        
