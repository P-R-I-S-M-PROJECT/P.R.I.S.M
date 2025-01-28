// === USER'S CREATIVE CODE ===
// =====================================================================
// 1. Define classes at the top
// =====================================================================
class Agent {
  float x;         // Horizontal (column) position
  float baseY;     // Base vertical position
  float offset;    // Random offset for vertical oscillation
  float size = 10; // Smaller shapes to avoid touching
  int sides;       // Polygon sides
  int currentColumn;   // Track which column this agent is in
  color col;       // Current color of the agent

  Agent(float x_, float y_, int s, float off, int column, color initialCol) {
    x = x_;
    baseY = y_;
    sides = s;
    offset = off;
    currentColumn = column;
    col = initialCol;
  }

  void display(float progress) {
    // Smooth looping from 0..1 => swirlAngle from 0..TWO_PI
    float swirlAngle = progress * TWO_PI;

    // Vertical bobbing
    float yPos = baseY + 20 * sin(swirlAngle + offset);

    // Draw the shape
    pushMatrix();
    translate(x, yPos);
    stroke(255);
    strokeWeight(1);
    fill(col);
    beginShape();
    for (int i = 0; i < sides; i++) {
      float a = map(i, 0, sides, 0, TWO_PI);
      vertex(size * cos(a), size * sin(a));
    }
    endShape(CLOSE);
    popMatrix();
  }

  // Move to a new column (adjust x, sides, and color)
  void setColumn(int newCol) {
    currentColumn = newCol;
    sides = shapeForColumn[newCol]; // adopt this column's polygon sides
    // Recompute x for new column
    x = startX + newCol * colSpacing;
    // Change color to a random rainbow color
    col = rainbow[int(random(rainbow.length))];
  }
}

// =====================================================================
// 2. Declare global variables
// =====================================================================
Agent[] agents;
int columns = 20;
int rows = 10;
int numAgents = columns * rows;

int[] shapeForColumn = new int[columns]; // each column has a specific shape

// Spacing variables
float colSpacing = 30;
float rowSpacing = 30;
float startX, startY;

// Rainbow colors
color[] rainbow = {
  color(255, 0, 0),
  color(255, 127, 0),
  color(255, 255, 0),
  color(0, 255, 0),
  color(0, 0, 255),
  color(75, 0, 130),
  color(148, 0, 211)
};

// Track timing for column jumps
float lastCheck = 0;
int jumpInterval = 500; // check every 500ms

// =====================================================================
// 3. Define initSketch() - Called once at start
// =====================================================================
void initSketch() {
  // Assign a polygon side count to each column
  for (int c = 0; c < columns; c++) {
    shapeForColumn[c] = int(random(3, 7)); // 3..6 sides
  }

  // Create agents array
  agents = new Agent[numAgents];

  // Center them around (0,0)
  startX = -(columns - 1) * colSpacing / 2.0;
  startY = -(rows - 1) * rowSpacing / 2.0;

  // Populate agents
  int index = 0;
  for (int c = 0; c < columns; c++) {
    for (int r = 0; r < rows; r++) {
      float x = startX + c * colSpacing;
      float y = startY + r * rowSpacing;
      float off = random(TWO_PI);
      // Initial color is white
      color initialCol = color(255);
      agents[index++] = new Agent(x, y, shapeForColumn[c], off, c, initialCol);
    }
  }
}

// =====================================================================
// 4. Define runSketch(progress) - Called each frame with progress [0..1]
// =====================================================================
void runSketch(float progress) {
  // Check if enough time has passed to consider random column jumps
  if (millis() - lastCheck > jumpInterval) {
    lastCheck = millis();
    // 1% chance for each agent to jump columns
    for (int i = 0; i < numAgents; i++) {
      if (random(1) < 0.01) {
        // Move to a different column
        int newC = agents[i].currentColumn;
        // Ensure we pick a different column
        while (newC == agents[i].currentColumn) {
          newC = int(random(columns));
        }
        agents[i].setColumn(newC);
      }
    }
  }

  background(0);

  // Display each agent
  for (int i = 0; i < numAgents; i++) {
    agents[i].display(progress);
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