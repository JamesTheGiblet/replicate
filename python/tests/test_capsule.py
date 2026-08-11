import unittest
import json
from src.capsule import Capsule


class TestCapsule(unittest.TestCase):
    """Test semantic capsule primitives."""

    def test_capsule_mint(self):
        """Test minting a capsule."""
        capsule = Capsule.mint(
            inherits=["replicant/protocol/run-v1"],
            declaration={"test": "value", "number": 42},
            licence="MSL-1.0"
        )
        
        self.assertIsNotNone(capsule.scp_id)
        self.assertTrue(capsule.scp_id.startswith("replicant/agent/"))
        self.assertEqual(capsule.inherits, ["replicant/protocol/run-v1"])
        self.assertEqual(capsule.declaration["test"], "value")
        self.assertEqual(capsule.declaration["number"], 42)
        self.assertEqual(capsule.licence, "MSL-1.0")
        self.assertIsNotNone(capsule.signature)

    def test_capsule_canonicalise(self):
        """Test canonical JSON serialization."""
        capsule = Capsule.mint(
            inherits=["test/protocol/v1"],
            declaration={"b": 2, "a": 1, "c": {"z": 26, "y": 25}},
            licence="TEST-1.0"
        )
        
        canonical = capsule.canonicalise()
        
        # Should be valid JSON
        parsed = json.loads(canonical)
        self.assertEqual(parsed["scp_id"], capsule.scp_id)
        self.assertEqual(parsed["inherits"], ["test/protocol/v1"])
        self.assertEqual(parsed["declaration"]["a"], 1)
        self.assertEqual(parsed["declaration"]["b"], 2)
        self.assertEqual(parsed["declaration"]["c"]["y"], 25)
        self.assertEqual(parsed["declaration"]["c"]["z"], 26)
        self.assertEqual(parsed["licence"], "TEST-1.0")
        
        # Ensure deterministic ordering
        self.assertIn('"a":1', canonical)
        self.assertIn('"b":2', canonical)
        self.assertIn('"y":25', canonical)
        self.assertIn('"z":26', canonical)

    def test_capsule_lineage(self):
        """Test lineage tracking."""
        parent = Capsule.mint(
            inherits=["replicant/protocol/run-v1"],
            declaration={"name": "Parent"},
            licence="MSL-1.0"
        )
        
        child = Capsule.mint(
            inherits=[parent.scp_id, "replicant/protocol/run-v1"],
            declaration={"name": "Child", "parent": parent.lineage_id()},
            licence="MSL-1.0"
        )
        
        self.assertEqual(child.inherits[0], parent.scp_id)
        self.assertEqual(child.declaration["parent"], parent.lineage_id())


if __name__ == "__main__":
    unittest.main()
