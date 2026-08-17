"""Role-safe Live GUI publication methods for the peer runtime."""

from __future__ import annotations

from contextlib import suppress

from ..policies.belief import scent_weights
from ..presentation import TurnBanner, build_live_view


class _RuntimePresentationMixin:
    """Represent RuntimePresentationMixin as one cohesive typed implementation boundary."""
    def _publish_live(self, banner: TurnBanner) -> None:
        """Publish only the observation boundary plus a truth-free belief."""
        if self.live_view_publisher is None:
            return
        observation = self._observation()
        step = max(self._next_outbound_step - 1, self.receiver.next_step - 1)
        view = build_live_view(observation, scent_weights(observation), banner, step)
        self.live_view_publisher.publish(view)

    def _publish_live_error(self) -> None:
        """Best-effort terminal status without masking the original runtime failure."""
        with suppress(OSError, ValueError):
            self._publish_live(TurnBanner.ERROR)
