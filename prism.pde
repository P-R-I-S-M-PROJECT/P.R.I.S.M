// === USER'S CREATIVE CODE ===
class GridPoint {
  float x;
  float y;
  
  GridPoint(float x, float y) {
    this.x = x;
    this.y = y;
  }
}

GridPoint[][] grid;
float gridSpacing = 60;
int cols, rows;

void initSketch() {
  cols = int(width / gridSpacing) + 1;
  rows = int(height / gridSpacing) + 1;
  grid = new GridPoint[cols][rows];
  
  // Initialize grid points centered at (0,0)
  for(int i = 0; i < cols; i++) {
    for(int j = 0; j < rows; j++) {
      float x = (i - cols/2) * gridSpacing;
      float y = (j - rows/2) * gridSpacing;
      grid[i][j] = new GridPoint(x, y);
    }
  }
}

void runSketch(float progress) {
  float angle = progress * TWO_PI;
  float amplitude = 30;
  
  for(int i = 0; i < cols; i++) {
    for(int j = 0; j < rows; j++) {
      GridPoint p = grid[i][j];
      
      // Apply sinusoidal deformation for smooth looping
      float displacedX = p.x + amplitude * sin(angle + p.y * 0.05);
      float displacedY = p.y + amplitude * cos(angle + p.x * 0.05);
      
      // Calculate RGB color based on displaced positions
      float r = map(displacedX, -width/2, width/2, 50, 255);
      float g = map(displacedY, -height/2, height/2, 100, 255);
      float b = 200 + 55 * sin(angle + p.x * 0.05);
      stroke(constrain(r, 0, 255), constrain(g, 0, 255), constrain(b, 100, 255));
      strokeWeight(2);
      
      // Draw lines to the right neighbor
      if(i < cols - 1) {
        GridPoint right = grid[i+1][j];
        float displacedXR = right.x + amplitude * sin(angle + right.y * 0.05);
        float displacedYR = right.y + amplitude * cos(angle + right.x * 0.05);
        line(displacedX, displacedY, displacedXR, displacedYR);
      }
      
      // Draw lines to the bottom neighbor
      if(j < rows - 1) {
        GridPoint bottom = grid[i][j+1];
        float displacedXB = bottom.x + amplitude * sin(angle + bottom.y * 0.05);
        float displacedYB = bottom.y + amplitude * cos(angle + bottom.x * 0.05);
        line(displacedX, displacedY, displacedXB, displacedYB);
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