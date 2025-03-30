from oblivious_transfer.oblivious_transfer import ObliviousTransfer
from elgamal.elgamal import Elgamal

m = 'Text'.encode('utf-8')

n = int(input("n: "))
messages = []
for i in range(int(n)):
    message = input(f"message m[{i}]: ").encode('utf-8')
    messages.append(message)

c = int(input(f"c: (0-{n-1}): "))

ot = ObliviousTransfer(n)
bob_keys, sk = ot.bob_ot1(c)
print(f"Bob -> Alice: {bob_keys}")

ciphertexts = ot.alice_ot1(messages, bob_keys)
print(f"Alice -> Bob: {ciphertexts}")

m_c = ot.bob_ot2(c, sk, ciphertexts)
print(f"Bob's message: {m_c}")


