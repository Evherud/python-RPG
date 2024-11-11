def sieve_of_eratosthenes(limit):
    # Create boolean array for marking numbers
    sieve = [True] * limit
    sieve[0] = sieve[1] = False
    
    # Mark non-prime numbers in the sieve
    for i in range(2, int(limit ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, limit, i):
                sieve[j] = False
    
    # Collect prime numbers
    primes = []
    for i in range(limit):
        if sieve[i]:
            primes.append(i)
            if len(primes) == 2000:
                return primes
    return primes

# Find first 2000 primes
limit = 20000  # Initial estimate of range needed
while True:
    primes = sieve_of_eratosthenes(limit)
    if len(primes) >= 2000:
        # Write to file
        with open('primes.txt', 'w') as f:
            for i, prime in enumerate(primes[:2000], 1):
                f.write(f"{i}. {prime}\n")
        break
    limit *= 2

print(f"First 2000 prime numbers have been written to primes.txt")
