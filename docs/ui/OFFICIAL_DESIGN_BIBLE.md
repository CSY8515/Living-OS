# Living OS Official Design Bible

## Product idea

Living OS is a personal world, not an administration dashboard. The user does
not feel that they are opening a menu of database tables; they feel that they
are entering a living environment that reflects today, growth, memory, and
direction.

The project name **Living OS** remains English. User-facing actions and
explanations are Korean-first.

## World principles

- The Home surface is a world entrance and an operating hub, not a KPI wall.
- Life, growth, nature, and space form one quiet visual universe.
- A central living object may represent the Core, continuity, or personal state.
- Supporting objects represent reachable capabilities without exposing internal
  architecture names.
- Subsystem, Engine, Registry, schema, and execution details belong in explicit
  management surfaces, not the primary personal experience.
- Information appears when it is relevant; empty space is part of the system.
- Ordinary SaaS card grids are minimized. A card is used only when the content
  genuinely needs a contained reading surface.

## Symbolic objects

Official concept work may use a restrained set of recurring objects:

- Core: continuity, identity, and the current moment.
- Orbit/path: reachable areas of life and movement between them.
- Seed/tree/light: growth, learning, and accumulated care.
- Constellation: relationships between records without implying causation.
- Horizon: future intention and calm system depth.

These are interaction and meaning devices, not decorative wallpaper.

## Authority

Official Concept Art is the final visual reference. Implementers reproduce its
approved composition, material, hierarchy, and mood within accessible UI
constraints. They do not create a new unofficial design, copy a commercial
product, or treat a generated mood board as the product.

If Concept Art has not been registered in `CONCEPT_ART/`, implementation must
pause at documentation and structural preparation. Missing art is not replaced
with invented final artwork.

## Architecture boundary

- Experience code calls public Subsystem interfaces only.
- Visual components do not own business rules or persistence.
- Domain state is never inferred from animation.
- A decorative object cannot masquerade as a control.
- Navigation labels and routes remain stable unless separately approved.
