import pygame

pygame.init()

WIDTH, HEIGHT = 600, 480
PANEL_HEIGHT = 80
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# define some node positions
nodes = [(100, 100), (200, 100), (300, 100), (400, 100), (500, 100)]

# define which nodes connect to which (by index)
edges = [(0, 1), (1, 2), (0, 3), (2, 4), (3, 4)]

# --- Runner setup (small circle traveling along the edges) ---
runner_radius = 6
runner_color = (255, 180, 60)
runner_edge_idx = 0
runner_t = 0.0          # 0.0 -> 1.0 progress along the current edge
runner_speed = 0.02     # fraction of the edge covered per frame

# --- Button setup ---
class Button:
    def __init__(self, rect, label, callback):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.callback = callback
        self.hovered = False

    def draw(self, surface):
        color = (90, 90, 140) if self.hovered else (60, 60, 90)
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, (150, 150, 200), self.rect, width=1, border_radius=6)
        text_surf = font.render(self.label, True, (230, 230, 230))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()



def add_node():
    print("Add Node clicked")

def add_edge():
    print("Add Edge clicked")

def reset_graph():
    print("Reset clicked")


panel_y = HEIGHT - PANEL_HEIGHT
button_w, button_h = 120, 40
gap = 20
start_x = 30

buttons = [
    Button((start_x, panel_y + (PANEL_HEIGHT - button_h) // 2, button_w, button_h), "Add Node", add_node),
    Button((start_x + (button_w + gap), panel_y + (PANEL_HEIGHT - button_h) // 2, button_w, button_h), "Add Edge", add_edge),
    Button((start_x + 2 * (button_w + gap), panel_y + (PANEL_HEIGHT - button_h) // 2, button_w, button_h), "Reset", reset_graph),
]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for b in buttons:
            b.handle_event(event)

    # --- update runner position ---
    runner_t += runner_speed
    if runner_t >= 1.0:
        runner_t = 0.0
        runner_edge_idx = (runner_edge_idx + 1) % len(edges)

    a_idx, b_idx = edges[runner_edge_idx]
    ax, ay = nodes[a_idx]
    bx, by = nodes[b_idx]
    runner_x = ax + (bx - ax) * runner_t
    runner_y = ay + (by - ay) * runner_t

    screen.fill((20, 20, 20))

    # draw lines first so circles sit on top
    for a, b in edges:
        pygame.draw.line(screen, (150, 150, 150), nodes[a], nodes[b], 1)

    # draw circles
    for pos in nodes:
        pygame.draw.circle(screen, (200, 200, 255), pos, 15)

    # draw the runner on top
    pygame.draw.circle(screen, runner_color, (int(runner_x), int(runner_y)), runner_radius)

    # --- draw bottom panel ---
    pygame.draw.rect(screen, (35, 35, 45), (0, panel_y, WIDTH, PANEL_HEIGHT))
    pygame.draw.line(screen, (80, 80, 80), (0, panel_y), (WIDTH, panel_y), 2)

    for b in buttons:
        b.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()