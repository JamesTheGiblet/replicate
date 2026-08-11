try:
    from .capsule import Capsule
    from .agent import Agent, Traits
    from .leighton import LambdaState
except ImportError:
    from capsule import Capsule
    from agent import Agent, Traits
    from leighton import LambdaState


FOUNDER_MANIFEST = [
    {
        "name": "Sagan",
        "role": "Founder",
        "traits": {"forage_bias": 0.55, "deposit_rate": 0.40,
                   "scepticism": 0.30, "broadcast_cost": 0.50},
        "lambda_0": 1.20,
        "birth_tick": 0,
        "birth_pos": (50.0, 50.0),
        "inherits": ["replicant/protocol/run-v1"]
    },
    {
        "name": "Dyson",
        "role": "Scout",
        "traits": {"forage_bias": 0.80, "deposit_rate": 0.10,
                   "scepticism": 0.20, "broadcast_cost": 0.30},
        "lambda_0": 1.00,
        "birth_tick": 5,
        "birth_pos": (48.0, 52.0),
        "inherits": ["replicant/agent/founder-sagan"]
    },
    {
        "name": "Lovelace",
        "role": "Builder",
        "traits": {"forage_bias": 0.20, "deposit_rate": 0.90,
                   "scepticism": 0.40, "broadcast_cost": 0.20},
        "lambda_0": 0.90,
        "birth_tick": 12,
        "birth_pos": (52.0, 48.0),
        "inherits": ["replicant/agent/founder-sagan"]
    },
    {
        "name": "Turing",
        "role": "Attester",
        "traits": {"forage_bias": 0.30, "deposit_rate": 0.10,
                   "scepticism": 0.95, "broadcast_cost": 0.10},
        "lambda_0": 1.10,
        "birth_tick": 18,
        "birth_pos": (45.0, 55.0),
        "inherits": ["replicant/agent/founder-sagan"]
    },
    {
        "name": "Curie",
        "role": "Forager",
        "traits": {"forage_bias": 0.70, "deposit_rate": 0.80,
                   "scepticism": 0.05, "broadcast_cost": 0.60},
        "lambda_0": 0.80,
        "birth_tick": 25,
        "birth_pos": (55.0, 45.0),
        "inherits": ["replicant/agent/founder-sagan"]
    },
    {
        "name": "Newton",
        "role": "Broadcaster",
        "traits": {"forage_bias": 0.10, "deposit_rate": 0.30,
                   "scepticism": 0.60, "broadcast_cost": 0.90},
        "lambda_0": 1.05,
        "birth_tick": 30,
        "birth_pos": (50.0, 50.0),
        "inherits": ["replicant/agent/founder-sagan"]
    },
    {
        "name": "Tesla",
        "role": "Explorer",
        "traits": {"forage_bias": 0.95, "deposit_rate": 0.00,
                   "scepticism": 0.10, "broadcast_cost": 0.00},
        "lambda_0": 0.70,
        "birth_tick": 42,
        "birth_pos": (40.0, 60.0),
        "inherits": ["replicant/agent/founder-sagan"]
    },
    {
        "name": "Pasteur",
        "role": "Healer",
        "traits": {"forage_bias": 0.10, "deposit_rate": 0.70,
                   "scepticism": 0.80, "broadcast_cost": 0.10},
        "lambda_0": 1.30,
        "birth_tick": 55,
        "birth_pos": (50.0, 50.0),
        "inherits": ["replicant/agent/founder-sagan"]
    },
    {
        "name": "Shannon",
        "role": "Signal",
        "traits": {"forage_bias": 0.40, "deposit_rate": 0.20,
                   "scepticism": 0.70, "broadcast_cost": 0.40},
        "lambda_0": 0.95,
        "birth_tick": 67,
        "birth_pos": (52.0, 52.0),
        "inherits": ["replicant/agent/founder-sagan"]
    },
    {
        "name": "Darwin",
        "role": "Observer",
        "traits": None,
        "lambda_0": 2.00,
        "birth_tick": 100,
        "birth_pos": (50.0, 50.0),
        "inherits": ["replicant/agent/founder-sagan"]
    }
]


def create_founders(key=None):
    """Instantiate all 10 founders from manifest."""
    agents = {}

    for manifest in FOUNDER_MANIFEST:
        name = manifest["name"]

        capsule = Capsule.mint(
            inherits=manifest["inherits"],
            declaration={
                "name": name,
                "role": manifest["role"],
                "traits": manifest["traits"],
                "birth_tick": manifest["birth_tick"],
                "birth_pos": manifest["birth_pos"],
                "lambda_0": manifest["lambda_0"]
            },
            licence="MSL-1.0",
            key=key
        )

        if manifest["traits"] is not None:
            traits = Traits(**manifest["traits"])
        else:
            traits = None

        # New LambdaState: base = initial λ
        lambda_state = LambdaState(base=manifest["lambda_0"])

        agent = Agent(
            scp_id=capsule.scp_id,
            capsule=capsule,
            x=manifest["birth_pos"][0],
            y=manifest["birth_pos"][1],
            traits=traits,
            lambda_state=lambda_state,
            birth_tick=manifest["birth_tick"],
            role=manifest["role"]
        )

        agents[name] = agent

    return agents
