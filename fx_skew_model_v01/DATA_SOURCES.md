# Datenquellen-Plan

Primäre Kandidaten für echte Marktdaten sind CME (Greeks / Implied Volatility / DataMine) und LSEG (FX Volatility Surface). Vor produktiver Nutzung müssen insbesondere 25-delta-Definition, Spot/Forward-Delta, premium-adjusted vs regular delta, RR-Vorzeichen, Bid/Ask/Mid und Snapshot-Zeit dokumentiert werden.

Der Prototyp erwartet einen normalisierten täglichen Datensatz und mischt verschiedene Datenanbieter nicht innerhalb eines Samples.
