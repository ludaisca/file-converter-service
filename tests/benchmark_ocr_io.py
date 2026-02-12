import time
import tempfile
import os

def benchmark_io_overhead(iterations=100, data_size=1024*1024): # 1MB dummy data
    # Scenario A: Disk I/O (Create temp file, write, read, delete)
    start_time = time.time()
    dummy_data = b'x' * data_size

    for _ in range(iterations):
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(dummy_data)
            tmp_path = tmp.name

        # Simulate reading the file (as Image.open would)
        with open(tmp_path, 'rb') as f:
            _ = f.read()

        os.unlink(tmp_path)

    end_time = time.time()
    disk_io_time = end_time - start_time

    # Scenario B: Memory (Pass object directly)
    start_time = time.time()
    # Simulate passing the object (no I/O)
    for _ in range(iterations):
        _ = dummy_data # Just accessing the variable

    end_time = time.time()
    memory_time = end_time - start_time

    print(f"Iterations: {iterations}")
    print(f"Data Size: {data_size} bytes")
    print(f"Disk I/O Time: {disk_io_time:.4f} seconds")
    print(f"Memory Time:   {memory_time:.4f} seconds")
    if memory_time > 0:
        print(f"Speedup:       {disk_io_time / memory_time:.2f}x")
    else:
        print(f"Speedup:       Infinite (approx)")

if __name__ == "__main__":
    benchmark_io_overhead()
