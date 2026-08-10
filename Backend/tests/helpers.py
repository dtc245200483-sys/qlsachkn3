_email_seq = 0


def next_test_email() -> str:
    global _email_seq
    _email_seq += 1
    return f"DTC{100000000 + _email_seq}@ictu.edu.vn"
