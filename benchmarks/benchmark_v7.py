"""Small reproducible v7 benchmark; avoids network and quantum-provider credentials."""
import statistics
import time
from jarvis_system_v7 import JARVISCore


def main(iterations: int = 5):
    samples = []
    for _ in range(iterations):
        runtime = JARVISCore(); started = time.perf_counter(); ok, _, trace = runtime.run("benchmark quantum circuit verification")
        assert ok and len(trace) == 4
        samples.append((time.perf_counter() - started) * 1000)
    print({"iterations": iterations, "mean_ms": round(statistics.mean(samples), 3), "p95_ms": round(sorted(samples)[max(0, int(.95 * len(samples)) - 1)], 3)})


if __name__ == "__main__": main()
