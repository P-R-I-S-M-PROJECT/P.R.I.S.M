// === USER'S CREATIVE CODE ===
// -----------------------------------------------------
// 1) Classes
// -----------------------------------------------------
class Particle {
  float x, y;       // Current position
  float vx, vy;     // Velocity
  float ax, ay;     // Acceleration
  float baseX, baseY;  // Unshifted grid position
  float k = 0.1;    // Spring stiffness
  float damping = 0.8; // Damping factor

  Particle(float px, float py) {
    baseX = px;
    baseY = py;
    x = px;
    y = py;
    vx = vy = 0;
  }

  // We only move vertically, so anchorX is constant
  void update(float anchorY) {
    // Spring force to anchor
    float force = k * (anchorY - y);
    ay = force;
    vy += ay;
    y += vy;
    vy *= damping;
  }
}

// -----------------------------------------------------
// 2) Global Variables
// -----------------------------------------------------
PGraphics letterMask;
Particle[][] grid;

// Increased number of columns/rows for more particles
int cols = 100;
int rows = 35;

float spacingX;        
float spacingY;        
color c1, c2;          
// Increased wave amplitude for more dramatic motion
float waveAmp = 60;    

// -----------------------------------------------------
// 3) Initialize
// -----------------------------------------------------
void initSketch() {
  // Initialize mask for text "PRISM" (kept same size but you can adjust if desired)
  letterMask = createGraphics(1080, 1080);
  letterMask.beginDraw();
  letterMask.background(0);
  letterMask.fill(255);
  letterMask.textAlign(CENTER, CENTER);
  letterMask.textSize(200);
  letterMask.text("PRISM", letterMask.width/2, letterMask.height/2);
  letterMask.endDraw();

  // Setup grid
  spacingX = 1080.0/(cols - 1);
  spacingY = 1080.0/(rows - 1);
  grid = new Particle[cols][rows];

  // Complementary color pair (kept, but feel free to experiment)
  c1 = color(255, 130, 0);   // Orange
  c2 = color(0, 200, 255);   // Teal

  // Create particles
  for(int i = 0; i < cols; i++) {
    for(int j = 0; j < rows; j++) {
      float px = -540 + i * spacingX;
      float py = -540 + j * spacingY;
      grid[i][j] = new Particle(px, py);
    }
  }
}

// -----------------------------------------------------
// 4) Animation Loop
//    progress goes 0.0 -> 1.0 -> 0.0 in a 6-second loop
// -----------------------------------------------------
void runSketch(float progress) {
  
  // Light fade each frame to increase text visibility
  noStroke();
  fill(0, 30);
  rectMode(CENTER);
  rect(0, 0, 1080, 1080);

  // A full cycle of sin() for a smooth loop
  float angleOffset = TWO_PI * progress;

  // Update/draw each particle
  for(int i = 0; i < cols; i++) {
    for(int j = 0; j < rows; j++) {
      Particle p = grid[i][j];

      // Traveling wave in vertical direction
      float wave = waveAmp * sin(angleOffset + (float)i * 0.2);
      float anchorY = p.baseY + wave;
      p.update(anchorY);

      // Convert to mask coordinates
      int maskX = int(p.x + 540);
      int maskY = int(p.y + 540);

      // Safety check on bounds
      if(maskX < 0 || maskX >= 1080 || maskY < 0 || maskY >= 1080) continue;

      // If the pixel is lit, draw a smaller particle
      float bright = brightness(letterMask.get(maskX, maskY));
      if(bright > 20) {
        // Horizontal gradient between c1 and c2
        float t = map(p.x, -540, 540, 0, 1);
        color col = lerpColor(c1, c2, constrain(t, 0, 1));

        noStroke();
        fill(col);
        // Smaller elliptical particles
        ellipse(p.x, p.y, 3, 3);
      }
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
        
        String renderPath = "renders/render_v35";
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