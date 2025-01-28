// === USER'S CREATIVE CODE ===
// ----------------------------------------------------
// 1) Define any classes at the top
// ----------------------------------------------------
class Agent {
  float baseAngle;
  float revolveSpeed;
  float baseRadius;
  float offset;

  Agent(float a, float rs, float br, float off) {
    baseAngle = a;
    revolveSpeed = rs;
    baseRadius = br;
    offset = off;
  }

  PVector getPos(float t) {
    // Position is determined by angle + time-driven rotation plus
    // a subtle radial oscillation for dynamic movement
    float angle = baseAngle + revolveSpeed * t;
    float r = baseRadius + 50 * sin(t + offset);
    return new PVector(cos(angle) * r, sin(angle) * r);
  }
}

// ----------------------------------------------------
// 2) Declare global variables
// ----------------------------------------------------
Agent[] agents;
int numAgents = 36; // Number of agents in the circle

// ----------------------------------------------------
// 3) initSketch() - Called once at start
// ----------------------------------------------------
void initSketch() {
  agents = new Agent[numAgents];
  // Distribute agents around the center with random speeds and slight randomness
  for (int i = 0; i < numAgents; i++) {
    float angle = map(i, 0, numAgents, 0, TWO_PI);
    float speed = random(2, 5);         // integer-ish rotation speeds for looping
    float rad   = random(150, 250);     // base radius for each agent
    float off   = random(TWO_PI);       // random offset for the radial oscillation
    agents[i]   = new Agent(angle, speed, rad, off);
  }
}

// ----------------------------------------------------
// 4) runSketch(progress) - Called each frame
//    progress goes from 0.0 to 1.0 over 6 seconds
// ----------------------------------------------------
void runSketch(float progress) {
  // Convert progress [0..1] to a full cycle [0..2PI]
  float t = progress * TWO_PI;

  // Set up drawing style
  noFill();
  strokeWeight(2);

  // Chromatic aberration offsets and colors
  PVector[] colorOffsets = {
    new PVector(  2,   0 ),  // slight shift right
    new PVector(  0,   2 ),  // slight shift down
    new PVector( -2,  -2 ),  // diagonal shift
    new PVector(  0,   0 )   // original position (white)
  };
  color[] colors = {
    color(255,   0,   0),
    color(  0, 255,   0),
    color(  0,   0, 255),
    color(255)          // white
  };

  // Draw four overlapping polygons with small positional shifts
  // to produce the chromatic aberration illusion
  for (int c = 0; c < 4; c++) {
    stroke(colors[c]);
    pushMatrix();
    translate(colorOffsets[c].x, colorOffsets[c].y);
    beginShape();
    for (int i = 0; i < numAgents; i++) {
      PVector pos = agents[i].getPos(t);
      vertex(pos.x, pos.y);
    }
    endShape(CLOSE);
    popMatrix();
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
        
        String renderPath = "renders/render_v4";
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