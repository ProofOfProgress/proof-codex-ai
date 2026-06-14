# Peripheral Blender quality brief (Gemini + LIGHTS ARE OFF refs)

Reference links included in prompt:
- https://youtube.com/shorts/R7cEIG_gqLU
- https://youtu.be/S0x2llxEAjk
- https://youtu.be/lnDP902qeqw
- https://www.youtube.com/@LIGHTSAREOFF

---

Here's the breakdown for the gas station horror shorts, focusing on achieving the LIGHTS ARE OFF Blender aesthetic:

## 1. What Makes the LIGHTS ARE OFF References Work

*   **Immediate Environmental Readability:** The viewer instantly understands the setting (e.g., a dark, isolated lab, a murky swimming pool) within the first second, establishing mood and context without exposition.
*   **Grounded, Tangible World:** Despite being CG, the environments feel lived-in and real. Materials are believable, lighting interacts realistically with surfaces, and assets are placed with intention, avoiding a "CG" feel.
*   **Purposeful, Cinematic Camera Work:** Every shot feels deliberate. Camera movements (dolly, push-in, subtle pans) and framing (rule of thirds, leading lines) guide the viewer's eye and build tension, mimicking live-action cinematography.
*   **Atmospheric, Horror-Focused Lighting:** Lighting is not just for visibility; it's a narrative tool. Shadows are deep, light sources are motivated (flickering fluorescents, dim streetlights), and contrast is used to create unease and highlight key elements.
*   **Integrated Creature Presentation:** The creatures are not just "placed" in the scene. They are lit by the same environmental lights, cast shadows, and interact with the world, making them feel like a genuine, terrifying part of the environment.

## 2. Concrete Fixes for Our Gas Station Draft

**Lighting:**

*   **Re-establish Key/Fill/Rim:** The current "black void" indicates a lack of fill light and potentially missing key/rim.
    *   **Key Light:** Use the gas station's overhead canopy lights and any visible interior lights as the primary source. These should be low-intensity but have a distinct color temperature (e.g., sickly yellow-green).
    *   **Fill Light:** Introduce very subtle, cool-toned fill light from the environment (e.g., distant moonlight, ambient sky light) to lift shadows just enough to reveal form without dispelling the darkness. This is crucial for readability.
    *   **Rim Light:** Use the headlights of any unseen vehicles, or the glow from the gas pumps themselves, to create subtle rim lighting on the creature and foreground elements, separating them from the background.
*   **Motivated Flicker:** The streetlight flicker mentioned in the codex is paramount. Implement a subtle, irregular flicker on the main overhead gas station lights and any streetlights. This should be timed to reveal the creature or specific details.
*   **Color Grading:** Avoid crushing the albedo. Instead, use EEVEE's color management to achieve a dark, desaturated night look with specific color accents (e.g., the pump sign colors, the creature's potential emissive elements).

**Textures:**

*   **Relink FBX Paths:** This is the top priority. Ensure all texture paths are correctly set up to point to the `Textures/` directory. This means checking UV mapping and material assignments in Blender.
*   **Material PBR Work:** Even for a night scene, materials need to have appropriate PBR values (roughness, metallic, normal maps). The asphalt should have subtle wetness/grime, the building should have weathered paint, and the signs should have a distinct emissive quality.
*   **Avoid Flatness:** Ensure textures have enough detail (normal maps, bump maps) to read as surfaces, not just flat colors, even in low light.

**Camera:**

*   **Clip 1 (POV toward pumps):** Start with a slow, steady forward dolly or a subtle handheld feel. The camera should be at human eye-level. The reveal of the figure should happen as the camera moves, not as a static shot.
*   **Clip 2 (Uncanny wave):** A slightly wider shot, perhaps a slow push-in or a static shot with subtle camera shake. The focus is on the creature's unnatural movement and the visible environment (canopy, signs, wet asphalt). Ensure the wet asphalt reflects the limited light sources.
*   **Clip 3 (Lunge):** A rapid, disorienting push-in or a Dutch tilt as the creature lunges. The camera should feel like it's being attacked. The background elements (emissive signs) must remain visible and readable, adding to the chaos.

**Scale:**

*   **Form 2 Creature:** Ensure the Form 2 creature is scaled correctly relative to the gas station elements (pumps, canopy, building). It should feel imposing and out of place, but not so large that it breaks the believability of the environment. The "too-tall" aspect should be a deliberate, unsettling exaggeration, not an accidental scaling error.
*   **Grounding:** The creature must be firmly planted on the ground plane. No floating or clipping through the asphalt.

## 3. EEVEE Settings Checklist

*   **Render Properties:**
    *   **Render Engine:** EEVEE
    *   **Viewport Performance:** Enable "High Quality Normals" and "Screen Space Reflections" if applicable for previews.
    *   **Shadows:**
        *   **Cube Size/Cascade Size:** Set to highest quality (e.g., 2048 or 4096) for sharp, detailed shadows.
        *   **Soft Shadows:** Enable for a more natural falloff, but be mindful of performance.
    *   **Bloom:**
        *   **Enable:** Crucial for the glowing effect of signs and potential creature emissives.
        *   **Threshold:** Adjust to control what glows.
        *   **Intensity:** Control the strength