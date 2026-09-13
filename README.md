# V🌔Space Cloud Browser V1

Browser-only public product foundation.

## Product structure
- Two Space families.
- Four authored public experiences:
  - Sand Moon — Moon
  - Sand Moon — Moon + Floor
  - Network Constellation — Field
  - Network Constellation — Journey
- Live microphone preview is the primary interaction.
- Optional one-minute browser recording.
- No cloud renderer, Python runtime, upload API, FFmpeg, or local V🌔Space paths are required by the deployed page.

## Asset boundary
`vspace-runtime.js` is intentionally flattened for the public prototype. It contains only browser-facing runtime material and does not mirror the private V🌔Space development directory structure.

## Local test
Use any static HTTP server. Microphone access works on localhost or HTTPS.

Example:
`python3 -m http.server 8788`

Open:
`http://127.0.0.1:8788`

## Deployment
The deployable static files are:
- index.html
- styles.css
- app.js
- vspace-runtime.js
- vspace_corner_logo.svg
- vspace_mark.svg

## Current fidelity note
The Network Field and Sand Moon geometry are derived from the uploaded ground truth.
The browser Journey camera and Moon + Floor presentation are conservative V1 public compositions built to establish the product/runtime structure; they are not claimed as exact ports of the separate local camera/floor experiments.

## V1.1 fidelity repair
- Network expression strengthened from the original mapper/shader vocabulary: breath, connection intensity, sparkle, onset impulses, warm bloom.
- Network Journey uses calm move/settle/observe/retreat/return phases derived from the uploaded persistent-camera ground truth.
- Floor Cosmos uses the exact three canonical SVG tile forms and six-row/border construction vocabulary.
- Sand Moon browser audio response is deliberately more perceptible while keeping the Moon silhouette bounded.

## V1.2 behavior grammar
- Sand Moon camera is fixed. All five variations are normalized to the same center and apparent size.
- Sand Moon sequence is V05 → V03 → V01 → V02 → V04, ten seconds each, repeating.
- Full 14,000-particle source geometry is restored for every Moon variation.
- Network Field camera is fixed; strong local graph bloom propagates by connection hops through the constellation.
- Network Journey uses the same graph-bloom grammar plus calm spatial travel.
- Moon + Floor cycles the same five Moon forms and uses the 5.5-second Particle Passage timing: 1.8s approach, 0.5s cover, 1.2s crossfade, 2.0s reveal.

## V1.2.1 hotfix
- Guards Moon variation lookup and runtime time state.
- Keeps the animation loop alive if one frame throws, so switching experiences remains possible.
- No visual grammar changes from V1.2.

## V1.2.2 single-scope correction
- Network Journey restored to the earlier calm travel presentation.
- Network Field retains the V1.2 fixed-camera traveling bloom.
- No Moon or Floor behavior changed.

## V1.2.3 Journey camera rhythm
Only Network Journey changed.

Journey rhythm:
- 0–15s wide establish
- 15–22s move inward
- 22–35s hold detail
- 35–45s pull back
- 45–55s wide pause
- 55–63s move inward from another angle
- 63–74s hold second detail
- 74–80s smooth pull out
- repeat with another bounded interior target

No hard cuts. Field, Sand Moon, and Moon + Floor are unchanged.

## V1.2.4 Journey deep-entry correction
Only Network Journey changed.

- Camera now crosses into the constellation rather than merely zooming.
- Near distance reduced to roughly 1.0–1.2 model units.
- Perspective expands enough that nearby lines/nodes leave multiple frame sides.
- Entry lasts 10s, interior observation 13s, retreat 12s, wide pause 10s.
- Second entry repeats from another bounded interior angle.
- No hard cuts.
- Field, Sand Moon, and Moon + Floor are unchanged.

## V1.2.5 Network Field sensitivity + halo grammar
Only Network Field changed.

- Camera and constellation geometry remain fixed.
- Node/core size is fixed; music never makes the star itself larger.
- Physical connection-line width is fixed.
- Glow is rendered as a separate halo around nodes and lines.
- Halo propagates through connected graph regions.
- Field alternates deterministic-irregular quiet/sensitive windows:
  6s quiet / 14s sensitive / 8s quiet / 18s sensitive /
  5s quiet / 12s sensitive / 9s quiet / 16s sensitive.
- Sensitive windows use a much lower activation threshold and much stronger halo gain.
- Network Journey and both Sand Moon experiences are untouched.

## V1.2.6 Field halo refinement
Only Network Field changed.
- Node halo brightness reduced to about 70% of V1.2.5.
- Halo radius reduced to about 90%.
- Node cores remain fixed-size.
- Node halos remain circular/radial with softer smoky falloff.
- Connection glow is no longer a thick packed bar: it is layered into delicate,
  round-capped, uneven traveling wisps around the unchanged physical line.
- Journey and both Moon experiences are untouched.

## V1.2.7 Moon + Floor endless floor passage
Only Sand Moon — Moon + Floor changed.

- Existing floor shape language and external-sound response are preserved.
- Floor rows now travel continuously from the horizon toward and through the viewer.
- Rows recycle at the far end so depth reads as indefinite rather than a finite stage.
- Passage periods add a modest forward-speed boost so the floor follows the camera passage.
- More far rows/columns keep the floor continuous deep into the frame.
- Plain Moon, Network Field, and Network Journey are untouched.

## V1.2.8 Moon visibility + floor frame extension
Changes are limited to the two Sand Moon experiences and the Moon + Floor surface.

Moon (shared by Moon and Moon + Floor):
- Moon brightness is no longer driven by the external microphone.
- Current browser has no separate internal/system-audio analyser, so Moon uses a
  neutral state rather than incorrectly reacting to the microphone.
- Particle cores are much brighter and always visible.
- Each source particle gets a small warm halo.
- A deterministic secondary micro-grain visually doubles particle density while
  preserving the authoritative 14k-point source geometry.

Moon + Floor:
- Floor keeps external microphone reactivity.
- Near rows now extend through the lower canvas edge instead of stopping mid-frame.
- Floor width is expanded so perspective continues beyond the visible frame.
- Existing endless forward row recycling remains.

Network Field and Network Journey are untouched.
