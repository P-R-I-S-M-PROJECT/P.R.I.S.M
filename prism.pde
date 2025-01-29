// === USER'S CREATIVE CODE ===
// -------------------------------------------
// 1) Classes for spring physics and particles
// -------------------------------------------
class GridNode {
  PVector origin;     // Original "rest" position
  PVector pos;        // Current position
  PVector vel;        // Velocity
  PVector acc;        // Acceleration
  float mass;         // Mass of the node, used in spring physics
  
  GridNode(float x, float y) {
    origin = new PVector(x, y);
    pos    = new PVector(x, y);
    vel    = new PVector();
    acc    = new PVector();
    mass   = 1.0;
  }
  
  void applyForce(PVector f) {
    // F = m * a => a = F/m
    acc.add(PVector.div(f, mass));
  }
  
  void update() {
    // Simple Euler integration
    vel.add(acc);
    pos.add(vel);
    acc.mult(0);
    // Dampen velocity slightly
    vel.mult(0.98);
  }
  
  void springToOrigin(float k) {
    // Hooke's law: F = -k * displacement
    PVector dir = PVector.sub(origin, pos);
    dir.mult(k);
    applyForce(dir);
  }
}

// -------------------------------------------
// 2) Global variables
// -------------------------------------------
GridNode[][] grid;
int cols = 20;
int rows = 20;
float spacing = 40;  // Distance between grid points
float springK = 0.02; // Spring constant
PGraphics letterMask; // Provided from the stub

// -------------------------------------------
// 3) initSketch() for setup
// -------------------------------------------
void initSketch() {
  // ----------------------------------------------------------------
  // A) Override the letterMask text with non-English "PRISM" text
  //    (Japanese "" meaning "PRISM" in English)
  // ----------------------------------------------------------------
  letterMask = createGraphics(1080, 1080);
  letterMask.beginDraw();
  letterMask.background(0);
  letterMask.fill(255);
  letterMask.textAlign(CENTER, CENTER);
  letterMask.textSize(200);
  letterMask.text("", letterMask.width/2, letterMask.height/2);
  letterMask.endDraw();
  
  // ----------------------------------------------------------------
  // B) Create a grid of nodes for spring-physics
  //    We'll center them around (0,0):
  // ----------------------------------------------------------------
  grid = new GridNode[cols][rows];
  float startX = -(cols-1)*spacing*0.5;
  float startY = -(rows-1)*spacing*0.5;
  
  for (int x = 0; x < cols; x++) {
    for (int y = 0; y < rows; y++) {
      float posX = startX + x * spacing;
      float posY = startY + y * spacing;
      grid[x][y] = new GridNode(posX, posY);
    }
  }
}

// -------------------------------------------
// 4) runSketch(progress) for animation
// -------------------------------------------
void runSketch(float progress) {
  // progress in [0..1], looping over 6 seconds
  // We'll create a fluid, organic motion with sine + noise forces
  // Also, let's map progress to an angle for looping
  float angle = progress * TWO_PI; // Ranges 0..2PI for a smooth loop

  // Load the letterMask pixels for text-based masking
  letterMask.loadPixels();
  
  // A) Update the grid nodes
  for (int x = 0; x < cols; x++) {
    for (int y = 0; y < rows; y++) {
      GridNode node = grid[x][y];
      
      // Spring force pulling node back to origin
      node.springToOrigin(springK);
      
      // Add an oscillating force to create fluid motion
      float nx = 0.01 * (x + 50*progress); 
      float ny = 0.01 * (y + 50*progress);
      // Combine noise with a sine wave for more variation
      float nForce = noise(nx, ny) - 0.5;
      float sForce = sin(angle + (x+y)*0.2) * 0.05;
      
      // Combine both forces in a random direction
      PVector extraForce = new PVector(nForce + sForce, -sForce + nForce);
      node.applyForce(extraForce);
      
      // Update node positions
      node.update();
    }
  }
  
  // B) Draw the grid connections within the text mask
  strokeCap(ROUND);
  for (int x = 0; x < cols-1; x++) {
    for (int y = 0; y < rows-1; y++) {
      // We'll link each node to the one at [x+1,y], [x,y+1] for a grid
      GridNode n1 = grid[x][y];
      GridNode n2 = grid[x+1][y];
      GridNode n3 = grid[x][y+1];
      
      // For each line segment, we check midpoint inside letterMask
      // We'll sample at the midpoint of the line (n1 -> n2, n1 -> n3)
      
      // Condition 1: Horizontal neighbor
      float midXh = (n1.pos.x + n2.pos.x) * 0.5 + width/2;
      float midYh = (n1.pos.y + n2.pos.y) * 0.5 + height/2;
      boolean isInMaskH = false;
      if (midXh >= 0 && midXh < width && midYh >= 0 && midYh < height) {
        color cH = letterMask.pixels[(int)midYh * width + (int)midXh];
        if (brightness(cH) > 127) {
          isInMaskH = true;
        }
      }
      if (isInMaskH) {
        // Stroke variation: thickness depends on distance from original
        float dist1 = PVector.dist(n1.pos, n1.origin);
        float dist2 = PVector.dist(n2.pos, n2.origin);
        float sw    = map(dist1+dist2, 0, 200, 1, 3);
        float shade = map(dist1+dist2, 0, 200, 180, 255); // grayscale
        stroke(shade);
        strokeWeight(sw);
        line(n1.pos.x, n1.pos.y, n2.pos.x, n2.pos.y);
      }
      
      // Condition 2: Vertical neighbor
      float midXv = (n1.pos.x + n3.pos.x) * 0.5 + width/2;
      float midYv = (n1.pos.y + n3.pos.y) * 0.5 + height/2;
      boolean isInMaskV = false;
      if (midXv >= 0 && midXv < width && midYv >= 0 && midYv < height) {
        color cV = letterMask.pixels[(int)midYv * width + (int)midXv];
        if (brightness(cV) > 127) {
          isInMaskV = true;
        }
      }
      if (isInMaskV) {
        float dist1 = PVector.dist(n1.pos, n1.origin);
        float dist3 = PVector.dist(n3.pos, n3.origin);
        float sw    = map(dist1+dist3, 0, 200, 1, 3);
        float shade = map(dist1+dist3, 0, 200, 180, 255);
        stroke(shade);
        strokeWeight(sw);
        line(n1.pos.x, n1.pos.y, n3.pos.x, n3.pos.y);
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
        
        String renderPath = "renders/render_v32";
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