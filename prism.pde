// === USER'S CREATIVE CODE ===
// --------------------------------------
// 1. Define any classes at the top
// --------------------------------------
class WindParticle {
  float x, y;
  float oldX, oldY;

  WindParticle() {
    x = random(-540, 540);
    y = random(-540, 540);
    oldX = x;
    oldY = y;
  }

  void update(float time, float scale, float speed) {
    // Use noise to get a fluid, ever-shifting direction
    float angle = noise(x * scale, y * scale, time) * TWO_PI * 2.0;
    
    // Store old positions for trail drawing
    oldX = x;
    oldY = y;
    
    // Update position based on direction and speed
    x += cos(angle) * speed;
    y += sin(angle) * speed;

    // Wrap-around at edges to keep particles in view
    if (x < -540) x = 540;
    if (x >  540) x = -540;
    if (y < -540) y = 540;
    if (y >  540) y = -540;
  }

  void display() {
    // Monochrome line
    stroke(230, 50); 
    strokeWeight(1);
    line(oldX, oldY, x, y);
  }
}

// --------------------------------------
// 2. Declare global variables
// --------------------------------------
WindParticle[] windParticles;
int PARTICLE_COUNT = 400;  // Adjust for more or fewer trails

// --------------------------------------
// 3. Define initSketch() for setup
// --------------------------------------
void initSketch() {
  // Initialize particles
  windParticles = new WindParticle[PARTICLE_COUNT];
  for (int i = 0; i < PARTICLE_COUNT; i++) {
    windParticles[i] = new WindParticle();
  }
}

// --------------------------------------
// 4. Define runSketch(progress) for animation
// --------------------------------------
void runSketch(float progress) {
  // Map progress (0 to 1) to time and motion parameters
  float time = progress * 5.0;                  // Adjust for a slower/faster temporal flow
  float scale = map(progress, 0, 1, 0.0005, 0.003); // Scale factor for noise variation
  float speed = map(progress, 0, 1, 0.5, 3.0);  // Wind velocity
  
  // Update and display each particle
  for (int i = 0; i < PARTICLE_COUNT; i++) {
    windParticles[i].update(time, scale, speed);
    windParticles[i].display();
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