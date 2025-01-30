// === USER'S CREATIVE CODE ===
// -----------------------------------------
// 1) Define any classes at the top
// -----------------------------------------
class Layout {
  PVector[][] positions;
  float[][] sizes;
  float[][] shades;
  
  Layout(int n) {
    positions = new PVector[n][n];
    sizes     = new float[n][n];
    shades    = new float[n][n];
  }
}

// -----------------------------------------
// 2) Declare global variables
// -----------------------------------------
final int N = 8;        // Number of squares per row/column
Layout[] layouts = new Layout[3]; 
int[] seeds = new int[3]; // Each layout gets its own random seed

// -----------------------------------------
// 3) Define initSketch() for setup
// -----------------------------------------
void initSketch() {
  // Generate distinct seeds for the 3 layouts
  for(int i = 0; i < 3; i++){
    seeds[i] = (int) random(100000);
  }
  
  // Create the 3 layouts
  for(int i = 0; i < 3; i++){
    layouts[i] = generateLayout(seeds[i]);
  }
}

// Utility to generate random city-like layout
Layout generateLayout(int seed) {
  randomSeed(seed);
  Layout newLayout = new Layout(N);
  
  // Random spacing that influences overall grid pattern
  float spacing = random(60, 90);
  
  for (int r = 0; r < N; r++) {
    for (int c = 0; c < N; c++) {
      // Base location with some random offset
      float xBase = (c - N/2.0) * spacing;
      float yBase = (r - N/2.0) * spacing;
      float offsetX = random(-spacing * 0.3, spacing * 0.3);
      float offsetY = random(-spacing * 0.3, spacing * 0.3);

      // Store position
      newLayout.positions[r][c] = new PVector(xBase + offsetX, yBase + offsetY);

      // Random size and grayscale
      newLayout.sizes[r][c]  = random(spacing * 0.3, spacing * 0.8);
      newLayout.shades[r][c] = random(40, 220);
    }
  }
  return newLayout;
}

// -----------------------------------------
// 4) Define runSketch(progress) for animation
// -----------------------------------------
void runSketch(float progress) {
  // We have 3 layouts, each active for 2 seconds in a 6-second loop
  // progress goes 0..1 over 6 seconds
  // segment = floor(progress*3): 0,1,2
  // segment fraction = progress*3 - segment
  // we morph layouts[segment] => layouts[(segment+1)%3]
  
  float seg = progress * 3.0;       // 0..3
  int segIndex = floor(seg);        // which segment: 0..2
  float segFrac = seg - segIndex;   // fraction within segment (0..1)
  
  Layout fromL = layouts[segIndex];
  Layout toL   = layouts[(segIndex + 1) % 3];
  
  // Draw squares
  rectMode(CENTER);
  noStroke();
  
  for (int r = 0; r < N; r++) {
    for (int c = 0; c < N; c++) {
      // Interpolate position
      PVector p0 = fromL.positions[r][c];
      PVector p1 = toL.positions[r][c];
      float x = lerp(p0.x, p1.x, segFrac);
      float y = lerp(p0.y, p1.y, segFrac);
      
      // Interpolate size
      float s0 = fromL.sizes[r][c];
      float s1 = toL.sizes[r][c];
      float sz = lerp(s0, s1, segFrac);

      // Interpolate shade
      float sh0 = fromL.shades[r][c];
      float sh1 = toL.shades[r][c];
      float shade = lerp(sh0, sh1, segFrac);
      
      fill(shade);
      rect(x, y, sz, sz);
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
        
        String renderPath = "renders/render_v9";
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