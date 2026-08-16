"""Tests proving strategy inputs do not leak hidden true coordinates."""

from dataclasses import fields

from police_thief_lab import Action, GameConfig, Observation, Position, Role, Simulator


def test_observation_schema_has_no_opponent_position() -> None:
    """The policy DTO has no field capable of carrying opponent truth."""
    observation_fields = {field.name for field in fields(Observation)}
    assert "opponent_position" not in observation_fields
    assert "world_state" not in observation_fields
    assert "state" not in observation_fields


def test_role_observations_contain_only_own_position() -> None:
    """Each role sees its own coordinate and no coordinate belonging to its opponent."""
    simulator = Simulator(GameConfig(police_start=Position(0, 0), thief_start=Position(6, 6)))
    police = simulator.observe(Role.POLICE)
    thief = simulator.observe(Role.THIEF)
    assert police.local.own_position == Position(0, 0)
    assert thief.local.own_position == Position(6, 6)
    assert not hasattr(police, "__dict__")
    assert not hasattr(thief, "opponent_position")


def test_backend_is_called_with_observation_only() -> None:
    """The execution boundary passes no simulator or WorldState argument."""

    class RecordingBackend:
        received: Observation | None = None

        def choose_action(self, observation: Observation) -> Action:
            self.received = observation
            return observation.legal_actions[-1]

    backend = RecordingBackend()
    simulator = Simulator(GameConfig())
    simulator.play_turn(backend)
    assert isinstance(backend.received, Observation)
    assert backend.received.local.role is Role.THIEF
