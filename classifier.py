# -*- coding: utf-8 -*-

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt

print(f'{torch.__version__}')
print(f'{torchvision.__version__}')

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)

transform = transforms.Compose(
    [transforms.ToTensor(),
     transforms.Normalize((0.5,),(0.5))])

trainset = torchvision.datasets.FashionMNIST(root='./data',train=True,
                                             download=True, transform=transform)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=64,
                                          shuffle=True,num_workers=2)
testset = torchvision.datasets.FashionMNIST(root='./data',train=False,
                                             download=True, transform=transform)
testloader = torch.utils.data.DataLoader(trainset, batch_size=64,
                                          shuffle=False,num_workers=2)

class CNN(nn.Module):
  def __init__(self):
    super(CNN,self).__init__()
    self.conv1 = nn.Conv2d(1,16,3,padding=1)
    self.conv2 = nn.Conv2d(16,32,3, padding=1)
    self.pool = nn.MaxPool2d(2,2)
    self.fc1 = nn.Linear(32 * 7 * 7, 128)
    self.fc2 = nn.Linear(128,10)

  def forward(self,x):
    x = self.pool(nn.functional.relu(self.conv1(x)))
    x = self.pool(nn.functional.relu(self.conv2(x)))
    x = x.view(-1, 32 * 7* 7)
    x = nn.functional.relu(self.fc1(x))
    x = self.fc2(x)
    return x

net = CNN().to(device)

optimizer = optim.Adam(net.parameters(),lr=0.001)
criterion = nn.CrossEntropyLoss()

for epoch in range(10):
  running_loss = 0.0
  for i,data in enumerate(trainloader,0):
    inputs, labels = data[0].to(device),data[1].to(device)
    optimizer.zero_grad()
    outputs = net(inputs)
    loss = criterion(outputs, labels)
    loss.backward()
    optimizer.step()
    running_loss += loss.item()
    if i % 200 == 199:
      print('[%d, %5d] loss : %.3f' % (epoch + 1, i + 1, running_loss / 200))
      running_loss = 0.0
print(f'Training finished')

correct = 0
total = 0
with torch.no_grad():
  for data in testloader:
    images, labels = data[0].to(device), data[1].to(device)
    outputs = net(images)
    _, predicted = torch.max(outputs.data, 1)
    total += labels.size(0)
    correct += (predicted == labels).sum().item()

print(f'Accuracy of the network on 10000 test images: %d %%' % (100 * correct / total))

label_map = {0: "T-shirt/top", 1: "T-shirt/top", 2: "T-shirt/top",  # map all tops to a single label
             3: "Trouser", 4: "Trouser",                            # map all trousers to a single label
             5: "Pullover", 6: "Dress", 7: "Coat",                  # map pullovers, dresses, and coats to their respective labels
             8: "Sandal", 9: "Sneaker"}


net.eval()
with torch.no_grad():
  dataiter = iter(testloader)
  images, labels = next(dataiter)
  images, labels = images.to(device), labels.to(device)
  outputs = net(images)
  _, predicted = torch.max(outputs, 1)
  for i in range(4):
    plt.imshow(images[i].cpu().numpy().squeeze(),cmap='gray')
    index = int(predicted[i])
    ground_truth = int(labels[i])
    plt.title('Ground Truth: {} Prediction: {}'.format(label_map[ground_truth], label_map[index]))
    plt.show()

