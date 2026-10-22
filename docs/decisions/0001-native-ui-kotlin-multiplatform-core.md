# 0001 — Native UI on each platform, shared Kotlin Multiplatform core

- Status: accepted
- Date: 2026-10-22
- Deciders: Gaurav, Claude

## Context
Kept depends on platform-specific pieces: share extensions, Apple Foundation
Models, Gemini Nano, Vision/ML Kit, background processing rules. The team is
two founders plus AI agents, so duplicated logic is expensive.

## Decision
SwiftUI (iOS) and Jetpack Compose (Android) for UI and platform AI.
Kotlin Multiplatform for shared logic: data model, filing, search ranking,
actions, backup and sync orchestration.

## Alternatives
- Fully native, no shared code: best fit, but every feature built twice.
- Flutter / React Native: one UI, but on-device AI and share extensions need
  heavy native modules anyway, and the UI feels less native.
- Compose Multiplatform UI on iOS: stable since 1.8.0, but we want the
  platform look and the simplest path to Apple's AI frameworks.

## Consequences
Shared logic is written once and tested once. iOS engineers work with a
Kotlin framework. Revisit if Compose Multiplatform clearly beats native for
our screens.
