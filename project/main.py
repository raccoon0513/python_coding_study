import tkinter as tk
import pygetwindow as gw
import random
import math

class DesktopBrickBreaker:
    def __init__(self, root):
        self.root = root
        self.root.title("Desktop Breaker Overlay")
        
        
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-transparentcolor", "black") 
        self.root.attributes("-topmost", True)
        self.root.configure(bg="black")

        
        self.canvas = tk.Canvas(root, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()

        
        self.state = "COUNTDOWN"
        self.countdown_val = 5
        self.lives = 5
        
        
        self.bricks = []
        self.balls = []
        self.powerups = []
        self.bullets = []
        self.particles = [] 
        
        
        self.gun_level = 0
        self.shoot_timer = 0
        self.firework_timer = 0
        
        
        self.lives_text = self.canvas.create_text(
            30, self.screen_h - 30, text=f"Lives: {self.lives}", 
            fill="white", font=("Arial", 24, "bold"), anchor="sw"
        )
        self.center_text = self.canvas.create_text(
            self.screen_w // 2, self.screen_h // 2, 
            text="", fill="white", font=("Arial", 72, "bold")
        )

        self.create_bricks()
        self.start_countdown()
        self.update_game()

    def start_countdown(self):
        self.state = "COUNTDOWN"
        self.countdown_val = 5
        self.canvas.itemconfig(self.center_text, text=str(self.countdown_val))
        self.tick_countdown()

    def tick_countdown(self):
        if self.countdown_val > 0:
            self.canvas.itemconfig(self.center_text, text=str(self.countdown_val))
            self.countdown_val -= 1
            self.root.after(1000, self.tick_countdown)
        else:
            self.canvas.itemconfig(self.center_text, text="")
            self.spawn_ball(self.screen_w // 2, self.screen_h // 2)
            self.state = "PLAYING"

    def create_bricks(self):
        
        rows, cols = 10, 24
        brick_w = self.screen_w // cols
        brick_h = 35
        for r in range(rows):
            for c in range(cols):
                x1 = c * brick_w + 5
                y1 = r * brick_h + 50
                x2 = x1 + brick_w - 5
                y2 = y1 + brick_h - 5
                brick = self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill="grey", outline="white", width=2
                )
                self.bricks.append(brick)

    def spawn_ball(self, x, y):
        ball_radius = 10
        ball_id = self.canvas.create_oval(
            x - ball_radius, y - ball_radius, x + ball_radius, y + ball_radius,
            fill="white", outline="black"
        )
        self.balls.append({
            "id": ball_id, "x": x, "y": y, 
            "dx": 6, "dy": -6, "radius": ball_radius
        })

    def break_brick(self, item):
        if item in self.bricks:
            bx1, by1, bx2, by2 = self.canvas.coords(item)
            self.canvas.delete(item)
            self.bricks.remove(item)
            
            drop_roll = random.random()
            ptype = None
            color = ""
            percent = [0.05, 10, 30]
            life_p = percent[0]/100
            gun_p = life_p+(percent[1]/100)
            ball_p = gun_p+(percent[2]/100)
               
            if drop_roll < life_p:         
                ptype = "LIFE"
                color = "green"
            elif drop_roll < gun_p:       
                ptype = "GUN"
                color = "red"
            elif drop_roll < ball_p:       
                ptype = "BALL"
                color = "blue"

            if ptype:
                px, py = (bx1 + bx2) / 2, by2
                pid = self.canvas.create_rectangle(
                    px - 10, py - 10, px + 10, py + 10, 
                    fill=color, outline="white", width=2
                )
                self.powerups.append({"id": pid, "x": px, "y": py, "type": ptype, "dy": 3})

    def fire_bullets(self, paddle_center, paddle_y):
        count = 1 if self.gun_level == 1 else (3 if self.gun_level == 2 else 5)
        speed = 10
        
        if count == 1:
            angles = [0]
        elif count == 3:
            angles = [-30, 0, 30]
        else:
            angles = [-45, -22.5, 0, 22.5, 45]
            
        for angle in angles:
            rad = math.radians(angle)
            dx = math.sin(rad) * speed
            dy = -math.cos(rad) * speed
            bid = self.canvas.create_oval(
                paddle_center - 3, paddle_y - 15, paddle_center + 3, paddle_y - 5, 
                fill="yellow"
            )
            self.bullets.append({"id": bid, "x": paddle_center, "y": paddle_y - 10, "dx": dx, "dy": dy})

    def create_firework(self, cx, cy):
        colors = ["#FF5733", "#33FF57", "#3357FF", "#F033FF", "#FFF033", "#00FFFF", "white"]
        color = random.choice(colors)
        for _ in range(40):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 10)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            pid = self.canvas.create_oval(cx-3, cy-3, cx+3, cy+3, fill=color, outline="")
            
            self.particles.append({"id": pid, "x": cx, "y": cy, "dx": dx, "dy": dy, "life": random.randint(40, 100)})

    def update_game(self):
        
        paddle_x1, paddle_y1, paddle_x2, paddle_y2 = 0, 0, 0, 0
        paddle_width, paddle_center = 0, 0
        try:
            active_win = gw.getActiveWindow()
            if active_win and active_win.title != "Desktop Breaker Overlay":
                paddle_x1, paddle_y1 = active_win.left, active_win.top
                paddle_x2, paddle_y2 = active_win.right, active_win.bottom
                paddle_width = paddle_x2 - paddle_x1
                if paddle_width > 0:
                    paddle_center = paddle_x1 + (paddle_width / 2)
        except Exception:
            pass

        
        if self.state == "PLAYING":
            
            if len(self.bricks) == 0:
                self.state = "CLEARED"
                self.canvas.itemconfig(self.center_text, text="CONGRATULATIONS!", fill="gold")
                
                for p in self.powerups: self.canvas.delete(p["id"])
                for blt in self.bullets: self.canvas.delete(blt["id"])
                for ball in self.balls: self.canvas.delete(ball["id"])
                self.powerups.clear()
                self.bullets.clear()
                self.balls.clear()
                
                self.root.after(10000, self.root.destroy)

            
            for p in self.powerups[:]:
                p["y"] += p["dy"]
                
                if paddle_width > 0 and (paddle_x1 <= p["x"] <= paddle_x2) and \
                   (paddle_y1 - 15 <= p["y"] + 10 <= paddle_y1 + 10):
                    if p["type"] == "GUN":
                        self.gun_level = min(self.gun_level + 1, 3)
                    elif p["type"] == "BALL":
                        self.spawn_ball(p["x"], paddle_y1 - 15)
                    elif p["type"] == "LIFE": 
                        self.lives += 1
                        self.canvas.itemconfig(self.lives_text, text=f"Lives: {self.lives}")
                        
                    self.canvas.delete(p["id"])
                    self.powerups.remove(p)
                    continue
                
                if p["y"] > self.screen_h:
                    self.canvas.delete(p["id"])
                    self.powerups.remove(p)
                    continue
                    
                self.canvas.coords(p["id"], p["x"] - 10, p["y"] - 10, p["x"] + 10, p["y"] + 10)

            
            if self.gun_level > 0 and paddle_width > 0:
                if self.shoot_timer > 0:
                    self.shoot_timer -= 1
                else:
                    self.shoot_timer = 120 
                    self.fire_bullets(paddle_center, paddle_y1)

            for b in self.bullets[:]:
                b["x"] += b["dx"]
                b["y"] += b["dy"]
                
                if b["y"] < 0 or b["x"] < 0 or b["x"] > self.screen_w:
                    self.canvas.delete(b["id"])
                    self.bullets.remove(b)
                    continue
                
                overlapping = self.canvas.find_overlapping(b["x"] - 3, b["y"] - 3, b["x"] + 3, b["y"] + 3)
                hit_brick = False
                for item in overlapping:
                    if item in self.bricks:
                        self.break_brick(item)
                        hit_brick = True
                        break 
                
                if hit_brick:
                    self.canvas.delete(b["id"])
                    self.bullets.remove(b)
                    continue
                    
                self.canvas.coords(b["id"], b["x"] - 3, b["y"] - 3, b["x"] + 3, b["y"] + 3)

            
            for ball in self.balls[:]:
                ball["x"] += ball["dx"]
                ball["y"] += ball["dy"]

                if ball["x"] - ball["radius"] <= 0 or ball["x"] + ball["radius"] >= self.screen_w:
                    ball["dx"] *= -1
                if ball["y"] - ball["radius"] <= 0:
                    ball["dy"] *= -1
                
                if ball["y"] + ball["radius"] >= self.screen_h:
                    self.canvas.delete(ball["id"])
                    self.balls.remove(ball)
                    continue

                if paddle_width > 0 and (paddle_x1 <= ball["x"] <= paddle_x2) and \
                   (paddle_y1 - 10 <= ball["y"] + ball["radius"] <= paddle_y1 + 10) and \
                   ball["dy"] > 0: 
                    hit_ratio = (ball["x"] - paddle_center) / (paddle_width / 2)
                    ball["dx"] = hit_ratio * 10
                    ball["dy"] *= -1
                    ball["y"] = paddle_y1 - ball["radius"]

                ball_bbox = [
                    ball["x"] - ball["radius"], ball["y"] - ball["radius"],
                    ball["x"] + ball["radius"], ball["y"] + ball["radius"]
                ]
                overlapping = self.canvas.find_overlapping(*ball_bbox)
                for item in overlapping:
                    if item in self.bricks:
                        bx1, by1, bx2, by2 = self.canvas.coords(item)
                        prev_x = ball["x"] - ball["dx"]
                        
                        if prev_x + ball["radius"] <= bx1 or prev_x - ball["radius"] >= bx2:
                            ball["dx"] *= -1
                        else:
                            ball["dy"] *= -1
                            
                        self.break_brick(item)
                        break

                self.canvas.coords(
                    ball["id"],
                    ball["x"] - ball["radius"], ball["y"] - ball["radius"],
                    ball["x"] + ball["radius"], ball["y"] + ball["radius"]
                )

            
            if len(self.balls) == 0 and self.state == "PLAYING":
                self.lives -= 1
                self.canvas.itemconfig(self.lives_text, text=f"Lives: {self.lives}")
                
                if self.lives > 0:
                    self.gun_level = 0
                    for p in self.powerups: self.canvas.delete(p["id"])
                    for blt in self.bullets: self.canvas.delete(blt["id"])
                    self.powerups.clear()
                    self.bullets.clear()
                    self.start_countdown()
                else:
                    self.state = "GAMEOVER"
                    self.canvas.itemconfig(self.center_text, text="GAME OVER", fill="red")

        
        elif self.state == "CLEARED":
            self.firework_timer += 1
            
            
            if self.firework_timer % 30 == 0:
                fx = random.randint(100, self.screen_w - 100)
                fy = random.randint(100, self.screen_h // 2)
                self.create_firework(fx, fy)
                
            
            for p in self.particles[:]:
                p["x"] += p["dx"]
                p["y"] += p["dy"]
                p["dy"] += 0.15 
                p["life"] -= 1
                
                if p["life"] <= 0:
                    self.canvas.delete(p["id"])
                    self.particles.remove(p)
                else:
                    self.canvas.coords(p["id"], p["x"]-3, p["y"]-3, p["x"]+3, p["y"]+3)

        self.root.after(4, self.update_game)

if __name__ == "__main__":
    root = tk.Tk()
    game = DesktopBrickBreaker(root)
    root.bind('<Escape>', lambda e: root.destroy())
    root.mainloop()