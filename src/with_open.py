
row_amount = 0
unique_ip = []
ip_500 = []

with open("log.csv", "r") as log_file:
    header = next(log_file)
    for line in log_file:
        row_data = line.strip().split(",")
        row_amount +=1
        if row_data[1] not in unique_ip:
            unique_ip.append(row_data[1])
        if row_data[2] == "500":
            ip_500.append(row_data[1])
        print(row_data)

print(row_amount)
print(unique_ip)
print(ip_500)