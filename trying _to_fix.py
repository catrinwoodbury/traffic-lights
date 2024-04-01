estimatedtime = 6
i = 0
while estimatedtime >= 2:
    departure = estimatedtime
    while i:
        print(i)
        print(departure, i)
        i = i + 1
        if i >= 4:
            continue
    print("estimated: ", estimatedtime)
    estimatedtime = estimatedtime - 1
print("Complete!")
