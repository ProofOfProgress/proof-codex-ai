# Gemini review — Micro jumpscare draft #2

**Score:** 4 / 10 — **Pass:** False
**Summary:** Draft #2 shows significant issues with texture import and lighting, failing to meet the 'finished in Blender' quality bar. The environment is not readable, and the creature is not integrated into the scene. The 'ground void' is a critical technical issue.

## Potential
The core concept of a gas station lunge with a zombie attack motion has high viral potential for the 3-second scare format. The bait frame shows promise for establishing dread, and the lunge peak, if properly lit and integrated, could be impactful. The key is to achieve a 'finished' look that matches the reference channel.

## Mixamo motion
The 'Zombie Attack' motion is a good starting point for the lunge. Ensure the character's rig is correctly imported and that the animation plays smoothly. Pay attention to how the character's feet interact with the ground during the lunge to ensure it looks grounded and not like it's sliding or floating.

## Ground void fix
Ensure the ground plane has proper geometry and a material applied. Check for any holes or gaps in the mesh. If using a displacement map, ensure it's correctly applied and doesn't create transparency. Verify that the ground object is not set to be invisible or transparent in the render settings.

## Strengths
- The bait frame (0.15s) successfully establishes a sense of unease with the partially obscured figure in the background.
- The chosen Mixamo 'Zombie Attack' motion is appropriate for an aggressive lunge.
- The 3-second format with a clear hook and payoff is well-suited for viral shorts.
- The owner notes indicate a clear understanding of the desired horror tone and audio impact.

## Issues
- Windows texture paths broke during FBX import, resulting in untextured grey blocks and a failure to read the gas station environment.
- Night grade crushed albedo, creating a black void instead of a discernible scene.
- Procedural fallback cubes were visually dominant, indicating a failure of the intended environment assets.
- The ground has a visible 'void' or see-through issue, indicating a fundamental geometry or material problem.
- The creature (Form 2) is not integrated into the scene; it appears to be floating or not properly lit by the scene's lighting.
- Lighting is insufficient and does not create the intended horror atmosphere or motivate the scare.
- Camera work appears basic and not intentionally framed to build dread or emphasize the scare.

## Priority fixes
1. Relink textures and ensure all FBX assets are correctly imported with working texture paths.
2. Fix the 'ground void' issue by ensuring the ground geometry is solid and properly textured.
3. Re-light the scene using EEVEE best practices for night exteriors and horror lighting (key, fill, rim, motivated flicker).
4. Re-frame the camera to build dread and emphasize the lunge.
5. Integrate the creature into the scene by ensuring it's properly lit by the scene's lights and grounded on the environment.
6. Review and adjust materials to ensure they read correctly in low light.
7. Perform vision QC with the reference videos and this document before re-rendering.