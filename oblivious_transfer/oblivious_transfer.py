from copy import deepcopy

from elgamal.elgamal import Elgamal

class ObliviousTransfer:
    """
    1 out of n oblivious transfer protocol. Requires one round of communication.

    Problem:
        Alice has n messages m_0, m_1, ..., m_{n-1}. Bob has a choice integer c in [0, n-1].
        Bob wants to learn m_c without revealing c to Alice.
        Alice wants to send m_c to Bob without revealing m_i for i != c.

    Functions:
        bob_ot1(c):                                 Returns public keys {b_0, b_1, ..., b_{n-1}} and secret key sk
        alice_ot1(messages, bob_keys):              Returns ciphertexts {c_0, c_1, ..., c_{n-1}}
        bob_ot2(c, sk, ciphertexts):                Returns m_c, the message Bob wants to learn

    Protocol:
        1.  Bob has a choice integer c in [0, n-1]. He calls bob_ot1(c) to get public keys {b_0, b_1, ..., b_{n-1}} and secret key sk.
            Bob keeps sk secret and sends {b_0, b_1, ..., b_{n-1}} to Alice.
        2.  Alice has n messages m_1, m_2, ..., m_n. She receives bob_keys = {b_0, b_1, ..., b_{n-1}} from Bob. She calls
            alice_ot1(messages, bob_keys) to get ciphertexts {c_0, c_1, ..., c_{n-1}}. Alice sends {c_0, c_1, ..., c_{n-1}} to Bob.
        3.  Bob receives alice_ciphertexts = {c_0, c_1, ..., c_{n-1}} from Alice. He calls bob_ot2(c, sk, ciphertexts) to get m_c.

    """
    def __init__(self, n):
        self.n = n

    def bob_ot1(self, c):
        pk, sk = Elgamal.newkeys(128)
        b = [deepcopy(pk) for _ in range(self.n)]
        for i in range(self.n):
            b[i].y = b[i].y - c + i
        return b, sk

    def alice_ot1(self, messages, bob_keys):
        return [Elgamal.encrypt(messages[i], bob_keys[i]) for i in range(self.n)]

    def bob_ot2(self, c, sk, ciphertexts):
        return Elgamal.decrypt(ciphertexts[c], sk)




