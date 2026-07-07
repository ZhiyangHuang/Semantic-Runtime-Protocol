import os
import unittest

from srp_experiment.srp.encoder import (
    HashingSemanticEncoder,
    build_encoder,
    cosine_similarity,
    update_state_vector,
)
from srp_experiment.srp.compress import chunk_memory


class TestEncoder(unittest.TestCase):
    def test_hashing_encoder_is_deterministic(self):
        encoder = HashingSemanticEncoder()
        a = encoder.encode_passage("Hello world")
        b = encoder.encode_passage("Hello world")
        self.assertEqual(a, b)
        self.assertEqual(len(a), 256)

    def test_cosine_similarity_basics(self):
        self.assertEqual(cosine_similarity([], []), 0.0)
        self.assertAlmostEqual(cosine_similarity([1.0, 0.0], [1.0, 0.0]), 1.0)
        self.assertAlmostEqual(cosine_similarity([1.0, 0.0], [0.0, 1.0]), 0.0)

    def test_build_encoder_env_switch(self):
        previous = os.environ.get("SRP_ENCODER")
        try:
            os.environ["SRP_ENCODER"] = "hashing"
            encoder = build_encoder()
            self.assertIsInstance(encoder, HashingSemanticEncoder)
        finally:
            if previous is None:
                os.environ.pop("SRP_ENCODER", None)
            else:
                os.environ["SRP_ENCODER"] = previous

    def test_update_state_vector_is_normalized(self):
        previous = [1.0, 0.0]
        current = [0.0, 1.0]
        updated = update_state_vector(previous, current, decay=0.5)
        self.assertEqual(len(updated), 2)
        self.assertAlmostEqual(sum(x * x for x in updated), 1.0, places=6)

    def test_chunk_memory_produces_stable_ids(self):
        chunks = chunk_memory("First sentence. Second sentence with more words.", max_words=3)
        self.assertTrue(chunks)
        self.assertTrue(chunks[0].startswith("1:"))


if __name__ == "__main__":
    unittest.main()
