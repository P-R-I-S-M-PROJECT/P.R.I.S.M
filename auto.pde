// === USER'S CREATIVE CODE ===
// Parameters for spiral particles
int numParticles = 200;
Particle[] particles;
float baseRadius = 250;

class Particle {
    float angle;
    float radius;
    float speed;
    float phase;
    int hue;
    
    Particle(float initAngle) {
        angle = initAngle;
        radius = random(50, baseRadius);
        speed = random(0.5, 2.0);
        phase = random(TWO_PI);
        hue = int(random(180, 255));
    }
    
    void update(float progress) {
        angle += 0.02 * speed;
        float wobble = sin(progress * TWO_PI * 2 + phase) * 20;
        float currentRadius = radius + wobble;
        
        float x = cos(angle) * currentRadius;
        float y = sin(angle) * currentRadius;
        
        float size = map(sin(progress * TWO_PI + phase), -1, 1, 2, 8);
        
        stroke(hue, 200, 255, 150);
        strokeWeight(size);
        point(x, y);
        
        // Draw connecting lines with fading opacity
        if (currentRadius < baseRadius - 30) {
            float nextX = cos(angle + 0.1) * (currentRadius + 10);
            float nextY = sin(angle + 0.1) * (currentRadius + 10);
            stroke(hue, 200, 255, 50);
            strokeWeight(0.5);
            line(x, y, nextX, nextY);
        }
    }
}

void initSketch() {
    colorMode(HSB, 255);
    particles = new Particle[numParticles];
    for (int i = 0; i < numParticles; i++) {
        particles[i] = new Particle(random(TWO_PI));
    }
}

void runSketch(float progress) {
    // Add subtle rotation to entire system
    rotate(progress * TWO_PI * 0.25);
    
    // Draw circular guide
    noFill();
    stroke(180, 50, 255, 30);
    strokeWeight(1);
    ellipse(0, 0, baseRadius * 2, baseRadius * 2);
    
    // Update and draw particles
    for (Particle p : particles) {
        p.update(progress);
    }
    
    // Draw central point
    stroke(200, 255, 255);
    strokeWeight(4);
    point(0, 0);
}
// === SYSTEM FRAMEWORK ===
void setup() {
    size(800, 800);
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
        
        String renderPath = "renders/render_v2352";
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