count = 0
import pickle
with open('counts.pkl','wb') as f:
    pickle.dump(count,f)