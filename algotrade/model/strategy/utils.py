
class Utils():

	def __init__(self):
        pass

	def get_levels(data_prev):
        K = 2
        data_prices = np.array(data_prev["Close"])
        kmeans = KMeans(n_clusters=K).fit(data_prices.reshape(-1, 1))
        clusters = kmeans.predict(data_prices.reshape(-1, 1))

        min_max_values = []
        for i in range(K):
            min_max_values.append([np.inf, -np.inf])
        for i in range(len(data_prices)):
            cluster = clusters[i]
            if data_prices[i] < min_max_values[cluster][0]:
                min_max_values[cluster][0] = data_prices[i]
            if data_prices[i] > min_max_values[cluster][1]:
                min_max_values[cluster][1] = data_prices[i]

        output = []
        s = sorted(min_max_values, key=lambda x: x[0])
        for i, (_min, _max) in enumerate(s):
            if i == 0:
                output.append(_min)
            if i == len(min_max_values) - 1:
                output.append(_max)
            else:
                output.append(sum([_max, s[i+1][0]]) / 2)
            
        return output