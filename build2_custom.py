# LSTM for closing bitcoin price with regression framing
import numpy as np
import matplotlib.pyplot as plt
from pandas import read_csv
from keras.models import Sequential, load_model
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import math

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

import pudb;pu.db
# convert an array of values into a dataset matrix
def create_dataset(dataset):
  dataX, dataY = [], []
  for i in range(len(dataset)-1):
    dataX.append(dataset[i])
    dataY.append(dataset[i + 1])
  return np.asarray(dataX), np.asarray(dataY)

# fix random seed for reproducibility
np.random.seed(7)

# load the dataset
df = read_csv('./data/new.csv')
df = df.iloc[::-1]
#df = df.drop(['Date','Open','High','Low','Volume','Market Cap'], axis=1)
dataset = df.close
dataset = dataset.astype('float32')
dataset_r = dataset.reshape(len(dataset), 1)


# normalize the dataset
scaler = MinMaxScaler(feature_range=(0, 1))
dataset = scaler.fit_transform(dataset_r)

#prepare the X and Y label
X,y = create_dataset(dataset)

#Take 80% of data as the training sample and 20% as testing sample
trainX, testX, trainY, testY = train_test_split(X, y, test_size=0.20, shuffle=False)

# reshape input to be [samples, time steps, features]
trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
testX = np.reshape(testX, (testX.shape[0], 1, testX.shape[1]))

# create and fit the LSTM network
model = Sequential()
model.add(LSTM(4, input_shape=(1, 1)))
model.add(Dense(1))
model.compile(loss='mean_squared_error', optimizer='adam')
model.fit(trainX, trainY, epochs=5, batch_size=1, verbose=2)

#save model for later use
model.save('./savedModel')

#load_model
model = load_model('./savedModel')

# make predictions
trainPredict = model.predict(trainX)
testPredict = model.predict(testX)

futurePredict = model.predict(np.asarray([[testPredict[-1]]]))
futurePredict = scaler.inverse_transform(futurePredict)



"""
data = np.asarray([[testPredict[-1]]])

for jj in range(0,1200):
    futurePredict = model.predict(data)
#   t = np.reshape(futurePredict, (len(futurePredict),1,1))
#   data = np.concatenate((data, t))
    data = np.asarray([[futurePredict[-1]]])
    if jj == 0:
        wholeFuture = futurePredict
    else:
        wholeFuture = np.concatenate((wholeFuture, futurePredict))

"""
data = np.asarray([[testPredict[-1]]])
predictLength = 2000

for jj in range(0, predictLength):
    futurePredict = model.predict(data)
    #t = np.reshape(futurePredict, (len(futurePredict),1,1))
    t=np.asarray([[futurePredict[-1]]])
    data = np.concatenate((data, t))

    if (len(futurePredict)%500==0):
        fullData = np.concatenate((trainPredict, futurePredict))
        xx,yy = create_dataset(fullData)
        xx = np.reshape(xx,(xx.shape[0],1,xx.shape[1]))
        model.fit(xx,yy, epochs=5, batch_size=1, verbose=2)
#    data = np.asarray([[futurePredict[-1]]])
#    if jj == 0:
#        wholeFuture = futurePredict
#    else:
#        wholeFuture = np.concatenate((wholeFuture, futurePredict))



wholeFuture = futurePredict

futurePredictNorm = scaler.inverse_transform(wholeFuture)
print("Bitcoin price for tomorrow: ", wholeFuture)
print("Unnormalized: ", futurePredictNorm)


# invert predictions
trainPredict = scaler.inverse_transform(trainPredict)
trainY = scaler.inverse_transform(trainY)
testPredict = scaler.inverse_transform(testPredict)
testY = scaler.inverse_transform(testY)

print("Price for last 5 days: ")
print(testPredict[-5:])
print("Bitcoin price for tomorrow: ", futurePredict)

# calculate root mean squared error
trainScore = math.sqrt(mean_squared_error(trainY[:,0], trainPredict[:,0]))
print('Train Score: %.2f RMSE' % (trainScore))
testScore = math.sqrt(mean_squared_error(testY[:,0], testPredict[:,0]))
print('Test Score: %.2f RMSE' % (testScore))

# shift train predictions for plotting
trainPredictPlot = np.empty_like(dataset)
trainPredictPlot[:, :] = np.nan
trainPredictPlot[1:len(trainPredict)+1, :] = trainPredict

# shift test predictions for plotting
testPredictPlot = np.empty_like(dataset)
testPredictPlot[:, :] = np.nan
testPredictPlot[len(trainPredict):len(dataset)-1, :] = testPredict


futurePredictPlot = np.empty_like(dataset)
futurePredictPlot = np.resize(futurePredictPlot,(len(futurePredictPlot) + predictLength,1))
futurePredictPlot[:, :] = np.nan
#futurePredictPlot[len(futurePredictNorm):len(currency_close_price)-1, :] = futurePredictNorm
futurePredictPlot[len(trainPredict)+len(testPredict):len(futurePredictPlot)-1, :]= futurePredictNorm


# plot baseline and predictions
plt.plot(scaler.inverse_transform(dataset))
plt.plot(trainPredictPlot)
plt.plot(testPredictPlot)
plt.plot(futurePredictPlot)
plt.show()

