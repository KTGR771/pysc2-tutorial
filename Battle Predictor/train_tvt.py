import csv
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from joblib import dump, load

xs = []
ys = []
 
with open("tvt.csv") as csvfile:
  csvreader = csv.reader(csvfile)
  for row in csvreader:
    predictor_marines = int(row[0])
    enemy_marines = int(row[1])
    score = int(row[2])
     
    xs.append((predictor_marines, enemy_marines))
    ys.append(1 if score > 0 else 0)
 
logreg = LogisticRegression()
 
train, test, train_labels, test_labels = train_test_split(xs, ys)
 
logreg.fit(train, train_labels)
 
predictions = logreg.predict(test)
 
print(accuracy_score(test_labels, predictions))
