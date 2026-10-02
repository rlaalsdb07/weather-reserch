"""
소수(Prime Number) 탐색 및 판별 알고리즘 모음
- 1. 기본 제곱근 나눗셈법 (Trial Division)
- 2. 6k ± 1 최적화 나눗셈법
- 3. 에라토스테네스의 체 (Sieve of Eratosthenes) - 범위 탐색 표준
- 4. 오일러의 선형 체 (Linear Sieve) - O(N)
"""

def is_prime_basic(n: int) -> bool:
    """1. 기본 제곱근 나눗셈법: O(sqrt(N))"""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def is_prime_6k(n: int) -> bool:
    """
    2. 6k ± 1 최적화 나눗셈법: 2와 3의 배수를 제외하고 6k±1 패턴만 확인
    연산 횟수를 기본 방식 대비 약 1/3 수준으로 절감
    """
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False

    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def sieve_of_eratosthenes(limit: int) -> list[int]:
    """
    3. 에라토스테네스의 체: O(N log(log N))
    특정 범위(1 ~ limit)의 소수를 일괄 탐색할 때 가장 권장되는 알고리즘
    """
    if limit < 2:
        return []

    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False

    for i in range(2, int(limit ** 0.5) + 1):
        if is_prime[i]:
            # i*i 이전의 배수는 이미 이전 소수들에 의해 지워졌으므로 i*i부터 시작
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False

    return [num for num, prime in enumerate(is_prime) if prime]


def linear_sieve(limit: int) -> list[int]:
    """
    4. 오일러의 선형 체 (Linear Sieve): O(N)
    각 합성수를 '가장 작은 소인수(SPF)'로 정확히 한 번만 방문하여 지움
    """
    if limit < 2:
        return []

    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    primes = []

    for i in range(2, limit + 1):
        if is_prime[i]:
            primes.append(i)
        for p in primes:
            if i * p > limit:
                break
            is_prime[i * p] = False
            # i가 p로 나누어떨어지면 p는 i*p의 최소 소인수이므로 루프 종료
            if i % p == 0:
                break

    return primes


if __name__ == "__main__":
    limit = 100

    # 1. 에라토스테네스의 체 실행
    primes = sieve_of_eratosthenes(limit)

    print(f"=== 1부터 {limit} 사이의 소수 목록 ===")
    print(primes)
    print(f"\n총 개수: {len(primes)}개")
