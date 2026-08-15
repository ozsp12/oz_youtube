"""Simulation-based synthetic data for a hypothetical music platform.

The generator does not learn from individual records. It combines explicit
scenario parameters with public aggregate population weights and a seeded
NumPy random-number generator. The resulting tables are suitable for software
tests and teaching examples, not for demographic or commercial inference.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd


BRAZILIAN_STATE_NAMES = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}


@dataclass(frozen=True)
class StreamingConfig:
    """Parameters controlling one reproducible simulation scenario."""

    seed: int = 42
    n_artists: int = 10
    albums_per_artist: int = 3
    tracks_per_album: int = 12
    n_users: int = 1_000
    mean_age: float = 30.0
    age_standard_deviation: float = 8.0
    minimum_age: int = 13
    maximum_age: int = 90
    sex_states: tuple[str, ...] = ("F", "M")
    sex_probabilities: tuple[float, ...] = (0.5, 0.5)
    start: str = "2021-01-01"
    periods: int = 100
    frequency: str = "30min"
    mean_events_per_period: float = 30.0
    popularity_concentration: float = 0.7

    def __post_init__(self) -> None:
        positive_integer_fields = {
            "n_artists": self.n_artists,
            "albums_per_artist": self.albums_per_artist,
            "tracks_per_album": self.tracks_per_album,
            "n_users": self.n_users,
            "periods": self.periods,
        }
        for name, value in positive_integer_fields.items():
            if value < 1:
                raise ValueError(f"{name} must be at least 1")
        if self.age_standard_deviation <= 0:
            raise ValueError("age_standard_deviation must be positive")
        if self.minimum_age > self.maximum_age:
            raise ValueError("minimum_age cannot exceed maximum_age")
        if self.mean_events_per_period < 0:
            raise ValueError("mean_events_per_period cannot be negative")
        if self.popularity_concentration <= 0:
            raise ValueError("popularity_concentration must be positive")
        if len(self.sex_states) != len(self.sex_probabilities):
            raise ValueError("sex states and probabilities must have equal length")
        if not np.isclose(sum(self.sex_probabilities), 1.0):
            raise ValueError("sex probabilities must sum to one")
        if any(probability < 0 for probability in self.sex_probabilities):
            raise ValueError("sex probabilities cannot be negative")


class StreamingPlatformGenerator:
    """Generate normalized catalog, user, and listening-event tables."""

    def __init__(self, config: StreamingConfig | None = None) -> None:
        self.config = config or StreamingConfig()
        self.rng = np.random.default_rng(self.config.seed)

    @staticmethod
    def read_population(path: str | Path) -> pd.DataFrame:
        """Read municipal IBGE estimates and return state sampling weights."""
        frame = pd.read_csv(path, sep=";")
        required = {"uf", "cidade", "populacao_estimada"}
        missing = required.difference(frame.columns)
        if missing:
            raise ValueError(f"population file is missing columns: {sorted(missing)}")

        frame = frame.loc[:, sorted(required)].copy()
        frame["populacao_estimada"] = pd.to_numeric(
            frame["populacao_estimada"], errors="raise"
        )
        if (frame["populacao_estimada"] <= 0).any():
            raise ValueError("population estimates must be positive")
        unknown_states = set(frame["uf"]).difference(BRAZILIAN_STATE_NAMES)
        if unknown_states:
            raise ValueError(f"unknown state codes: {sorted(unknown_states)}")

        state_population = (
            frame.groupby("uf", as_index=False)["populacao_estimada"]
            .sum()
            .rename(columns={"populacao_estimada": "population"})
        )
        state_population["state_name"] = state_population["uf"].map(
            BRAZILIAN_STATE_NAMES
        )
        state_population["sampling_probability"] = (
            state_population["population"] / state_population["population"].sum()
        )
        return state_population.loc[
            :, ["uf", "state_name", "population", "sampling_probability"]
        ]

    def create_catalog(self) -> pd.DataFrame:
        """Create a unique artist–album–track catalog with popularity weights."""
        rows = [
            {
                "artist_id": f"artist_{artist:03d}",
                "album_id": f"artist_{artist:03d}_album_{album:02d}",
                "track_id": (
                    f"artist_{artist:03d}_album_{album:02d}_track_{track:02d}"
                ),
            }
            for artist in range(1, self.config.n_artists + 1)
            for album in range(1, self.config.albums_per_artist + 1)
            for track in range(1, self.config.tracks_per_album + 1)
        ]
        catalog = pd.DataFrame(rows)
        alpha = np.full(len(catalog), self.config.popularity_concentration)
        catalog["sampling_probability"] = self.rng.dirichlet(alpha)
        return catalog

    def create_users(self, state_population: pd.DataFrame) -> pd.DataFrame:
        """Create synthetic users sampled from explicit scenario distributions."""
        states = state_population["uf"].to_numpy()
        state_probabilities = state_population["sampling_probability"].to_numpy()
        ages = self.rng.normal(
            self.config.mean_age,
            self.config.age_standard_deviation,
            self.config.n_users,
        )
        ages = np.rint(
            np.clip(ages, self.config.minimum_age, self.config.maximum_age)
        ).astype(int)

        return pd.DataFrame(
            {
                "user_id": [
                    f"user_{index:07d}"
                    for index in range(1, self.config.n_users + 1)
                ],
                "age_years": ages,
                "sex_state": self.rng.choice(
                    self.config.sex_states,
                    size=self.config.n_users,
                    p=self.config.sex_probabilities,
                ),
                "uf": self.rng.choice(
                    states,
                    size=self.config.n_users,
                    p=state_probabilities,
                ),
            }
        )

    def create_events(
        self, users: pd.DataFrame, catalog: pd.DataFrame
    ) -> pd.DataFrame:
        """Generate paired user–track events at regular simulation ticks."""
        timestamps = pd.date_range(
            start=self.config.start,
            periods=self.config.periods,
            freq=self.config.frequency,
        )
        user_ids = users["user_id"].to_numpy()
        track_ids = catalog["track_id"].to_numpy()
        track_probabilities = catalog["sampling_probability"].to_numpy()

        batches: list[pd.DataFrame] = []
        for timestamp in timestamps:
            event_count = int(self.rng.poisson(self.config.mean_events_per_period))
            if event_count == 0:
                continue
            batches.append(
                pd.DataFrame(
                    {
                        "event_timestamp": np.repeat(timestamp, event_count),
                        "user_id": self.rng.choice(user_ids, size=event_count),
                        "track_id": self.rng.choice(
                            track_ids,
                            size=event_count,
                            p=track_probabilities,
                        ),
                        "listening_seconds": self.rng.integers(
                            30, 301, size=event_count
                        ),
                    }
                )
            )

        if not batches:
            return pd.DataFrame(
                columns=[
                    "event_id",
                    "event_timestamp",
                    "user_id",
                    "track_id",
                    "listening_seconds",
                ]
            )
        events = pd.concat(batches, ignore_index=True)
        events.insert(
            0,
            "event_id",
            [f"event_{index:09d}" for index in range(1, len(events) + 1)],
        )
        return events

    def generate(self, population_path: str | Path) -> Mapping[str, pd.DataFrame]:
        """Generate all related tables for one scenario."""
        state_population = self.read_population(population_path)
        catalog = self.create_catalog()
        users = self.create_users(state_population)
        events = self.create_events(users, catalog)
        return {
            "state_population": state_population,
            "catalog": catalog,
            "users": users,
            "events": events,
        }

    @staticmethod
    def quality_report(
        tables: Mapping[str, pd.DataFrame]
    ) -> pd.Series:
        """Return compact relational-integrity and uniqueness checks."""
        users = tables["users"]
        catalog = tables["catalog"]
        events = tables["events"]
        return pd.Series(
            {
                "users": len(users),
                "tracks": len(catalog),
                "events": len(events),
                "duplicate_user_ids": int(users["user_id"].duplicated().sum()),
                "duplicate_track_ids": int(catalog["track_id"].duplicated().sum()),
                "duplicate_event_ids": int(events["event_id"].duplicated().sum()),
                "unknown_event_users": int(
                    (~events["user_id"].isin(users["user_id"])).sum()
                ),
                "unknown_event_tracks": int(
                    (~events["track_id"].isin(catalog["track_id"])).sum()
                ),
                "missing_event_values": int(events.isna().sum().sum()),
            },
            name="value",
        )
