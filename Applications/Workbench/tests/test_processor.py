import subprocess
import sys
import unittest

BINARY = sys.argv.pop(1)

def run(operation, data, amount, width=3, height=1):
    return subprocess.run([BINARY, operation, str(width), str(height), str(amount), "0", "0"],
                          input=bytes(data), capture_output=True)

class ProcessorTests(unittest.TestCase):
    def test_threshold_boundary(self):
        self.assertEqual(run("threshold", [99, 100, 101], 100).stdout, bytes([0, 255, 255]))

    def test_region_stops_at_disconnected_island(self):
        self.assertEqual(run("region", [90, 0, 90], 1).stdout, bytes([255, 0, 0]))

    def test_smoothing_edges(self):
        self.assertEqual(run("smooth", [0, 60, 120], 1).stdout, bytes([30, 60, 90]))

    def test_zero_noise_is_identity(self):
        self.assertEqual(run("noise", [1, 130, 255], 0).stdout, bytes([1, 130, 255]))

    def test_truncated_buffer(self):
        self.assertNotEqual(run("threshold", [42], 1).returncode, 0)

if __name__ == "__main__":
    unittest.main()
