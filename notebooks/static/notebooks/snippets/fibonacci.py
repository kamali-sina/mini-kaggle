def fibonacci(number):
    if number <= 0:
        return [0]
    sequence = [0, 1]
    while len(sequence) <= number:
        next_value = sequence[len(sequence) - 1] + sequence[len(sequence) - 2]
        sequence.append(next_value)
    return sequence


fibonacci(7)  # [0, 1, 1, 2, 3, 5, 8, 13]
