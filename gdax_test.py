# Steven Wang
# 20180830

# test if there is missing data point
file_name_list = ['BTC-USD_data.txt',
                  'ETH-USD_data.txt',
                  'LTC-USD_data.txt']

n = []
initial = 1452297600

start = initial
with open(file_name_list[0]) as f:
    for line in f:
        end = int(line.split(',')[0])
        if end - start > 3600:
            n.append(end)
            print(n)
        start = end

#################################################
for i in range(len(n) - 1):
    print(n[i + 1] - n[i])
