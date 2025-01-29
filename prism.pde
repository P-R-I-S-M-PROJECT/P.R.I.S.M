// === USER'S CREATIVE CODE ===
// ------------------------------------------------------
// 1) Classes (if any); for this sketch, none needed
// ------------------------------------------------------

// ------------------------------------------------------
// 2) Global variables
// ------------------------------------------------------
color c1, c2;          // Two complementary base colors
int gridCount = 13;    // Number of cells along each dimension
float cellSize = 80;   // Distance between cell centers

// ------------------------------------------------------
// 3) initSketch() - Called once at start
// ------------------------------------------------------
void initSketch() {
  // Define complementary colors (e.g., pinkish and bluish)
  c1 = color(255, 50, 80);
  c2 = color(80, 200, 255);
}

// ------------------------------------------------------
// 4) runSketch(progress) - Called every frame
//    progress: 0.0 -> 1.0 over 6 seconds, loops smoothly
// ------------------------------------------------------
void runSketch(float progress) {
  
  // Overall angle to foster looping motion
  float swirlAngle = progress * TWO_PI; // rotates full circle from 0..1
  
  // Use sine wave to modulate color blending over time
  float colorFactor = 0.5 + 0.5 * sin(progress * TWO_PI);
  color dynamicColor = lerpColor(c1, c2, colorFactor);
  
  // Loop over the grid
  float offset = (gridCount - 1) * cellSize * 0.5; // for centering
  for (int row = 0; row < gridCount; row++) {
    for (int col = 0; col < gridCount; col++) {
      
      // Calculate base position
      float x = col * cellSize - offset;
      float y = row * cellSize - offset;
      
      // "Glitch" value from Perlin noise (smooth randomness)
      // This value changes over time and across the grid
      float n = noise(col * 0.3, row * 0.3, progress * 2.0);
      // Map noise [0..1] to [-1..1]
      float glitchVal = map(n, 0, 1, -1, 1);
      
      // Use glitchVal to create slight random translation & rotation
      float transOffset = glitchVal * 8.0;         // random shift in position
      float angleOffset = glitchVal * swirlAngle * 0.3; // random shift in rotation
      
      pushMatrix();
      // Translate to cell center + glitch offset
      translate(x + transOffset, y - transOffset);
      // Apply a small rotation glitch
      rotate(angleOffset);
      
      // Draw arcs in two opposing motion sets to create a strong motion illusion
      noFill();
      stroke(dynamicColor);
      strokeWeight(2);
      
      // Adjust radius to fit each cell nicely
      float r = cellSize * 0.6;
      int arcCount = 8; // number of arcs per swirl set
      
      // First swirl set (rotates in sync with swirlAngle)
      for (int i = 0; i < arcCount; i++) {
        float startA = swirlAngle + i * (TWO_PI / arcCount) * 0.5;
        float endA   = startA + (TWO_PI / arcCount) * 0.5;
        arc(0, 0, r, r, startA, endA);
      }
      
      // Second swirl set (opposite direction)
      stroke(lerpColor(c2, c1, colorFactor)); // invert the color blend
      for (int j = 0; j < arcCount; j++) {
        float startB = -swirlAngle + j * (TWO_PI / arcCount) * 0.5;
        float endB   = startB + (TWO_PI / arcCount) * 0.5;
        arc(0, 0, r * 0.9, r * 0.9, startB, endB);
      }
      
      popMatrix();
    }
  }
}
// END OF YOUR CREATIVE CODE

// === SYSTEM FRAMEWORK ===
void setup() {
    size(1080, 1080);
    frameRate(60);
    smooth();
    initSketch();  // Initialize user's sketch
}

final int totalFrames = 360;
boolean hasError = false;

void draw() {
    try {
        background(0);
        stroke(255);  // Default stroke but can be changed
        float progress = float(frameCount % totalFrames) / totalFrames;
        translate(width/2, height/2);
        
        runSketch(progress);  // Run user's sketch with current progress
        
        String renderPath = "renders/render_v13";
        saveFrame(renderPath + "/frame-####.png");
        if (frameCount >= totalFrames) {
            exit();
        }
    } catch (Exception e) {
        println("Error in draw(): " + e.toString());
        hasError = true;
        exit();
    }
}