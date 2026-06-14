# Peripheral Blender quality brief (Gemini + LIGHTS ARE OFF refs)

Reference links included in prompt:
- https://youtube.com/shorts/R7cEIG_gqLU
- https://youtube.com/shorts/zCA4NuvoVXI
- https://youtu.be/S0x2llxEAjk
- https://youtu.be/lnDP902qeqw
- https://www.youtube.com/@LIGHTSAREOFF

---

Here's the breakdown for the gas station horror short, adhering to the LIGHTS ARE OFF quality bar:

## 1. What Makes the LIGHTS ARE OFF References Work

*   **Instant Environment Readability:** Even in low light, the viewer immediately understands the setting (pool, sewer, lab) within the first second. This is achieved through strong silhouette, iconic environmental elements, and deliberate composition.
*   **Masterful Dread-Building Through Lighting:** The lighting isn't just for visibility; it's a character. It uses harsh shadows, motivated light sources (flickering lights, car headlights), and subtle color shifts to create unease and guide the viewer's eye towards the threat.
*   **Precise Camera Work for Pacing:** Every camera move, from slow pushes to sudden pans, is intentional. They build tension, reveal information strategically, and punctuate the scares. The camera often acts as the viewer's eyes, enhancing immersion.
*   **Earned Reveals and Payoffs:** The scares aren't gratuitous. They are built up through atmosphere and anticipation, with the reveal of the creature or threat timed perfectly to maximize impact within the short runtime. The payoff feels earned by the preceding tension.
*   **"Finished" Blender Aesthetic:** Despite being entirely in Blender, the scenes feel tangible and real. Materials are well-chosen and applied, assets are integrated seamlessly, and the overall polish suggests a complete, intentional artistic vision, not a work-in-progress.

## 2. Concrete Fixes for Our Gas Station Draft

*   **Textures:**
    *   **Immediate Action:** Relink all broken FBX texture paths. Ensure all textures are located within the `Textures/` directory relative to the project file.
    *   **Material Check:** Verify that all imported textures have appropriate PBR properties (Albedo, Roughness, Normal, Metallic if applicable) and are correctly assigned in the shader nodes. Avoid flat, untextured grey surfaces.
    *   **Night-Appropriate Materials:** For the wet asphalt, ensure a subtle reflection map or roughness variation is present to catch the limited light. For signs, ensure emissive materials are set up correctly to glow.
*   **Lighting:**
    *   **Motivated Streetlights:** Re-establish the primary light sources as the gas station's overhead canopy lights and any visible streetlights. Implement a subtle flicker effect on these lights to create dynamic shadows and moments of partial darkness.
    *   **Key, Fill, Rim:** Apply a classic 3-point lighting setup, even for exteriors.
        *   **Key:** The primary light source (e.g., a flickering streetlight).
        *   **Fill:** A very dim, cool-toned fill light to lift shadows just enough to reveal form without eliminating mystery.
        *   **Rim:** A subtle rim light to separate the creature from the background, especially when it's at the tree line.
    *   **Color Grading:** Avoid crushing the albedo to black. Instead, use a desaturated, cool color palette for the night. Introduce subtle color variations (e.g., a hint of sickly green or blue from the pump lights) to enhance the unsettling atmosphere.
*   **Camera:**
    *   **Clip 1 (POV Walk):** Start with a steady, slightly low-angle POV walk towards the pumps. The camera should feel grounded and observant. The reveal of the figure at the tree line should be a slow pan or a subtle camera drift that draws attention.
    *   **Clip 2 (Uncanny Wave):** Use a slightly wider shot here, perhaps a slow push-in towards the pumps. The camera should capture the environment (canopy, signs, wet asphalt) clearly. The creature's wave should be framed to feel unnatural and isolated.
    *   **Clip 3 (Lunge):** A rapid, disorienting camera move. This could be a quick zoom or a sudden tilt/roll as the creature lunges. The final frame should be a tight close-up of the creature's face, with the emissive pump signs still visible and slightly out of focus in the background, providing context and a sense of place.
*   **Scale:**
    *   **Creature Integration:** Ensure the Form 2 creature is scaled correctly relative to the gas station environment. It should feel imposing but not so large that it breaks the believability of its interaction with the set. Ground it firmly on the asphalt.

## 3. EEVEE Settings Checklist

*   **Exposure:**
    *   **Enable:** Ensure "Exposure" is checked in the Render Properties.
    *   **Adjust:** Set a low "Min" and "Max" value to control the overall brightness and contrast, aiming for a dark, moody feel.
    *   **Contrast:** Fine-tune the "Contrast" slider to achieve punchy shadows and highlights without losing detail.
*   **Bloom:**
    *   **Enable:** Check "Bloom" in the Render Properties.
    *   **Threshold:** Set a moderate "Threshold" (e.g., 0.8-1.0) so only the brightest emissive elements (pump signs) bloom.
    *   **Intensity:** Keep "Intensity" low (e.g., 0.1-0.3) to avoid an overly "glowing" or unrealistic look.
    *   **Knee:** Adjust "Knee" for a softer bloom falloff.
*   **Probes (Light & Reflection):**
    *   **Light Probes:** Place several "Cube" or "Sphere" light probes throughout the scene, especially near the creature and the