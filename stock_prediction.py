import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from sklearn.metrics import root_mean_squared_error

#%%
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

#S&P 500 index
ticker = '^GSPC'

#dataframes
df = yf.download(ticker, '2020-01-01')
df.Close.plot(figsize=(12, 6))
plt.title('S&P 500 Index')

#creates a normalised version of the closing price data; improves model's performance
scaler = StandardScaler()
df['Close'] = scaler.fit_transform(df['Close'])

#creates sequences of data for the LSTM model
sequence_length = 30
data = []

for i in range(len(df) - sequence_length):
    data.append(df.Close[i:i + sequence_length])

#turns data into numpy array
data = np.array(data)

train_size = int(len(data) * 0.8)

#using torch tensors for training and testing
X_train = torch.from_numpy(data[:train_size, : -1, :]).type(torch.Tensor).to(device)
y_train = torch.from_numpy(data[:train_size, -1, :]).type(torch.Tensor).to(device)
X_test = torch.from_numpy(data[train_size:, : -1, :]).type(torch.Tensor).to(device)
y_test = torch.from_numpy(data[train_size:, -1, :]).type(torch.Tensor).to(device)

#defining the model

class PredictionModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers, output_dim):
        super(PredictionModel, self).__init__()

        self.num_layers = num_layers
        self.hidden_dim = hidden_dim

        #LSTM layer
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        #fully connected layer
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim, device=device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim, device=device)

        out, (hn, cn) = self.lstm(x, (h0.detach(), c0.detach()))
        out = self.fc(out[:, -1, :])
        
        #returns prediction
        return out

#creating the model
model = PredictionModel(input_dim=1, hidden_dim=50, num_layers=2, output_dim=1).to(device)

#criterion for training
criterion = nn.MSELoss()
optimiser = optim.Adam(model.parameters(), lr=0.01)

#training the model in loops
num_epochs = 100
for epoch in range(num_epochs):
    y_train_pred = model(X_train)
    
    #calculating loss
    loss = criterion(y_train_pred, y_train)

    if i % 25 == 0:
        print(i, loss.item())
    
    optimiser.zero_grad()
    loss.backward()
    optimiser.step()

#testing the model with unseen data
model.eval()

y_test_pred = model(X_test)

y_train_pred = scaler.inverse_transform(y_train_pred.cpu().detach().numpy())
y_train = scaler.inverse_transform(y_train.cpu().detach().numpy())
y_test_pred = scaler.inverse_transform(y_test_pred.cpu().detach().numpy())
y_test = scaler.inverse_transform(y_test.cpu().detach().numpy())

#calculating mean squared error
train_rmse = root_mean_squared_error(y_train[:, 0], y_train_pred[:, 0])
test_rmse = root_mean_squared_error(y_test[:, 0], y_test_pred[:, 0])

#visualising the results
fig = plt.figure(figsize=(12, 10))

gs = fig.add_gridspec(4, 1)
ax1 = fig.add_subplot(gs[:3, 0])
ax1.plot(df.index[-len(y_test):], y_test, color = 'blue', label = 'Actual Price')
ax1.plot(df.index[-len(y_test):], y_test_pred, color = 'green', label = 'Predicted Price')
ax1.legend()
plt.title(f"{ticker} Stock Price Prediction")
plt.xlabel('Date')
plt.ylabel('Price')

ax2 = fig.add_subplot(gs[3, 0])
ax2.axhline(test_rmse, color='blue', linestyle=' -- ', label=f'RMSE:')
ax2.plot(df[-len(y_test):].index, abs(y_test - y_test_pred), color='red', label='Prediction Error')
ax2.legend()
plt.title('Prediction Error')
plt.xlabel('Date')
plt.ylabel('Error')
plt.tight_layout()
plt.show()