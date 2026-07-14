"""Allowed mood / activity / genre values (keep these locked)."""

from enum import Enum


class Mood(str, Enum):
    happy = "happy"
    sad = "sad"
    excited = "excited"
    bored = "bored"
    calm = "calm"
    energetic = "energetic"
    focused = "focused"


class Activity(str, Enum):
    study = "study"
    work = "work"
    party = "party"
    relax = "relax"
    workout = "workout"
    commute = "commute"


class Genre(str, Enum):
    lo_fi = "lo-fi"
    ambient = "ambient"
    electronic = "electronic"
    dance = "dance"
    indie = "indie"
    folk = "folk"
    rock = "rock"
    jazz = "jazz"
