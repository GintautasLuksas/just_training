
row_amount = 0
unique_ip = []
unique_ip_amount = 0
ip_500 = []

with (open("log.csv", "r") as log_file):
    header = next(log_file)
    for line in log_file:
        row_data = line.strip().split(",")
        row_amount +=1
        if row_data[1] not in unique_ip:
            unique_ip.append(row_data[1])
            unique_ip_amount += 1
        if row_data[2] == "500":
            if row_data[1] not in ip_500:
                ip_500.append(row_data[1])


#print(f'Total row amount: {row_amount}')
#print(f'Unique IP amount: {unique_ip_amount}')
#print(f'Error 500 effected IPs:{ip_500}')


the_list = ["50", "5", "8"]
changed_list = []
for n in the_list:
    changed_list.append(int(n))

print(changed_list)

