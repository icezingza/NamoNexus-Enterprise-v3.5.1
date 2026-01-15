"""Legacy core entry running the supervisor chain loop."""
from __future__ import annotations

from time import sleep

from app.core.supervisor_chain_v7 import SupervisorChainV7
from src.security_patch import secure_random_uniform


def main() -> None:
    chain = SupervisorChainV7()
    signals = [secure_random_uniform(-0.2, 0.5) for _ in range(5)]
    reports = chain.run_loop(signals, symbols="legacy-loop", delay=0.0)
    for report in reports:
        print(report)


if __name__ == "__main__":
    main()
