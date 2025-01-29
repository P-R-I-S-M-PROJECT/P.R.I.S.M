// === USER'S CREATIVE CODE ===
// -----------------------------------------------------
// 1) Define any classes at the top
// -----------------------------------------------------
class Agent {
  float baseAngle;   // Base angular position
  float baseRadius;  // Base radial distance from center
  float greyVal;     // Grayscale tone
  
  Agent(float angle, float radius) {
    baseAngle = angle;
    baseRadius = radius;
    // Randomize each agent's grayscale for subtle variation
    greyVal = random(80, 230);
  }
  
  // Display this agent as a skewed triangle for the optical illusion
  void display(float globalAngle, float skewFactor) {
    // Evolve each agent's angle by adding the global angle
    float angle = baseAngle + globalAngle;
    
    // Compute base position (circular layout)
    float xPos = cos(angle) * baseRadius;
    float yPos = sin(angle) * baseRadius;
    
    // Use grayscale stroke and a semi-transparent fill
    stroke(greyVal);
    fill(greyVal, 80);
    
    pushMatrix();
      // Translate agent to its position
      translate(xPos, yPos);
      
      // Apply skew/scale in Y to create an anamorphic distortion
      scale(1, skewFactor);
      
      // Rotate the triangle so it faces outward from the circle
      rotate(angle);
      
      // Draw a simple triangle
      float triSize = 20;
      triangle(-triSize/2, triSize/2, 
                0,         -triSize/2, 
                triSize/2, triSize/2);
    popMatrix();
  }
}

// -----------------------------------------------------
// 2) Declare global variables
// -----------------------------------------------------
Agent[] agents;       // Array of agents
int numAgents = 60;   // How many agents form the ring
float radius = 300;   // Base radius for placing agents

// -----------------------------------------------------
// 3) Define initSketch() for setup
// -----------------------------------------------------
void initSketch() {
  agents = new Agent[numAgents];
  
  // Distribute agents evenly around a circle
  for (int i = 0; i < numAgents; i++) {
    float angle  = map(i, 0, numAgents, 0, TWO_PI);
    float offset = random(-15, 15);  // Slight random radius offset
    agents[i] = new Agent(angle, radius + offset);
  }
}

// -----------------------------------------------------
// 4) Define runSketch(progress) for animation
// -----------------------------------------------------
void runSketch(float progress) {
  // Global rotation angle from 0..1 -> 0..TWO_PI
  float globalAngle = progress * TWO_PI;
  
  // Create a smooth skew factor to distort shapes:
  //   Skew from ~0.5..1.5 and back, ensuring a smooth loop
  float skewFactor = 1.0 + 0.5 * sin(globalAngle * 2.0);
  
  // Use no harsh fill edges
  noStroke();
  
  // Light outlines to accent geometry
  strokeWeight(1.5);
  
  // Draw each agent with the current global angle and skew
  for (Agent a : agents) {
    a.display(globalAngle, skewFactor);
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
        
        String renderPath = "renders/render_v25";
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