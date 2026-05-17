**Game Example: Snake Game**
================================

### Requirements

* Python 3.8+
* Pygame library (`pip install pygame`)

### Code


import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Define Constants
WIDTH, HEIGHT = 800, 600
BLOCK_SIZE = 20
SPEED = 10

# Define Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Define Game Variables
score = 0
direction = 'RIGHT'
snake = [(200, 200), (220, 200), (240, 200)]
food = (400, 300)

# Create Game Window
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Game Loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != 'DOWN':
                direction = 'UP'
            elif event.key == pygame.K_DOWN and direction != 'UP':
                direction = 'DOWN'
            elif event.key == pygame.K_LEFT and direction != 'RIGHT':
                direction = 'LEFT'
            elif event.key == pygame.K_RIGHT and direction != 'LEFT':
                direction = 'RIGHT'

    # Move Snake
    head = snake[-1]
    if direction == 'UP':
        new_head = (head[0], head[1] - BLOCK_SIZE)
    elif direction == 'DOWN':
        new_head = (head[0], head[1] + BLOCK_SIZE)
    elif direction == 'LEFT':
        new_head = (head[0] - BLOCK_SIZE, head[1])
    elif direction == 'RIGHT':
        new_head = (head[0] + BLOCK_SIZE, head[1])
    snake.append(new_head)

    # Check Collision with Food
    if snake[-1] == food:
        score += 1
        food = (random.randint(0, WIDTH - BLOCK_SIZE) // BLOCK_SIZE * BLOCK_SIZE,
                random.randint(0, HEIGHT - BLOCK_SIZE) // BLOCK_SIZE * BLOCK_SIZE)
    else:
        snake.pop(0)

    # Check Collision with Wall or Self
    if (snake[-1][0] < 0 or snake[-1][0] >= WIDTH or
            snake[-1][1] < 0 or snake[-1][1] >= HEIGHT or
            snake[-1] in snake[:-1]):
        print(f"Game Over! Your score is {score}.")
        pygame.quit()
        sys.exit()

    # Draw Game
    screen.fill(BLACK)
    for pos in snake:
        pygame.draw.rect(screen, WHITE, pygame.Rect(pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))
    pygame.draw.rect(screen, RED, pygame.Rect(food[0], food[1], BLOCK_SIZE, BLOCK_SIZE))
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))
    pygame.display.flip()

    # Cap FPS
    pygame.time.Clock().tick(SPEED)


### Explanation

This code creates a simple Snake game using Pygame. The game window is 800x600 pixels, and the snake moves at a speed of 10 FPS. The snake can be controlled using the arrow keys, and the game ends if the snake collides with the wall or itself. The score is displayed at the top left corner of the screen.