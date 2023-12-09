import pandas as pd
from collections import OrderedDict

# Đọc dữ liệu từ file CSV
df = pd.read_csv('data.csv')

cusVip = list(OrderedDict.fromkeys(df['Doanh Thu Theo Khách Vip']))
cusMember = list(OrderedDict.fromkeys(df['Doanh Thu theo Membership']))
cusNormal = list(OrderedDict.fromkeys(df['Doanh thu theo khách Vãng lai']))
print(cusVip)
print(cusMember)
print(cusNormal)