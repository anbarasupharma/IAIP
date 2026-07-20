import tkinter as tk
import random
import colorsys

class MedSnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("⚕️ Med-Snake")
        self.root.configure(bg="#e0f2f1")
        self.root.geometry("450x660") 
        self.root.resizable(False, False)

        # Game Constants
        self.GRID_SIZE = 20
        self.TILE_COUNT = 20
        self.SPEED = 280  # Slower motion to make it kid-friendly

        # Variables
        self.score = 0
        self.high_score = 0
        self.game_over = False
        
        # --- UI Setup ---
        score_frame = tk.Frame(self.root, bg="#ffffff", bd=1, relief="solid", highlightbackground="#b2dfdb", highlightthickness=1)
        score_frame.pack(pady=10, padx=20, fill="x")

        self.lbl_score = tk.Label(score_frame, text="💊 0", font=("Segoe UI", 14, "bold"), bg="#ffffff", fg="#004d40")
        self.lbl_score.pack(side="left", padx=20, pady=5)

        self.lbl_high_score = tk.Label(score_frame, text="🏆 0", font=("Segoe UI", 14, "bold"), bg="#ffffff", fg="#004d40")
        self.lbl_high_score.pack(side="right", padx=20, pady=5)

        # Game Canvas
        self.canvas = tk.Canvas(self.root, width=400, height=400, bg="#ffffff", highlightthickness=4, highlightbackground="#00796b")
        self.canvas.pack()

        # --- Mobile / Touch Controls ---
        control_frame = tk.Frame(self.root, bg="#e0f2f1")
        control_frame.pack(pady=15)

        btn_font = ("Arial", 18)
        tk.Button(control_frame, text="⬆️", font=btn_font, width=4, command=lambda: self.set_direction(0, -1)).grid(row=0, column=1, pady=2)
        tk.Button(control_frame, text="⬅️", font=btn_font, width=4, command=lambda: self.set_direction(-1, 0)).grid(row=1, column=0, padx=2)
        tk.Button(control_frame, text="➡️", font=btn_font, width=4, command=lambda: self.set_direction(1, 0)).grid(row=1, column=2, padx=2)
        tk.Button(control_frame, text="⬇️", font=btn_font, width=4, command=lambda: self.set_direction(0, 1)).grid(row=2, column=1, pady=2)

        # Initialize Game
        self.reset_game()

        # Bind Keyboard Controls
        self.root.bind("<KeyPress>", self.handle_keypress)

        # Start the Game Loop
        self.update_game()

    def get_hex_from_hsl(self, h, s, l):
        """Converts HSL to Hex color codes for Tkinter."""
        r, g, b = colorsys.hls_to_rgb(h / 360.0, l / 100.0, s / 100.0)
        return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

    def reset_game(self):
        # Starting position and movement
        self.snake = [(10, 10)]
        self.dx = 0
        self.dy = 0
        self.game_over = False
        
        # Reset Score
        self.score = 0
        self.lbl_score.config(text=f"💊 {self.score}")
        
        # Special Food Variables
        self.special_food = None
        self.special_timer = 0
        self.blink_state = True
        
        # Snake Styling
        self.is_main_snake = True
        self.set_snake_colors()
        
        self.place_food()

    def set_snake_colors(self):
        """Sets the colors based on which alternate snake is currently active."""
        if self.is_main_snake:
            self.head_color = self.get_hex_from_hsl(174, 100, 35) # Teal
            self.body_color = self.get_hex_from_hsl(174, 100, 65)
        else:
            self.head_color = self.get_hex_from_hsl(280, 100, 45) # Purple
            self.body_color = self.get_hex_from_hsl(280, 100, 75)

    def place_food(self):
        """Randomly places the normal pill on the grid."""
        while True:
            self.food = (random.randint(0, self.TILE_COUNT - 1), random.randint(0, self.TILE_COUNT - 1))
            if self.food not in self.snake and self.food != self.special_food:
                break

    def place_special_food(self):
        """Places a high-dose drug (bonus points) on the grid."""
        while True:
            self.special_food = (random.randint(0, self.TILE_COUNT - 1), random.randint(0, self.TILE_COUNT - 1))
            if self.special_food not in self.snake and self.special_food != self.food:
                self.special_timer = 25  # It will disappear after 25 moves
                break

    def handle_keypress(self, event):
        """Routes keyboard arrows to the movement function."""
        key = event.keysym
        if key == "Left": self.set_direction(-1, 0)
        elif key == "Right": self.set_direction(1, 0)
        elif key == "Up": self.set_direction(0, -1)
        elif key == "Down": self.set_direction(0, 1)

    def set_direction(self, new_dx, new_dy):
        """Sets direction from either keyboard or touch buttons."""
        if self.game_over:
            self.reset_game()
            self.update_game() # Restart the loop
            return

        # Prevent reversing into itself
        if self.dx != 0 and new_dx == -self.dx: return
        if self.dy != 0 and new_dy == -self.dy: return
        
        self.dx, self.dy = new_dx, new_dy

    def update_game(self):
        """Core game logic loop."""
        if self.game_over:
            self.draw_elements() # Draw the game over screen once
            return # Stop the loop until reset

        if self.dx != 0 or self.dy != 0:
            head_x, head_y = self.snake[0]
            
            # Calculate new head position
            new_x = head_x + self.dx
            new_y = head_y + self.dy
            
            wrapped_border = False

            # Screen Wrapping Logic (Teleport to other side)
            if new_x < 0:
                new_x = self.TILE_COUNT - 1
                wrapped_border = True
            elif new_x >= self.TILE_COUNT:
                new_x = 0
                wrapped_border = True
                
            if new_y < 0:
                new_y = self.TILE_COUNT - 1
                wrapped_border = True
            elif new_y >= self.TILE_COUNT:
                new_y = 0
                wrapped_border = True

            new_head = (new_x, new_y)

            # Self-Collision Check (This is the only way to get Game Over now)
            if new_head in self.snake:
                self.game_over = True
            else:
                # If we passed through the border, swap the snake!
                if wrapped_border:
                    self.is_main_snake = not self.is_main_snake
                    self.set_snake_colors()

                self.snake.insert(0, new_head)
                
                # Normal Food Eating Check
                if new_head == self.food:
                    self.score += 1
                    self.lbl_score.config(text=f"💊 {self.score}")
                    
                    # 20% chance to spawn a special high-dose drug
                    if self.special_food is None and random.random() < 0.20:
                        self.place_special_food()
                        
                    self.place_food()
                    
                # Special Food Eating Check
                elif self.special_food and new_head == self.special_food:
                    self.score += 5  # Bonus points
                    self.lbl_score.config(text=f"💊 {self.score}")
                    self.special_food = None
                    
                    # Golden power-up color! (Will reset next time you pass the border)
                    self.head_color = self.get_hex_from_hsl(45, 100, 50)
                    self.body_color = self.get_hex_from_hsl(45, 100, 75)
                else:
                    self.snake.pop() # Remove tail if no food eaten

                # Update High Score
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.lbl_high_score.config(text=f"🏆 {self.high_score}")

        # Handle Special Food Timer
        if self.special_food:
            self.special_timer -= 1
            if self.special_timer <= 0:
                self.special_food = None # Disappears if not eaten fast enough

        # Draw the updated frame
        self.draw_elements()
        
        # Schedule the next frame
        self.root.after(self.SPEED, self.update_game)

    def draw_elements(self):
        """Clears the canvas and redraws all elements."""
        self.canvas.delete("all")

        # Game Over Screen
        if self.game_over:
            self.canvas.create_text(200, 170, text="GAME OVER", font=("Arial", 28, "bold"), fill="red")
            self.canvas.create_text(200, 220, text="Tap any button or press an arrow key\nto restart.", font=("Arial", 12), fill="#004d40", justify="center")
            return

        # Draw Normal Food (Pill Emoji)
        fx, fy = self.food
        self.canvas.create_text((fx * self.GRID_SIZE) + 10, (fy * self.GRID_SIZE) + 10, text="💊", font=("Arial", 14))

        # Draw Special Food (Blinking Syringe)
        if self.special_food:
            self.blink_state = not self.blink_state # Toggle visibility
            if self.blink_state:
                sx, sy = self.special_food
                self.canvas.create_text((sx * self.GRID_SIZE) + 10, (sy * self.GRID_SIZE) + 10, text="💉", font=("Arial", 16))

        # Draw Snake
        for i, (sx, sy) in enumerate(self.snake):
            color = self.head_color if i == 0 else self.body_color
            x1 = sx * self.GRID_SIZE
            y1 = sy * self.GRID_SIZE
            x2 = x1 + self.GRID_SIZE
            y2 = y1 + self.GRID_SIZE
            
            # Draw circular segments
            self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="")

if __name__ == "__main__":
    root = tk.Tk()
    app = MedSnakeGame(root)
    root.focus_force() 
    root.mainloop()