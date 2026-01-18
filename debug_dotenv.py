import os

with open('.env') as f:
    for i, line in enumerate(f, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        try:
            k, v = line.split('=', 1)
            print(f"Line {i}: Setting {k}={v}")
            os.environ[k] = v
        except Exception as e:
            print(f"Error on line {i}: {line}")
            print(e)
            break