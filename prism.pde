// === USER'S CREATIVE CODE ===
// -----------------------------------------------------
// 1) CLASSES
// -----------------------------------------------------
class Agent {
  float baseAngle;   // Fixed angular position on the circle
  float offset;      // Random phase offset for sin wave
  float baseRadius;  // Base distance from center
  float waveAmp;     // Magnitude of radial wave

  Agent(float angle, float off, float bR, float wAmp) {
    baseAngle   = angle;
    offset      = off;
    baseRadius  = bR;
    waveAmp     = wAmp;
  }

  // Return current position based on time t
  PVector getPosition(float t) {
    // Oscillate radius to create "breathing" effect
    float r = baseRadius + waveAmp * sin(4.0 * t + offset);
    float x = r * cos(baseAngle);
    float y = r * sin(baseAngle);
    return new PVector(x, y);
  }
}

// -----------------------------------------------------
// 2) GLOBAL VARIABLES
// -----------------------------------------------------
Agent[] agents;
int numAgents = 200;

// -----------------------------------------------------
// 3) INIT SKETCH
// -----------------------------------------------------
void initSketch() {
  agents = new Agent[numAgents];
  for (int i = 0; i < numAgents; i++) {
    float angle = (TWO_PI * i) / numAgents;
    float off   = random(TWO_PI);
    // Construct each agent with a base angle, offset,
    // a moderate radius, and a wave amplitude
    agents[i] = new Agent(angle, off, 300, 80);
  }
}

// -----------------------------------------------------
// 4) RUN SKETCH
// -----------------------------------------------------
void runSketch(float progress) {
  // "progress" goes from 0.0 to 1.0; map that to 0..TWO_PI
  float t = progress * TWO_PI;

  // Rotate the entire scene for a full revolution
  pushMatrix();
  rotate(t);

  stroke(255);
  noFill();
  strokeWeight(2);

  // Draw lines between agents to create patterned moir
  for (int i = 0; i < numAgents; i++) {
    PVector p1 = agents[i].getPosition(t);
    // Connect to next agent
    PVector p2 = agents[(i + 1) % numAgents].getPosition(t);
    // Also connect to the "opposite" agent for extra complexity
    PVector p3 = agents[(i + numAgents / 2) % numAgents].getPosition(t);

    line(p1.x, p1.y, p2.x, p2.y);
    line(p1.x, p1.y, p3.x, p3.y);
  }
  popMatrix();
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
        
        String renderPath = "renders/render_v3";
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